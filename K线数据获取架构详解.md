# 现行 HTML K线数据获取架构详解

> 更新日期：2026-04-15
> 来源文件：digdog.html (原 stock.html) v0.0.1

---

## 1. 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    search() 查询入口                      │
│         同时发起 K线数据 + 实时行情 两个并行请求            │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│  fetchData()    │             │  fetchRealtime() │
│  K线历史数据     │             │  实时行情        │
└─────────────────┘             └─────────────────┘
          │                               │
          ▼                               │
┌─────────────────────────────┐           │
│      数据源自动切换           │           │
│  (按优先级逐个尝试)           │           │
└─────────────────────────────┘           │
          │                               │
    ┌─────┴─────┐                         │
    ▼           ▼                         │
┌────────┐  ┌────────┐          ┌────────────────┐
│日/周/月 │  │分钟线  │          │ 腾讯实时行情    │
│数据源   │  │数据源  │          │ qt.gtimg.cn   │
└────────┘  └────────┘          └────────────────┘
```

---

## 2. 数据源优先级配置（2026-04-14固定）

### fetchData() 核心逻辑（2471-2553行）

```javascript
// 判断是否分钟线
const isMinutePeriod = ['5', '30', '60'].includes(period);

// 分钟线：东方财富 → 腾讯
if (isMinutePeriod) {
    sources = [
        { name: '东方财富', fn: fetchEastMoney },
        { name: '腾讯', fn: fetchTencent },
    ];
}
// 日/周/月：Tushare → 腾讯（GitHub Pages跳过Tushare）
else {
    const isGitHubPages = window.location.hostname.includes('github.io');
    if (isGitHubPages) {
        sources = [{ name: '腾讯', fn: fetchTencent }];
    } else {
        sources = [
            { name: 'Tushare', fn: fetchTushareDaily },
            { name: '腾讯', fn: fetchTencent },
        ];
    }
}
```

### 数据源优先级表

| 周期类型 | 主力数据源 | 备用数据源 | 备注 |
|---------|-----------|-----------|------|
| 日/周/月K | Tushare | 腾讯 web.ifzq | Tushare需要后端支持 |
| 分钟线(5/30/60分) | 东方财富(JSONP) | 腾讯 web.ifzq | 东方财富不受CORS限制 |
| 实时行情 | 腾讯 qt.gtimg.cn | - | 单独调用，10秒刷新 |

**GitHub Pages特殊处理**：由于CORS限制，GitHub Pages上跳过Tushare，直接使用腾讯API。

---

## 3. 各数据源详细解析

### 3.1 Tushare（日/周/月主力）

**位置**：2128-2190行

```
API地址：http://localhost:5000/api（本地后端）
├── /api/stock/daily?code={code}&limit=200    // 日K
├── /api/stock/weekly?code={code}&limit=200   // 周K
├── /api/stock/monthly?code={code}&limit=200  // 月K
├── /api/stock/info?code={code}               // 股票信息
└── /api/stock/search?keyword={keyword}       // 搜索股票
```

**特点**：
- 需要本地后端服务（Python Flask）
- 数据质量最高，有复权处理
- GitHub Pages上不可用（CORS限制）

---

### 3.2 腾讯API（主要备用）

**位置**：2316-2354行

```
URL: https://web.ifzq.gtimg.cn/appstock/app/kline/kline

参数格式：
├── 日K:   param=sh600519,day,,,200
├── 周K:   param=sh600519,week,,,200
├── 月K:   param=sh600519,month,,,200
├── 5分钟:  param=sh600519,m5,,,200
├── 30分钟: param=sh600519,m30,,,200
└── 60分钟: param=sh600519,m60,,,200
```

**返回数据结构**：
```json
{
  "data": {
    "sh600519": {
      "day": [
        ["2024-01-15", "开盘", "收盘", "最高", "最低", "成交量"],
        ...
      ]
    }
  }
}
```

**特点**：
- 通过CORS代理访问（`fetchWithProxy`）
- 分钟线参数用`m`前缀（m5/m30/m60）
- 数据稳定，但分钟线偶有缺失

---

### 3.3 东方财富API（分钟线主力）

**位置**：2356-2435行

```
URL: https://push2his.eastmoney.com/api/qt/stock/kline/get

参数：
├── secid: 1.{code}（上海）或 0.{code}（深圳）
├── klt: 周期参数
│   ├── 101 = 日K
│   ├── 102 = 周K
│   ├── 103 = 月K
│   ├── 5   = 5分钟
│   ├── 30  = 30分钟
│   └── 60  = 60分钟
├── fqt: 1（前复权）
├── end: 20500101（获取所有）
├── lmt: 200（条数）
└── cb: {callbackName}（JSONP回调）
```

**JSONP调用流程**：
```javascript
1. 生成唯一回调函数名：emCallback_时间戳_随机数
2. 将回调函数挂载到 window 对象
3. 创建 <script> 标签加载API
4. API返回时调用回调函数
5. 解析逗号分隔的数据："日期,开盘,收盘,最高,最低,成交量"
6. 清理：删除回调函数、移除script标签
```

**特点**：
- **不受CORS限制**（JSONP方式）
- 有10秒超时处理
- 非交易时间可能无分钟数据
- 日期格式：`20251111`（无分隔符）

---

### 3.4 新浪API（备用，代码中有但未使用）

**位置**：2437-2469行

```
URL: https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketDataService.getKLineData

