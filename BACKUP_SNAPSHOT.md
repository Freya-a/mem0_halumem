# Baseline backup snapshot

This snapshot records the local project before the next method is added, including the native mem0 baseline, HaluMem data, diagnosis, variants, and development-subset results in `results/`.

The two upstream repositories are included as ordinary directories, not Git submodules, so their checked-out files remain in this snapshot:

- HaluMem: https://github.com/MemTensor/HaluMem, commit `718f16ff0c83413b1c86fa83fc13cc1a639871f9`.
- mem0 v0.1.118: https://github.com/mem0ai/mem0, commit `ed5a1e9fc68fcd7671a70c33a540d24573755449`.

Local environment files containing credentials, Python bytecode/cache directories, and the nested repositories' `.git` metadata were excluded. Existing ignore rules remain unchanged; results and ignored data were explicitly added for this snapshot, but new files under ignored paths need to be explicitly added in future commits.
