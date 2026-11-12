# ai-recipes-zh 006 标准答案计算脚本（Python 3，无第三方依赖）
import json
def irr_monthly(pv, pmts):
    lo, hi = 0.0, 0.1
    for _ in range(200):
        r = (lo + hi) / 2
        v = sum(p / (1 + r) ** (i + 1) for i, p in enumerate(pmts))
        if v > pv: lo = r
        else: hi = r
    return r
N = 12
P = 7699.0
fund_y = 0.013
fm = (1 + fund_y) ** (1 / 12) - 1   # 货币基金按月复利的月收益率
# A 信用卡账单分期
feeA = round(P * 0.006, 2)
prinA = P / N
pA = [prinA + feeA] * N
# B 等额本息 年化15%
rb = 0.15 / 12
pmtB = P * rb / (1 - (1 + rb) ** -N)
pB = [pmtB] * N
# C 免息不立减
pC = [7999 / N] * N
def end_balance(cash0, pays):
    b = cash0
    for p in pays:
        b = b * (1 + fm) - p
    return b
cash = 8000.0
res = {}
for k, pays in [('A', pA), ('B', pB), ('C', pC)]:
    r = irr_monthly(P, pays)
    tot = sum(pays)
    res[k] = {
        'monthly_payment': round(pays[0], 2),
        'total_paid': round(tot, 2),
        'extra_vs_D_nominal': round(tot - P, 2),
        'irr_monthly_pct': round(r * 100, 4),
        'apr_nominal_pct': round(r * 12 * 100, 2),
        'apr_effective_pct': round(((1 + r) ** 12 - 1) * 100, 2),
        'cash_after_12m': round(end_balance(cash, pays), 2),
    }
dD = (cash - P) * (1 + fm) ** 12
res['D'] = {'total_paid': P, 'cash_after_12m': round(dD, 2)}
for k in res:
    res[k]['net_cost_vs_keeping_8000'] = round(cash * (1 + fm) ** 12 - res[k]['cash_after_12m'], 2)
rank = sorted(res, key=lambda k: -res[k]['cash_after_12m'])
out = {'fund_monthly_rate_pct': round(fm * 100, 5), 'results': res, 'rank_best_to_worst': rank,
       'best': rank[0], 'saving_vs_second': round(res[rank[0]]['cash_after_12m'] - res[rank[1]]['cash_after_12m'], 2),
       'why_not_7_2': '0.6% 每期按最初全部本金收手续费，但本金每月在减少，平均只占用约一半本金约 6.5 个月，所以真实年化约为 7.2% 的 1.8 倍'}
print(json.dumps(out, ensure_ascii=False, indent=2))
json.dump(out, open('answer_key.json', 'w'), ensure_ascii=False, indent=2)

# 自检：复现人民银行公告〔2021〕第3号附件示例（10万元、先付1000元服务费、每月8833.3元×12）
r = irr_monthly(99000, [8833.3] * 12)
print('PBOC 示例自检：单利口径(名义) %.2f%%（公告 12.80%%），IRR 复利口径 %.2f%%（公告 13.58%%）' % (r * 1200, ((1 + r) ** 12 - 1) * 100))
