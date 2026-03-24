"""
NPC AI Core — Hierarchical Inference Middleware
================================================
Engine-agnostic NPC AI middleware. Connects any game engine to a
hierarchical AI system via HTTP POST/JSON.

Routes:
  POST /npc              → main NPC interaction endpoint
  GET  /historial/<id>   → retrieve conversation history
  DELETE /historial/<id> → clear conversation history

To connect your AI model, replace the respuesta_simple() function
with a call to your preferred LLM (Claude, Gemini, Ollama, etc.)
"""

from flask import Flask, request, jsonify
import json
import traceback

app = Flask(__name__)

# Historial de conversación por NPC
# Clave: nombre del NPC, Valor: lista de mensajes
historiales = {}

RESPUESTAS_SIMPLES = {
    "hola": "Buenas. ¿Qué vas a tomar?",
    "cerveza": "Una moneda de cobre. Aquí tienes.",
    "gracias": "No hay de qué.",
    "adios": "Que te vaya bien, forastero.",
    "precio": "Depende de lo que quieras.",
}

def respuesta_simple(mensaje: str) -> str | None:
    mensaje_lower = mensaje.lower()
    for clave, respuesta in RESPUESTAS_SIMPLES.items():
        if clave in mensaje_lower:
            return respuesta
    return None

@app.route('/npc', methods=['POST'])
def npc_responde():
    try:
        datos = request.get_json()
        mensaje_jugador = datos.get('mensaje', '')
        estado_mundo = datos.get('estado', '')
        npc_id = datos.get('npc_id', 'aldric')

        # Inicializar historial si no existe
        if npc_id not in historiales:
            historiales[npc_id] = []

        # Guardar mensaje del jugador en historial
        historiales[npc_id].append({
            "rol": "jugador",
            "texto": mensaje_jugador
        })

        # Intentar respuesta simple primero
        respuesta = respuesta_simple(mensaje_jugador)

        # Si no hay respuesta simple, usar fallback con contexto
        if not respuesta:
            respuesta = "Gruñe algo ininteligible."

        # Guardar respuesta del NPC en historial
        historiales[npc_id].append({
            "rol": "npc",
            "texto": respuesta
        })

        print(f"[{npc_id}] Jugador: {mensaje_jugador}")
        print(f"[{npc_id}] Aldric: {respuesta}")
        print(f"[{npc_id}] Historial: {len(historiales[npc_id])} mensajes")

        return jsonify({
            "dialogo": respuesta,
            "emocion": "neutral",
            "accion": "idle",
            "historial": historiales[npc_id]
        })

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return jsonify({
            "dialogo": "Gruñe algo ininteligible.",
            "emocion": "neutral",
            "accion": "idle",
            "historial": []
        }), 200

@app.route('/historial/<npc_id>', methods=['GET'])
def obtener_historial(npc_id):
    return jsonify(historiales.get(npc_id, []))

@app.route('/historial/<npc_id>', methods=['DELETE'])
def limpiar_historial(npc_id):
    historiales[npc_id] = []
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(port=8080, debug=True)