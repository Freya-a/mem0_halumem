#!/bin/zsh
set -eu
cd /home/shu1004/ld/system/mem0_halumem_diagnosis
# Fill local credentials before running. Each run gets fresh databases.
# Restore exact installed versions if needed:
# conda run -n mem0_halumem python -m pip install -r /home/shu1004/ld/system/mem0_halumem_diagnosis/results/local_smoke/20261028T145645+0800_51d0925c/requirements-freeze.txt
conda run -n mem0_halumem python -m pip check
conda run -n mem0_halumem python scripts/local_smoke.py --env-file /home/shu1004/ld/system/mem0_halumem_diagnosis/.env.local
