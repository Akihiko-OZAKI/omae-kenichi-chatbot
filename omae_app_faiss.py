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
        
        # チャットボットで応答生成
        response_data = chatbot.generate_response(message, similar_docs)
        
        # 応答を整形
        response = response_data.get('response', '申し訳ございません。応答を生成できませんでした。')
        sources = response_data.get('sources', [])
        confidence = response_data.get('confidence', 0.0)
        
        # チャット履歴に追加
        chat_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': response,
            'sources': sources,
            'confidence': confidence
        }
        session['chat_history'].append(chat_entry)
        
        # 履歴が長すぎる場合は古いものを削除
        if len(session['chat_history']) > 20:
            session['chat_history'] = session['chat_history'][-20:]
        
        return jsonify({
            'success': True,
            'response': response,
            'sources': sources,
            'confidence': confidence,
            'timestamp': chat_entry['timestamp']
        })
        
    except Exception as e:
        logger.error(f"チャットAPIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'エラーが発生しました: {str(e)}'
        })

def _extract_keywords_from_history(history_entries):
    """履歴からキーワードを抽出"""
    keywords = []
    for entry in history_entries:
        message = entry.get('message', '')
        response = entry.get('response', '')
        
        # 重要なキーワードを抽出
        important_words = [
            '戦略', '経営', 'リーダーシップ', 'グローバル', 'デジタル',
            'strategy', 'management', 'leadership', 'global', 'digital',
            '50代', 'サラリーマン', 'キャリア', 'ビジネス',
            'career', 'business', 'salaryman'
        ]
        
        for word in important_words:
            if word in message or word in response:
                keywords.append(word)
    
    return ' '.join(set(keywords))  # 重複を除去

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    """チャット履歴取得API"""
    try:
        history = session.get('chat_history', [])
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logger.error(f"履歴取得エラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'履歴取得エラー: {str(e)}'
        })

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """チャット履歴クリアAPI"""
    try:
        session['chat_history'] = []
        return jsonify({
            'success': True,
            'message': '履歴をクリアしました'
        })
    except Exception as e:
        logger.error(f"履歴クリアエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'履歴クリアエラー: {str(e)}'
        })

@app.route('/api/status', methods=['GET'])
def get_status():
    """システムステータス取得API"""
    try:
        stats = vector_store.get_statistics() if vector_store else {}
        return jsonify({
            'success': True,
            'status': 'running',
            'vector_store_loaded': vector_store is not None,
            'chatbot_loaded': chatbot is not None,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"ステータス取得エラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'ステータス取得エラー: {str(e)}'
        })

@app.route('/api/search', methods=['POST'])
def search():
    """検索API（デバッグ用）"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        n_results = data.get('n_results', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': '検索クエリが空です'
            })
        
        similar_docs = vector_store.search_similar(query, n_results=n_results)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': similar_docs
        })
        
    except Exception as e:
        logger.error(f"検索APIエラー: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'検索エラー: {str(e)}'
        })

@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    return jsonify({
        'success': False,
        'error': 'ページが見つかりません'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラー"""
    logger.error(f"内部エラー: {str(error)}")
    return jsonify({
        'success': False,
        'error': '内部サーバーエラーが発生しました'
    }), 500

if __name__ == '__main__':
    # コンポーネントの初期化
    if not initialize_components():
        logger.error("初期化に失敗しました。アプリケーションを終了します。")
        sys.exit(1)
    
    # 開発サーバーの起動
    logger.info("大前研一チャットボットを起動中...")
    
    # Render用のポート設定
    port = int(os.environ.get('PORT', 5000))
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # 本番環境ではデバッグを無効化
        threaded=True
    )
