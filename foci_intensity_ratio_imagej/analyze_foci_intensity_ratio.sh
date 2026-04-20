#!/bin/bash

# Input and output files
input_file="nuclei_intensity_results_cdc7_g03_th75_z7.csv"
aligned_file="aligned_results_cdc7_g03_th75_z7.csv"
output_file="nuclei_ratio_analysis_cdc7_g03_th75_z7.csv"
debug_file="debug_log.txt"

# Step 1: Fix misaligned data
awk -F',' '
BEGIN {
    OFS = ",";
    print "Debug Log" > "'"$debug_file"'";
}
{
    # Check for lines that only have ROI_Mean_Intensity_Excluding_Spots
    if ($1 == "" && NF == 2) {
        if (prev_nucleus != "") {
            # Assign the value to the current nucleus
            roi_mean_intensity_map[prev_nucleus] = $2;
        } else {
            print "Error: Misaligned data with no preceding nucleus on line " NR >> "'"$debug_file"'";
        }
    } else {
        # Process valid lines
        prev_nucleus = $1;
        data[NR] = $0;
    }
}
END {
    # Output the fixed data
    for (i = 1; i <= NR; i++) {
        if (data[i] != "") {
            split(data[i], fields, FS);
            if (fields[1] != "" && roi_mean_intensity_map[fields[1]] != "") {
                # Append ROI_Mean_Intensity_Excluding_Spots to the line
                print data[i], roi_mean_intensity_map[fields[1]];
            } else {
                # Keep the line as is
                print data[i];
            }
        }
    }
}
' "$input_file" > "$aligned_file"

# Step 2: Analyze aligned data and compute the ratio
awk -F',' '
BEGIN {
    OFS = ",";
    print "Nucleus,Count_Ratio_Over_2" > "'"$output_file"'";
}
NR > 1 { # Skip header row
    nucleus = $1;
    mean_intensity = $4;
    roi_mean_intensity = $7;

    # Handle nucleus transitions
    if (nucleus != current_nucleus && current_nucleus != "") {
        # Output the count for the previous nucleus
        if (roi_mean_intensity_map[current_nucleus] == "") {
            print "Warning: Missing ROI_Mean_Intensity for " current_nucleus >> "'"$debug_file"'";
        }
        print current_nucleus, count_over_2 >> "'"$output_file"'";
        count_over_2 = 0; # Reset counter
    }

    # Update the current nucleus
    current_nucleus = nucleus;

    # Store the latest ROI_Mean_Intensity value for each nucleus
    if (roi_mean_intensity != "") {
        roi_mean_intensity_map[nucleus] = roi_mean_intensity;
    }

    # Calculate the ratio if ROI_Mean_Intensity is available
    if (roi_mean_intensity_map[nucleus] > 0) {
        ratio = mean_intensity / roi_mean_intensity_map[nucleus];
        if (ratio > 2) {
            count_over_2++;
        }
    }
}
END {
    # Handle the last nucleus
    if (current_nucleus != "") {
        if (roi_mean_intensity_map[current_nucleus] == "") {
            print "Warning: Missing ROI_Mean_Intensity for " current_nucleus >> "'"$debug_file"'";
        }
        print current_nucleus, count_over_2 >> "'"$output_file"'";
    }
}
' "$aligned_file"