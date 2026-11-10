// 用本机 npm 自带的 semver 包实际计算（不联网）
const semver = require(process.argv[2]);
const v = '0.2.2-rc.1', r = '^0.2.1-rc.5';
console.log('semver pkg version:', require(process.argv[2] + '/package.json').version);
console.log(`satisfies(${v}, ${r}) =`, semver.satisfies(v, r));
console.log(`satisfies(${v}, ${r}, {includePrerelease:true}) =`, semver.satisfies(v, r, { includePrerelease: true }));
console.log('validRange:', semver.validRange(r));
for (const x of ['0.2.1-rc.5','0.2.1','0.2.2','0.2.9','0.3.0']) console.log(`satisfies(${x}) =`, semver.satisfies(x, r));
