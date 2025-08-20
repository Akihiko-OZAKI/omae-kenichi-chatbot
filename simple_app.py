#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易版大前研一チャットボット（Flaskなし）
"""

import json
import logging
from chat_bot import ChatBot
from simple_vector_store import SimpleVectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """メイン関数"""
    print("=== 大前研一チャットボット ===")
    print("終了するには 'quit' または 'exit' と入力してください")
    print()
    
    # コンポーネントの初期化
    try:
        vector_store = SimpleVectorStore()
        chat_bot = ChatBot()
        print("✅ チャットボットが初期化されました")
        print()
    except Exception as e:
        print(f"❌ 初期化エラー: {str(e)}")
        return
    
    # チャットループ
    while True:
        try:
            # ユーザー入力
            user_input = input("あなた: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '終了']:
                print("チャットボットを終了します。お疲れさまでした！")
                break
            
            if not user_input:
                continue
            
            # 応答生成
            print("🤔 大前研一の知恵を探しています...")
            
            similar_docs = vector_store.search_similar(user_input, n_results=3)
            response_data = chat_bot.generate_response(user_input, similar_docs)
            
            # 応答表示
            print(f"大前研一: {response_data['response']}")
            
            # ソース情報の表示
            if response_data.get('sources'):
                print(f"📚 参考: {', '.join(response_data['sources'])}")
            
            print()
            
        except KeyboardInterrupt:
            print("\nチャットボットを終了します。お疲れさまでした！")
            break
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            print()

if __name__ == '__main__':
    main()
