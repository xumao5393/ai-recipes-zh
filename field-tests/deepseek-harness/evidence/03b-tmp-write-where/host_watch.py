#!/usr/bin/env python3
"""Sample host /proc while 03b bash sleeps. Mask hostname/user paths. No environ values."""
import os, time, json, re, pathlib, sys

OUT = pathlib.Path(sys.argv[1])
MARKER = sys.argv[2]
DURATION = float(sys.argv[3]) if len(sys.argv)>3 else 20.0
OUT.mkdir(parents=True, exist_ok=True)
host_ns = os.readlink('/proc/self/ns/mnt')
samples = []
t0 = time.time()
seen_pids = set()

def mask(s: str) -> str:
    s = re.sub(r'/home/[^/\s]+', '/home/<user>', s)
    s = re.sub(r'grok-bot-vm-\d+', '<host>', s)
    s = re.sub(r'/workspace/fourday-[^\s]*', '/workspace/<evidence-root>/...', s)
    return s

while time.time() - t0 < DURATION:
    snap = {"t": round(time.time()-t0, 3), "procs": []}
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        base = f'/proc/{pid}'
        try:
            cmd = open(f'{base}/cmdline','rb').read().replace(b'\x00', b' ').decode('utf-8','replace').strip()
        except Exception:
            continue
        if not cmd:
            continue
        interesting = False
        low = cmd.lower()
        if 'bwrap' in low or ('bash' in low and ('dsh03b' in cmd or MARKER in cmd or '/tmp/dsh03b' in cmd)):
            interesting = True
        if 'dsh' in low and 'headless' in low:
            interesting = True
        if not interesting:
            continue
        info = {"pid": int(pid), "cmd": mask(cmd)[:500]}
        try:
            info["ppid"] = int(open(f'{base}/status').read().split('PPid:')[1].split('\n',1)[0].strip())
        except Exception:
            pass
        try:
            info["ns_mnt"] = os.readlink(f'{base}/ns/mnt')
            info["ns_mnt_same_as_host"] = (info["ns_mnt"] == host_ns)
        except Exception as e:
            info["ns_mnt_err"] = type(e).__name__
        # environ: names only
        try:
            env = open(f'{base}/environ','rb').read().split(b'\x00')
            names = []
            for e in env:
                if not e: continue
                if b'=' in e:
                    names.append(e.split(b'=',1)[0].decode('utf-8','replace'))
            info["environ_names"] = sorted(set(names))
            info["environ_name_count"] = len(info["environ_names"])
        except Exception:
            pass
        # mountinfo /tmp lines
        try:
            lines = []
            for line in open(f'{base}/mountinfo'):
                parts = line.split()
                if len(parts) > 4 and (parts[4] == '/tmp' or parts[4].startswith('/tmp/')):
                    lines.append(mask(line.rstrip()))
            info["mountinfo_tmp_lines"] = lines
        except Exception:
            pass
        # root/tmp listing for marker
        try:
            root_tmp = f'{base}/root/tmp'
            if os.path.isdir(root_tmp):
                hits = [x for x in os.listdir(root_tmp) if MARKER in x or x.startswith('dsh03b')]
                info["root_tmp_marker_hits"] = hits
                for h in hits:
                    p = os.path.join(root_tmp, h)
                    try:
                        info.setdefault("root_tmp_files", {})[h] = {
                            "size": os.path.getsize(p),
                            "content_head": open(p).read(200)
                        }
                    except Exception as e:
                        info.setdefault("root_tmp_files", {})[h] = {"err": type(e).__name__}
        except Exception as e:
            info["root_tmp_err"] = type(e).__name__
        snap["procs"].append(info)
        seen_pids.add(int(pid))
    if snap["procs"]:
        samples.append(snap)
    time.sleep(0.25)

host = {
    "host_ns_mnt": host_ns,
    "marker": MARKER,
    "host_tmp_ls_marker": [x for x in os.listdir('/tmp') if MARKER in x or x.startswith('dsh03b')],
    "samples_with_procs": len(samples),
    "samples": samples,
}
open(OUT/'host-watch.json','w').write(json.dumps(host, indent=2, ensure_ascii=False))
open(OUT/'host-ns-mnt.txt','w').write(host_ns+'\n')
print('samples', len(samples), 'seen_pids', sorted(seen_pids))
