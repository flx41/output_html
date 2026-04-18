# digdog.html (原 stock.html) 数据获取渠道 v0.0.1（2026-04-17 确认）

## 数据源总览

| 数据类型 | 主力数据源 | 备用数据源 | 状态 |
|---------|-----------|-----------|------|
| 日/周/月K线 | Tushare API | 腾讯 web.ifzq | ✅ 可用 |
| 分钟线(5/30/60分) | 东方财富 JSONP | 腾讯 web.ifzq | ✅ 可用 |
| 实时行情 | 腾讯 qt.gtimg.cn | - | ✅ 可用 |
| 股票搜索 | Tushare API | - | ✅ 可用 |

## 各数据源详情

### 1. Tushare API (后端代理)
- **用途**: 日/周/月K线数据（主力数据源）
- **端点**: `/stock/daily`, `/stock/weekly`, `/stock/monthly`
- **限制**: GitHub Pages 上因 CORS 限制不可用
- **状态**: ✅ 可用

### 2. 东方财富 (JSONP)
- **用途**: 分钟线数据（主力数据源）
- **端点**: `https://push2his.eastmoney.com/api/qt/stock/kline/get`
- **特点**: JSONP 方式，不受 CORS 限制
- **状态**: ✅ 可用

### 3. 腾讯 (两套接口)
- **K线**: `https://web.ifzq.gtimg.cn/appstock/app/kline/kline` (备用)
- **实时**: `https://qt.gtimg.cn/q=` (实时行情专用)
- **状态**: ✅ 可用

### 4. 新浪 (已废弃)
- **用途**: K线数据（备用数据源，但代码中有实现）
- **端点**: `https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketDataService.getKLineData`
- **状态**: ❌ 已废，未启用

## 数据获取流程

```
用户查询股票
    ↓
fetchData(code, period)
    ├─ 日/周/月K线
    │   ├─ GitHub Pages → 腾讯 web.ifzq
    │   └─ 其他环境 → Tushare → 腾讯 web.ifzq
    │
    └─ 分钟线(5/30/60分)
        └─ 东方财富 JSONP → 腾讯 web.ifzq

实时行情单独调用
    └─ fetchRealtime(code) → 腾讯 qt.gtimg.cn
```

## 备注
- 东方财富 JSONP 不受 CORS 限制，GitHub Pages 可用
- Tushare 在 GitHub Pages 上因 CORS 跳过
- 新浪代码已实现但未启用
- 实时行情每30秒刷新一次（交易时间内）
