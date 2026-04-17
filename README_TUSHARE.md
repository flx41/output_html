# Tushare版价格行为分析工具

## 概述
这是price_action_tradingview.html的Tushare版本，使用Tushare作为数据源，提供更准确、更全面的A股数据。

## 主要改进

### 1. 数据源改进
- **Tushare数据源**：更准确、更全面的A股数据
- **动态股票搜索**：支持搜索所有A股，不再局限于30只股票
- **股票信息丰富**：包含行业、地区、上市日期等信息

### 2. 功能增强
- **复权数据**：支持前复权、后复权
- **财务数据**：可扩展获取财务指标
- **行业分类**：支持按行业搜索股票

### 3. 性能优化
- **数据缓存**：减少重复API调用
- **批量获取**：支持批量获取多只股票数据
- **错误处理**：更完善的错误处理和回退机制

## 安装和使用

### 方法1：使用Tushare后端（推荐）

1. **安装依赖**：
   ```bash
   pip3 install flask tushare pandas
   ```

2. **启动后端服务**：
   ```bash
   python3 ~/Desktop/41mbp\ 共享/output_html/tushare_backend.py
   ```

3. **打开HTML文件**：
   ```
   http://localhost:5000/static/price_action_tradingview_tushare.html
   ```
   或者直接打开文件：
   ```
   ~/Desktop/41mbp 共享/output_html/price_action_tradingview_tushare.html
   ```

### 方法2：使用原版（无需后端）

如果不想运行后端服务，可以使用原版：
```
~/Desktop/41mbp 共享/output_html/price_action_tradingview.html
```

## API接口

Tushare后端提供以下API接口：

### 1. 获取股票列表
```
GET /api/stock/list
```

### 2. 获取日线数据
```
GET /api/stock/daily?code=000001&limit=100
```

### 3. 获取周线数据
```
GET /api/stock/weekly?code=000001&limit=100
```

### 4. 获取月线数据
```
GET /api/stock/monthly?code=000001&limit=100
```

### 5. 获取股票信息
```
GET /api/stock/info?code=000001
```

### 6. 搜索股票
```
GET /api/stock/search?keyword=茅台
```

## 节省算力的优化

### 1. 数据缓存
- 股票列表缓存：减少重复请求
- 历史数据缓存：避免重复获取相同数据
- 搜索结果缓存：提高搜索响应速度

### 2. 延迟加载
- 按需加载分钟数据：只在用户选择时加载
- 分批加载数据：避免一次性加载过多数据
- 懒加载指标：只在需要时计算技术指标

### 3. 计算优化
- 使用Web Workers：在后台线程计算指标
- 优化算法：改进EMA、MACD等算法实现
- 减少DOM操作：批量更新UI

### 4. 内存管理
- 限制数据长度：只保留最近的数据
- 清理无用数据：及时释放内存
- 分页加载：支持大数据量分页

### 5. 网络优化
- 请求合并：合并多个API请求
- 压缩传输：启用gzip压缩
- 连接复用：使用HTTP/2

## 配置说明

### Tushare Token
Token已配置在代码中：`cb6cff2f0fc800c9ef862bd55a2ad39035db25bf98d6b125e6c7f1fc`

### 服务器配置
- 默认端口：5000
- 主机：0.0.0.0（允许外部访问）
- 调试模式：开启

### 数据限制
- 默认获取100条数据
- 支持日线、周线、月线
- 支持搜索所有A股

## 故障排除

### 1. 后端服务无法启动
```bash
# 检查端口是否被占用
lsof -i :5000

# 使用其他端口
python3 tushare_backend.py --port 5001
```

### 2. 无法获取数据
```bash
# 测试Tushare API
python3 ~/.hermes/skills/research/tushare-data/quick_test.py

# 检查网络连接
ping api.tushare.pro
```

### 3. 前端无法连接后端
- 确保后端服务正在运行
- 检查浏览器控制台错误信息
- 确认CORS配置正确

## 扩展功能

### 1. 添加更多技术指标
- DMI（动向指标）
- SAR（抛物线指标）
- OBV（能量潮指标）

### 2. 添加财务数据
- 市盈率（PE）
- 市净率（PB）
- 每股收益（EPS）

### 3. 添加新闻数据
- 公司公告
- 行业新闻
- 市场分析

## 更新日志

### 2026-04-13
- 创建Tushare版本
- 添加动态股票搜索
- 添加股票信息查询
- 优化数据获取流程

## 文件说明

- `price_action_tradingview_tushare.html` - Tushare版HTML文件
- `tushare_backend.py` - Tushare后端API服务
- `price_action_tradingview.html` - 原版HTML文件
- `README_TUSHARE.md` - 本说明文档

## 注意事项

1. **频率限制**：Tushare API有频率限制，请合理使用
2. **Token安全**：Token已硬编码，请注意安全
3. **数据延迟**：数据可能有15分钟延迟
4. **网络要求**：需要稳定的网络连接