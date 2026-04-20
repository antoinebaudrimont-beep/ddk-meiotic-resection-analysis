# ImageJ foci intensity quantification and ratio analysis

This folder contains an ImageJ/Fiji macro and a Bash post-processing script used to quantify fluorescence foci within manually defined nuclei.

The workflow was developed for microscopy images in which nuclei are manually annotated as ROIs, local fluorescence maxima are detected inside each nucleus, and the intensity of each detected focus is compared with the background or mean nuclear intensity.

## Files

```text
foci_intensity_quantification.ijm
analyze_foci_intensity_ratio.sh
