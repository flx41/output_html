# 腾讯K线复权接口文档

> 更新日期：2026-04-14
> 来源：DIGDOD项目分析

---

## 一、接口地址

### 前复权K线
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param={市场}{代码},{周期},,,{数量},qfq
```

### 不复权K线
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_day&param={市场}{代码},{周期},,,{数量}
```

---

## 二、参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| _var | JSONP变量名 | kline_dayqfq |
| 市场 | sh=上海, sz=深圳 | sh |
| 代码 | 股票代码 | 600519 |
| 周期 | day/week/month | day |
| 起始 | 留空 | |
| 结束 | 留空 | |
| 数量 | 最大320 | 320 |
| 复权 | qfq=前复权, hfq=后复权 | qfq |

---

## 三、请求示例

### 日K（前复权）
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayqfq&param=sh600519,day,,,320,qfq
```

### 周K（前复权）
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_weekqfq&param=sh600519,week,,,320,qfq
```

### 月K（前复权）
```
https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_monthqfq&param=sh600519,month,,,320,qfq
```

---

## 四、返回格式

### JSONP格式
```javascript
kline_dayqfq={"code":0,"msg":"","data":{"sh600519":{"qfqday":[...]}}};
```

### 数据结构
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "sh600519": {
      "qfqday": [
        ["日期", "开盘", "收盘", "最高", "最低", "成交量"],
        ["2026-04-14", "1442.60", "1446.90", "1448.60", "1435.00", "24233"],
        ...
      ],
      "qt": { 实时行情数据 },
      "prec": "昨收价",
      "version": "18"
    }
  }
}
```

### K线字段顺序
```
[0] 日期: 2026-04-14
[1] 开盘: 1442.60
[2] 收盘: 1446.90
[3] 最高: 1448.60
[4] 最低: 1435.00
[5] 成交量: 24233 (手)
```

---

## 五、优势对比

| 特性 | 腾讯fqkline | baostock | 新浪 |
|------|-------------|----------|------|
| 前复权 | ✅ qfq | ✅ | ❌ |
| 后复权 | ✅ hfq | ✅ | ❌ |
| 不复权 | ✅ | ✅ | ✅ |
| 日K | ✅ | ✅ | ✅ |
| 周K | ✅ | ✅ | ✅ |
| 月K | ✅ | ✅ | ✅ |
| 速度 | 快 | 慢 | 快 |
| 需登录 | ❌ | ❌ | ❌ |
| 稳定性 | 高 | 高 | 低(已废) |

---

## 六、额外数据

该接口同时返回实时行情数据（qt字段），包含：
- 当前价、涨跌幅
- 成交量、成交额
- 五档盘口
- 换手率、市盈率等

**一个请求 = K线 + 实时行情**

---

## 七、Python调用示例

```python
import requests
import json

def get_tencent_kline(code, period='day', count=320, adj='qfq'):
    """获取腾讯K线数据（支持复权）"""
    prefix = 'sh' if code.startswith('6') else 'sz'
    var_name = f'kline_{period}{adj}'
    
    url = f'https://web.ifzq.gtimg.cn/appstock/app/fqkline/get'
    params = {
        '_var': var_name,
        'param': f'{prefix}{code},{period},,,{count},{adj}'
    }
    
    resp = requests.get(url)
    text = resp.text
    
    # 解析JSONP
    json_str = text.split('=', 1)[1].rstrip(';')
    data = json.loads(json_str)
    
    # 获取K线数据
    kline_key = f'{adj}{period}' if adj else period
    klines = data['data'][f'{prefix}{code}'][kline_key]
    
    result = []
    for k in klines:
        result.append({
            'date': k[0],
            'open': float(k[1]),
            'close': float(k[2]),
            'high': float(k[3]),
            'low': float(k[4]),
            'volume': float(k[5])
        })
    
    return result

# 使用
klines = get_tencent_kline('600519', 'day', 100, 'qfq')
```

---

## 八、对现有项目的价值

### stock.html
- 可以获取前复权K线，价格更准确
- 一个接口同时获取K线+实时行情
- 减少请求数量

### kline_api_server.py
- 可作为主力数据源
- 备选：新浪 → 腾讯 → baostock

---

*建议集成到项目中*
