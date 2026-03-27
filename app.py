from flask import Flask, request
from twilio.rest import Client
from claude_agent import get_ai_response
from farm_data import get_or_create_farm
from weather import get_kolar_weather
from mandi_prices import get_mandi_prices
import os, base64

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    phone     = request.form.get('From')
    msg_body  = request.form.get('Body', '').strip()
    media_url = request.form.get('MediaUrl0')
    num_media = int(request.form.get('NumMedia', 0))

    if not phone:
        return {'error': 'Missing From'}, 400

    farm = get_or_create_farm(phone)
    farm['weather'] = get_kolar_weather()
    prices = get_mandi_prices()
    farm['price'] = prices.get('Kolar', {}).get('Grade A', 18)

    image_b64 = None
    if num_media > 0 and media_url:
        image_b64 = fetch_image_as_b64(media_url)

    reply = get_ai_response(
        farmer_phone=phone,
        message=msg_body,
        farm_data=farm,
        image_b64=image_b64
    )

    client = Client(
        os.environ['TWILIO_ACCOUNT_SID'],
        os.environ['TWILIO_AUTH_TOKEN']
    )
    client.messages.create(
        from_=os.environ['TWILIO_WHATSAPP_FROM'],
        to=phone,
        body=reply
    )
    return '', 204

def fetch_image_as_b64(url):
    import requests
    auth = (os.environ['TWILIO_ACCOUNT_SID'],
            os.environ['TWILIO_AUTH_TOKEN'])
    r = requests.get(url, auth=auth, timeout=10)
    r.raise_for_status()
    return base64.b64encode(r.content).decode()

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

After pasting, **scroll down** and click the green **"Commit changes"** button. Then click **"Commit directly to the main branch"** and click **"Commit changes"** again.

Then watch your Render logs — within 1 minute you should see:
```
==> Your service is live 🎉
