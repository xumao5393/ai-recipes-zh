# 时间(开始): 2026-11-09 17:32:34 EST
# 命令: unshare -rn node --test test/   (cwd=clone 根，README L79 原样)
# exit=1 耗时=0.107s
node:internal/modules/cjs/loader:1568
  throw err;
  ^

Error: Cannot find module '<workspace>/crossborder/sandbox/05-dsh-trade-assistant/src/test'
    at Module._resolveFilename (node:internal/modules/cjs/loader:1564:15)
    at wrapResolveFilename (node:internal/modules/cjs/loader:1118:27)
    at defaultResolveImplForCJSLoading (node:internal/modules/cjs/loader:1142:10)
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 49.002056

✖ failing tests:

test at test:1:1
✖ test (41.637779ms)
  'test failed'
