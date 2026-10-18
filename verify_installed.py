import sys,pathlib,tempfile,subprocess,json,hashlib,os
ROOT=pathlib.Path(__file__).absolute().parent
PYTHON=pathlib.Path(sys.argv[1]).absolute()
CONSOLE=PYTHON.parent/'midi-pedal-ledger'
CASES=json.loads((ROOT/'smoke.json').read_text())
with tempfile.TemporaryDirectory() as d:
 work=pathlib.Path(d)
 def run(args,expected):
  proc=subprocess.run([str(CONSOLE),*map(str,args)],cwd=work,capture_output=True,text=True,timeout=20)
  assert proc.returncode==expected,(proc.returncode,expected,proc.stdout,proc.stderr)
  return proc
 run(['--help'],0)
 for i,case in enumerate(CASES):
  source=work/('case'+str(i));raw=bytes.fromhex(case['data']);source.write_bytes(raw)
  proc=run([source,*case['args']],case['exit']);r=json.loads(proc.stdout)
  assert eval(case['assertion'],{'r':r,'abs':abs,'len':len})
  assert source.read_bytes()==raw
 bad=work/'bad';bad.write_bytes(b'NOT A VALID FORMAT')
 proc=run([bad,*CASES[0]['args']],2);assert not proc.stdout and proc.stderr
 if 'midi-pedal-ledger' in ('midi-pedal-ledger','dbf-record-audit'):
  generated=work/'invented';run(['--make-example',generated],0);before=generated.read_bytes()
  run([generated],0);run(['--make-example',generated],2);assert generated.read_bytes()==before
 print(json.dumps({'installed_console':'midi-pedal-ledger','cases':len(CASES),'malformed_exit':2,'source_bytes_preserved':True,'cwd_outside_checkout':True}))
