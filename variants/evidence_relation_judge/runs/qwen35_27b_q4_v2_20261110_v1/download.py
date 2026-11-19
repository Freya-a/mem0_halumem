"""Download pinned official bytes via the HF mirror resolver and verify before promotion."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib, math, os, subprocess, sys, time

root=Path(__file__).resolve().parents[2]
directory=root/'model/Qwen3.5-27B-Q4_K_M'
prefix=directory/'Qwen3.5-27B-Q4_K_M.gguf.part'
target=directory/'Qwen3.5-27B-Q4_K_M.gguf'
size=16740812704
expected='84b5f7f112156d63836a01a69dc3f11a6ba63b10a23b8ca7a7efaf52d5a2d806'
url='https://hf-mirror.com/unsloth/Qwen3.5-27B-GGUF/resolve/3221f178a6b842d04f1fb42f1c413534adcc0a6a/Qwen3.5-27B-Q4_K_M.gguf'
if target.exists():
    raise SystemExit('Final model already exists; do not overwrite')
start=prefix.stat().st_size
chunk=math.ceil((size-start)/8)
parts=[]
for i in range(8):
    low=start+i*chunk; high=min(size,low+chunk)-1
    if low<=high: parts.append((directory/f'range_{i:02}',low,high))
print('prefix_bytes',start,'ranges',[(x[1],x[2]) for x in parts],flush=True)
def fetch(item):
    path,low,high=item
    got=path.stat().st_size if path.exists() else 0
    if got>high-low+1: raise RuntimeError(f'oversized {path}')
    if got<high-low+1:
        with path.open('ab') as out:
            cmd=['curl','--noproxy','*','--silent','--show-error','--fail','--location','--connect-timeout','20','--range',f'{low+got}-{high}',url]
            subprocess.run(cmd,stdout=out,check=True)
    if path.stat().st_size!=high-low+1: raise RuntimeError(f'incomplete {path}')
    print('completed',path.name,flush=True)
with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(fetch,parts))
combined=directory/'Qwen3.5-27B-Q4_K_M.gguf.verifying'
hash_obj=hashlib.sha256()
with combined.open('xb') as out:
    for path in [prefix]+[x[0] for x in parts]:
        with path.open('rb') as inp:
            while block:=inp.read(8*1024*1024):
                hash_obj.update(block); out.write(block)
actual=hash_obj.hexdigest()
print('sha256',actual,'size',combined.stat().st_size,flush=True)
if actual!=expected or combined.stat().st_size!=size: raise SystemExit('Verification failed; file retained for inspection')
os.link(combined,target)
combined.unlink()
for path in [prefix]+[x[0] for x in parts]: path.unlink()
print('verified and installed',target,flush=True)
