import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ключ берем из настроек сервера (безопасность)
GEMINI_KEY = os.environ.get("GEMINI_KEY")

@app.route('/', methods=['GET'])
def health_check():
    return "Proxy is alive!", 200

@app.route('/generate', methods=['POST'])
def generate():
    if not GEMINI_KEY:
        return jsonify({"error": "No API key set on server"}), 500

    data = request.json
    user_text = data.get('text', '')
    history = data.get('history', []) # Поддержка истории диалога!

    # Формируем запрос к Google API (Gemini 1.5 Flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    # Конвертируем историю в формат Google
    contents = []
    for msg in history:
        role = "model" if msg['role'] == 'assistant' else "user"
        contents.append({"role": role, "parts": [{"text": msg['content']}]})
    
    # Добавляем текущий запрос
    contents.append({"role": "user", "parts": [{"text": user_text}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }

    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            return jsonify({"error": f"Google Error: {response.text}"}), response.status_code

        result = response.json()
        answer = result['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"reply": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)