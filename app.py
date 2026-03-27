from flask import Flask, request
from twilio.rest import Client
import os, base64, json
from claude_agent import get_ai_response
from farm_data import get_or_create_farm

from weather import get_kolar_weather

farm = get_or_create_farm(phone)
farm['weather'] = get_kolar_weather()  # live weather!
app = Flask(__name__)

def get_twilio_client():
    return Client(
        os.environ.get('TWILIO_ACCOUNT_SID', ''),
        os.environ.get('TWILIO_AUTH_TOKEN', '')
    )

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    phone    = request.form.get('From')
    msg_body = request.form.get('Body', '').strip()
    media_url = request.form.get('MediaUrl0')
    num_media = int(request.form.get('NumMedia', 0))

    if not phone:
        return {'error': 'Missing From field'}, 400

    farm = get_or_create_farm(phone)

    image_b64 = None
    if num_media > 0 and media_url:
        image_b64 = fetch_image_as_b64(media_url)

    reply = get_ai_response(
        farmer_phone=phone,
        message=msg_body,
        farm_data=farm,
        image_b64=image_b64
    )

    # In production: send via Twilio. In test: just return reply
    if os.environ.get('TESTING'):
        return {'reply': reply, 'phone': phone}, 200

    twilio_client = get_twilio_client()
    twilio_client.messages.create(
        from_=os.environ.get('TWILIO_WHATSAPP_FROM', ''),
        to=phone,
        body=reply
    )
    return '', 204

def fetch_image_as_b64(url):
    import requests as req
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN', '')
    if account_sid and auth_token:
        auth = (account_sid, auth_token)
        r = req.get(url, auth=auth, timeout=10)
    else:
        r = req.get(url, timeout=10)
    r.raise_for_status()
    return base64.b64encode(r.content).decode()

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
