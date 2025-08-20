"""
大前研一専用FAISSベクトルストア管理モジュール
Colabで学習済みのFAISSインデックスを使用したRAG機能を提供
"""

import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FAISSVectorStore:
    """FAISSベクトルストア管理クラス"""
    
    def __init__(self, 
                 index_path: str = "./学習結果/faiss_index_ip.faiss",
                 meta_path: str = "./学習結果/faiss_meta.json",
                 texts_path: str = "./学習結果/faiss_texts.jsonl"):
        """
        FAISSVectorStoreの初期化
        
        Args:
            index_path: FAISSインデックスファイルのパス
            meta_path: メタデータJSONファイルのパス
            texts_path: テキストJSONLファイルのパス
        """
        self.index_path = index_path
        self.meta_path = meta_path
        self.texts_path = texts_path
        
        self.index = None
        self.metadata = None
        self.texts = None
        self.embedding_model = None
        
        self.load_faiss_index()
        self.load_metadata()
        self.load_texts()
        self.init_embedding_model()
    
    def load_faiss_index(self):
        """FAISSインデックスの読み込み"""
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                logger.info(f"FAISSインデックスを読み込みました: {self.index_path}")
                logger.info(f"インデックスサイズ: {self.index.ntotal} ベクトル")
            else:
                raise FileNotFoundError(f"FAISSインデックスファイルが見つかりません: {self.index_path}")
        except Exception as e:
            logger.error(f"FAISSインデックス読み込みエラー: {str(e)}")
            raise
    
    def load_metadata(self):
        """メタデータの読み込み"""
        try:
            if os.path.exists(self.meta_path):
                with open(self.meta_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"メタデータを読み込みました: {self.meta_path}")
                logger.info(f"メタデータ数: {len(self.metadata)}")
            else:
                raise FileNotFoundError(f"メタデータファイルが見つかりません: {self.meta_path}")
        except Exception as e:
            logger.error(f"メタデータ読み込みエラー: {str(e)}")
            raise
    
    def load_texts(self):
        """テキストデータの読み込み"""
        try:
            if os.path.exists(self.texts_path):
                self.texts = []
                with open(self.texts_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            self.texts.append(json.loads(line))
                logger.info(f"テキストデータを読み込みました: {self.texts_path}")
                logger.info(f"テキスト数: {len(self.texts)}")
            else:
                raise FileNotFoundError(f"テキストファイルが見つかりません: {self.texts_path}")
        except Exception as e:
            logger.error(f"テキストデータ読み込みエラー: {str(e)}")
            raise
    
    def init_embedding_model(self):
        """埋め込みモデルの初期化"""
        try:
            # Colabで使用したのと同じモデル
            self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-base')
            logger.info("埋め込みモデルを初期化しました: intfloat/multilingual-e5-base")
        except Exception as e:
            logger.error(f"埋め込みモデル初期化エラー: {str(e)}")
            raise
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        類似ドキュメントの検索
        
        Args:
            query: 検索クエリ
            n_results: 取得する結果数
            
        Returns:
            類似ドキュメントのリスト
        """
        try:
            # クエリにプレフィックスを追加（Colab学習時と同じ）
            query_with_prefix = f"query: {query}"
            
            # クエリの埋め込みベクトルを生成
            query_embedding = self.embedding_model.encode([query_with_prefix], normalize_embeddings=True)[0]
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # FAISSで類似度検索を実行
            distances, indices = self.index.search(query_embedding, n_results)
            
            # 結果を整形
            similar_docs = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.texts):
                    doc = self.texts[idx]
                    meta = self.metadata[idx] if idx < len(self.metadata) else {}
                    
                    similar_docs.append({
                        'content': doc.get('text', ''),
                        'source': meta.get('source', ''),
                        'page': meta.get('page', ''),
                        'distance': float(distance),
                        'index': int(idx)
                    })
            
            logger.info(f"検索完了: {len(similar_docs)}件の結果を取得")
            return similar_docs
            
        except Exception as e:
            logger.error(f"検索エラー: {str(e)}")
            return []
    
    def get_document_by_index(self, index: int) -> Optional[Dict]:
        """
        インデックスでドキュメントを取得
        
        Args:
            index: ドキュメントのインデックス
            
        Returns:
            ドキュメント情報
        """
        try:
            if 0 <= index < len(self.texts):
                doc = self.texts[index]
                meta = self.metadata[index] if index < len(self.metadata) else {}
                
                return {
                    'content': doc.get('text', ''),
                    'source': meta.get('source', ''),
                    'page': meta.get('page', ''),
                    'index': index
                }
            return None
        except Exception as e:
            logger.error(f"ドキュメント取得エラー: {str(e)}")
            return None
    
    def get_statistics(self) -> Dict:
        """ベクトルストアの統計情報を取得"""
        try:
            return {
                'total_vectors': self.index.ntotal if self.index else 0,
                'vector_dimension': self.index.d if self.index else 0,
                'metadata_count': len(self.metadata) if self.metadata else 0,
                'texts_count': len(self.texts) if self.texts else 0,
                'index_type': 'IndexFlatIP' if self.index else 'None'
            }
        except Exception as e:
            logger.error(f"統計情報取得エラー: {str(e)}")
            return {}

