# DDK meiotic resection analysis

This repository contains code and documentation associated with the DDK meiotic resection project in *Caenorhabditis elegans*.

It is intended as a file repository linked to the DDK manuscript. The scripts provided here were used to process, quantify, or document specific analyses related to meiotic chromosome behavior, DDK-dependent recombination phenotypes, and microscopy-based measurements.

## Repository content

### 1. DAPI segmentation and fluorescence intensity quantification

`cellpose_dapi_segmentation_intensity_pipeline.py`

This Python pipeline segments DAPI-stained nuclei using Cellpose and quantifies fluorescence intensity in a paired green channel on a per-nucleus basis.

The script was designed for microscopy datasets in which DAPI images are used to define nuclear regions of interest and a second fluorescence channel is measured within those regions.

Main outputs include structured CSV files containing:

- segmentation parameters
- experimental metadata
- per-nucleus intensity measurements

A separate README describing this script is provided in `ReadMe.md`.

## Intended use

The repository is provided for transparency and reproducibility. The scripts are intended to document the analysis logic used for the associated study rather than to serve as a fully generalized software package.

Users should adapt paths, filenames, pixel sizes, segmentation parameters, and channel naming conventions to their own datasets before running the scripts.

## Requirements

Requirements depend on the specific script. For the currently included Cellpose-based pipeline, the main dependencies are:

- Python 3
- Cellpose
- NumPy
- pandas
- tifffile

Additional dependencies may be required as more analysis modules are added.

## Manuscript citation

This repository is associated with the manuscript:

**DDK promotes meiotic DNA-end resection in *Caenorhabditis elegans***  
Antoine Baudrimont et al.

Full citation, DOI, and publication details will be added once available.

## Repository status

This repository is under active curation. Additional scripts, documentation, and analysis-specific README files may be added as the manuscript-associated datasets are finalized.

## Contact

For questions about the analyses or scripts, please contact:

Antoine Baudrimont  
GitHub: `antoinebaudrimont-beep`

## License

This repository is released under the MIT License. See the `LICENSE` file for details.
