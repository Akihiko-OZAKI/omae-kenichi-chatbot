#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大前研一チャットボット Webアプリケーション（FAISS版）
Colabで学習済みのFAISSインデックスを使用
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from faiss_vector_store import FAISSVectorStore
from chat_bot import ChatBot

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flaskアプリケーションの初期化
app = Flask(__name__)
app.secret_key = 'omae_kenichi_chatbot_secret_key_2024'

# グローバル変数
vector_store = None
chatbot = None

def initialize_components():
    """コンポーネントの初期化"""
    global vector_store, chatbot
    
    try:
        # 学習結果ファイルのパスを設定
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        index_path = os.path.join(base_path, "faiss_index_ip.faiss")
        meta_path = os.path.join(base_path, "faiss_meta.json")
        texts_path = os.path.join(base_path, "faiss_texts.jsonl")
        
        logger.info("FAISSベクトルストアを初期化中...")
        vector_store = FAISSVectorStore(
            index_path=index_path,
            meta_path=meta_path,
            texts_path=texts_path
        )
        
        logger.info("チャットボットを初期化中...")
        chatbot = ChatBot()
        
        # 統計情報をログ出力
        stats = vector_store.get_statistics()
        logger.info(f"ベクトルストア統計: {stats}")
        
        logger.info("初期化完了")
        return True
        
    except Exception as e:
        logger.error(f"初期化エラー: {str(e)}")
        return False

@app.route('/')
def index():
    """メインページ"""
    return render_template('omae_index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """チャットAPI（コンテキスト対応版）"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'メッセージが空です'
            })
        
        # セッションにメッセージ履歴を保存
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        # 類似ドキュメントを検索（コンテキストを考慮）
        enhanced_query = message
        if session['chat_history']:
            # 前の会話履歴からコンテキストを追加
            last_entry = session['chat_history'][-1]
            context_keywords = _extract_keywords_from_history(session['chat_history'][-3:])
            if context_keywords:
                enhanced_query = f"{message} {context_keywords}"
        
        similar_docs = vector_store.search_similar(enhanced_query, n_results=3)
        
        # チャットボットでレスポンス生成
        response = chatbot.generate_response(message, similar_docs)
        
        # セッション履歴を更新
        session['chat_history'].append({
            'message': message,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 履歴が長すぎる場合は古いものを削除
        if len(session['chat_history']) > 10:
            session['chat_history'] = session['chat_history'][-10:]
        
        return jsonify({
            'success': True,
            'response': response,
            'similar_docs': similar_docs[:2]  # 最初の2件のみ返す
        })
        
    except Exception as e:
        logger.error(f"チャットAPIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'エラーが発生しました: {str(e)}'
        })

def _extract_keywords_from_history(history_entries):
    """会話履歴からキーワードを抽出"""
    if not history_entries:
        return ""
    
    keywords = []
    for entry in history_entries:
        message = entry.get('message', '')
        response = entry.get('response', '')
        
        # 簡単なキーワード抽出（実際の実装ではより高度な処理が必要）
        words = (message + ' ' + response).split()
        keywords.extend([w for w in words if len(w) > 3])
    
    return ' '.join(keywords[-5:])  # 最後の5つのキーワードのみ

@app.route('/api/health')
def health_check():
    """ヘルスチェックAPI"""
    try:
        if vector_store is None or chatbot is None:
            return jsonify({
                'status': 'error',
                'message': 'コンポーネントが初期化されていません'
            }), 500
        
        return jsonify({
            'status': 'healthy',
            'message': '大前研一チャットボットは正常に動作しています',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ヘルスチェックエラー: {str(e)}'
        }), 500

@app.route('/api/stats')
def get_stats():
    """統計情報API"""
    try:
        if vector_store is None:
            return jsonify({
                'success': False,
                'error': 'ベクトルストアが初期化されていません'
            })
        
        stats = vector_store.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'統計情報取得エラー: {str(e)}'
        })

# アプリケーション起動時の初期化
if __name__ == '__main__':
    logger.info("大前研一チャットボットを起動中...")
    
    # コンポーネント初期化
    if not initialize_components():
        logger.error("初期化に失敗しました。アプリケーションを終了します。")
        sys.exit(1)
    
    # ポート設定（Render用）
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"アプリケーションをポート {port} で起動します")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # 本番環境ではFalse
    )
