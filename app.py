from flask import Flask, request, render_template, jsonify
import datetime
import os

app = Flask(__name__)

# --- 設定 ---
# データを保存するファイル名
TRACKING_FILE = "tracking_data.txt"
SCORE_FILE = "scores.txt"

# --- ゲーム画面を表示するルート ---
@app.route('/')
def index():
    # URLパラメータからターゲットIDを取得（例: ?id=alpha）
    target_id = request.args.get('id', 'unknown')
    # index.htmlをレンダリングし、target_idを渡す
    return render_template('index.html', target_id=target_id)

# --- フィンガープリントを受信するAPIルート ---
@app.route('/api/track', methods=['POST'])
def track():
    # フロントエンドから送信されたJSONデータ
    data = request.json
    
    # IPアドレスの取得（Renderなどのプロキシを経由する場合を考慮）
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not ip_address:
        ip_address = "unknown"
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # トラッキングデータをテキストファイルに保存
    log_entry = f"{timestamp} | Target: {data.get('target_id')} | IP: {ip_address} | UA: {data.get('ua')} | Res: {data.get('res')} | Lang: {data.get('lang')}\n"
    
    with open(TRACKING_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
        
    # ★ログ画面に即座に出力する（flush=True を追加）
    print(f"【検知ログ】: {log_entry.strip()}", flush=True)
        
    return jsonify({"status": "success", "message": "Fingerprint received"})

# --- スコアを受信するAPIルート（ゲーム終了時に呼び出し） ---
@app.route('/api/score', methods=['POST'])
def save_score():
    data = request.json
    
    # IPアドレス（スコア送信時）
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not ip_address:
        ip_address = "unknown"
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # スコアデータを別のテキストファイルに保存
    score_entry = f"{timestamp} | Target: {data.get('target_id')} | IP: {ip_address} | Score: {data.get('score')} | Time: 30s\n"
    
    with open(SCORE_FILE, "a", encoding="utf-8") as f:
        f.write(score_entry)
        
    # ★ログ画面に即座に出力する（flush=True を追加）
    print(f"【スコアログ】: {score_entry.strip()}", flush=True)
        
    return jsonify({"status": "success", "message": "Score saved"})

if __name__ == '__main__':
    # データを保存するファイルがなければ作成
    if not os.path.exists(TRACKING_FILE):
        open(TRACKING_FILE, 'w').close()
    if not os.path.exists(SCORE_FILE):
        open(SCORE_FILE, 'w').close()
        
    # debug=True は開発用。Renderなどにデプロイする際はFalseにすることを推奨
    app.run(debug=false)
