from flask import Flask, request, jsonify
from flask_cors import CORS
from bd import (
    obtener_reglas, obtener_ejemplos_para_entrenar, obtener_respuesta_por_etiqueta,
    obtener_id_intencion, crear_intencion, insertar_ejemplo, insertar_respuesta
)
from pln_model import PLNClassifier
from inferencia import aplicar_inferencia

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # habilita CORS para todo

reglas = obtener_reglas()
clasificador = PLNClassifier()
clasificador.entrenar(obtener_ejemplos_para_entrenar())
contexto = {}

def esta_pidiendo_explicacion(texto):
    texto = texto.lower()
    return any(p in texto for p in [
        "por qué", "porque", "por que", "por", "explicación", "explica", "por eso", "me puedes explicar", "y eso"
    ])

def esta_preguntando_que_hace(texto):
    texto = texto.lower()
    return any(frase in texto for frase in [
        "qué haces", "que haces", "quién eres", "para qué sirves", "cuál es tu función"
    ])

@app.route("/", methods=["GET", "OPTIONS"])
def home():
    if request.method == "OPTIONS":
        return '', 200
    return "<h1>Navi backend funcionando 🧠🎮</h1>"

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return '', 200  # Responde a preflight

    global contexto, clasificador
    data = request.get_json()
    entrada = data.get("mensaje", "").strip().lower()

    if esta_pidiendo_explicacion(entrada) and "respuesta" in contexto:
        return jsonify(respuesta=contexto['respuesta']['explicacion'])

    if esta_preguntando_que_hace(entrada):
        return jsonify(respuesta="🤖 Navi: Soy tu asistente gamer. Te recomiendo juegos según tus gustos y aprendo contigo. ¡Solo dime qué te interesa jugar!")

    inferencia = aplicar_inferencia(entrada, reglas)
    if inferencia:
        contexto['respuesta'] = {"explicacion": "Basado en lo que dijiste, esta recomendación te puede gustar."}
        return jsonify(respuesta=inferencia)

    etiqueta = clasificador.predecir(entrada)
    resultado = obtener_respuesta_por_etiqueta(etiqueta)

    if resultado:
        texto, explicacion = resultado
        contexto['respuesta'] = {"etiqueta": etiqueta, "explicacion": explicacion}
        return jsonify(respuesta=texto)

    return jsonify(respuesta="Ups... no conozco ese tipo de juego todavía. ¡Pronto podré aprenderlo si me enseñas en consola! 🧠")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

