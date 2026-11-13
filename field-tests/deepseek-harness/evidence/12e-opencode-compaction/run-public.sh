#!/bin/bash
# 公开副本 2026-11-09 23:31 EST：原件已移到 internal-archive（sha256 b731d2efa72ecd6a3dac038eccd7fe5e40aeb5585b3d66d446a1359a3e57af5f）。与原件唯一差别是 R= 这一行：原件写的是本机绝对路径，这里改成必须由读者自己设置的环境变量。其余逐字相同。
# usage: run.sh TAG PORT STEPS BYTES PT_CSV [CONFIG_EXTRA_JSON]
set -u
R=${R:?请先 export R=<你的工作目录>，见正文「复现」}; D=$R/repo/evidence/12e-opencode-compaction; E=$D/run-$1
rm -rf $E $D/_raw_run-$1; mkdir -p $E
H=$R/sandbox-m12e/home-$1; rm -rf $H; mkdir -p $H/.config/opencode
W=$R/sandbox-m12e/workdir; rm -rf $W; mkdir -p $W; echo hello > $W/hello.txt
EXTRA=${6:-}
cat > $H/.config/opencode/opencode.json <<J
{"\$schema":"https://opencode.ai/config.json","model":"deepseek/deepseek-flash"$EXTRA,
 "providers":{"deepseek":{"settings":{"baseURL":"http://127.0.0.1:$2/v1","headerTimeout":5000,"chunkTimeout":5000}}}}
J
cp $H/.config/opencode/opencode.json $E/opencode.json
python3 $R/tools/oai_compaction_probe_server.py $2 $E $3 $4 $5 > $E/server.log 2>&1 & SP=$!
sleep 0.8; cd $W
s=$(date +%s.%N)
HOME=$H XDG_CONFIG_HOME=$H/.config XDG_DATA_HOME=$H/.local/share XDG_STATE_HOME=$H/.local/state XDG_CACHE_HOME=$H/.cache DEEPSEEK_API_KEY=dummy-replay OPENCODE_DISABLE_AUTOUPDATE=1 timeout ${TO:-120} $R/sandbox-opencode/node_modules/.bin/opencode run --format json "run the steps" > $E/run.jsonl 2> $E/run.err
rc=$?; e=$(date +%s.%N)
echo "tag=$1 steps=$3 bytes=$4 pt=$5 exit=$rc elapsed=$(python3 -c "print(round($e-$s,3))")s opencode=$($R/sandbox-opencode/node_modules/.bin/opencode --version 2>/dev/null | head -1)" > $E/summary.txt
sleep 0.3; kill $SP; cat $E/summary.txt
for f in $E/req-*.meta.json; do python3 -c "import json,sys;m=json.load(open('$f'));print(m['i'],m['kind'],m['body_len'],m['n_messages'],m['tools_n'],m['max_tokens'],repr(m['last_user_head'][:70]))"; done
