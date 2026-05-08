#!/usr/bin/bash

SIM_ROOT_FOLDER="/home/evangeloskatralis/Documents/simulations/chromaticity_LHC_Collision"

for chroma in $(seq -w 0 5 25); do
    echo "Generating plots for chromaticity: $chroma"
    python 001_generate_instability_plots.py --root_folder "$SIM_ROOT_FOLDER" --chroma "$chroma" --cmap "tab20"
    python 001_generate_instability_plots.py --root_folder "$SIM_ROOT_FOLDER" --chroma "$chroma" --cmap "magma"
done