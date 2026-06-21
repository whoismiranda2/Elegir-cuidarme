from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
import json
import os
from nlp_service import analizar_emocion_texto
from chatbot_service import responder_flora

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'elegir-cuidarme-2025-key')

ADMIN_CLAVE = os.environ.get('ADMIN_CLAVE', 'cuidarme2025')

# ── Helpers ──────────────────────────────────────────────────────────────────

def load_data(filename):
    path = os.path.join(os.path.dirname(__file__), 'data', filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def mascota(seccion):
    return load_data('mascota.json').get(seccion, [])

def load_feedback():
    path = os.path.join(os.path.dirname(__file__), 'data', 'feedback.json')
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_feedback(items):
    path = os.path.join(os.path.dirname(__file__), 'data', 'feedback.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# ── Rutas principales ────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('pages/index.html',
                           frases_mascota=mascota('inicio'))

@app.route('/emociones')
def emociones():
    return render_template('pages/emociones.html',
                           tecnicas=load_data('tecnicas.json'),
                           frases_mascota=mascota('emociones'))

@app.route('/actividades')
def actividades():
    return render_template('pages/actividades.html',
                           actividades=load_data('actividades.json'),
                           frases_mascota=mascota('actividades'))

@app.route('/videos')
def videos():
    return render_template('pages/videos.html',
                           videos=load_data('videos.json'),
                           frases_mascota=mascota('videos'))

@app.route('/info')
def info():
    return render_template('pages/info.html',
                           mitos=load_data('mitos.json'),
                           frases_mascota=mascota('info'))

@app.route('/evaluacion')
def evaluacion():
    return render_template('pages/evaluacion.html',
                           frases_mascota=mascota('inicio'))


# ── API: emoción ─────────────────────────────────────────────────────────────

@app.route('/api/emocion', methods=['POST'])
def registrar_emocion():
    data = request.get_json()
    emocion = data.get('emocion', '')
    respuestas = {
        'bien':    '¡Qué bueno saberlo! Sigue eligiendo cuidarte 💚',
        'normal':  'Está bien sentirse así. Aquí hay técnicas que pueden ayudarte 🌿',
        'triste':  'Gracias por contarlo. No estás solo — revisa las técnicas de hoy 💙',
        'enojado': 'El enojo también es válido. Prueba la técnica de respiración 🌬️',
        'ansioso': 'Respira. Estás a salvo. La técnica 4-7-8 puede ayudarte ahora mismo 🤍',
    }
    return jsonify({'ok': True, 'mensaje': respuestas.get(emocion, '¡Gracias por compartir cómo te sientes!')})


# ── API: chatbot Flora ───────────────────────────────────────────────────────

@app.route('/api/analizar-texto', methods=['POST'])
def analizar_texto():
    texto = request.get_json().get('texto', '')
    return jsonify(analizar_emocion_texto(texto))

@app.route('/api/chat-flora', methods=['POST'])
def chat_flora():
    mensaje = request.get_json().get('mensaje', '')
    return jsonify(responder_flora(mensaje))


# ── API: feedback ────────────────────────────────────────────────────────────

@app.route('/api/feedback', methods=['POST'])
def guardar_feedback():
    data = request.get_json()
    nombre    = data.get('nombre', '').strip()[:50]
    estrellas = data.get('estrellas', 0)
    comentario = data.get('comentario', '').strip()[:500]

    if not nombre or not comentario:
        return jsonify({'ok': False, 'error': 'Completa todos los campos'})
    if not isinstance(estrellas, int) or not (1 <= estrellas <= 5):
        return jsonify({'ok': False, 'error': 'Calificación inválida'})

    items = load_feedback()
    items.append({
        'nombre':     nombre,
        'estrellas':  estrellas,
        'comentario': comentario,
        'fecha':      datetime.now().strftime('%d/%m/%Y %H:%M')
    })
    save_feedback(items)
    return jsonify({'ok': True})


# ── Admin ────────────────────────────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = False
    if request.method == 'POST':
        if request.form.get('clave') == ADMIN_CLAVE:
            session['admin'] = True
        else:
            error = True

    if not session.get('admin'):
        return render_template('pages/admin.html', autenticado=False, error=error)

    items = sorted(load_feedback(), key=lambda x: x.get('fecha', ''), reverse=True)
    promedio = round(sum(i['estrellas'] for i in items) / len(items), 1) if items else 0
    dist = {i: sum(1 for x in items if x['estrellas'] == i) for i in range(1, 6)}

    return render_template('pages/admin.html',
                           autenticado=True,
                           feedbacks=items,
                           total=len(items),
                           promedio=promedio,
                           distribucion=dist,
                           error=False)

@app.route('/admin/salir')
def admin_salir():
    session.pop('admin', None)
    return redirect(url_for('admin'))


# ── Arranque ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
