#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大前研一ベクトルDB検索デバッグスクリプト
"""

import sys
sys.path.append('..')
from omae_vector_store import VectorStore

def debug_search():
    """検索結果をデバッグ"""
    try:
        # ベクトルストアを初期化
        vector_store = VectorStore(persist_directory="./omae_chroma_db")
        
        # テストクエリ
        test_queries = [
            "キャリア開発",
            "サラリーマンの生き方",
            "ビジネス戦略",
            "会社依存からの脱却"
        ]
        
        for query in test_queries:
            print(f"\n=== クエリ: {query} ===")
            similar_docs = vector_store.search_similar(query, n_results=3)
            
            if similar_docs:
                for i, doc in enumerate(similar_docs):
                    print(f"\n{i+1}. 距離: {doc['distance']:.3f}")
                    print(f"   テキスト: {doc['text'][:200]}...")
                    if doc['metadata']:
                        print(f"   メタデータ: {doc['metadata']}")
            else:
                print("検索結果なし")
                
    except Exception as e:
        print(f"エラー: {str(e)}")

if __name__ == "__main__":
    debug_search() 