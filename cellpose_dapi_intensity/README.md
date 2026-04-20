# DAPI segmentation and green-channel intensity quantification pipeline

This script performs automated segmentation of DAPI-stained nuclei using Cellpose and quantifies fluorescence intensity in a second channel (green) on a per-nucleus basis.

## Purpose

This pipeline was used to extract quantitative measurements of fluorescence signals from microscopy images by combining segmentation of nuclei (DAPI channel) with per-ROI intensity measurements in the green channel.

## Features

- Automated nucleus segmentation using Cellpose
- Support for 2D and RGB images
- Extraction of per-nucleus intensity values
- Automatic pairing of DAPI and green channel images
- Output of structured CSV files with:
  - experimental metadata
  - segmentation parameters
  - per-ROI measurements

## Input

- TIFF images (`.tif`, `.tiff`)
- Filenames must follow:
genotype_channel_gonad_X_part_Y.tif
Example:
cdc7_dapi_gonad_1_part_1.tif
cdc7_green_gonad_1_part_1.tif

## Output

- CSV file containing:
  - a PARAMETERS section
  - a MEASUREMENTS table with per-nucleus values

## Requirements

- Python 3
- cellpose (v4)
- numpy
- pandas
- tifffile

## Usage

Edit paths in the script:

python
input_dir = Path("path/to/images")
mask_dir  = Path("path/to/masks")
out_csv   = Path("measurements.csv")

Run:
python cellpose_dapi_segmentation_intensity_pipeline.py
Notes

* Only DAPI images are segmented
* Green channel is used for intensity quantification
* Pixel size should be adapted to the dataset
* GPU usage can be enabled with:
use_gpu = True

---

# ⚠️ Important fixes before upload

## 1. Remove hardcoded paths

Replace:
``python
input_dir = Path("/Volumes/Antoine_5/...")
with:
input_dir = Path("path/to/images")





