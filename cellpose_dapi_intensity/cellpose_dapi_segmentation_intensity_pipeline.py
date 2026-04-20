#!/usr/bin/env python3
"""
Per-ROI measurements (2D, Cellpose v4 robust, RGB-aware) with PARAMETERS header.

- ONLY segments *_dapi_* files.
- For each labeled DAPI nucleus, measure green-channel intensity per ROI.
- Removes cp_diameter from outputs.
- Prepends a PARAMETERS section at the top of the CSV (key,value pairs), then a blank line, then the MEASUREMENTS table.

PARAMETERS include:
    model = cellpose4_generalist
    channels = [0,0]
    diameter = 35
    flow_threshold = 0.4
    cellprob_threshold = 3.0
    normalize_percentiles = [1,99]
    pixel_size_x_nm = 0.0642
    pixel_size_y_nm = 0.0642

Assumes 2D (H,W) or RGB (H,W,3). If RGB, DAPI=Blue (2), GREEN=Green (1).
"""

import sys
import math
import warnings
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import re

import numpy as np
import pandas as pd
from tifffile import imread, imwrite

# ---- Cellpose import ----
try:
    from cellpose import models
except Exception as e:
    print(f"[ERROR] Failed to import cellpose: {e}", file=sys.stderr)
    models = None

# =======================
# USER SETTINGS (edit me)
# =======================
input_dir = Path("/Volumes/Antoine_5/PostDocVienna/cdc7/CDK12_flag/Quant/to_process")        # <-- EDIT
mask_dir  = Path("/Volumes/Antoine_5/PostDocVienna/cdc7/CDK12_flag/Quant/masks/")          # <-- EDIT
out_csv   = Path("/Volumes/Antoine_5/PostDocVienna/cdc7/CDK12_flag/Quant/measurements.csv")  # <-- EDIT
use_gpu   = True  # Use GPU if available

# If images are RGB, choose channels:
DAPI_RGB_CHANNEL_INDEX  = 2  # Blue for DAPI
GREEN_RGB_CHANNEL_INDEX = 1  # Green for intensity

# Cellpose params based on your example
DAPI_PARAMS = {
    "channels": [0, 0],
    "diameter": 35,
    "flow_threshold": 0.3,
    "cellprob_threshold": 2.0,
    "normalize": [1, 99],
}

# Pixel size (as provided), units: micrometers per pixel (parameter is wrongly named NM but it is all good)
PIXEL_SIZE_X_NM = 0.0642
PIXEL_SIZE_Y_NM = 0.0642

ALLOWED_EXTS = {".tif", ".tiff"}

FNAME_RE = re.compile(
    r'^(?P<genotype>[^_]+)_(?P<channel>dapi|green)_gonad_(?P<gonad>\d+)_part_(?P<part>\d+)\.(?:tif|tiff)$',
    re.IGNORECASE
)

def parse_fname(fname: str) -> Optional[Dict[str, Any]]:
    m = FNAME_RE.match(fname)
    if not m:
        return None
    d = m.groupdict()
    d["genotype"] = d["genotype"].lower()
    d["channel"] = d["channel"].lower()
    d["gonad"] = int(d["gonad"])
    d["part"] = int(d["part"])
    return d

def ensure_2d_or_rgb(img: np.ndarray, path: Path) -> Optional[np.ndarray]:
    if img.ndim == 2:
        return img
    if img.ndim == 3 and img.shape[2] == 3:
        return img
    warnings.warn(f"Skipping unsupported image (need 2D or RGB): {path.name} shape={img.shape}")
    return None

def to_float(img: np.ndarray) -> np.ndarray:
    if np.issubdtype(img.dtype, np.integer):
        return img.astype(np.float32, copy=False)
    return img.astype(np.float32, copy=False)

def extract_channel(img: np.ndarray, chan_index: int) -> np.ndarray:
    if img.ndim == 2:
        return img
    return img[..., int(chan_index)]

def percentile_normalize(img: np.ndarray, p1: float, p2: float) -> np.ndarray:
    img = to_float(img)
    lo = np.percentile(img, p1)
    hi = np.percentile(img, p2)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        lo = float(img.min())
        hi = float(img.max()) if img.max() > lo else lo + 1.0
    img = np.clip(img, lo, hi)
    img = (img - lo) / (hi - lo)
    return img

def build_green_name(meta: Dict[str, Any]) -> str:
    return f"{meta['genotype']}_green_gonad_{meta['gonad']:02d}_part_{meta['part']:02d}.tif"

def build_mask_name(meta: Dict[str, Any]) -> str:
    return f"{meta['genotype']}_dapi_gonad_{meta['gonad']:02d}_part_{meta['part']:02d}_mask.tif"

def fallback_green_name(dapi_name: str) -> str:
    return dapi_name.replace("_dapi_", "_green_", 1)