参数：
├── symbol: sh600519
├── scale: 240(日K)/1680(周K)/7200(月K)/5/30/60
├── ma: no
└── datalen: 200
```

**注意**：虽然有实现，但不在主数据源列表中。

---

## 4. 实时行情（独立模块）

**位置**：2205-2314行

```
URL: https://qt.gtimg.cn/q={市场前缀}{代码}
示例: https://qt.gtimg.cn/q=sh600519
```

**返回格式**：GBK编码，波浪号分隔

| 字段索引 | 内容 | 示例 |
|---------|------|------|
| [1] | 股票名称 | 贵州茅台 |
| [3] | 当前价格 | 1850.00 |
| [4] | 昨收价 | 1845.00 |
| [31] | 涨跌额 | +5.00 |
| [32] | 涨跌幅 | +0.27% |
| [37] | 成交额(万) | 256800 |
| [38] | 换手率 | 0.21 |
| [39] | 市盈率 | 35.6 |

**刷新策略**：
- 立即获取一次
- 每10秒定时刷新
- **仅交易时间刷新**（9:30-11:30, 13:00-15:00）

---

## 5. CORS代理机制

**位置**：2070-2126行

```javascript
// 当前只有一个代理
const CORS_PROXIES = [
    'https://kline-proxy.yangm2000.workers.dev/?url=',
];

// fetchWithProxy 流程：
1. 先尝试直接请求（5秒超时）
2. 失败后使用代理（8秒超时）
3. 所有代理都失败则报错
```

---

## 6. 数据验证与清洗

**位置**：2512-2537行

```javascript
// 严格过滤无效数据
validData = data.filter(d => {
    if (!d || !d.time) return false;           // 必须有时间和数据
    if (typeof d.open !== 'number') return false;  // 开盘价必须是数字
    if (typeof d.high !== 'number') return false;  // 最高价必须是数字
    if (typeof d.low !== 'number') return false;   // 最低价必须是数字
    if (typeof d.close !== 'number') return false; // 收盘价必须是数字
    if (d.high < d.low) return false;              // 最高不能小于最低
    return true;
});

// 按时间排序并去重
validData.sort((a, b) => a.time - b.time);
uniqueData = validData.filter((d, i, arr) => 
    i === 0 || d.time !== arr[i-1].time
);

// 最少10条数据
if (validData.length < 10) throw new Error('有效数据不足');
```

---

## 7. 市场前缀判断规则

```javascript
function getMarketPrefix(code) {
    // 指数代码判断
    if (code === '000001' || code === '000300') return 'sh';  // 上证指数、沪深300
    if (code === '399001' || code === '399006' || code === '399005') return 'sz';  // 深证成指、创业板指、中小板指
    
    // 股票代码判断
    if (code.startsWith('6')) return 'sh';  // 上海主板
    if (code.startsWith('0') || code.startsWith('3')) return 'sz';  // 深圳主板/创业板
    
    return 'sz';  // 默认深圳
}
```

---

## 8. 日期转时间戳函数

```javascript
function dateToTimestamp(dateStr) {
    // 格式: "2025-11-11" 或 "20251111"
    const normalized = dateStr.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3');
    const parts = normalized.split('-');
    // 使用UTC时间创建日期，避免时区问题
    const date = new Date(Date.UTC(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2])));
    return Math.floor(date.getTime() / 1000);
}
```

---

## 9. 完整调用流程图

```
用户点击"查询"
       │
       ▼
search() 开始
       │
       ├──────────────────────────────┐
       ▼                              ▼
fetchData(code, period)      fetchRealtime(code)
       │                              │
       ▼                              ▼
判断周期类型                  直接请求 qt.gtimg.cn
       │                              │
  ┌────┴────┐                         │
  ▼         ▼                         │
分钟线?   日/周/月?                     │
  │         │                         │
  ▼         ▼                         │
东方财富  GitHub Pages?                │
  │      ┌──┴──┐                      │
  │      ▼     ▼                      │
  │    是     否                      │
  │      │     │                      │
  │      ▼     ▼                      │
  │    腾讯  Tushare                   │
  │      │     │                      │
  │      └──┬──┘                      │
  │         │                         │
  ▼         ▼                         │
尝试数据源                             │
  │         │                         │
  │    成功? │                         │
  │    ┌──┴──┐                        │
  │    ▼     ▼                        │
  │   是    否 → 尝试下一个数据源       │
  │    │                              │
  ▼    ▼                              │
数据验证与清洗                          │
  │                                    │
  ▼                                    │
返回 {data, source}                    │
  │                                    │
  └──────────────┬─────────────────────┘
                 │
                 ▼
         Promise.all 等待两个请求
                 │
                 ▼
         更新UI + 图表显示
```

---

## 10. 代码位置索引

| 功能模块 | 行号范围 |
|---------|---------|
| CORS代理配置 | 2070-2126 |
| Tushare数据源 | 2128-2190 |
| 市场前缀判断 | 2192-2203 |
| 实时行情接口 | 2205-2241 |
| 实时行情刷新 | 2283-2314 |
| 腾讯API | 2316-2354 |
| 东方财富API | 2356-2435 |
| 新浪API（备用）| 2437-2469 |
| fetchData主函数 | 2471-2553 |
| search查询函数 | 2558-2607 |

---

## 总结

这个架构设计的核心优点是**自动故障转移**：
- 按优先级尝试多个数据源
- 一个失败自动切换到下一个
- 确保用户总能获取到数据

数据源可靠性排序：
1. **Tushare**（需后端，数据最全）
2. **东方财富**（JSONP无CORS限制，分钟线首选）
3. **腾讯**（稳定但需代理）
4. **新浪**（格式不稳定，最后备用）
