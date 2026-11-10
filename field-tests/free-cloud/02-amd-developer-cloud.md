# 02 AMD Developer Cloud 赠金（官方实读，2026-11-09）

来源：AMD 官方页 [AMD Developer Cloud](https://www.amd.com/en/developer/resources/cloud-access/amd-developer-cloud.html)，2026-11-09 curl 抓取（HTTP 200）；`devcloud.amd.com` 直接跳登录页，未登录未注册。原页与摘录在 `evidence/02-amd-devcloud/`。

## 官方写明的内容
- 通过第三方云平台提供 AMD Instinct **MI300X** GPU；两种方式：按量付费，或**申请**免费赠金。
- 加入 AMD AI Developer Program 的合格开发者可获首笔 **$100** 赠金（"Terms and conditions apply"）。
- 面向独立开发者和开源贡献者（ML、底层编程、AI 应用）；是否发放、发多少由 AMD 根据用途（推理/训练/微调）和详细使用说明**自行决定**。
- 获批后 3 个工作日内入账，显示在控制台 "My AMD Home"。
- 机型：1×MI300X（192 GB 显存、20 vCPU、240 GB 内存、720 GB 启动盘、5 TB 临时盘）或 8×MI300X。

## 官方写明的坑
- 赠金入账后 **30 天过期**。
- **关机照样计费/扣赠金**，只有销毁实例才停。
- 赠金用完或过期且没有绑卡：GPU VM 和数据被销毁；绑了卡则用完**自动扣卡**。
- 赠金只覆盖 MI300X GPU，挂载卷、对象存储、备份不在内。
- 条款含美国出口管制条款，其中禁止用于在中国、香港、澳门开发超级计算机等特定用途（原文见摘录）。

## 推测/未验证
- $100 能跑多少小时：官方页没写单价，本清单不编；需另查第三方平台定价后再补。
- 中国大陆开发者能否获批：官方页未写国家限制细节（除出口管制条款），未亲测。
