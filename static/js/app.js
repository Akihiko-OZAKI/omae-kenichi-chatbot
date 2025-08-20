/**
 * 社内ドキュメントナレッジベースチャットボット - フロントエンド
 */

class ChatBotApp {
    constructor() {
        this.messages = [];
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        // デバッグ機能を追加
        addDebugButtons();
    }

    setupEventListeners() {
        // チャット関連のみ
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (sendBtn) {
            sendBtn.addEventListener('click', () => {
                this.sendMessage();
            });
        }
    }





    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();

        if (!message || this.isProcessing) {
            return;
        }

        // ユーザーメッセージを表示
        this.addMessage(message, 'user');
        chatInput.value = '';

        // 言語を検出して処理中メッセージを表示
        const isJapanese = /[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(message);
        const processingMessage = isJapanese ? '🤔 大前研一の知恵を探しています...' : '🤔 Searching for Kenichi Ohmae\'s wisdom...';
        this.addMessage(processingMessage, 'bot', true);
        this.setProcessingState(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // 処理中メッセージを削除
            this.removeProcessingMessage();

            if (data.success) {
                this.addMessage(data.response, 'bot', data.sources, data.confidence);
            } else {
                this.addMessage(`エラー: ${data.error}`, 'bot');
            }
        } catch (error) {
            console.error('チャットエラー:', error);
            this.removeProcessingMessage();
            this.addMessage('通信エラーが発生しました', 'bot');
        } finally {
            this.setProcessingState(false);
        }
    }

