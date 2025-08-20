#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大前研一チャットボットアプリ（修正版）
"""

import os
import json
from flask import Flask, request, jsonify, render_template
import logging
import sys
# sys.path.append('..')  # コメントアウト
from chat_bot import ChatBot
from simple_vector_store import SimpleVectorStore as VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

vector_store = None
chat_bot = None

def init_components():
    global vector_store, chat_bot
    try:
        vector_store = VectorStore(persist_directory="./omae_chroma_db")
        logger.info("大前研一フルPDFベクトルDBを使用します（966ドキュメント）")
        chat_bot = ChatBot(api_key=None)  # Ollama使用
        logger.info("すべてのコンポーネントが正常に初期化されました")
        return True
    except Exception as e:
        logger.error(f"コンポーネント初期化エラー: {str(e)}")
        return False

if not init_components():
    logger.error("コンポーネントの初期化に失敗しました")
    exit(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'success': False, 'error': 'メッセージが空です'})
        
        logger.info(f"受信メッセージ: {message}")
        detected_lang = chat_bot.detect_language(message)
        logger.info(f"検出された言語: {detected_lang}")
        
        similar_docs = vector_store.search_similar(message, n_results=3)
        logger.info(f"検索結果: {len(similar_docs)}件")
        
        response_data = chat_bot.generate_response(message, similar_docs)
        
        return jsonify({
            'success': True,
            'response': response_data['response'],
            'sources': response_data.get('sources', []),
            'confidence': response_data.get('confidence', 0.8)
        })
    except Exception as e:
        logger.error(f"チャットエラー: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': '大前研一チャットボットが正常に動作しています'})

if __name__ == '__main__':
    logger.info("大前研一チャットボットを起動します...")
    app.run(debug=True, host='127.0.0.1', port=5001) 