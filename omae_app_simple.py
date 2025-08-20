#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大前研一チャットボット 軽量化版
メモリ使用量を削減してRender Free Planで動作
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flaskアプリケーションの初期化
app = Flask(__name__)

@app.route('/')
def index():
    """メインページ"""
    return render_template('omae_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """チャットAPI（軽量化版）"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'メッセージが空です'
            })
        
        # 簡単な応答（テスト用）
        if 'こんにちは' in message or 'hello' in message.lower():
            response = "こんにちは！大前研一チャットボットです。現在テストモードで動作しています。"
        elif '大前研一' in message or 'ohmae' in message.lower():
            response = "大前研一氏は、日本の経営コンサルタントで、マッキンゼー・アンド・カンパニーの元日本支社長です。戦略経営の第一人者として知られています。"
        else:
            response = "申し訳ございません。現在テストモードのため、限定的な応答しかできません。"
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"チャットAPIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'エラーが発生しました: {str(e)}'
        })

@app.route('/api/health')
def health_check():
    """ヘルスチェックAPI"""
    return jsonify({
        'status': 'healthy',
        'message': '大前研一チャットボット（軽量化版）は正常に動作しています',
        'timestamp': datetime.now().isoformat(),
        'version': 'lightweight-1.0'
    })

@app.route('/api/stats')
def get_stats():
    """統計情報API"""
    return jsonify({
        'success': True,
        'stats': {
            'mode': 'lightweight',
            'status': 'running',
            'version': '1.0'
        }
    })

if __name__ == '__main__':
    logger.info("大前研一チャットボット（軽量化版）を起動中...")
    
    # ポート設定（Render用）
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"アプリケーションをポート {port} で起動します")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
