#!/bin/bash
# usage: R=<this project root> run.sh TAG PORT STEPS BYTES PT_CSV [PT_AFTER]
# needs: dsh 0.2.2-rc.1 at $R/sandbox/node_modules/.bin/dsh ; probe server at $R/tools/anthropic_compaction_probe_server.py
set -u
: "${R:?set R}"; E=$R/repo/evidence/12f-dsh-compaction/run-$1
rm -rf $E $R/repo/evidence/12f-dsh-compaction/_raw_run-$1; mkdir -p $E
H=$R/sandbox-m12f/home-$1; rm -rf $H; mkdir -p $H
W=$R/sandbox-m12f/workdir; mkdir -p $W; rm -rf $W/*; echo hello > $W/hello.txt
PT_AFTER=${6:-} python3 $R/tools/anthropic_compaction_probe_server.py $2 $E $3 $4 $5 > $E/server.log 2>&1 & SP=$!
sleep 0.8; cd $W
s=$(date +%s.%N)
HOME=$H DEEPSEEK_BASE_URL=http://127.0.0.1:$2 DEEPSEEK_API_KEY=dummy-replay timeout ${TMO:-90} $R/sandbox/node_modules/.bin/dsh --profile headless --json "run the steps" > $E/run.jsonl 2> $E/run.err
rc=$?; e=$(date +%s.%N)
echo "tag=$1 steps=$3 bytes=$4 pt=$5 pt_after=${6:-none} exit=$rc elapsed=$(python3 -c "print(round($e-$s,3))")s" > $E/summary.txt
sleep 0.3; kill $SP; cat $E/summary.txt
python3 - "$E" <<'PY'
import json,glob,sys,collections
E=sys.argv[1]; ms=[json.load(open(f)) for f in sorted(glob.glob(E+"/req-*.meta.json"))]
c=collections.Counter(m["kind"].split("(")[0] for m in ms); print("requests",len(ms),dict(c))
for m in ms[:14]: print(m["i"],m["kind"],"msgs",m["n_messages"],"tr",m["tool_results_in_history"],"ckpt",m["has_checkpoint"],"len",m["body_len"],"max",m["max_tokens"])
PY
