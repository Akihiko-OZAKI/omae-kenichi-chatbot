#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易版Webサーバー（Flaskなし）
"""

import http.server
import socketserver
import json
import urllib.parse
import logging
from chat_bot import ChatBot
from simple_vector_store import SimpleVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# グローバル変数
vector_store = None
chat_bot = None

class ChatHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """GETリクエストの処理"""
        if self.path == '/':
            self.path = '/templates/omae_index.html'
        elif self.path.startswith('/static/'):
            # 静的ファイルの処理
            pass
        elif self.path == '/health':
            self.send_json_response({'status': 'healthy', 'message': '大前研一チャットボットが正常に動作しています'})
            return
        else:
            self.path = '/templates/omae_index.html'
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """POSTリクエストの処理"""
        if self.path == '/chat':
            self.handle_chat()
        else:
            self.send_error(404)
    
    def handle_chat(self):
        """チャットAPIの処理"""
        try:
            # リクエストボディの読み取り
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # JSONデータの解析
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '').strip()
            
            if not message:
                self.send_json_response({'success': False, 'error': 'メッセージが空です'})
                return
            
            # チャットボットの応答生成
            similar_docs = vector_store.search_similar(message, n_results=3)
            response_data = chat_bot.generate_response(message, similar_docs)
            
            # レスポンス送信
            self.send_json_response({
                'success': True,
                'response': response_data['response'],
                'sources': response_data.get('sources', []),
                'confidence': response_data.get('confidence', 0.8)
            })
            
        except Exception as e:
            logger.error(f"チャットエラー: {str(e)}")
            self.send_json_response({'success': False, 'error': str(e)})
    
    def send_json_response(self, data):
        """JSONレスポンスの送信"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def end_headers(self):
        """ヘッダーの終了"""
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def init_components():
    """コンポーネントの初期化"""
    global vector_store, chat_bot
    try:
        vector_store = SimpleVectorStore()
        chat_bot = ChatBot()
        logger.info("すべてのコンポーネントが正常に初期化されました")
        return True
    except Exception as e:
        logger.error(f"コンポーネント初期化エラー: {str(e)}")
        return False

def main():
    """メイン関数"""
    print("=== 大前研一チャットボット Webサーバー ===")
    
    # コンポーネントの初期化
    if not init_components():
        print("❌ コンポーネントの初期化に失敗しました")
        return
    
    # サーバーの設定
    PORT = 5001
    Handler = ChatHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ サーバーが起動しました: http://127.0.0.1:{PORT}")
            print("終了するには Ctrl+C を押してください")
            print()
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを終了します。お疲れさまでした！")
    except Exception as e:
        print(f"❌ サーバーエラー: {str(e)}")

if __name__ == '__main__':
    main()
