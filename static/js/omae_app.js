// 大前研一チャットボット用JavaScript（コンテキスト対応版）

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const confidenceNotice = document.getElementById('confidenceNotice');
    
    // ローカル会話履歴を保持
    let localConversationHistory = [];

    // メッセージ送信処理
    async function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // ユーザーメッセージを表示
        addMessage(message, 'user');
        messageInput.value = '';

        // 処理中状態を設定
        setProcessingState(true);
        
        // 処理中メッセージを表示
        const processingMessage = addMessage('🤔 大前研一が考え中...', 'bot');

        try {
            // コンテキスト情報を含めて送信
            const requestData = {
                message: message,
                context: localConversationHistory.slice(-3) // 最新3件の履歴を送信
            };
            
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const data = await response.json();

            // 処理中メッセージを削除
            processingMessage.remove();

            if (data.success) {
                // ボットの応答を表示
                addMessage(data.response, 'bot');
                
                // ローカル履歴を更新
                localConversationHistory.push({
                    message: message,
                    response: data.response,
                    timestamp: data.timestamp
                });
                
                // 履歴が長すぎる場合は古いものを削除
                if (localConversationHistory.length > 10) {
                    localConversationHistory = localConversationHistory.slice(-10);
                }
                
                // 信頼度が低い場合の警告表示
                if (data.confidence && data.confidence < 0.7) {
                    showConfidenceWarning();
                }
            } else {
                addMessage('申し訳ございません。エラーが発生しました。', 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            processingMessage.remove();
            addMessage('申し訳ございません。通信エラーが発生しました。', 'bot');
        } finally {
            setProcessingState(false);
        }
    }

    // メッセージをチャットに追加
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // フォローアップ質問の場合は特別なスタイルを適用
        if (sender === 'user' && isFollowupQuestion(text)) {
            messageDiv.classList.add('followup-question');
        }
        
        // 言語を検出して適切に表示
        const isJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(text);
        const isEnglish = /^[a-zA-Z\s.,!?;:'"()-]+$/.test(text);
        
        if (isJapanese && isEnglish) {
            // 両方の言語が含まれている場合
            const lines = text.split('\n');
            lines.forEach(line => {
                if (line.trim()) {
                    const p = document.createElement('p');
                    if (/[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(line)) {
                        p.className = 'japanese';
                    } else {
                        p.className = 'english';
                    }
                    p.textContent = line;
                    contentDiv.appendChild(p);
                }
            });
        } else if (isJapanese) {
            // 日本語のみ
            const p = document.createElement('p');
            p.className = 'japanese';
            p.textContent = text;
            contentDiv.appendChild(p);
        } else {
            // 英語のみ
            const p = document.createElement('p');
            p.className = 'english';
            p.textContent = text;
            contentDiv.appendChild(p);
        }
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // スクロールを最下部に
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
    
    // フォローアップ質問かどうかを判定
    function isFollowupQuestion(text) {
        const followupPatterns = [
            'それって', 'それは', 'その', 'これって', 'これは', 'この',
            'that', 'this', 'it', 'what about', 'how about',
            '詳しく', '具体的に', '例を', 'for example', 'specifically',
            'なぜ', 'どうして', 'why', 'how come',
            '他には', '他に', 'other', 'else', 'more'
        ];
        
        return followupPatterns.some(pattern => 
            text.toLowerCase().includes(pattern.toLowerCase())
        );
    }

    // 処理中状態の設定
    function setProcessingState(isProcessing) {
        sendButton.disabled = isProcessing;
        messageInput.disabled = isProcessing;
        
        if (isProcessing) {
            sendButton.textContent = '送信中...';
        } else {
            sendButton.textContent = '送信 / Send';
        }
    }

    // 信頼度警告の表示
    function showConfidenceWarning() {
        confidenceNotice.style.display = 'block';
        setTimeout(() => {
            confidenceNotice.style.display = 'none';
        }, 5000);
    }

    // イベントリスナーの設定
    sendButton.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 入力フィールドのフォーカス
    messageInput.focus();
}); 