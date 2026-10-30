#!/bin/zsh
set -eu
cd /Users/freya/Documents/git-folder/mem0_halumem_diagnosis
conda run --no-capture-output -n mem0_halumem python scripts/verify_update_case.py /Users/freya/Documents/git-folder/mem0_halumem_diagnosis/results/local_update_case/20261022T211159+0800_703b7de8
