#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare后端API服务
为price_action_tradingview.html提供数据接口
"""

from flask import Flask, request, jsonify
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Tushare配置
TOKEN='cb6cff2f0fc800c9ef862bd55a2ad39035db25bf98d6b125e6c7f1fc'
ts.set_token(TOKEN)
pro = ts.pro_api()

@app.route('/api/stock/list', methods=['GET'])
def get_stock_list():
    """获取股票列表"""
    try:
        # 获取股票列表
        stocks = pro.stock_basic(exchange='', list_status='L', 
                                fields='ts_code,symbol,name,area,industry,list_date,market')
        
        # 转换为JSON格式
        stock_list = []
        for _, row in stocks.iterrows():
            stock_list.append({
                'code': row['symbol'],
                'name': row['name'],
                'ts_code': row['ts_code'],
                'industry': row['industry'],
                'market': row['market']
            })
        
        return jsonify({
            'success': True,
            'data': stock_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/daily', methods=['GET'])
def get_daily_data():
    """获取日线数据"""
    try:
        code = request.args.get('code', '000001')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        limit = int(request.args.get('limit', 100))
        
        # 如果没有指定日期，默认获取最近100天
        if not start_date:
            start_date = (datetime.now() - timedelta(days=limit)).strftime('%Y%m%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        
        # 转换为tushare格式
        ts_code = f"{code}.{'SZ' if code.startswith('0') or code.startswith('3') else 'SH'}"
        
        # 获取数据
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': '没有数据'
            }), 404
        
        # 转换为前端格式
        data = []
        for _, row in df.iterrows():
            # 将日期字符串转换为时间戳
            date_str = str(row['trade_date'])
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            timestamp = int(date_obj.timestamp())
            
            data.append({
                'time': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['vol']) if 'vol' in row else 0
            })
        
        # 按时间排序
        data.sort(key=lambda x: x['time'])
        
        return jsonify({
            'success': True,
            'data': data,
            'source': 'tushare',
            'count': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/weekly', methods=['GET'])
def get_weekly_data():
    """获取周线数据"""
    try:
        code = request.args.get('code', '000001')
        limit = int(request.args.get('limit', 100))
        
        # 转换为tushare格式
        ts_code = f"{code}.{'SZ' if code.startswith('0') or code.startswith('3') else 'SH'}"
        
        # 获取周线数据
        df = pro.weekly(ts_code=ts_code, start_date='20200101', end_date=datetime.now().strftime('%Y%m%d'))
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': '没有数据'
            }), 404
        
        # 取最近的数据
        df = df.tail(limit)
        
        # 转换为前端格式
        data = []
        for _, row in df.iterrows():
            date_str = str(row['trade_date'])
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            timestamp = int(date_obj.timestamp())
            
            data.append({
                'time': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['vol']) if 'vol' in row else 0
            })
        
        # 按时间排序
        data.sort(key=lambda x: x['time'])
        
        return jsonify({
            'success': True,
            'data': data,
            'source': 'tushare',
            'count': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/monthly', methods=['GET'])
def get_monthly_data():
    """获取月线数据"""
    try:
        code = request.args.get('code', '000001')
        limit = int(request.args.get('limit', 100))
        
        # 转换为tushare格式
        ts_code = f"{code}.{'SZ' if code.startswith('0') or code.startswith('3') else 'SH'}"
        
        # 获取月线数据
        df = pro.monthly(ts_code=ts_code, start_date='20200101', end_date=datetime.now().strftime('%Y%m%d'))
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': '没有数据'
            }), 404
        
        # 取最近的数据
        df = df.tail(limit)
        
        # 转换为前端格式
        data = []
        for _, row in df.iterrows():
            date_str = str(row['trade_date'])
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            timestamp = int(date_obj.timestamp())
            
            data.append({
                'time': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['vol']) if 'vol' in row else 0
            })
        
        # 按时间排序
        data.sort(key=lambda x: x['time'])
        
        return jsonify({
            'success': True,
            'data': data,
            'source': 'tushare',
            'count': len(data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/info', methods=['GET'])
def get_stock_info():
    """获取股票信息"""
    try:
        code = request.args.get('code', '000001')
        
        # 转换为tushare格式
        ts_code = f"{code}.{'SZ' if code.startswith('0') or code.startswith('3') else 'SH'}"
        
        # 获取股票信息
        stock_info = pro.stock_basic(ts_code=ts_code, fields='ts_code,symbol,name,area,industry,list_date,market')
        
        if stock_info.empty:
            return jsonify({
                'success': False,
                'error': '股票不存在'
            }), 404
        
        row = stock_info.iloc[0]
        
        return jsonify({
            'success': True,
            'data': {
                'code': row['symbol'],
                'name': row['name'],
                'ts_code': row['ts_code'],
                'industry': row['industry'],
                'area': row['area'],
                'market': row['market'],
                'list_date': row['list_date']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stock/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    try:
        keyword = request.args.get('keyword', '')
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': '请输入搜索关键词'
            }), 400
        
        # 获取所有股票
        stocks = pro.stock_basic(exchange='', list_status='L', 
                                fields='ts_code,symbol,name,area,industry')
        
        # 搜索匹配的股票
        results = []
        keyword = keyword.upper()
        
        for _, row in stocks.iterrows():
            if (keyword in row['symbol'] or 
                keyword in row['name'] or 
                keyword in row['ts_code']):
                results.append({
                    'code': row['symbol'],
                    'name': row['name'],
                    'ts_code': row['ts_code'],
                    'industry': row['industry']
                })
        
        # 限制结果数量
        results = results[:20]
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("启动Tushare后端服务...")
    print("API接口:")
    print("  GET /api/stock/list - 获取股票列表")
    print("  GET /api/stock/daily?code=000001&limit=100 - 获取日线数据")
    print("  GET /api/stock/weekly?code=000001&limit=100 - 获取周线数据")
    print("  GET /api/stock/monthly?code=000001&limit=100 - 获取月线数据")
    print("  GET /api/stock/info?code=000001 - 获取股票信息")
    print("  GET /api/stock/search?keyword=茅台 - 搜索股票")
    print("\n服务地址: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)