    addMessage(text, sender, sources = null, confidence = null, isProcessing = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (isProcessing) {
            messageDiv.id = 'processing-message';
        }

        // 信頼度警告の管理
        if (sender === 'bot' && confidence !== null && confidence < 0.5) {
            this.showConfidenceWarning();
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                <i class="fas fa-${sender === 'user' ? 'user' : 'robot'}"></i>
                <div class="message-text">
                    ${this.escapeHtml(text)}
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showConfidenceWarning() {
        const confidenceNotice = document.getElementById('confidenceNotice');
        if (confidenceNotice) {
            confidenceNotice.style.display = 'block';
        }
    }

    removeProcessingMessage() {
        const processingMessage = document.getElementById('processing-message');
        if (processingMessage) {
            processingMessage.remove();
        }
    }

    setProcessingState(processing) {
        this.isProcessing = processing;
        const sendBtn = document.getElementById('sendBtn');
        const chatInput = document.getElementById('chatInput');

        if (sendBtn && chatInput) {
            if (processing) {
                sendBtn.innerHTML = '<div class="loading"></div>';
                sendBtn.disabled = true;
                chatInput.disabled = true;
            } else {
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
                sendBtn.disabled = false;
                chatInput.disabled = false;
            }
        }
    }

    showStatus(message, type = 'info') {
        const statusDiv = document.createElement('div');
        statusDiv.className = `status status-${type}`;
        statusDiv.textContent = message;

        const container = document.querySelector('.container');
        container.insertBefore(statusDiv, container.firstChild);

        setTimeout(() => {
            statusDiv.remove();
        }, 5000);
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// デバッグ機能を追加（現在は無効化）
function addDebugButtons() {
    // デバッグ機能は現在無効化しています
    console.log('デバッグ機能は現在無効化されています');
}

function loadDebugStats() {
    showStatus('統計情報を取得中...', 'info');
    
    fetch('/debug/stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showStatus('統計情報の取得に失敗しました: ' + data.error, 'error');
                return;
            }
            
            displayDebugStats(data);
            showStatus('統計情報を取得しました', 'success');
        })
        .catch(error => {
            console.error('統計情報取得エラー:', error);
            showStatus('統計情報の取得に失敗しました', 'error');
        });
}

function displayDebugStats(stats) {
    const debugOutput = document.getElementById('debug-output');
    
    let html = `
        <div class="debug-stats">
            <h4>📊 PDF統計情報</h4>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-label">総PDF数:</span>
                    <span class="stat-value">${stats.total_pdfs}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">総注釈数:</span>
                    <span class="stat-value">${stats.total_annotations}</span>
                </div>
            </div>
            
            <h5>注釈タイプ別統計:</h5>
            <div class="annotation-stats">
    `;
    
    for (const [type, count] of Object.entries(stats.annotation_types)) {
        html += `
            <div class="annotation-type">
                <span class="type-name">${type}:</span>
                <span class="type-count">${count}</span>
            </div>
        `;
    }
    
    html += `
            </div>
            
            <h5>PDFファイル一覧:</h5>
            <div class="pdf-list">
    `;
    
    stats.pdf_files.forEach(filename => {
        html += `<div class="pdf-item">📄 ${filename}</div>`;
    });
    
    html += `
            </div>
        </div>
    `;
    
    debugOutput.innerHTML = html;
}

function showPdfList() {
    const debugOutput = document.getElementById('debug-output');
    
    fetch('/debug/stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                debugOutput.innerHTML = `<div class="error">PDF一覧の取得に失敗しました: ${data.error}</div>`;
                return;
            }
            
            let html = `
                <div class="pdf-debug-list">
                    <h4>📚 PDF詳細情報</h4>
            `;
            
            data.pdf_files.forEach(filename => {
                html += `
                    <div class="pdf-debug-item">
                        <div class="pdf-name">📄 ${filename}</div>
                        <div class="pdf-actions">
                            <button onclick="debugPdf('${filename}')" class="debug-action-btn">詳細</button>
                            <button onclick="debugFirstPage('${filename}')" class="debug-action-btn">1ページ目</button>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            debugOutput.innerHTML = html;
        })
        .catch(error => {
            console.error('PDF一覧取得エラー:', error);
            debugOutput.innerHTML = '<div class="error">PDF一覧の取得に失敗しました</div>';
        });
}

function debugPdf(filename) {
    showStatus(`${filename}の詳細情報を取得中...`, 'info');
    
    fetch(`/debug/pdf/${filename}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showStatus('PDF詳細の取得に失敗しました: ' + data.error, 'error');
                return;
            }
            
            displayPdfDebug(data);
            showStatus(`${filename}の詳細情報を取得しました`, 'success');
        })
        .catch(error => {
            console.error('PDF詳細取得エラー:', error);
            showStatus('PDF詳細の取得に失敗しました', 'error');
        });
}

function displayPdfDebug(data) {
    const debugOutput = document.getElementById('debug-output');
    
    let html = `
        <div class="pdf-debug-details">
            <h4>📄 ${data.filename} 詳細情報</h4>
            <div class="pdf-info">
                <div class="info-item">
                    <span class="info-label">総ページ数:</span>
                    <span class="info-value">${data.total_pages}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">総テキスト長:</span>
                    <span class="info-value">${data.total_text_length}文字</span>
                </div>
            </div>
            
            <h5>注釈サマリー:</h5>
            <div class="annotation-summary">
    `;
    
    for (const [type, count] of Object.entries(data.annotation_summary)) {
        html += `
            <div class="annotation-summary-item">
                <span class="summary-type">${type}:</span>
                <span class="summary-count">${count}</span>
            </div>
        `;
    }
    
    html += `
            </div>
            
            <h5>サンプルページ情報:</h5>
            <div class="sample-pages">
    `;
    
    data.sample_pages.forEach(page => {
        html += `
            <div class="sample-page">
                <div class="page-header">📄 ページ ${page.page_number}</div>
                <div class="page-details">
                    <div>テキスト長: ${page.text_length}文字</div>
                    <div>基本重要度: ${page.importance_score.toFixed(3)}</div>
                    <div>総合重要度: ${page.comprehensive_score.comprehensive_score.toFixed(3)}</div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    debugOutput.innerHTML = html;
}

function debugFirstPage(filename) {
    showStatus(`${filename}の1ページ目を分析中...`, 'info');
    
    fetch(`/debug/annotations/${filename}/0`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showStatus('ページ分析に失敗しました: ' + data.error, 'error');
                return;
            }
            
            displayPageDebug(data);
            showStatus(`${filename}の1ページ目を分析しました`, 'success');
        })
        .catch(error => {
            console.error('ページ分析エラー:', error);
            showStatus('ページ分析に失敗しました', 'error');
        });
}

function displayPageDebug(data) {
    const debugOutput = document.getElementById('debug-output');
    
    let html = `
        <div class="page-debug-details">
            <h4>📄 ${data.filename} - ページ ${data.page_number}</h4>
            
            <h5>テキストプレビュー:</h5>
            <div class="text-preview">${data.text_preview}</div>
            
            <h5>重要度スコア:</h5>
            <div class="importance-scores">
                <div class="score-item">
                    <span class="score-label">基本スコア:</span>
                    <span class="score-value">${data.importance_scores.basic.toFixed(3)}</span>
                </div>
                <div class="score-item">
                    <span class="score-label">総合スコア:</span>
                    <span class="score-value">${data.importance_scores.comprehensive.comprehensive_score.toFixed(3)}</span>
                </div>
            </div>
            
            <h5>検出された注釈:</h5>
            <div class="detected-annotations">
    `;
    
    for (const [type, annotations] of Object.entries(data.annotations)) {
        if (annotations.length > 0) {
            html += `
                <div class="annotation-type-group">
                    <div class="type-header">🎯 ${type} (${annotations.length}個)</div>
                    <div class="annotation-list">
                `;
            
            annotations.slice(0, 5).forEach(ann => {  // 最初の5個のみ表示
                html += `
                    <div class="annotation-item">
                        <span class="ann-type">${ann.type || type}</span>
                        <span class="ann-confidence">信頼度: ${(ann.confidence || 0.5).toFixed(2)}</span>
                    </div>
                `;
            });
            
            if (annotations.length > 5) {
                html += `<div class="annotation-more">... 他${annotations.length - 5}個</div>`;
            }
            
            html += `
                    </div>
                </div>
            `;
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    debugOutput.innerHTML = html;
}

function testAnnotationDetection() {
    showStatus('注釈検出テストを実行中...', 'info');
    
    // 最初のPDFファイルでテスト
    fetch('/debug/stats')
        .then(response => response.json())
        .then(data => {
            if (data.pdf_files.length > 0) {
                debugFirstPage(data.pdf_files[0]);
            } else {
                showStatus('テスト用のPDFファイルが見つかりません', 'error');
            }
        })
        .catch(error => {
            console.error('注釈検出テストエラー:', error);
            showStatus('注釈検出テストに失敗しました', 'error');
        });
}

// アプリケーションの初期化
document.addEventListener('DOMContentLoaded', () => {
    new ChatBotApp();
}); 