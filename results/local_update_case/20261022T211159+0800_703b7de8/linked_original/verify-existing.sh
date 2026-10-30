#!/bin/zsh
set -eu
cd /Users/freya/Documents/git-folder/mem0_halumem_diagnosis
conda run -n mem0_halumem python scripts/local_smoke.py --verify-run /Users/freya/Documents/git-folder/mem0_halumem_diagnosis/results/local_smoke/20261022T203207+0800_a40c12d5
