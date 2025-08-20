#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大前研一チャットボット システムテスト
"""

import os
import sys
import logging
from faiss_vector_store import FAISSVectorStore
from chat_bot import ChatBot

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_vector_store():
    """FAISSベクトルストアのテスト"""
    print("=== FAISSベクトルストアテスト ===")
    
    try:
        # ベクトルストアの初期化
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        index_path = os.path.join(base_path, "faiss_index_ip.faiss")
        meta_path = os.path.join(base_path, "faiss_meta.json")
        texts_path = os.path.join(base_path, "faiss_texts.jsonl")
        
        print(f"インデックスパス: {index_path}")
        print(f"メタデータパス: {meta_path}")
        print(f"テキストパス: {texts_path}")
        
        # ファイル存在確認
        for path, name in [(index_path, "インデックス"), (meta_path, "メタデータ"), (texts_path, "テキスト")]:
            if os.path.exists(path):
                size = os.path.getsize(path) / (1024 * 1024)  # MB
                print(f"✓ {name}ファイル: {path} ({size:.1f}MB)")
            else:
                print(f"✗ {name}ファイルが見つかりません: {path}")
                return False
        
        # ベクトルストアの初期化
        vector_store = FAISSVectorStore(
            index_path=index_path,
            meta_path=meta_path,
            texts_path=texts_path
        )
        
        # 統計情報の表示
        stats = vector_store.get_statistics()
        print(f"✓ ベクトルストア初期化成功")
        print(f"  総ベクトル数: {stats.get('total_vectors', 0)}")
        print(f"  ベクトル次元: {stats.get('vector_dimension', 0)}")
        print(f"  メタデータ数: {stats.get('metadata_count', 0)}")
        print(f"  テキスト数: {stats.get('texts_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ ベクトルストアテスト失敗: {str(e)}")
        return False

def test_search():
    """検索機能のテスト"""
    print("\n=== 検索機能テスト ===")
    
    try:
        # ベクトルストアの初期化
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        vector_store = FAISSVectorStore(
            index_path=os.path.join(base_path, "faiss_index_ip.faiss"),
            meta_path=os.path.join(base_path, "faiss_meta.json"),
            texts_path=os.path.join(base_path, "faiss_texts.jsonl")
        )
        
        # テストクエリ
        test_queries = [
            "グローバル戦略",
            "リーダーシップ",
            "デジタル変革",
            "50代の生き残り",
            "Global strategy"
        ]
        
        for query in test_queries:
            print(f"\nクエリ: '{query}'")
            results = vector_store.search_similar(query, n_results=2)
            
            if results:
                print(f"✓ 検索成功: {len(results)}件の結果")
                for i, result in enumerate(results[:2]):
                    source = result.get('source', 'Unknown')
                    page = result.get('page', 'Unknown')
                    distance = result.get('distance', 0.0)
                    content_preview = result.get('content', '')[:100] + "..."
                    print(f"  {i+1}. {source} (p.{page}) - 類似度: {distance:.3f}")
                    print(f"     {content_preview}")
            else:
                print(f"✗ 検索失敗: 結果なし")
        
        return True
        
    except Exception as e:
        print(f"✗ 検索テスト失敗: {str(e)}")
        return False

def test_chatbot():
    """チャットボットのテスト"""
    print("\n=== チャットボットテスト ===")
    
    try:
        # チャットボットの初期化
        chatbot = ChatBot()
        print("✓ チャットボット初期化成功")
        
        # テストメッセージ
        test_messages = [
            "グローバル戦略について教えて",
            "現代のリーダーに必要な能力は？",
            "50代のサラリーマンが生き残るには？",
            "What is business strategy?",
            "How to overcome failure?"
        ]
        
        for message in test_messages:
            print(f"\nメッセージ: '{message}'")
            
            # 言語検出テスト
            lang = chatbot.detect_language(message)
            print(f"  検出言語: {lang}")
            
            # 意図分析テスト
            intent = chatbot.analyze_question_intent(message)
            print(f"  検出トピック: {intent.get('topic', 'unknown')}")
            print(f"  検出感情: {intent.get('emotion', 'neutral')}")
        
        return True
        
    except Exception as e:
        print(f"✗ チャットボットテスト失敗: {str(e)}")
        return False

def test_integration():
    """統合テスト"""
    print("\n=== 統合テスト ===")
    
    try:
        # コンポーネントの初期化
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        vector_store = FAISSVectorStore(
            index_path=os.path.join(base_path, "faiss_index_ip.faiss"),
            meta_path=os.path.join(base_path, "faiss_meta.json"),
            texts_path=os.path.join(base_path, "faiss_texts.jsonl")
        )
        chatbot = ChatBot()
        
        # 統合テストクエリ
        test_query = "グローバル戦略について教えて"
        print(f"テストクエリ: '{test_query}'")
        
        # 検索実行
        similar_docs = vector_store.search_similar(test_query, n_results=3)
        print(f"✓ 検索完了: {len(similar_docs)}件の結果")
        
        # 応答生成
        response_data = chatbot.generate_response(test_query, similar_docs)
        response = response_data.get('response', '')
        confidence = response_data.get('confidence', 0.0)
        
        print(f"✓ 応答生成完了")
        print(f"  信頼度: {confidence:.2f}")
        print(f"  応答長: {len(response)}文字")
        print(f"  応答プレビュー: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 統合テスト失敗: {str(e)}")
        return False

def main():
    """メイン関数"""
    print("大前研一チャットボット システムテスト開始")
    print("=" * 50)
    
    tests = [
        ("FAISSベクトルストア", test_vector_store),
        ("検索機能", test_search),
        ("チャットボット", test_chatbot),
        ("統合テスト", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}テストで例外発生: {str(e)}")
            results.append((test_name, False))
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("テスト結果サマリー")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 全てのテストが成功しました！システムは正常に動作します。")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。システムの確認が必要です。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

