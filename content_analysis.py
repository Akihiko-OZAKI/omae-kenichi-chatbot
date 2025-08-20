#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学習結果ファイルの内容分析
大前研一チャットボットの学習データを詳しく確認
"""

import os
import json
import re
from collections import Counter

def analyze_metadata():
    """メタデータの詳細分析"""
    print("=== メタデータ詳細分析 ===")
    
    base_path = os.path.join(os.path.dirname(__file__), "学習結果")
    meta_path = os.path.join(base_path, "faiss_meta.json")
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"総メタデータ数: {len(metadata)}件")
    
    # ソースファイルの統計
    sources = Counter(item.get('source', 'Unknown') for item in metadata)
    print(f"\nソースファイル統計:")
    for source, count in sources.most_common():
        print(f"  {source}: {count}件")
    
    # ページ数の統計
    pages = [item.get('page', 0) for item in metadata]
    print(f"\nページ数統計:")
    print(f"  最小ページ: {min(pages)}")
    print(f"  最大ページ: {max(pages)}")
    print(f"  平均ページ: {sum(pages) / len(pages):.1f}")
    
    # テキスト長の統計
    lengths = [item.get('len', 0) for item in metadata]
    print(f"\nテキスト長統計:")
    print(f"  最小長: {min(lengths)}文字")
    print(f"  最大長: {max(lengths)}文字")
    print(f"  平均長: {sum(lengths) / len(lengths):.1f}文字")
    
    # 長いテキストの上位10件
    long_texts = sorted(metadata, key=lambda x: x.get('len', 0), reverse=True)[:10]
    print(f"\n長いテキスト上位10件:")
    for i, item in enumerate(long_texts, 1):
        source = item.get('source', 'Unknown')
        page = item.get('page', 'Unknown')
        length = item.get('len', 0)
        print(f"  {i}. {source} (p.{page}): {length}文字")

def analyze_texts():
    """テキストデータの詳細分析"""
    print("\n=== テキストデータ詳細分析 ===")
    
    base_path = os.path.join(os.path.dirname(__file__), "学習結果")
    texts_path = os.path.join(base_path, "faiss_texts.jsonl")
    
    texts = []
    with open(texts_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    text_data = json.loads(line)
                    texts.append(text_data)
                except json.JSONDecodeError:
                    continue
    
    print(f"総テキスト数: {len(texts)}件")
    
    # テキスト長の統計
    text_lengths = [len(text.get('text', '')) for text in texts]
    print(f"\nテキスト長統計:")
    print(f"  最小長: {min(text_lengths)}文字")
    print(f"  最大長: {max(text_lengths)}文字")
    print(f"  平均長: {sum(text_lengths) / len(text_lengths):.1f}文字")
    
    # 長いテキストの上位10件
    long_texts = sorted(texts, key=lambda x: len(x.get('text', '')), reverse=True)[:10]
    print(f"\n長いテキスト上位10件:")
    for i, text_data in enumerate(long_texts, 1):
        text = text_data.get('text', '')
        length = len(text)
        preview = text[:100] + "..." if len(text) > 100 else text
        print(f"  {i}. {length}文字: {preview}")
    
    # キーワード分析
    all_text = ' '.join(text.get('text', '') for text in texts)
    
    # 日本語キーワード
    japanese_words = re.findall(r'[\u4e00-\u9fff]{2,}', all_text)
    japanese_counter = Counter(japanese_words)
    print(f"\n日本語キーワード上位20件:")
    for word, count in japanese_counter.most_common(20):
        print(f"  {word}: {count}回")
    
    # 英語キーワード
    english_words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
    english_counter = Counter(english_words)
    print(f"\n英語キーワード上位20件:")
    for word, count in english_counter.most_common(20):
        print(f"  {word}: {count}回")

def analyze_ocr_results():
    """OCR結果の詳細分析"""
    print("\n=== OCR結果詳細分析 ===")
    
    base_path = os.path.join(os.path.dirname(__file__), "学習結果")
    ocr_path = os.path.join(base_path, "ocr_results_all.json")
    
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    print(f"総OCR結果数: {len(ocr_data)}件")
    
    # ソースファイルの統計
    sources = Counter(item.get('source', 'Unknown') for item in ocr_data)
    print(f"\nソースファイル統計:")
    for source, count in sources.most_common():
        print(f"  {source}: {count}件")
    
    # ページ数の統計
    page_counts = []
    total_text_length = 0
    
    for item in ocr_data:
        pages = item.get('pages', [])
        page_counts.append(len(pages))
        
        for page in pages:
            text = page.get('text', '')
            total_text_length += len(text)
    
    print(f"\nページ数統計:")
    print(f"  最小ページ: {min(page_counts) if page_counts else 0}")
    print(f"  最大ページ: {max(page_counts) if page_counts else 0}")
    print(f"  平均ページ: {sum(page_counts) / len(page_counts) if page_counts else 0:.1f}")
    print(f"  総テキスト長: {total_text_length:,}文字")

def find_specific_content():
    """特定の内容を検索"""
    print("\n=== 特定内容検索 ===")
    
    base_path = os.path.join(os.path.dirname(__file__), "学習結果")
    texts_path = os.path.join(base_path, "faiss_texts.jsonl")
    
    # 検索キーワード
    keywords = [
        "大前研一",
        "グローバル戦略",
        "リーダーシップ",
        "デジタル変革",
        "50代",
        "サラリーマン",
        "経営戦略",
        "Kenichi Ohmae",
        "Global strategy",
        "Leadership"
    ]
    
    texts = []
    with open(texts_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    text_data = json.loads(line)
                    texts.append(text_data)
                except json.JSONDecodeError:
                    continue
    
    for keyword in keywords:
        print(f"\nキーワード: '{keyword}'")
        matches = []
        
        for i, text_data in enumerate(texts):
            text = text_data.get('text', '')
            if keyword in text:
                matches.append((i, text))
        
        print(f"  マッチ数: {len(matches)}件")
        
        if matches:
            print("  最初の3件:")
            for idx, text in matches[:3]:
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"    [{idx}] {preview}")

def main():
    """メイン関数"""
    print("大前研一チャットボット 学習結果ファイル詳細分析")
    print("=" * 60)
    
    try:
        analyze_metadata()
        analyze_texts()
        analyze_ocr_results()
        find_specific_content()
        
        print("\n" + "=" * 60)
        print("分析完了")
        print("=" * 60)
        
    except Exception as e:
        print(f"分析中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()


