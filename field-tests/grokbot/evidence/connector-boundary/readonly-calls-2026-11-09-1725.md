# 只读调用实测（2026-11-09 约17:23 EST，n=1）
（脱敏版：账号地址与 Mao 邮箱/网盘的计数属于私人数据，已删除；原件在本专题 internal-archive/connector-boundary/，见 MASKING.txt。）
1. Gmail get_me → 调用成功，返回账号地址（<account>）和邮件、会话总数（已读到计数，数值不公开）。
2. Gmail search_emails query="newer_than:7d" idsOnly=true maxResults=500 → 调用成功，返回 message id 列表（已读到计数，数值不公开）。未读任何正文。
3. Drive search visibility="anyoneWithLink" pageSize=50 → 调用成功（结果不公开）。
   未查 anyoneCanFind / domainWithLink。
未做任何写入、发送、分享、删除。消息 id、文件名未入库。
