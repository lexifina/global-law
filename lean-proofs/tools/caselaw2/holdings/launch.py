"""Start a long job detached, without a window: python launch.py <log> <tpm> <cmd...>
The job's TPM is read from <log>.tpm (editable while it runs)."""
import os, subprocess, sys
log, tpm, cmd = sys.argv[1], sys.argv[2], sys.argv[3:]
open(log + ".tpm", "w").write(tpm)
env = dict(os.environ, HOLDINGS_TPM=tpm, HOLDINGS_TPM_FILE=log + ".tpm", PYTHONUNBUFFERED="1")
flags = 0x08000000 | 0x00000200 | 0x01000000 | 0x00004000
p = subprocess.Popen(cmd, stdout=open(log, "a"), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env,
                     creationflags=flags, cwd=os.path.dirname(os.path.abspath(__file__)), close_fds=True)
open(log + ".pid", "w").write(str(p.pid))
print(p.pid)
