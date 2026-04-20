// ImageJ macro to mark nuclei, detect maxima within each nucleus, measure intensity, and save results

// Open an image
//open("/Users/paouned6/Desktop/rpa1_cdc7.tif");

// Convert the image to 8-bit if necessary
//run("8-bit");

// Initialize the ROI Manager
roiManager("reset");

// Prompt the user to manually mark nuclei
waitForUser("Mark all nuclei with the ROI Manager, then click OK to proceed.");


// Get the list of ROIs representing nuclei
//roiManager("Save", "/Users/paouned6/Desktop/nuclei.zip");
roiManager("Save", "/Users/paouned6/Desktop/nuclei.zip");
// Create a results file
resultsPath = File.directory + "nuclei_intensity_results.csv";
File.open(resultsPath);
//print("Nucleus,Maxima_X,Maxima_Y,Mean_Intensity,Integrated_Density");
File.append("Nucleus,Maxima_X,Maxima_Y,Mean_Intensity,Integrated_Density,nPoints", resultsPath);

// Create a second results file
//resultsPathtwo = File.directory + "count_rpa1.csv";
//File.open(resultsPathtwo);
//File.append("Nucleus,nPoints", resultsPathtwo);
// Loop through each nucleus
roiManager("reset");
roiManager("Open", "/Users/paouned6/Desktop/nuclei.zip");
nNuclei = roiManager("count");

for (i = 0; i < nNuclei; i++) {
    // Select the current nucleus ROI
    roiManager("Select", i);
//    roiManager("Measure");
    // Get the coordinates of the current nucleus
    roiName = RoiManager.getName(i);   
    run("Find Maxima...", "prominence=45 output=[Point Selection] strict");

    // Get the list of point selections (maxima)
    getSelectionCoordinates(xpoints, ypoints);
    nPoints = lengthOf(xpoints);

    // Loop through each maximum and create a circular ROI around it
    for (j = 0; j < nPoints; j++) {
        x = xpoints[j];
        y = ypoints[j];
        makeOval(x-2.5, y-2.5, 5, 5);  // Draw a circle of 5 pixels diameter centered at each point
        run("Measure");
        // Optionally, annotate the image with the detected maxima
roiManager("Show All with labels");
        // Get the measured mean intensity and integrated density
        meanIntensity = getResult("Mean", nResults-1);
        integratedDensity = getResult("RawIntDen", nResults-1);
        
        // Save the results to the external file
//        File.open(resultsPath);
        File.append(roiName + "," + x + "," + y + "," + meanIntensity + "," + integratedDensity +"," + nPoints, resultsPath);
// File.open(resultsPathtwo);
       // File.append(roiName + "," + nPoints, resultsPathtwo);
    }
    
    // Clear results for the next nucleus
    roiManager("Deselect");
    run("Clear Results");
}

// Close the results file
//File.close(resultsPath+ "nuclei_intensity_results.csv");

print("Analysis complete. Results saved to " + resultsPath);
