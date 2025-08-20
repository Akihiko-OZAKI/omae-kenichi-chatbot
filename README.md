# 大前研一チャットボット 🤖

大前研一氏の著書13冊を学習したAIチャットボットです。  
質問に対して大前研一氏の視点で回答します。

## 🌟 特徴

- **多言語対応**: 日本語・英語の質問に対応
- **コンテキスト保持**: 会話の流れを理解してフォローアップ質問に対応
- **高精度検索**: FAISSベースのベクトル検索で関連情報を迅速に取得
- **13冊の書籍データ**: 大前研一氏の主要著書を学習済み

## 📚 学習済み書籍

1. 大前研一 サラリーマン・リカバリー
2. 大前研一 サラリーマンサバイバル  
3. 大前研一 やりたいことは全部やれ!
4. 大前研一 ビジネス・ウエポン
5. その他9冊の著書

**総ページ数**: 3,221ページ  
**学習チャンク数**: 3,266件

## 🚀 クイックスタート

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. アプリケーションの起動

```bash
python omae_app_faiss.py
```

### 3. ブラウザでアクセス

```
http://localhost:5000
```

## 🛠️ 技術仕様

### バックエンド
- **Python**: 3.11+
- **Webフレームワーク**: Flask
- **ベクトル検索**: FAISS (IndexFlatIP)
- **埋め込みモデル**: intfloat/multilingual-e5-base
- **OCR**: EasyOCR (GPU対応)

### フロントエンド
- **HTML/CSS/JavaScript**: モダンなUI
- **レスポンシブデザイン**: モバイル対応

### データ処理
- **チャンクサイズ**: 800文字
- **オーバーラップ**: 120文字
- **正規化**: 有効
- **プリフィックス**: passage:/query:

## 📁 プロジェクト構造

```
omae_kenichi/
├── omae_app_faiss.py      # メインアプリケーション
├── chat_bot.py            # チャットボットロジック
├── faiss_vector_store.py  # ベクトルストア管理
├── 学習結果/              # 学習済みデータ
│   ├── faiss_index_ip.faiss
│   ├── faiss_meta.json
│   ├── faiss_texts.jsonl
│   └── ocr_results_all.json
├── templates/             # HTMLテンプレート
├── static/               # CSS/JS/画像ファイル
├── requirements.txt      # 依存関係
└── render.yaml          # Renderデプロイ設定
```

## 🔧 開発・テスト

### システムテスト
```bash
python test_system.py
```

### 簡単テスト
```bash
python simple_test.py
```

## 🌐 デプロイ

### Render
```bash
# render.yamlで自動デプロイ設定済み
```

### ローカル開発
```bash
python omae_app_faiss.py
```

## 📝 使用例

**日本語質問**:
```
Q: サラリーマンが副業を始める際の注意点は？
A: 大前研一氏の視点から、時間管理と本業への影響を考慮した戦略的な副業の進め方について回答します...
```

**English Question**:
```
Q: What is the key to business success?
A: From Kenichi Ohmae's perspective, the key to business success involves...
```

## 🔮 今後の予定

- [ ] 本田宗一郎チャットボットとの統合
- [ ] 中島らも氏チャットボットの追加
- [ ] 宮崎学氏チャットボットの追加
- [ ] アンサンブル相談システムの構築
- [ ] 多言語対応の拡張

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

プルリクエストやイシューの報告を歓迎します！

---

**開発者**: AI Study Project  
**最終更新**: 2024年12月
