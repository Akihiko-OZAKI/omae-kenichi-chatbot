"""
大前研一専用ベクトルストア管理モジュール
ChromaDBを使用したベクトルデータベースの管理とRAG機能を提供
"""

import os
import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """ベクトルストア管理クラス"""
    
    def __init__(self, persist_directory: str = "./omae_chroma_db"):
        """
        VectorStoreの初期化
        
        Args:
            persist_directory: ベクトルDBの保存ディレクトリ
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_model = None
        self.init_database()
        self.init_embedding_model()
    
    def init_database(self):
        """ChromaDBの初期化"""
        try:
            # ChromaDBクライアントの初期化
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 利用可能なコレクションを確認
            collections = self.client.list_collections()
            logger.info(f"利用可能なコレクション: {[col.name for col in collections]}")
            
            # コレクションの取得または作成
            collection_name = None
            
            # 大前研一のコレクションを優先
            if any(col.name == "omae_kenichi_books" for col in collections):
                collection_name = "omae_kenichi_books"
                logger.info("大前研一書籍コレクションを読み込みました")
            elif any(col.name == "omae_summary" for col in collections):
                collection_name = "omae_summary"
                logger.info("大前研一要約コレクションを読み込みました")
            else:
                collection_name = "omae_kenichi_books"
                logger.info("新しい大前研一コレクションを作成します")
            
            try:
                self.collection = self.client.get_collection(collection_name)
                logger.info(f"コレクション '{collection_name}' を読み込みました")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "大前研一書籍ナレッジベース"}
                )
                logger.info(f"新しいコレクション '{collection_name}' を作成しました")
                
        except Exception as e:
            logger.error(f"ベクトルDB初期化エラー: {str(e)}")
            raise
    
    def init_embedding_model(self):
        """埋め込みモデルの初期化"""
        try:
            # 多言語対応の埋め込みモデル
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("埋め込みモデルを初期化しました")
        except Exception as e:
            logger.error(f"埋め込みモデル初期化エラー: {str(e)}")
            raise
    
    def search_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        類似ドキュメントの検索
        
        Args:
            query: 検索クエリ
            n_results: 取得する結果数
            
        Returns:
            類似ドキュメントのリスト
        """
        try:
            # クエリの埋め込みベクトルを生成
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # 類似度検索を実行
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 結果を整形
            similar_docs = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_docs.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0.0
                    })
            
            return similar_docs
            
        except Exception as e:
            logger.error(f"検索エラー: {str(e)}")
            return [] 