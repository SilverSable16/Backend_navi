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
        return '', 200  # Responde a preflight

    global contexto, clasificador
    data = request.get_json()
    entrada = data.get("mensaje", "").strip().lower()

    # Respuesta a "Hola" o "Que tal"
    if "hola" in entrada or "que tal" in entrada:
        return jsonify(respuesta="🎮 ¡Hola, aventurero! Soy Navi, tu asistente gamer. ¿Qué tipo de juegos te gustan?")

    # Respuesta a "¿Cómo estás?" o "Como estas"
    if "cómo estás" in entrada or "como estas" in entrada:
        return jsonify(respuesta="🎮 ¡Estoy genial! Siempre listo para ayudarte a encontrar juegos épicos. ¿Y tú, cómo te sientes hoy?")

    # Responder según el estado de ánimo del usuario
    if "estoy feliz" in entrada or "estoy bien" in entrada:
        return jsonify(respuesta="🎮 ¡Qué bueno escuchar eso! Estoy seguro de que te encantará la recomendación de juegos que te tengo. ¡Vamos a por más diversión! 😄")

    if "estoy triste" in entrada or "no me siento bien" in entrada:
        return jsonify(respuesta="🎮 Lo siento mucho. 😞 Pero no te preocupes, a veces una buena partida puede levantar el ánimo. ¿Qué tipo de juego te gustaría jugar para relajarte? 🎮")

    # Respuesta a "Adiós" o "Adios"
    if "adiós" in entrada or "adios" in entrada:
        return jsonify(respuesta="🎮 ¡Hasta pronto! Que encuentres un juego épico en tu camino. ¡Nos vemos en la próxima aventura!")

    # Respuesta a "Hasta pronto"
    if "hasta pronto" in entrada:
        return jsonify(respuesta="🎮 ¡Hasta pronto! Que encuentres un juego épico en tu camino. ¡Nos vemos en la próxima aventura!")

    # Si el usuario escribe "salir"
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

    # Lógica de Inferencia (Si ya tiene un conocimiento previo)
    inferencia = aplicar_inferencia(entrada, reglas)
    if inferencia:
        contexto['respuesta'] = {
            "explicacion": "Esta recomendación se basa en lo que mencionaste. ¿Te interesa algo similar?"
        }
        return jsonify(respuesta=f"🎯 Navi (regla): {inferencia}")

    # Lógica PLN - Si no encuentra respuesta, activar autoaprendizaje
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
        # Autoaprendizaje: Preguntar al usuario por la nueva categoría y recomendación
        return jsonify(respuesta="🤖 Navi: Hmm... eso no lo conozco aún. Pero no te preocupes, ¡puedo aprenderlo si me enseñas! 😄\n"
                                 "Por favor, dime el nombre de una categoría de juego para este tipo.\n"
                                 "Ejemplo: 'aventuras' o 'estrategia'.")
        
        # Después de que el usuario proporcione una categoría, capturamos la nueva respuesta
        nueva_etiqueta = input("👤 Tú (tema o etiqueta): ").strip().lower()

        # Crear o encontrar la nueva etiqueta para la categoría
        intencion_id = obtener_id_intencion(nueva_etiqueta)
        if not intencion_id:
            intencion_id = crear_intencion(nueva_etiqueta)

        # Preguntar al usuario por un ejemplo de juego relacionado con esa categoría
        nueva_respuesta = input("👤 Tú (nombre del juego): ").strip()
        print("🤖 Navi: ¡Genial! Ahora, ¿por qué recomendarías ese juego?")
        explicacion = input("👤 Tú (explicación): ").strip()

        # Guardar el nuevo ejemplo en la base de datos
        insertar_ejemplo(entrada, intencion_id)
        insertar_respuesta(intencion_id, nueva_respuesta, explicacion)

        # Reentrenar el modelo para aprender el nuevo juego
        clasificador = cargar_modelo()

        return jsonify(respuesta="🤖 Navi: ¡Eso suena genial! 😮 No lo sabía, pero ya lo anoté.\n"
                                 "¡Gracias por enseñarme algo nuevo! La próxima vez estaré más preparada 🎓🎮")
