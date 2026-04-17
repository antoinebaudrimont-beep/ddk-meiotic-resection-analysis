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