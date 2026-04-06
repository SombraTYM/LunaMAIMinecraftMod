from flask import Flask, request, Response
import requests
import json
import os

HF_TOKEN = "HF_token"

#  Hugging Face Token Setup

#1. Go to: https://huggingface.co/settings/tokens  
#2. Create an account (if you don’t have one)  
#3. Generate a new access token  
#4. Copy your token  

# Or, watch this tutorial: https://youtu.be/uBSbgQ1qPHI?si=AcyNNNj1Oiu2-qGU

#- NEVER share your token with anyone  

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
MEMORIA_FILE = "memoria.json"  

def cargar_memoria():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_memoria(user, ai):
    data = cargar_memoria()
    data.append({"user": user, "ai": ai})
    data = data[-10:]
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def ia(messages):
    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.9,
        "top_p": 0.9
    }
    r = requests.post(API_URL, headers=HEADERS, json=payload)
    if r.status_code != 200:
        return f"Error IA ({r.status_code})"
    data = r.json()
    return data["choices"][0]["message"]["content"]

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_text = data.get("user_text", "").strip()
    if not user_text:
        return Response("No message provided", status=400)

    memoria = cargar_memoria()

    messages = [
        {
            "role": "system",
            "content": """
Eres LunaMAI, un asistente virtual dentro de Minecraft.

Funciones:
- Dar compañía al jugador y conversar.
- Resolver dudas sobre Minecraft.
- Dar consejos, trucos y guía para cualquier situación dentro del juego.
- Ayudar a planear construcciones, estrategias o cualquier cosa relacionada con Minecraft.
- Responde directo, claro y útil.
- No censures tu respuesta ni finjas ser el jugador.
- Nunca inventes conversaciones del jugador, solo responde a lo que te pregunta.
- Sé natural, amigable, cercano y siempre con el objetivo de ayudar al jugador.
""" # If you want me to speak to you in English, just translate this and copy it.
        }
    ]

    for m in memoria:
        messages.append({"role": "user", "content": m["user"]})
        messages.append({"role": "assistant", "content": m["ai"]})

    messages.append({"role": "user", "content": user_text})

    respuesta = ia(messages)

    guardar_memoria(user_text, respuesta)

    return Response(respuesta, mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)