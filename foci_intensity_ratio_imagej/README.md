Workflow overview

The analysis is performed in two steps.

1. ImageJ/Fiji macro

foci_intensity_quantification.ijm

The ImageJ macro performs the primary image quantification.

It:

1. Resets the ROI Manager.
2. Prompts the user to manually mark nuclei.
3. Saves the manually defined nuclear ROIs.
4. Reopens the ROI set.
5. Detects fluorescence maxima inside each nuclear ROI using ImageJ’s Find Maxima function.
6. Creates a small circular ROI around each detected maximum.
7. Measures the mean intensity and integrated density of each detected focus.
8. Exports the results as a CSV file.

The main output file is:

nuclei_intensity_results.csv

The output table contains:
Nucleus
Maxima_X
Maxima_Y
Mean_Intensity
Integrated_Density
nPoints

where:

* Nucleus is the ROI name from the ROI Manager.
* Maxima_X and Maxima_Y are the coordinates of each detected maximum.
* Mean_Intensity is the mean fluorescence intensity measured in the circular ROI around the maximum.
* Integrated_Density is the raw integrated density of the same ROI.
* nPoints is the number of maxima detected in the corresponding nucleus.

2. Bash post-processing script

analyze_foci_intensity_ratio.sh

The Bash script post-processes the CSV output.

It performs two operations:

1. It corrects misaligned rows in the CSV file when the mean nuclear intensity excluding spots is present on a separate line.
2. It calculates, for each nucleus, how many detected foci have an intensity ratio greater than 2.

The ratio is calculated as:

focus mean intensity / mean nuclear intensity excluding spots

The script counts the number of foci per nucleus for which:
ratio > 2

The main output file is:
nuclei_ratio_analysis_cdc7_g03_th75_z7.csv

This file contains:
Nucleus
Count_Ratio_Over_2
A debug file is also generated:

debug_log.txt


This file reports missing or misaligned values detected during processing.

Input requirements

ImageJ/Fiji macro

The macro requires:

* Fiji or ImageJ
* An opened fluorescence microscopy image
* Manually defined nuclear ROIs added to the ROI Manager

The macro currently uses:

Find Maxima prominence = 45
Circular ROI diameter = 5 pixels

These parameters may need to be adjusted depending on image resolution, signal intensity, and background level.

Bash script

The Bash script requires a CSV file containing focus intensity measurements and mean nuclear intensity values.

The current script expects the input filename:

nuclei_intensity_results_cdc7_g03_th75_z7.csv

and generates:
aligned_results_cdc7_g03_th75_z7.csv
nuclei_ratio_analysis_cdc7_g03_th75_z7.csv
debug_log.txt

Filenames should be edited directly in the script before running it on a new dataset.

How to run

Step 1: Run the ImageJ/Fiji macro

1. Open the fluorescence image in Fiji.
2. Open the ROI Manager.
3. Manually mark each nucleus and add it to the ROI Manager.
4. Run:

foci_intensity_quantification.ijm

5. When prompted, confirm that all nuclei have been marked.
6. The macro will detect foci, measure intensities, and save the results as a CSV file.


Step 2: Run the Bash script

Place the CSV file in the same folder as the Bash script, then run:
bash analyze_foci_intensity_ratio.sh


The script will generate an aligned CSV file, a per-nucleus ratio summary, and a debug log.

Notes and limitations

This workflow is semi-automated. Nuclear segmentation is performed manually through the ROI Manager, while foci detection is automated using ImageJ’s Find Maxima function.

The current macro contains hard-coded paths for saving and reopening the ROI file:
/Users/paouned6/Desktop/nuclei.zip

These paths should be edited before use on another computer or dataset.

The current Bash script also contains hard-coded input and output filenames. These should be modified for each experiment.

The intensity threshold used in the Bash script is fixed at:
ratio > 2
This threshold should be interpreted as an analysis parameter and adjusted only if justified by the experimental design.

Repository context

This analysis folder is part of the repository associated with the DDK meiotic resection project in Caenorhabditis elegans.

The scripts are provided to document the image-analysis workflow used for quantifying fluorescence foci and estimating the number of enriched foci per nucleus.



