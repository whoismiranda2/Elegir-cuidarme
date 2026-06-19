from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# ── Datos en memoria (sin base de datos) ────────────────────────────────────

def load_data(filename):
    path = os.path.join(os.path.dirname(__file__), 'data', filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def mascota(seccion):
    return load_data('mascota.json').get(seccion, [])


# ── Rutas principales ────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('pages/index.html',
                           frases_mascota=mascota('inicio'))


@app.route('/emociones')
def emociones():
    tecnicas = load_data('tecnicas.json')
    return render_template('pages/emociones.html',
                           tecnicas=tecnicas,
                           frases_mascota=mascota('emociones'))


@app.route('/actividades')
def actividades():
    actividades_data = load_data('actividades.json')
    return render_template('pages/actividades.html',
                           actividades=actividades_data,
                           frases_mascota=mascota('actividades'))


@app.route('/videos')
def videos():
    videos_data = load_data('videos.json')
    return render_template('pages/videos.html',
                           videos=videos_data,
                           frases_mascota=mascota('videos'))


@app.route('/info')
def info():
    mitos = load_data('mitos.json')
    return render_template('pages/info.html',
                           mitos=mitos,
                           frases_mascota=mascota('info'))


# ── API: registrar emoción del día (sin usuario, solo sesión anónima) ────────

@app.route('/api/emocion', methods=['POST'])
def registrar_emocion():
    data = request.get_json()
    emocion = data.get('emocion', '')
    respuestas = {
        'bien':    '¡Qué bueno saberlo! Sigue eligiendo cuidarte 💚',
        'normal':  'Está bien sentirse así. Aquí hay técnicas que pueden ayudarte 🌿',
        'triste':  'Gracias por contarlo. No estás sole — revisa las técnicas de hoy 💙',
        'enojado': 'El enojo también es válido. Prueba la técnica de respiración 🌬️',
        'ansioso': 'Respira. Estás a salvo. La técnica 4-7-8 puede ayudarte ahora mismo 🤍',
    }
    mensaje = respuestas.get(emocion, '¡Gracias por compartir cómo te sientes!')
    return jsonify({'ok': True, 'mensaje': mensaje})


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
