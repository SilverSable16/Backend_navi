from bd import (
    obtener_reglas, obtener_ejemplos_para_entrenar, obtener_respuesta_por_etiqueta,
    obtener_id_intencion, crear_intencion, insertar_ejemplo, insertar_respuesta
)
from pln_model import PLNClassifier
from inferencia import aplicar_inferencia

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

def cargar_modelo():
    ejemplos = obtener_ejemplos_para_entrenar()
    clasificador = PLNClassifier()
    clasificador.entrenar(ejemplos)
    return clasificador

if __name__ == "__main__":
    print("🎮 ¡Hola! Soy Navi, tu guía en el mundo de los videojuegos. 🧠✨\n"
          "Puedo ayudarte a descubrir juegos según tus gustos. Solo dime qué te interesa y yo me encargo del resto.\n"
          "¿Te gustan las historias épicas? ¿O prefieres acción, estrategia o algo para jugar con amigos?\n"
          "Puedes preguntarme '¿por qué?' si quieres saber más sobre mis recomendaciones.\n"
          "📝 Escribe 'salir' cuando quieras terminar nuestra charla. ¡Vamos a jugar con ideas!\n")

    reglas = obtener_reglas()
    clasificador = cargar_modelo()
    contexto = {}

    while True:
        entrada = input("👤 Tú: ").strip().lower()

        if entrada == "salir":
            print("🎮 Navi: ¡Hasta pronto, aventurero! Que encuentres un juego épico en tu camino. 👾🕹️")
            break

        if esta_pidiendo_explicacion(entrada) and "respuesta" in contexto:
            print(f"🤖 Navi: {contexto['respuesta']['explicacion']}")
            continue

        if esta_preguntando_que_hace(entrada):
            print("🤖 Navi: ¡Estoy aquí para ayudarte a descubrir videojuegos increíbles! 🎯\n"
                  "Solo dime qué te gusta (por ejemplo, historia, aventuras, jugar con amigos...) y te recomendaré algo genial.\n"
                  "Y si no conozco algo, me puedes enseñar. ¡Estoy en constante aprendizaje, como tú! 💡")
            continue

        # INFERENCIA LÓGICA
        inferencia = aplicar_inferencia(entrada, reglas)
        if inferencia:
            print(f"🎯 Navi (regla): {inferencia}")
            contexto['respuesta'] = {
                "explicacion": "Esta recomendación se basa en lo que mencionaste. ¿Te interesa algo similar?"
            }
            continue

        # PLN
        etiqueta = clasificador.predecir(entrada)
        resultado = obtener_respuesta_por_etiqueta(etiqueta)

        if resultado:
            texto, explicacion = resultado
            print(f"🎮 Navi (PLN): {texto}")
            contexto['respuesta'] = {
                "etiqueta": etiqueta,
                "explicacion": explicacion
            }
        else:
            # APRENDIZAJE AUTOMÁTICO
            print("🤖 Navi: Hmm... eso no lo conozco aún. Pero no te preocupes, ¡puedo aprenderlo si me enseñas! 😄")
            nueva_etiqueta = input("👤 Tú (tema o etiqueta): ").strip().lower()

            intencion_id = obtener_id_intencion(nueva_etiqueta)
            if not intencion_id:
                intencion_id = crear_intencion(nueva_etiqueta)

            print("🤖 Navi: ¿Qué juego recomendarías tú para ese tipo?")
            nueva_respuesta = input("👤 Tú (nombre del juego): ").strip()

            print("🤖 Navi: ¿Por qué recomendarías ese juego?")
            explicacion = input("👤 Tú (explicación): ").strip()

            insertar_ejemplo(entrada, intencion_id)
            insertar_respuesta(intencion_id, nueva_respuesta, explicacion)

            print("🤖 Navi: ¡Eso suena genial! 😮 No lo sabía, pero ya lo anoté.\n"
                  "¡Gracias por enseñarme algo nuevo! La próxima vez estaré más preparada 🎓🎮")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


