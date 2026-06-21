from flask import Flask, render_template, request, jsonify, redirect, url_for, session
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

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        return None
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    import psycopg2
    return psycopg2.connect(db_url)

def init_db():
    conn = get_db_connection()
    if conn is None:
        print('[feedback] DATABASE_URL no configurada — se usará lista vacía.')
        return
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        id        SERIAL PRIMARY KEY,
                        nombre    VARCHAR(50)  NOT NULL,
                        estrellas INTEGER      NOT NULL,
                        comentario VARCHAR(500) NOT NULL,
                        fecha     TIMESTAMP    DEFAULT NOW()
                    )
                """)
        print('[feedback] Tabla feedback lista.')
    except Exception as e:
        print(f'[feedback] Error al inicializar DB: {e}')
    finally:
        conn.close()

def load_feedback():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute('SELECT nombre, estrellas, comentario, fecha FROM feedback ORDER BY fecha DESC')
                rows = cur.fetchall()
        return [
            {
                'nombre':     r[0],
                'estrellas':  r[1],
                'comentario': r[2],
                'fecha':      r[3].strftime('%d/%m/%Y %H:%M') if r[3] else ''
            }
            for r in rows
        ]
    except Exception as e:
        print(f'[feedback] Error al leer feedback: {e}')
        return []
    finally:
        conn.close()

def save_feedback(nombre, estrellas, comentario):
    conn = get_db_connection()
    if conn is None:
        print('[feedback] Sin conexión a DB — feedback no guardado.')
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO feedback (nombre, estrellas, comentario) VALUES (%s, %s, %s)',
                    (nombre, estrellas, comentario)
                )
        return True
    except Exception as e:
        print(f'[feedback] Error al guardar feedback: {e}')
        return False
    finally:
        conn.close()

init_db()


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
    nombre     = data.get('nombre', '').strip()[:50]
    estrellas  = data.get('estrellas', 0)
    comentario = data.get('comentario', '').strip()[:500]

    if not nombre or not comentario:
        return jsonify({'ok': False, 'error': 'Completa todos los campos'})
    if not isinstance(estrellas, int) or not (1 <= estrellas <= 5):
        return jsonify({'ok': False, 'error': 'Calificación inválida'})

    ok = save_feedback(nombre, estrellas, comentario)
    if not ok:
        return jsonify({'ok': False, 'error': 'No se pudo guardar. Inténtalo de nuevo.'})
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
