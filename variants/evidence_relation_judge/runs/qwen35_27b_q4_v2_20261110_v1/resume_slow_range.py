from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import math,subprocess
root=Path(__file__).resolve().parents[2]/'model/Qwen3.5-27B-Q4_K_M'
base=root/'range_01'
first=3212802292+base.stat().st_size
end=5145375207
chunk=math.ceil((end+1-first)/8)
url='https://hf-mirror.com/unsloth/Qwen3.5-27B-GGUF/resolve/3221f178a6b842d04f1fb42f1c413534adcc0a6a/Qwen3.5-27B-Q4_K_M.gguf'
parts=[(root/f'range_01_sub_{i:02}',first+i*chunk,min(end,first+(i+1)*chunk-1)) for i in range(8) if first+i*chunk<=end]
print('subranges',[(a,b) for _,a,b in parts],flush=True)
def fetch(item):
 p,a,b=item
 got=p.stat().st_size if p.exists() else 0
 if got>b-a+1: raise RuntimeError('oversized')
 if got<b-a+1:
  with p.open('ab') as out: subprocess.run(['curl','--noproxy','*','--silent','--show-error','--fail','--location','--connect-timeout','20','--range',f'{a+got}-{b}',url],stdout=out,check=True)
 if p.stat().st_size!=b-a+1: raise RuntimeError('incomplete')
 print('complete',p.name,flush=True)
with ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(fetch,parts))
with base.open('ab') as out:
 for p,a,b in parts:
  with p.open('rb') as f:
   while block:=f.read(8*1024*1024): out.write(block)
if base.stat().st_size!=5145375207-3212802292+1: raise RuntimeError('wrong merged length')
for p,_,_ in parts: p.unlink()
print('range_01 complete',flush=True)
