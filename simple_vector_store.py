#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡易版ベクトルストア（ChromaDBなし）
"""

import os
import json
import logging
from typing import List, Dict, Optional
import random

logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """簡易版ベクトルストア管理クラス"""
    
    def __init__(self, persist_directory: str = "./omae_chroma_db"):
        """
        SimpleVectorStoreの初期化
        
        Args:
            persist_directory: データの保存ディレクトリ
        """
        self.persist_directory = persist_directory
        self.documents = []
        self.load_documents()
    
    def load_documents(self):
        """ドキュメントの読み込み"""
        try:
            # サンプルドキュメントを作成
            self.documents = [
                {
                    "id": "1",
                    "content": "大前研一は、日本の経営コンサルタントであり、グローバル戦略の専門家です。彼は、企業のグローバル化戦略について多くの洞察を提供しています。",
                    "source": "大前研一の経営論",
                    "metadata": {"author": "大前研一", "category": "経営戦略"}
                },
                {
                    "id": "2", 
                    "content": "グローバル化の時代において、企業は国境を越えた競争に直面しています。大前研一は、このような環境での成功要因について分析しています。",
                    "source": "グローバル戦略論",
                    "metadata": {"author": "大前研一", "category": "グローバル化"}
                },
                {
                    "id": "3",
                    "content": "デジタル技術の進歩により、ビジネスモデルは大きく変化しています。大前研一は、デジタル時代の経営について重要な指摘をしています。",
                    "source": "デジタル経営論", 
                    "metadata": {"author": "大前研一", "category": "デジタル化"}
                },
                {
                    "id": "4",
                    "content": "リーダーシップの本質は、変化する環境に対応する能力にあります。大前研一は、現代のリーダーに求められる資質について論じています。",
                    "source": "リーダーシップ論",
                    "metadata": {"author": "大前研一", "category": "リーダーシップ"}
                },
                {
                    "id": "5",
                    "content": "イノベーションは、既存の枠組みを超える思考から生まれます。大前研一は、創造的破壊の重要性を強調しています。",
                    "source": "イノベーション論",
                    "metadata": {"author": "大前研一", "category": "イノベーション"}
                }
            ]
            logger.info(f"{len(self.documents)}件のドキュメントを読み込みました")
        except Exception as e:
            logger.error(f"ドキュメント読み込みエラー: {str(e)}")
            self.documents = []
    
    def search_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        類似ドキュメントの検索（簡易版）
        
        Args:
            query: 検索クエリ
            n_results: 取得する結果数
            
        Returns:
            類似ドキュメントのリスト
        """
        try:
            # 簡易的な検索（キーワードマッチング）
            query_lower = query.lower()
            scored_docs = []
            
            for doc in self.documents:
                score = 0
                content_lower = doc["content"].lower()
                
                # キーワードマッチング
                keywords = ["大前研一", "経営", "戦略", "グローバル", "デジタル", "リーダーシップ", "イノベーション"]
                for keyword in keywords:
                    if keyword.lower() in query_lower and keyword.lower() in content_lower:
                        score += 1
                
                if score > 0:
                    scored_docs.append((doc, score))
            
            # スコアでソート
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            
            # 結果を返す
            results = [doc for doc, score in scored_docs[:n_results]]
            
            # 結果が少ない場合はランダムに追加
            if len(results) < n_results:
                remaining_docs = [doc for doc in self.documents if doc not in results]
                random.shuffle(remaining_docs)
                results.extend(remaining_docs[:n_results - len(results)])
            
            logger.info(f"検索結果: {len(results)}件")
            return results
            
        except Exception as e:
            logger.error(f"検索エラー: {str(e)}")
            return self.documents[:n_results]
    
    def add_document(self, content: str, source: str = "", metadata: Dict = None):
        """
        ドキュメントの追加
        
        Args:
            content: ドキュメントの内容
            source: ソース情報
            metadata: メタデータ
        """
        try:
            doc_id = str(len(self.documents) + 1)
            doc = {
                "id": doc_id,
                "content": content,
                "source": source,
                "metadata": metadata or {}
            }
            self.documents.append(doc)
            logger.info(f"ドキュメントを追加しました: {doc_id}")
        except Exception as e:
            logger.error(f"ドキュメント追加エラー: {str(e)}")
