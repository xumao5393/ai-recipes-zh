# 手算（写于运行前）· 规则来自 assets/workbench.html 装柜模块

来源行号（commit e4c909ec）：
- VEHICLES：约 L6152–6160
- lgEffDims：packMode==='thick' 时 `{l:l+2*th, w:w+2*th, h:h+2*th}`；packMode==='rate' 时按体积膨胀
- lgGross：`net + tare + (usePallet ? palletWeight : 0)`
- totalCbm：对每件 `lgEffDims(it).l * .w * .h * qty / 1e6` 求和（与是否装得下无关）
- totalGw：`lgGross(it) * qty` 求和
- containerVol（装载率分母）：`v.w * v.h * v.d`（cm³），不是表里的 `v.vol`
- usage（装载率）：`usedVolume / containerVol * 100`，usedVolume 是已放入箱的占位体积 `bw*bh*bd` 之和（含间隙）
- nEst：`max(1, ceil(totalCbm/(v.vol*0.85)), ceil(totalGw/(v.maxWeight*0.9)))`

手算只对 **totalCbm / totalGw / nEst** 做闭合运算；装载率 usage 依赖排布引擎，留给脚本对照，手算不猜。

## A · 50×40×30 ×100，无包装，20GP / 40HQ
- eff = 50×40×30
- totalCbm = 50×40×30×100 / 1e6 = **6.000000**
- totalGw = (10+1)×100 = **1100**
- 20GP nEst = max(1, ceil(6/(33.2*0.85))=ceil(6/28.22)=ceil(0.2126)=1, ceil(1100/(28000*0.9))=ceil(1100/25200)=1) = **1**
- 40HQ nEst = max(1, ceil(6/(76.3*0.85))=ceil(6/64.855)=1, ceil(1100/(26000*0.9))=1) = **1**

## B · 同上，packThick=2
- eff = 54×44×34
- totalCbm = 54×44×34×100 / 1e6 = 8078400/1e6 = **8.078400**
- totalGw = **1100**（包装不计入毛重公式）
- 20GP nEst = max(1, ceil(8.0784/28.22)=ceil(0.2863)=1, 1) = **1**
- 40HQ nEst = max(1, ceil(8.0784/64.855)=ceil(0.1246)=1, 1) = **1**

## C · demoItems，无包装
- Watch: 46×32×28×600 / 1e6 = 24729600/1e6 = 24.729600；gw=(14+1)×600=9000
- Speaker: 60×40×40×120 / 1e6 = 11520000/1e6 = 11.520000；gw=(22+2)×120=2880
- Kit: 40×30×20×90 / 1e6 = 2160000/1e6 = 2.160000；gw=(6+0.5)×90=585
- **totalCbm = 24.7296 + 11.52 + 2.16 = 38.409600**
- **totalGw = 9000 + 2880 + 585 = 12465**
- 20GP nEst = max(1, ceil(38.4096/28.22)=ceil(1.3611)=2, ceil(12465/25200)=ceil(0.4946)=1) = **2**
- 40HQ nEst = max(1, ceil(38.4096/64.855)=ceil(0.5922)=1, ceil(12465/23400)=ceil(0.5327)=1) = **1**

以上手算是照源码规则写的，只能证明代码按它自己的规则在算，不能证明柜型容积表或装载算法对真实装柜合理。
