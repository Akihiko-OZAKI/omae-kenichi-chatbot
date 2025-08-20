# Gunicorn設定ファイル
import multiprocessing

# ワーカー数
workers = multiprocessing.cpu_count() * 2 + 1

# ワーカークラス
worker_class = 'sync'

# バインドアドレス
bind = '0.0.0.0:8000'

# タイムアウト設定
timeout = 120
keepalive = 2

# ログ設定
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# プロセス名
proc_name = 'omae-kenichi-chatbot'

# デーモン化（本番環境ではTrue）
daemon = False

# ユーザー・グループ（本番環境で設定）
# user = 'www-data'
# group = 'www-data'

# ワーカーの最大リクエスト数
max_requests = 1000
max_requests_jitter = 50

# プリロード
preload_app = True


