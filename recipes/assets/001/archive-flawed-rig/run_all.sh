#!/bin/bash
# 正式实测。每档用不同 SEED 独立跑（同样的请求会命中接口缓存，必须换 SEED）。
# v1：FETCH_MAX_CHARS=12000（结果在 runs/v1_fetch12000）
# v2：FETCH_MAX_CHARS=5000 （结果在 runs/v2_fetch5000）
cd "$(dirname "$0")"
PY=${PY:-python}
MAXC=${FETCH_MAX_CHARS:-5000}
OUT=${OUT:-runs/v2_fetch5000}; mkdir -p $OUT
LEVELS=${LEVELS:-"level1 level2 level3"}
for seed in 11 22 33; do
  for l in $LEVELS; do
    echo "== $l seed=$seed $(date '+%F %T %Z')"
    FETCH_MAX_CHARS=$MAXC SEED=$seed $PY harness.py $l $OUT/${l}_seed${seed} 2>&1 | grep -v '^ *|'
  done
done
