#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colab全ファイル全ページOCR処理（進捗保存機能付き）
"""

# システム依存関係のインストール
!apt-get update
!apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-jpn

# Python依存関係のインストール（NumPy 1.x系で互換性確保）
!pip install "numpy<2.0"
!pip install opencv-python==4.8.1.78
!pip install pytesseract==0.3.10 Pillow==10.0.0 pdf2image==1.16.3

import os
import json
import numpy as np
import cv2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import logging
from google.colab import drive
import glob
import shutil
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColabOCRProcessor:
    def __init__(self):
        """
        Colab用OCR処理の初期化
        """
        # Tesseract 5.0の設定（Colabでは既に利用可能）
        self.config = '--oem 3 --psm 6 -l jpn+eng'
        
    def preprocess_image(self, image):
        """
        画像の前処理（ノイズ除去、コントラスト改善）
        """
        # グレースケール変換
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # コントラスト改善
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # 二値化
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def extract_text_from_image(self, image):
        """
        画像からテキストを抽出
        """
        try:
            # PIL ImageをOpenCV形式に変換
            if isinstance(image, Image.Image):
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                image_cv = image
            
            # 前処理
            processed_image = self.preprocess_image(image_cv)
            
            # OCR実行
            text = pytesseract.image_to_string(processed_image, config=self.config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR処理エラー: {str(e)}")
            return ""
    
    def process_pdf(self, pdf_path):
        """
        PDFを処理してテキストを抽出（全ページ）
        """
        try:
            logger.info(f"PDF処理開始: {pdf_path}")
            
            # PDFを画像に変換（高解像度）
            images = convert_from_path(pdf_path, dpi=300)
            
            results = []
            
            for page_num, image in enumerate(images, 1):
                logger.info(f"ページ {page_num} を処理中...")
                
                # OCR処理
                text = self.extract_text_from_image(image)
                
                # 結果を保存
                result = {
                    "text": text,
                    "page": page_num,
                    "source": os.path.basename(pdf_path),
                    "type": "improved_ocr_colab_full",
                    "importance_score": 0.8 if text.strip() else 0.1
                }
                
                results.append(result)
                
                logger.info(f"ページ {page_num} 完了: {len(text)} 文字")
                
                # 進捗表示（10ページごと）
                if page_num % 10 == 0:
                    print(f"進捗: {page_num}/{len(images)} ページ完了")
            
            return results
            
        except Exception as e:
            logger.error(f"PDF処理エラー: {str(e)}")
            return []

def mount_google_drive():
    """
    Google Driveをマウント
    """
    print("Google Driveをマウント中...")
    drive.mount('/content/drive')
    print("Google Driveマウント完了")

def copy_files_with_ascii_names():
    """
    日本語ファイル名をASCII名にコピー
    """
    drive_path = "/content/drive/MyDrive/Colab Notebooks/書籍PDF"
    local_path = "/content/pdf_files"
    
    # ローカルディレクトリ作成
    os.makedirs(local_path, exist_ok=True)
    
    # 大前研一を含むPDFファイルを検索
    pattern = os.path.join(drive_path, "*大前研一*.pdf")
    pdf_files = glob.glob(pattern)
    
    print(f"発見されたPDFファイル数: {len(pdf_files)}")
    
    copied_files = []
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            # ASCII名でコピー
            ascii_name = f"omae_kenichi_{i:02d}.pdf"
            local_file = os.path.join(local_path, ascii_name)
            
            shutil.copy2(pdf_file, local_file)
            copied_files.append(local_file)
            
            print(f"{i}. {os.path.basename(pdf_file)} → {ascii_name}")
            
        except Exception as e:
            print(f"コピーエラー {i}: {str(e)}")
            continue
    
    return copied_files

def save_progress(all_results, processed_files, output_dir):
    """
    進捗を保存
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 結果ファイルを保存
    output_path = os.path.join(output_dir, f"ocr_results_{timestamp}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    # 進捗ファイルを保存
    progress_path = os.path.join(output_dir, f"progress_{timestamp}.json")
    progress_data = {
        "timestamp": timestamp,
        "processed_files": processed_files,
        "total_results": len(all_results),
        "total_text_length": sum(len(r['text']) for r in all_results)
    }
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    print(f"進捗保存: {output_path}")
    print(f"進捗情報: {progress_path}")
    
    return output_path, progress_path

def main():
    """
    メイン処理
    """
    print("=== Colab全ファイル全ページOCR処理（進捗保存機能付き）===")
    
    # 出力ディレクトリ作成
    output_dir = "/content/ocr_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Google Driveをマウント
    mount_google_drive()
    
    # ファイルをASCII名でコピー
    pdf_files = copy_files_with_ascii_names()
    
    if not pdf_files:
        print("PDFファイルが見つかりませんでした")
        return
    
    print(f"\n全{len(pdf_files)}ファイルを処理します")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"{i}. {os.path.basename(pdf_file)}")
    
    # 全結果を格納
    all_results = []
    processed_files = []
    
    # 各PDFファイルを処理
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n=== 処理中 ({i}/{len(pdf_files)}): {os.path.basename(pdf_path)} ===")
        
        try:
            # OCR処理（全ページ）
            processor = ColabOCRProcessor()
            results = processor.process_pdf(pdf_path)
            
            if results:
                all_results.extend(results)
                processed_files.append({
                    "file": os.path.basename(pdf_path),
                    "pages": len(results),
                    "text_length": sum(len(r['text']) for r in results)
                })
                
                print(f"処理完了: {len(results)} ページ")
                
                # 企業名の検索テスト
                text_all = " ".join([r['text'] for r in results])
                companies = ['ヤマハ', 'YAMAHA', '日立', 'Hitachi', 'パナソニック', 'Panasonic']
                found_companies = [company for company in companies if company in text_all]
                
                if found_companies:
                    print(f"発見された企業名: {found_companies}")
                else:
                    print("企業名が見つかりませんでした")
                    
                # サンプルテキストを表示
                if results:
                    sample = results[0]
                    print(f"\nサンプルテキスト（ページ{sample['page']}）:")
                    print(f"{sample['text'][:200]}...")
                
                # 各ファイル処理後に進捗を保存
                output_path, progress_path = save_progress(all_results, processed_files, output_dir)
                
                # 結果ファイルをダウンロード
                from google.colab import files
                files.download(output_path)
                files.download(progress_path)
                
            else:
                print("処理結果が空でした")
                
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
            # エラーが発生しても進捗を保存
            if all_results:
                save_progress(all_results, processed_files, output_dir)
            continue
    
    # 最終結果を保存
    if all_results:
        final_output_path, final_progress_path = save_progress(all_results, processed_files, output_dir)
        
        print(f"\n=== 全処理完了 ===")
        print(f"総ページ数: {len(all_results)}")
        print(f"処理したPDF数: {len(processed_files)}")
        print(f"最終結果ファイル: {final_output_path}")
        
        # 統計情報を表示
        print("\n=== 統計情報 ===")
        total_text_length = sum(len(r['text']) for r in all_results)
        print(f"総文字数: {total_text_length:,}")
        
        # 企業名の全体検索
        text_all = " ".join([r['text'] for r in all_results])
        companies = ['ヤマハ', 'YAMAHA', '日立', 'Hitachi', 'パナソニック', 'Panasonic']
        found_companies = [company for company in companies if company in text_all]
        
        if found_companies:
            print(f"全体で発見された企業名: {found_companies}")
        else:
            print("全体で企業名が見つかりませんでした")
        
        # 最終ファイルをダウンロード
        from google.colab import files
        files.download(final_output_path)
        files.download(final_progress_path)
        
        print("\n=== 全処理完了 ===")
    else:
        print("処理結果がありませんでした")

if __name__ == "__main__":
    main()

