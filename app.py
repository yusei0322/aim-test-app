from flask import Flask, request, render_template, jsonify
import datetime

app = Flask(__name__)

# ゲーム画面を表示するルート
@app.route('/')
def index():
    # URLパラメータからターゲットIDを取得（例: ?id=alpha）
    target_id = request.args.get('id', 'unknown')
    return render_template('index.html', target_id=target_id)

# フィンガープリントを受信するAPIルート
@app.route('/api/track', methods=['POST'])
def track():
    data = request.json
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # ここでデータベースやファイルに保存する（今回はコンソールに出力）
    print(f"--- ターゲットアクセス検知 ---")
    print(f"時間: {timestamp}")
    print(f"IP: {ip_address}")
    print(f"ターゲットID: {data.get('target_id')}")
    print(f"User-Agent: {data.get('ua')}")
    print(f"解像度: {data.get('res')}")
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)