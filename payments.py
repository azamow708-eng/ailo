import requests
from config import NOWPAYMENTS_API_KEY
from db import update_subscription
from flask import Flask, request

NOWPAYMENTS_BASE = "https://api.nowpayments.io/v1"
app = Flask(__name__)

def create_invoice(user_id, amount_usd=18, plan="30d", callback_url="https://YOUR_RENDER_URL/nowpayments_webhook"):
    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}
    data = {
        "price_amount": amount_usd,
        "price_currency": "usd",
        "order_id": f"{user_id}_{plan}_{int(datetime.now().timestamp())}",
        "ipn_callback_url": callback_url,
        "pay_currency": "usdt"
    }
    r = requests.post(f"{NOWPAYMENTS_BASE}/invoice", json=data, headers=headers)
    return r.json() if r.status_code==201 else None

@app.route("/nowpayments_webhook", methods=['POST'])
def nowpayments_webhook():
    data = request.json
    if data.get('payment_status') == 'finished':
        user_id = int(data['order_id'].split("_")[0])
        plan = data['order_id'].split("_")[1]
        update_subscription(user_id, plan=plan)
    return "OK", 200
