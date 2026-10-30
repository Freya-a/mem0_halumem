#!/bin/zsh
set -eu
cd /Users/freya/Documents/git-folder/mem0_halumem_diagnosis
# Fill local credentials before running. Each run gets fresh databases.
# Restore exact installed versions if needed:
# conda run -n mem0_halumem python -m pip install -r /Users/freya/Documents/git-folder/mem0_halumem_diagnosis/results/local_smoke/20261022T202837+0800_bcdcdf1e/requirements-freeze.txt
conda run -n mem0_halumem python -m pip check
conda run -n mem0_halumem python scripts/local_smoke.py
