from flask import Flask, request, render_template, jsonify
import datetime
import os

app = Flask(__name__)

TRACKING_FILE = "tracking_data.txt"
SCORE_FILE = "scores.txt"

# --- IPアドレスを綺麗に取得する補助関数 ---
def get_real_ip():
    raw_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    # 複数ある場合は一番左（本当のクライアントIP）だけを取得
    return raw_ip.split(',')[0].strip() if raw_ip else "unknown"

@app.route('/')
def index():
    target_id = request.args.get('id', 'unknown')
    return render_template('index.html', target_id=target_id)

@app.route('/api/track', methods=['POST'])
def track():
    data = request.json
    ip_address = get_real_ip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"{timestamp} | Target: {data.get('target_id')} | IP: {ip_address} | UA: {data.get('ua')} | Res: {data.get('res')} | Lang: {data.get('lang')}\n"
    
    with open(TRACKING_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"【検知ログ】: {log_entry.strip()}", flush=True)
    return jsonify({"status": "success"})

@app.route('/api/score', methods=['POST'])
def save_score():
    data = request.json
    ip_address = get_real_ip()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    score_entry = f"{timestamp} | Target: {data.get('target_id')} | IP: {ip_address} | Score: {data.get('score')} | Time: 30s\n"
    
    with open(SCORE_FILE, "a", encoding="utf-8") as f:
        f.write(score_entry)
    print(f"【スコアログ】: {score_entry.strip()}", flush=True)
    return jsonify({"status": "success"})

# --- 【新規追加】比較分析レポート生成ルート ---
@app.route('/compare')
def compare_targets():
    if not os.path.exists(TRACKING_FILE):
        return "<h3>まだトラッキングデータがありません。</h3>"
        
    target1 = "umi"
    target2 = "jin"
    data1, data2 = None, None
    
    # ファイルを下から読み込み、最新のアクセス記録を取得
    with open(TRACKING_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in reversed(lines):
            if f"Target: {target1} |" in line and not data1:
                data1 = line.strip()
            elif f"Target: {target2} |" in line and not data2:
                data2 = line.strip()
                
    if not data1 or not data2:
        return f"<h3>分析エラー: {target1} と {target2} の両方のデータが揃っていません。</h3><p>二人がリンクを踏んだ後に再度アクセスしてください。</p>"
        
    # データを要素ごとに分解
    def parse_line(line):
        parts = line.split(" | ")
        parsed = {}
        for part in parts:
            if ": " in part:
                k, v = part.split(": ", 1)
                parsed[k] = v.strip()
        return parsed
        
    d1 = parse_line(data1)
    d2 = parse_line(data2)
    
    # 比較ロジック
    ip_match = (d1.get("IP") == d2.get("IP"))
    ua_match = (d1.get("UA") == d2.get("UA"))
    res_match = (d1.get("Res") == d2.get("Res"))
    
    # 確率の算出（IP一致は超強力な証拠）
    probability = 0
    if ip_match: probability += 70  # 同一Wi-Fi環境の可能性大
    if ua_match: probability += 20  # 全く同じブラウザとOS
    if res_match: probability += 10 # 全く同じ画面サイズ
    
    # HTMLレポートの生成
    html = f"""
    <html><head><meta charset="utf-8"><title>分析レポート</title></head>
    <body style="font-family: sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 800px; margin: auto;">
            <h2 style="color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px;">👤 同一人物分析レポート: {target1} vs {target2}</h2>
            <h1 style="color: {'#e74c3c' if probability > 80 else '#f39c12' if probability > 40 else '#27ae60'};">
                同一人物の可能性: {probability}％
            </h1>
            
            <h3>【判定の根拠】</h3>
            <ul>
                <li><b>IPアドレス（ネットワーク環境）:</b> <span style="color: {'red' if ip_match else 'black'};">{"一致 🔴 (決定的証拠)" if ip_match else "不一致"}</span><br>
                    <small>({target1}: {d1.get("IP")} / {target2}: {d2.get("IP")})</small></li>
                <li style="margin-top: 10px;"><b>ブラウザとOS環境（User-Agent）:</b> <span style="color: {'red' if ua_match else 'black'};">{"一致 🔴" if ua_match else "不一致"}</span></li>
                <li style="margin-top: 10px;"><b>画面解像度:</b> <span style="color: {'red' if res_match else 'black'};">{"一致 🔴" if res_match else "不一致"}</span></li>
            </ul>
            
            <hr style="margin: 20px 0;">
            <h3>📝 取得生データ（最新のアクセス）</h3>
            <p style="background: #eee; padding: 10px; font-family: monospace; font-size: 0.9em; word-wrap: break-word;">
                <b>{target1}:</b> {data1}<br><br>
                <b>{target2}:</b> {data2}
            </p>
        </div>
    </body></html>
    """
    return html

if __name__ == '__main__':
    if not os.path.exists(TRACKING_FILE):
        open(TRACKING_FILE, 'w').close()
    if not os.path.exists(SCORE_FILE):
        open(SCORE_FILE, 'w').close()
    app.run(debug=True)
