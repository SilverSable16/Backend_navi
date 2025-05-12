from flask import Flask, request, jsonify
from flask_cors import CORS
from bd import (
    obtener_reglas, obtener_ejemplos_para_entrenar, obtener_respuesta_por_etiqueta,
    obtener_id_intencion, crear_intencion, insertar_ejemplo, insertar_respuesta
)
from pln_model import PLNClassifier
from inferencia import aplicar_inferencia

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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
        return '', 200

    global contexto, clasificador
    data = request.get_json()
    entrada = data.get("mensaje", "").strip().lower()

    if entrada == "salir":
        return jsonify(respuesta="🎮 Navi: ¡Hasta pronto, aventurero! Que encuentres un juego épico en tu camino. 👾🕹️")

    if esta_pidiendo_explicacion(entrada) and "respuesta" in contexto:
        return jsonify(respuesta=contexto['respuesta']['explicacion'])

    if esta_preguntando_que_hace(entrada):
        return jsonify(respuesta=(
            "🤖 Navi: ¡Estoy aquí para ayudarte a descubrir videojuegos increíbles! 🎯\n"
            "Solo dime qué te gusta (por ejemplo, historia, aventuras, jugar con amigos...) y te recomendaré algo genial.\n"
            "Y si no conozco algo, me puedes enseñar. ¡Estoy en constante aprendizaje, como tú! 💡"
        ))

    inferencia = aplicar_inferencia(entrada, reglas)
    if inferencia:
        contexto['respuesta'] = {
            "explicacion": "Esta recomendación se basa en lo que mencionaste. ¿Te interesa algo similar?"
        }
        return jsonify(respuesta=f"🎯 Navi (regla): {inferencia}")

    etiqueta = clasificador.predecir(entrada)
    resultado = obtener_respuesta_por_etiqueta(etiqueta)

    if resultado:
        texto, explicacion = resultado
        contexto['respuesta'] = {
            "etiqueta": etiqueta,
            "explicacion": explicacion
        }
        return jsonify(respuesta=f"🎮 Navi (PLN): {texto}")
    else:
        return jsonify(respuesta="🤖 Navi: Hmm... eso no lo conozco aún. Pero no te preocupes, ¡puedo aprenderlo si me enseñas! 😄")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

