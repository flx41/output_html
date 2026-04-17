# 腾讯股票数据接口文档

> 更新日期：2026-04-14
> 无需认证，免费调用

---

## 一、实时行情接口

### 接口地址
```
https://qt.gtimg.cn/q={股票代码}
```

### 请求示例
```
单只股票：https://qt.gtimg.cn/q=sh600519
多只股票：https://qt.gtimg.cn/q=sh600519,sz000858,sh000001
```

### 返回格式
- 编码：GBK
- 格式：`v_{市场代码}="字段1~字段2~...";`

### 字段对照表

| 序号 | 字段名 | 示例值 | 说明 |
|------|--------|--------|------|
| 0 | 市场代码 | sh600519 | sh=上海, sz=深圳 |
| 1 | 股票名称 | 贵州茅台 | |
| 2 | 股票代码 | 600519 | |
| 3 | 当前价格 | 1446.90 | |
| 4 | 昨收价 | 1443.31 | |
| 5 | 今开价 | 1442.60 | |
| 6 | 成交量(手) | 24233 | 1手=100股 |
| 7 | 外盘 | 115553 | 主动买入 |
| 8 | 内盘 | 12680 | 主动卖出 |
| 9-18 | 五档卖盘 | | 卖1-卖5 |
| 19-28 | 五档买盘 | | 买1-买5 |
| 29 | 时间 | 20260414153316 | YYYYMMDDHHmmss |
| 30 | 涨跌状态 | | |
| 31 | 涨跌额 | 3.59 | |
| 32 | 涨跌幅% | 0.25 | |
| 33 | 最高价 | 1448.60 | |
| 34 | 最低价 | 1435.00 | |
| 35 | 成交额/量/笔 | 1446.90/24233/3492544230 | 价格/量/成交额(元) |
| 37 | 成交额(万) | 349254 | |
| 38 | 换手率% | 0.19 | |
| 39 | 市盈率 | 20.13 | |

### Python 解析示例
```python
import requests

def get_realtime_quote(code):
    url = f"https://qt.gtimg.cn/q={code}"
    resp = requests.get(url)
    text = resp.content.decode('gbk')
    
    # 解析字段
    data = text.split('~')
    return {
        'name': data[1],
        'code': data[2],
        'price': float(data[3]),
        'close': float(data[4]),  # 昨收
        'open': float(data[5]),
        'volume': int(data[6]),   # 成交量(手)
        'high': float(data[33]),
        'low': float(data[34]),
        'change': float(data[31]),
        'change_pct': float(data[32]),
        'amount': float(data[37]),  # 成交额(万)
        'turnover': float(data[38]),  # 换手率
        'pe': float(data[39]),  # 市盈率
    }

# 使用
quote = get_realtime_quote('sh600519')
print(quote)
```

---

## 二、K线数据接口

### 接口地址
```
https://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={代码},{周期},,,{数量}
```

### 周期参数

| 周期 | 参数值 | 说明 |
|------|--------|------|
| 5分钟 | m5 | |
| 15分钟 | m15 | |
| 30分钟 | m30 | |
| 60分钟 | m60 | |
| 日K | day | |
| 周K | week | |
| 月K | month | |

### 请求示例
```
日K线：https://web.ifzq.gtimg.cn/appstock/app/kline/kline?param=sh600519,day,,,100
5分钟：https://web.ifzq.gtimg.cn/appstock/app/kline/kline?param=sh600519,m5,,,200
```

### 返回格式
- 编码：UTF-8
- 格式：JSON

### 返回数据结构
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "sh600519": {
      "day": [
        ["2026-04-14", "开盘", "收盘", "最高", "最低", "成交量"],
        ...
      ]
    }
  }
}
```

### K线字段顺序
```
[日期, 开盘价, 收盘价, 最高价, 最低价, 成交量(手)]
```

### Python 解析示例
```python
import requests

def get_kline(code, period='day', count=100):
    url = f"https://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={code},{period},,,{count}"
    resp = requests.get(url)
    data = resp.json()
    
    klines = data['data'][code][period]
    result = []
    for k in klines:
        result.append({
            'date': k[0],
            'open': float(k[1]),
            'close': float(k[2]),
            'high': float(k[3]),
            'low': float(k[4]),
            'volume': float(k[5]),
        })
    return result

# 使用
klines = get_kline('sh600519', 'day', 100)
```

---

## 三、分钟线接口（详细）

### 接口地址
```
https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={代码}
```

### 返回格式
```json
{
  "code": 0,
  "data": {
    "sh600519": {
      "data": {
        "data": [
          "0930 1442.60 174 25101240.40",
          "0931 1442.43 567 81815793.65",
          ...
        ]
      }
    }
  }
}
```

### 分钟数据字段
```
"时间 价格 成交量 成交额"
```

---

## 四、市场代码对照

| 前缀 | 市场 |
|------|------|
| sh | 上海证券交易所 |
| sz | 深圳证券交易所 |

### 代码规则
| 代码开头 | 市场 |
|----------|------|
| 60xxxx | 上海主板 |
| 68xxxx | 上海科创板 |
| 00xxxx | 深圳主板 |
| 30xxxx | 深圳创业板 |
| 000001 | 上证指数 |
| 399001 | 深证成指 |

---

## 五、注意事项

1. **编码问题**：实时行情接口返回GBK编码，需要转换
2. **无认证**：接口无需API Key，但可能有频率限制
3. **数据延迟**：免费接口可能有15分钟延迟
4. **批量查询**：实时行情支持逗号分隔批量查询
5. **HTTPS**：所有接口都支持HTTPS

---

## 六、与现有代码的对比

| 数据源 | 实时行情 | 日K线 | 分钟线 | 编码 |
|--------|----------|-------|--------|------|
| 腾讯 qt.gtimg.cn | ✓ | ✗ | ✗ | GBK |
| 腾讯 web.ifzq.gtimg.cn | ✓ | ✓ | ✓ | UTF-8 |
| 东方财富 | ✗ | ✓ | ✓ | JSONP |
| Tushare | ✗ | ✓ | ✗ | JSON |

**建议**：实时行情使用 `qt.gtimg.cn`，K线使用 `web.ifzq.gtimg.cn`
