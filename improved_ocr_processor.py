#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改善されたOCR処理スクリプト（Tesseract 5.0使用）
"""

import os
import json
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedOCRProcessor:
    def __init__(self, tesseract_path=None):
        """
        OCR処理の初期化
        Args:
            tesseract_path: Tesseractの実行ファイルパス
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Tesseract 5.0の設定
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
    
    def extract_text_from_image(self, image_path):
        """
        画像からテキストを抽出
        """
        try:
            # 画像読み込み
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"画像の読み込みに失敗: {image_path}")
                return ""
            
            # 前処理
            processed_image = self.preprocess_image(image)
            
            # OCR実行
            text = pytesseract.image_to_string(processed_image, config=self.config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR処理エラー: {str(e)}")
            return ""
    
    def process_pdf(self, pdf_path, output_path=None):
        """
        PDFを処理してテキストを抽出
        """
        try:
            logger.info(f"PDF処理開始: {pdf_path}")
            
            # PDFを画像に変換
            images = convert_from_path(pdf_path, dpi=300)
            
            results = []
            
            for page_num, image in enumerate(images, 1):
                logger.info(f"ページ {page_num} を処理中...")
                
                # 画像を一時ファイルに保存
                temp_image_path = f"temp_page_{page_num}.png"
                image.save(temp_image_path, "PNG")
                
                # OCR処理
                text = self.extract_text_from_image(temp_image_path)
                
                # 一時ファイル削除
                os.remove(temp_image_path)
                
                # 結果を保存
                result = {
                    "text": text,
                    "page": page_num,
                    "source": os.path.basename(pdf_path),
                    "type": "improved_ocr",
                    "importance_score": 0.8 if text.strip() else 0.1
                }
                
                results.append(result)
                
                logger.info(f"ページ {page_num} 完了: {len(text)} 文字")
            
            # 結果を保存
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                logger.info(f"結果を保存: {output_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"PDF処理エラー: {str(e)}")
            return []

def main():
    """
    メイン処理
    """
    # PDFファイルのパス
    pdf_path = "static/uploads/pdf"
    
    # 出力ファイルのパス
    output_path = "improved_ocr_results.json"
    
    # OCR処理の実行
    processor = ImprovedOCRProcessor()
    results = processor.process_pdf(pdf_path, output_path)
    
    print(f"処理完了: {len(results)} ページ")
    print(f"結果ファイル: {output_path}")

if __name__ == "__main__":
    main()
