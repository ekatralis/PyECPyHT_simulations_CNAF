#!/usr/bin/env bash
set -euo pipefail

SIM_ROOT_FOLDER="/home/evangeloskatralis/Documents/simulations/chromaticity_LHC_Collision"

# Default to 4 if no argument is given
MAX_JOBS="${1:-4}"

echo "Running with MAX_JOBS=$MAX_JOBS"

parallel -j $MAX_JOBS \
  python 001_generate_instability_plots.py \
    --root_folder "$SIM_ROOT_FOLDER" \
    --chroma {1} \
    --cmap {2} \
  ::: $(seq -w 0 5 25) \
  ::: tab20 magma