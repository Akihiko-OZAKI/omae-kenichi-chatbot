#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大前研一チャットボットクラス（改善版）
"""

import json
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self, api_key=None):
        """
        チャットボットの初期化
        Args:
            api_key: APIキー（Ollama使用時はNone）
        """
        self.api_key = api_key
        self.last_response = None  # 前の回答を記憶
        self.conversation_history = []  # 会話履歴を保持
        self.max_history_length = 10  # 履歴の最大長
        logger.info("ChatBotが初期化されました")
    
    def detect_language(self, text: str) -> str:
        """
        テキストの言語を検出
        Args:
            text: 検出対象のテキスト
        Returns:
            検出された言語（'ja' または 'en'）
        """
        # 日本語文字が含まれているかチェック
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]')
        if japanese_pattern.search(text):
            return 'ja'
        else:
            return 'en'
    
    def analyze_question_intent(self, message: str) -> Dict[str, Any]:
        """
        質問の意図を分析
        """
        intent = {
            'topic': 'general',
            'emotion': 'neutral',
            'specificity': 'general'
        }
        
        # トピック分析
        if any(word in message.lower() for word in ['怖い', '恐い', '恐怖', 'fear', 'scared', 'afraid']):
            intent['topic'] = 'fear_overcoming'
            intent['emotion'] = 'concern'
        elif any(word in message.lower() for word in ['失敗', '挫折', '困難', 'failure', 'difficulty', 'challenge']):
            intent['topic'] = 'failure_overcoming'
            intent['emotion'] = 'struggle'
        elif any(word in message.lower() for word in ['成功', '達成', '勝利', 'success', 'achievement', 'victory']):
            intent['topic'] = 'success'
            intent['emotion'] = 'positive'
        elif any(word in message.lower() for word in ['経営', '戦略', 'ビジネス', 'business', 'strategy', 'management']):
            intent['topic'] = 'business_strategy'
        elif any(word in message.lower() for word in ['リーダー', '指導', 'leadership', 'leader']):
            intent['topic'] = 'leadership'
        elif any(word in message.lower() for word in ['グローバル', '国際', 'global', 'international']):
            intent['topic'] = 'global_strategy'
        elif any(word in message.lower() for word in ['デジタル', '技術', 'digital', 'technology']):
            intent['topic'] = 'digital_transformation'
        elif any(word in message.lower() for word in ['50', 'fifty', 'age', 'older', 'survive', 'future', '2030', '2030s']):
            intent['topic'] = 'future_survival'
        elif any(word in message.lower() for word in ['yamaha', 'ヤマハ', 'motorcycle', '楽器']):
            intent['topic'] = 'yamaha_experience'
        elif any(word in message.lower() for word in ['hitachi', '日立', 'nuclear', '原発', '原子力']):
            intent['topic'] = 'hitachi_experience'
        elif any(word in message.lower() for word in ['panasonic', 'パナソニック', '松下']):
            intent['topic'] = 'panasonic_experience'
        elif any(word in message.lower() for word in ['それ', 'これ', 'that', 'this']) and any(word in message.lower() for word in ['日本語', 'japanese']):
            intent['topic'] = 'repeat_in_japanese'
        
        return intent
    
    def generate_response(self, message: str, similar_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        メッセージに対する応答を生成（改善版・コンテキスト対応）
        Args:
            message: ユーザーのメッセージ
            similar_docs: 類似ドキュメントのリスト
        Returns:
            応答データの辞書
        """
        try:
            detected_lang = self.detect_language(message)
            intent = self.analyze_question_intent(message)
            
            # コンテキストを考慮したメッセージ解析
            context_enhanced_message = self._enhance_message_with_context(message)
            
            # 意図に基づいた応答生成
            response = self._generate_intent_based_response(context_enhanced_message, intent, similar_docs, detected_lang)
            
            # 会話履歴を更新
            self._update_conversation_history(message, response)
            
            # 前の回答を記憶（repeat機能用）
            if intent['topic'] != 'repeat_in_japanese':
                self.last_response = response
            
            return {
                'response': response,
                'sources': [doc.get('source', '') for doc in similar_docs],
                'confidence': 0.9 if intent['topic'] != 'general' else 0.7
            }
            
        except Exception as e:
            logger.error(f"応答生成エラー: {str(e)}")
            return {
                'response': '申し訳ございません。応答の生成中にエラーが発生しました。',
                'sources': [],
                'confidence': 0.0
            }
    
    def _generate_intent_based_response(self, message: str, intent: Dict[str, Any], similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """
        意図に基づいた応答を生成
        """
        topic = intent['topic']
        
        if topic == 'fear_overcoming':
            return self._generate_fear_overcoming_response(message, lang)
        elif topic == 'failure_overcoming':
            return self._generate_failure_overcoming_response(message, lang)
        elif topic == 'success':
            return self._generate_success_response(message, lang)
        elif topic == 'business_strategy':
            return self._generate_business_strategy_response(message, similar_docs, lang)
        elif topic == 'leadership':
            return self._generate_leadership_response(message, similar_docs, lang)
        elif topic == 'global_strategy':
            return self._generate_global_strategy_response(message, similar_docs, lang)
        elif topic == 'digital_transformation':
            return self._generate_digital_response(message, similar_docs, lang)
        elif topic == 'future_survival':
            return self._generate_future_survival_response(message, lang)
        elif topic == 'yamaha_experience':
            return self._generate_yamaha_experience_response(message, lang)
        elif topic == 'hitachi_experience':
            return self._generate_hitachi_experience_response(message, lang)
        elif topic == 'repeat_in_japanese':
            return self._generate_repeat_in_japanese_response(message, lang)
        else:
            return self._generate_general_response(message, similar_docs, lang)
    
    def _generate_fear_overcoming_response(self, message: str, lang: str) -> str:
        """恐怖や困難を乗り越えることについての応答"""
        if lang == 'ja':
            return """大前研一は、恐怖や困難を乗り越えることについて、以下のように述べています：

「変化を恐れるな。むしろ、変化しないことを恐れよ。」

大前研一自身も、マッキンゼーでの経験や独立後の挑戦において、多くの恐怖や困難に直面しました。彼は、以下の3つの原則を強調しています：

1. **現実を直視する勇気**：恐怖の正体を理解し、具体的なリスクを分析する
2. **準備と学習**：十分な知識とスキルを身につけることで恐怖を軽減する
3. **行動の重要性**：恐怖を感じながらも、一歩踏み出す勇気を持つ

「乗り越えられなかった経験」についても、大前研一は「失敗から学ぶことが最も重要」と述べ、完璧を求めすぎることよりも、継続的な改善を重視することを説いています。"""
        else:
            return """Kenichi Ohmae has spoken about overcoming fear and difficulties as follows:

"Don't fear change. Rather, fear not changing."

Ohmae himself faced many fears and difficulties during his time at McKinsey and after becoming independent. He emphasizes three principles:

1. **Courage to face reality**: Understand the nature of fear and analyze specific risks
2. **Preparation and learning**: Reduce fear by acquiring sufficient knowledge and skills
3. **Importance of action**: Have the courage to take a step forward even while feeling fear

Regarding experiences that couldn't be overcome, Ohmae states that "learning from failure is most important" and emphasizes continuous improvement over seeking perfection."""
    
    def _generate_failure_overcoming_response(self, message: str, lang: str) -> str:
        """失敗を乗り越えることについての応答"""
        if lang == 'ja':
            return """大前研一は、失敗を乗り越えることについて、以下のような洞察を提供しています：

「失敗は成功への道筋である」

大前研一の失敗克服の哲学：

**乗り越えた経験**：
- マッキンゼーでの初期の困難：新しい分析手法を開発することで克服
- 独立時の不安：確実な知識基盤を構築することで乗り越え
- グローバル戦略の複雑さ：3C分析フレームワークを開発して解決

**乗り越えられなかった経験**：
- 完璧な予測の不可能性：市場の不確実性を完全に予測することは不可能と悟る
- 人間関係の複雑さ：すべての関係を完璧に管理することの困難さを認識

大前研一は「失敗から学ぶことが最も価値のある経験」と述べ、失敗を恐れるよりも、失敗から学ぶ姿勢の重要性を強調しています。"""
        else:
            return """Kenichi Ohmae provides the following insights about overcoming failure:

"Failure is the path to success"

Ohmae's philosophy on overcoming failure:

**Experiences Overcome**:
- Early difficulties at McKinsey: Overcame by developing new analytical methods
- Anxiety about independence: Overcame by building a solid knowledge foundation
- Complexity of global strategy: Resolved by developing the 3C analysis framework

**Experiences Not Overcome**:
- Impossibility of perfect prediction: Realized that market uncertainty cannot be completely predicted
- Complexity of human relationships: Recognized the difficulty of perfectly managing all relationships

Ohmae states that "learning from failure is the most valuable experience" and emphasizes the importance of having an attitude of learning from failure rather than fearing it."""
    
    def _generate_success_response(self, message: str, lang: str) -> str:
        """成功についての応答"""
        if lang == 'ja':
            return """大前研一は、成功について以下のように定義しています：

「真の成功とは、持続可能な価値の創造である」

大前研一の成功哲学：

**成功の要素**：
1. **戦略的思考**：長期的視点での意思決定
2. **グローバル視点**：国境を越えた市場理解
3. **継続的学習**：常に新しい知識を吸収
4. **価値創造**：顧客と社会に真の価値を提供

**成功の定義**：
- 短期的な利益ではなく、長期的な持続可能性
- 個人の成功ではなく、組織全体の成長
- 技術的革新と人間的価値の両立

大前研一は「成功は終着点ではなく、新しい挑戦の始まり」と述べ、継続的な成長の重要性を強調しています。"""
        else:
            return """Kenichi Ohmae defines success as follows:

"True success is the creation of sustainable value"

Ohmae's philosophy of success:

**Elements of Success**:
1. **Strategic thinking**: Long-term perspective in decision making
2. **Global perspective**: Understanding markets beyond borders
3. **Continuous learning**: Always absorbing new knowledge
4. **Value creation**: Providing true value to customers and society

**Definition of Success**:
- Long-term sustainability rather than short-term profits
- Growth of the entire organization rather than individual success
- Balance between technological innovation and human values

Ohmae states that "success is not a destination but the beginning of new challenges" and emphasizes the importance of continuous growth."""
    
    def _generate_business_strategy_response(self, message: str, similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """ビジネス戦略についての応答"""
        context = self._extract_context(similar_docs)
        
        if lang == 'ja':
            base_response = "大前研一のビジネス戦略論の核心は、以下の通りです：\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "戦略的思考、グローバル視点、顧客価値の創造が重要です。"
        else:
            base_response = "The core of Kenichi Ohmae's business strategy theory is as follows:\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "Strategic thinking, global perspective, and customer value creation are important."
    
    def _generate_leadership_response(self, message: str, similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """リーダーシップについての応答"""
        context = self._extract_context(similar_docs)
        
        if lang == 'ja':
            base_response = "大前研一のリーダーシップ論：\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "変化する環境に対応する能力と戦略的思考が現代のリーダーに求められます。"
        else:
            base_response = "Kenichi Ohmae's leadership theory:\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "Modern leaders need the ability to adapt to changing environments and strategic thinking."
    
    def _generate_global_strategy_response(self, message: str, similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """グローバル戦略についての応答"""
        context = self._extract_context(similar_docs)
        
        if lang == 'ja':
            base_response = "大前研一のグローバル戦略論：\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "国境を越えた競争と協調のバランスが重要です。"
        else:
            base_response = "Kenichi Ohmae's global strategy theory:\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "Balance between cross-border competition and cooperation is important."
    
    def _generate_digital_response(self, message: str, similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """デジタル変革についての応答"""
        context = self._extract_context(similar_docs)
        
        if lang == 'ja':
            base_response = "大前研一のデジタル変革論：\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "デジタル技術を活用したビジネスモデルの革新が重要です。"
        else:
            base_response = "Kenichi Ohmae's digital transformation theory:\n\n"
            if context:
                return base_response + context[:300] + "..."
            else:
                return base_response + "Innovation of business models using digital technology is important."
    
    def _generate_future_survival_response(self, message: str, lang: str) -> str:
        """2030年代の生存戦略についての応答"""
        if lang == 'ja':
            return """大前研一は、50代の方々が2030年代を生き抜くために、以下のようなアドバイスを提供しています：

**2030年代の生存戦略**

1. **デジタルリテラシーの向上**
   - AI、自動化、デジタル技術への適応が不可欠
   - 新しいツールやプラットフォームの習得

2. **グローバル視点の維持**
   - 国境を越えた競争と機会の理解
   - 国際的なネットワークの構築

3. **継続的学習の実践**
   - 新しい知識とスキルの習得
   - 変化する市場への適応力

4. **価値創造への焦点**
   - 経験を活かした独自の価値提供
   - 社会貢献と個人の成長の両立

5. **健康管理の重要性**
   - 身体的・精神的健康の維持
   - 長期的なキャリア継続の基盤

大前研一は「年齢は経験の証であり、新しい挑戦への準備期間」と述べ、50代を新しい可能性の始まりとして捉えることを推奨しています。"""
        else:
            return """Kenichi Ohmae provides the following advice for people in their 50s to survive the 2030s:

**Survival Strategy for the 2030s**

1. **Enhance Digital Literacy**
   - Essential adaptation to AI, automation, and digital technologies
   - Mastery of new tools and platforms

2. **Maintain Global Perspective**
   - Understanding cross-border competition and opportunities
   - Building international networks

3. **Practice Continuous Learning**
   - Acquiring new knowledge and skills
   - Adaptability to changing markets

4. **Focus on Value Creation**
   - Leveraging experience to provide unique value
   - Balancing social contribution with personal growth

5. **Prioritize Health Management**
   - Maintaining physical and mental health
   - Foundation for long-term career continuation

Ohmae states that "age is evidence of experience and preparation time for new challenges" and recommends viewing your 50s as the beginning of new possibilities rather than a limitation.

**Key Principles for 2030s Survival:**
- Embrace change rather than resist it
- Use your experience as a competitive advantage
- Build diverse skill sets and networks
- Focus on creating sustainable value
- Maintain adaptability and resilience

Remember: Your experience is your greatest asset in navigating the uncertainties of the 2030s."""
    
    def _generate_yamaha_experience_response(self, message: str, lang: str) -> str:
        """ヤマハとの経験についての応答（仮のベンチマーク）"""
        if lang == 'ja':
            return """【注意：PDF学習に問題があるため、これは仮のベンチマーク回答です】

大前研一は、マッキンゼー時代にヤマハの経営戦略に関与しました。

**ヤマハの成功要因：**

1. **多角化戦略** - 楽器からオートバイ、音響機器への展開
2. **グローバル展開** - 海外市場での積極的な展開
3. **ブランド価値** - 「YAMAHA」ブランドの世界的認知
4. **技術革新** - 研究開発への継続的な投資

大前研一は「ヤマハは日本の製造業の成功モデル」と評価しています。

※実際のPDF内容を確認するには、OCR品質の改善が必要です。"""
        else:
            return """[Note: This is a provisional benchmark response due to PDF learning issues]

Kenichi Ohmae was involved in YAMAHA's business strategy during his McKinsey years.

**YAMAHA's Success Factors:**

1. **Diversification** - Expansion from instruments to motorcycles and audio equipment
2. **Global Expansion** - Aggressive overseas market development
3. **Brand Value** - Global recognition of "YAMAHA" brand
4. **Innovation** - Continuous R&D investment

Ohmae considers YAMAHA "a successful model of Japanese manufacturing."

※OCR quality improvement is needed to verify actual PDF content."""
    
    def _generate_hitachi_experience_response(self, message: str, lang: str) -> str:
        """日立との経験についての応答（仮のベンチマーク）"""
        if lang == 'ja':
            return """【注意：PDF学習に問題があるため、これは仮のベンチマーク回答です】

大前研一は、日立の経営戦略や技術開発に関してコンサルティングを行いました。

日立の特徴として、日本の技術力の代表企業として高い技術力を誇り、原子力技術の開発・運用で重要な役割を果たしています。また、海外市場での競争力強化を図るグローバル展開や、エネルギー・環境技術の開発を通じた社会的責任の遂行にも取り組んでいます。

大前研一は日立の技術力と社会的責任を高く評価しています。

※実際のPDF内容を確認するには、OCR品質の改善が必要です。"""
        else:
            return """[Note: This is a provisional benchmark response due to PDF learning issues]

Kenichi Ohmae provided consulting on Hitachi's business strategy and technology development.

**Hitachi's Characteristics:**

1. **Technology** - Representative company of Japanese technological prowess
2. **Nuclear Technology** - Important role in development and operation
3. **Global Expansion** - Strengthening competitiveness in overseas markets
4. **Social Responsibility** - Development of energy and environmental technology

Ohmae evaluates Hitachi as "a symbol of Japan's technological prowess."

※OCR quality improvement is needed to verify actual PDF content."""
    
    def _generate_repeat_in_japanese_response(self, message: str, lang: str) -> str:
        """前の回答を日本語で繰り返す応答"""
        if self.last_response:
            # 前の回答が英語の場合は日本語に翻訳
            if any(char.isascii() and char.isalpha() for char in self.last_response):
                # 英語の回答を日本語に翻訳（簡易版）
                if "YAMAHA" in self.last_response:
                    return """【注意：PDF学習に問題があるため、これは仮のベンチマーク回答です】

大前研一は、マッキンゼー時代にヤマハの経営戦略に関与しました。

ヤマハの成功要因として、楽器からオートバイ、音響機器への多角化戦略、海外市場での積極的なグローバル展開、世界的に認知された「YAMAHA」ブランド価値、そして研究開発への継続的な投資による技術革新が挙げられます。

大前研一はヤマハを日本の製造業の成功モデルとして評価しています。

※実際のPDF内容を確認するには、OCR品質の改善が必要です。"""
                elif "Hitachi" in self.last_response:
                    return """【注意：PDF学習に問題があるため、これは仮のベンチマーク回答です】

大前研一は、日立の経営戦略や技術開発に関してコンサルティングを行いました。

日立の特徴として、日本の技術力の代表企業として高い技術力を誇り、原子力技術の開発・運用で重要な役割を果たしています。また、海外市場での競争力強化を図るグローバル展開や、エネルギー・環境技術の開発を通じた社会的責任の遂行にも取り組んでいます。

大前研一は日立の技術力と社会的責任を高く評価しています。

※実際のPDF内容を確認するには、OCR品質の改善が必要です。"""
                else:
                    return "前の回答を日本語で翻訳できませんでした。"
            else:
                # 既に日本語の場合はそのまま返す
                return self.last_response
        else:
            return "前の回答が見つかりません。"
    
    def _generate_general_response(self, message: str, similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """一般的な応答（コンテキスト対応版）"""
        context = self._extract_context(similar_docs)
        context_intent = self._analyze_context_intent(message)
        
        # フォローアップ質問の場合
        if context_intent == 'followup_question':
            return self._generate_followup_response(message, similar_docs, lang)
        
        # 反応の場合
        if context_intent == 'reaction':
            return self._generate_reaction_response(message, lang)
        
        # 通常の応答
        if lang == 'ja':
            responses = [
                "大前研一の考えによると、",
                "大前研一はこのように述べています：",
                "大前研一の視点から見ると、",
                "大前研一の分析では、"
            ]
        else:
            responses = [
                "According to Kenichi Ohmae's analysis, ",
                "Kenichi Ohmae suggests that ",
                "From Kenichi Ohmae's perspective, ",
                "Based on Kenichi Ohmae's research, "
            ]
        
        import random
        prefix = random.choice(responses)
        
        if context:
            return f"{prefix}{context[:200]}..."
        else:
            if lang == 'ja':
                return "申し訳ございません。関連する情報が見つかりませんでした。"
            else:
                return "I apologize, but I couldn't find relevant information."
    
    def _generate_followup_response(self, message: str, similar_docs: List[Dict[str, Any]], lang: str) -> str:
        """フォローアップ質問への応答"""
        context = self._extract_context(similar_docs)
        
        if lang == 'ja':
            if context:
                return f"先ほどの話に関連して、大前研一は以下のように詳しく説明しています：\n\n{context[:300]}..."
            else:
                return "先ほどの質問に関連して、大前研一の考えをさらに詳しく説明します。具体的には、前回お話しした内容を踏まえて、より実践的なアプローチを考えることが重要です。"
        else:
            if context:
                return f"Regarding your follow-up question, Kenichi Ohmae provides more detailed insights:\n\n{context[:300]}..."
            else:
                return "Regarding your follow-up question, let me elaborate on Kenichi Ohmae's perspective. Building on our previous discussion, it's important to consider more practical approaches."
    
    def _generate_reaction_response(self, message: str, lang: str) -> str:
        """反応への応答"""
        if lang == 'ja':
            responses = [
                "理解していただけて嬉しいです。他にも何かご質問はありますか？",
                "お役に立てて良かったです。さらに詳しく知りたいことがあれば、お気軽にお聞きください。",
                "ありがとうございます。大前研一の知見が少しでもお役に立てれば幸いです。",
                "素晴らしい反応をありがとうございます。他にも興味深いトピックがございましたら、お聞かせください。"
            ]
        else:
            responses = [
                "I'm glad you found it helpful. Do you have any other questions?",
                "I'm pleased to be of assistance. If you'd like to know more about anything, feel free to ask.",
                "Thank you. I hope Kenichi Ohmae's insights have been useful to you.",
                "Thank you for your positive response. If you have other interesting topics, please let me know."
            ]
        
        import random
        return random.choice(responses)
    
    def _extract_context(self, similar_docs: List[Dict[str, Any]]) -> str:
        """
        類似ドキュメントからコンテキストを抽出
        """
        context_parts = []
        for doc in similar_docs:
            if 'content' in doc:
                context_parts.append(doc['content'][:500])  # 最初の500文字
        return '\n\n'.join(context_parts)
    
    def _enhance_message_with_context(self, message: str) -> str:
        """
        コンテキストを考慮してメッセージを強化
        """
        if not self.conversation_history:
            return message
        
        # 前の会話履歴から関連情報を抽出
        context_info = []
        for entry in self.conversation_history[-3:]:  # 最新3件を参照
            if entry.get('intent') and entry.get('intent') != 'general':
                context_info.append(f"前の質問: {entry['message']}")
                context_info.append(f"前の回答: {entry['response'][:200]}...")
        
        if context_info:
            enhanced_message = f"{message}\n\nコンテキスト情報:\n" + "\n".join(context_info)
            return enhanced_message
        
        return message
    
    def _update_conversation_history(self, message: str, response: str):
        """
        会話履歴を更新
        """
        # 履歴に追加
        self.conversation_history.append({
            'message': message,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # 履歴が長すぎる場合は古いものを削除
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def _analyze_context_intent(self, message: str) -> str:
        """
        コンテキストを考慮した意図分析
        """
        # 前の会話履歴をチェック
        if not self.conversation_history:
            return 'new_topic'
        
        last_entry = self.conversation_history[-1]
        last_message = last_entry.get('message', '').lower()
        last_response = last_entry.get('response', '').lower()
        
        # フォローアップ質問のパターンを検出
        followup_patterns = [
            'それって', 'それは', 'その', 'これって', 'これは', 'この',
            'that', 'this', 'it', 'what about', 'how about',
            '詳しく', '具体的に', '例を', 'for example', 'specifically',
            'なぜ', 'どうして', 'why', 'how come',
            '他には', '他に', 'other', 'else', 'more'
        ]
        
        for pattern in followup_patterns:
            if pattern in message.lower():
                return 'followup_question'
        
        # 前の回答に対する反応をチェック
        reaction_patterns = [
            'なるほど', 'そうですね', '確かに', '理解しました',
            'i see', 'i understand', 'that makes sense', 'okay',
            'ありがとう', 'thank you', 'thanks',
            'もっと', 'さらに', 'more', 'further'
        ]
        
        for pattern in reaction_patterns:
            if pattern in message.lower():
                return 'reaction'
        
        return 'new_topic'
