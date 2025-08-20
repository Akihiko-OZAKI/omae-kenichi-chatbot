#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学習結果ファイルの簡単な確認テスト
依存関係なしで実行可能
"""

import os
import json

def test_files():
    """学習結果ファイルの存在確認と基本情報の表示"""
    print("=== 学習結果ファイル確認 ===")
    
    base_path = os.path.join(os.path.dirname(__file__), "学習結果")
    
    files = [
        ("faiss_index_ip.faiss", "FAISSインデックス"),
        ("faiss_meta.json", "メタデータ"),
        ("faiss_texts.jsonl", "テキストデータ"),
        ("ocr_results_all.json", "OCR結果")
    ]
    
    for filename, description in files:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✓ {description}: {filename} ({size_mb:.1f}MB)")
        else:
            print(f"✗ {description}: {filename} (見つかりません)")
    
    return True

def test_metadata():
    """メタデータファイルの内容確認"""
    print("\n=== メタデータ確認 ===")
    
    try:
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        meta_path = os.path.join(base_path, "faiss_meta.json")
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"✓ メタデータ読み込み成功: {len(metadata)}件")
        
        # 最初の数件を表示
        print("\n最初の5件のメタデータ:")
        for i, item in enumerate(metadata[:5]):
            source = item.get('source', 'Unknown')
            page = item.get('page', 'Unknown')
            print(f"  {i+1}. {source} (p.{page})")
        
        # ソースファイルの統計
        sources = {}
        for item in metadata:
            source = item.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\nソースファイル統計:")
        for source, count in sorted(sources.items()):
            print(f"  {source}: {count}件")
        
        return True
        
    except Exception as e:
        print(f"✗ メタデータ確認失敗: {str(e)}")
        return False

def test_texts():
    """テキストファイルの内容確認"""
    print("\n=== テキストデータ確認 ===")
    
    try:
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        texts_path = os.path.join(base_path, "faiss_texts.jsonl")
        
        texts = []
        with open(texts_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        text_data = json.loads(line)
                        texts.append(text_data)
                        if len(texts) >= 5:  # 最初の5件のみ
                            break
                    except json.JSONDecodeError as e:
                        print(f"  行{line_num}でJSONエラー: {e}")
                        continue
        
        print(f"✓ テキストデータ読み込み成功: {len(texts)}件（最初の5件）")
        
        # 最初の数件を表示
        for i, text_data in enumerate(texts):
            text = text_data.get('text', '')
            preview = text[:100] + "..." if len(text) > 100 else text
            print(f"\n  {i+1}. テキストプレビュー:")
            print(f"     {preview}")
        
        return True
        
    except Exception as e:
        print(f"✗ テキストデータ確認失敗: {str(e)}")
        return False

def test_ocr_results():
    """OCR結果ファイルの確認"""
    print("\n=== OCR結果確認 ===")
    
    try:
        base_path = os.path.join(os.path.dirname(__file__), "学習結果")
        ocr_path = os.path.join(base_path, "ocr_results_all.json")
        
        with open(ocr_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f)
        
        print(f"✓ OCR結果読み込み成功: {len(ocr_data)}件")
        
        # 統計情報
        total_pages = sum(len(item.get('pages', [])) for item in ocr_data)
        total_text_length = sum(
            len(page.get('text', '')) 
            for item in ocr_data 
            for page in item.get('pages', [])
        )
        
        print(f"  総ページ数: {total_pages}")
        print(f"  総テキスト長: {total_text_length:,}文字")
        
        # 最初の数件を表示
        print("\n最初の3件のOCR結果:")
        for i, item in enumerate(ocr_data[:3]):
            source = item.get('source', 'Unknown')
            pages = len(item.get('pages', []))
            print(f"  {i+1}. {source}: {pages}ページ")
        
        return True
        
    except Exception as e:
        print(f"✗ OCR結果確認失敗: {str(e)}")
        return False

def main():
    """メイン関数"""
    print("大前研一チャットボット 学習結果ファイル確認")
    print("=" * 50)
    
    tests = [
        ("ファイル存在確認", test_files),
        ("メタデータ確認", test_metadata),
        ("テキストデータ確認", test_texts),
        ("OCR結果確認", test_ocr_results)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}で例外発生: {str(e)}")
            results.append((test_name, False))
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("確認結果サマリー")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n総合結果: {passed}/{total} 確認通過")
    
    if passed == total:
        print("🎉 全ての学習結果ファイルが正常です！")
        print("次のステップ: 依存関係をインストールしてチャットボットを起動")
    else:
        print("⚠️  一部のファイルに問題があります。確認が必要です。")

if __name__ == "__main__":
    main()

