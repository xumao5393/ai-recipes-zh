#!/bin/bash
# 公开副本 2026-11-10 01:30 EST：原件在 internal-archive（sha256 3633a514a746f830a51fec2e3db84acd2e63e21e220edab43ca732f22f24c848）。与原件唯一差别是 R= 这一行：原件写的是本机绝对路径，这里改成必须由读者自己设置的环境变量。其余逐字相同。
# usage: run.sh TAG PORT STEPS BYTES PT_CSV [TIMEOUT]   (env PT_AFTER, CT, EXTRA_ENV passed through)
set -u
R=${R:?请先 export R=<你的工作目录>，见正文「复现」}; D=$R/repo/evidence/12g-claude-code-compaction; E=$D/run-$1
rm -rf $E $D/_raw_run-$1; mkdir -p $E
H=$R/sandbox-m12g/home-$1; rm -rf $H; mkdir -p $H
W=$R/sandbox-m12g/workdir-$1; rm -rf $W; mkdir -p $W; echo hello > $W/hello.txt
python3 $R/tools/cc_compaction_probe_server.py $2 $E $3 $4 $5 > $E/server.log 2>&1 & SP=$!
sleep 0.8; cd $W; s=$(date +%s.%N)
env HOME=$H ANTHROPIC_BASE_URL=http://127.0.0.1:$2 ANTHROPIC_API_KEY=dummy-replay ANTHROPIC_MODEL=${MODEL:-deepseek-v4-flash} DISABLE_TELEMETRY=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 ${EXTRA_ENV:-} \
  timeout ${6:-120} $R/sandbox-claude-code/node_modules/.bin/claude -p --output-format json --allowedTools Bash --max-turns $(( $3 + 4 )) "run the steps" > $E/run.json 2> $E/run.err
rc=$?; e=$(date +%s.%N)
echo "tag=$1 steps=$3 bytes=$4 pt=$5 PT_AFTER=${PT_AFTER:-} CT=${CT:-} MODEL=${MODEL:-deepseek-v4-flash} EXTRA_ENV=${EXTRA_ENV:-} exit=$rc elapsed=$(python3 -c "print(round($e-$s,3))")s" > $E/summary.txt
sleep 0.3; kill $SP; cat $E/summary.txt
python3 - $E <<'PY'
import json,glob,sys
for f in sorted(glob.glob(sys.argv[1]+"/req-*.meta.json")):
    m=json.load(open(f)); print(m["i"],m["path"][:30],m["kind"],"msgs",m["n_messages"],"tr",m["tool_results_in_history"],"max_tokens",m["max_tokens"],"len",m["body_len"],"|",m["last_user_head"][:70].replace("\n"," "))
PY