def cellpose_eval_robust(mdl, img_norm: np.ndarray) -> np.ndarray:
    out = mdl.eval(
        img_norm,
        channels=DAPI_PARAMS["channels"],
        diameter=DAPI_PARAMS["diameter"],
        flow_threshold=DAPI_PARAMS["flow_threshold"],
        cellprob_threshold=DAPI_PARAMS["cellprob_threshold"],
        do_3D=False,
        normalize=False,
        resample=True,
    )
    if isinstance(out, tuple):
        masks = out[0]
    else:
        masks = out
    return masks.astype(np.uint16)

def per_object_measurements(mask: np.ndarray, green: np.ndarray):
    labels = np.unique(mask)
    labels = labels[labels != 0]
    for lab in labels:
        roi = (mask == lab)
        area = int(roi.sum())
        if area == 0:
            raw = 0.0
            mean = float('nan')
            equiv_diam = float('nan')
        else:
            vals = green[roi]
            raw = float(vals.sum())
            mean = float(raw / area)
            equiv_diam = 2.0 * (area / np.pi) ** 0.5
        yield int(lab), raw, area, mean, float(equiv_diam)

def write_parameters_header(csv_path: Path):
    lines = []
    lines.append("PARAMETERS,key,value")
    lines.append("PARAMETERS,model,cellpose4_generalist")
    lines.append(f"PARAMETERS,channels,\"{DAPI_PARAMS['channels']}\"")
    lines.append(f"PARAMETERS,diameter,{DAPI_PARAMS['diameter']}")
    lines.append(f"PARAMETERS,flow_threshold,{DAPI_PARAMS['flow_threshold']}")
    lines.append(f"PARAMETERS,cellprob_threshold,{DAPI_PARAMS['cellprob_threshold']}")
    lines.append(f"PARAMETERS,normalize_percentiles,\"{DAPI_PARAMS['normalize']}\"")
    lines.append(f"PARAMETERS,pixel_size_x_µm,{PIXEL_SIZE_X_NM}")
    lines.append(f"PARAMETERS,pixel_size_y_µm,{PIXEL_SIZE_Y_NM}")
    lines.append("")
    csv_path.write_text("\n".join(lines))

def append_dataframe(csv_path: Path, df: pd.DataFrame):
    df.to_csv(csv_path, mode="a", index=False)

def main():
    print(f"[INFO] Input: {input_dir}")
    print(f"[INFO] Masks: {mask_dir}")
    print(f"[INFO] CSV:   {out_csv}")
    mask_dir.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    if models is None:
        print("[FATAL] Cellpose not available; aborting.", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Initializing Cellpose (generalist)...")
    mdl = models.CellposeModel(gpu=use_gpu)
    print("[INFO] Cellpose ready. GPU =", use_gpu)

    write_parameters_header(out_csv)

    dapi_files = []
    for p in input_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTS and "_dapi_" in p.name.lower():
            dapi_files.append(p)
    dapi_files.sort()

    rows = []

    for dapi_path in dapi_files:
        meta = parse_fname(dapi_path.name)
        green_name = build_green_name(meta) if meta else fallback_green_name(dapi_path.name)
        green_path = dapi_path.parent / green_name
        if not green_path.exists():
            warnings.warn(f"Missing green image for {dapi_path.name}: expected {green_name}")
            continue

        dapi_img = imread(str(dapi_path))
        green_img = imread(str(green_path))
        dapi_in = ensure_2d_or_rgb(dapi_img, dapi_path)
        green_in = ensure_2d_or_rgb(green_img, green_path)
        if dapi_in is None or green_in is None:
            continue

        dapi_2d = extract_channel(dapi_in, DAPI_RGB_CHANNEL_INDEX)
        green_2d = extract_channel(green_in, GREEN_RGB_CHANNEL_INDEX)
        dapi_norm = percentile_normalize(dapi_2d, *DAPI_PARAMS['normalize'])
        mask = cellpose_eval_robust(mdl, dapi_norm)

        mask_name = build_mask_name(meta) if meta else dapi_path.stem + "_mask.tif"
        rel_parent = dapi_path.parent.relative_to(input_dir) if dapi_path.parent != input_dir else Path("")
        mask_out = (mask_dir / rel_parent / mask_name)
        mask_out.parent.mkdir(parents=True, exist_ok=True)
        imwrite(str(mask_out), mask, photometric="minisblack")

        for lab, raw, area, mean, equiv_diam in per_object_measurements(mask, green_2d):
            rows.append({
                "genotype": meta['genotype'] if meta else "",
                "gonad": meta['gonad'] if meta else -1,
                "part": meta['part'] if meta else -1,
                "file_base": dapi_path.stem.replace("_dapi_", "_"),
                "nucleus_id": int(lab),
                "raw_intensity": raw,
                "area_pixels": area,
                "mean_intensity": mean,
                "equiv_diameter_px": equiv_diam,
                "mask_path": str(mask_out),
                "dapi_image": str(dapi_path),
                "green_image": str(green_path),
            })

    df = pd.DataFrame.from_records(rows)
    append_dataframe(out_csv, df)

if __name__ == "__main__":
    main()
