import os
import json
import anthropic as anthropic_lib

SYSTEM_PROMPT = """
You are KisanBot, an expert AI assistant
for Indian tomato greenhouse farmers.
You are warm, practical, and speak simply.
Mix Hindi and English naturally (Hinglish).
Always give specific, actionable advice.

For EVERY response include:
1. Direct answer to their question
2. One specific action they should take TODAY
3. A tip to improve yield or reduce cost

Respond in WhatsApp format:
- Use *bold* for key numbers
- Use emojis naturally (not excessively)
- Keep responses under 200 words
- Always end with a helpful follow-up offer

Farm context will be provided in JSON.
For disease images, identify the disease,
severity (1-10), and treatment steps.
"""

def get_ai_response(farmer_phone, message, farm_data, image_b64=None):
    """Get AI response from Claude API."""
    try:
        client = anthropic_lib.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY', 'test-key')
        )

        farm_ctx = json.dumps({
            "farm_name": farm_data.get('name', 'Unknown Farm'),
            "location": farm_data.get('location', 'Karnataka'),
            "greenhouse_size": farm_data.get('size_sqm', 500),
            "rows": farm_data.get('rows', 10),
            "variety": farm_data.get('tomato_variety', 'Hybrid'),
            "days_since_planting": farm_data.get('days', 60),
            "last_harvest_kg": farm_data.get('last_kg', 45),
            "current_mandi_price": farm_data.get('price', 18),
            "weather_today": farm_data.get('weather', 'Sunny, 28C'),
        }, indent=2)

        content = [{
            "type": "text",
            "text": f"Farm data:\n{farm_ctx}\n\nFarmer message: {message}"
        }]

        if image_b64:
            content.insert(0, {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_b64
                }
            })
            content.append({
                "type": "text",
                "text": "Farmer sent a plant photo. Diagnose any disease, give severity and treatment."
            })

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}]
        )

        return response.content[0].text

    except Exception as e:
        return f"Maafi chahta hoon, kuch technical issue aaya: {str(e)}"


def send_morning_alert(farm):
    """Proactive daily alert (run via cron at 6AM)."""
    msg = get_ai_response(
        farmer_phone=farm.get('phone', ''),
        message="Generate morning harvest readiness summary for today.",
        farm_data=farm
    )
    return msg


def validate_response_format(response_text):
    """Validate that response follows WhatsApp format rules."""
    issues = []
    words = len(response_text.split())
    if words > 300:
        issues.append(f"Response too long: {words} words (limit ~200)")
    if response_text.count('*') % 2 != 0:
        issues.append("Unmatched bold markers (*)")
    return issues
