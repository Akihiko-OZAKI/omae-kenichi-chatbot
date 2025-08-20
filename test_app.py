#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト用Flaskアプリケーション
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({'message': '大前研一チャットボットが正常に動作しています！'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("テストアプリケーションを起動します...")
    app.run(debug=True, host='127.0.0.1', port=5001)
