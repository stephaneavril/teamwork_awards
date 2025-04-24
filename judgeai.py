from flask import Flask, request, render_template, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/videos_teamwork'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}
RESULTS_FILE = "teamwork_results.json"
VOTES_FILE = 'votes.json'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cargar_datos(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def guardar_datos(path, datos):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/teamwork_awards')
def teamwork_awards():
    resultados = cargar_datos(RESULTS_FILE)
    return render_template("teamwork_awards.html", resultados=resultados)


@app.route('/evaluar', methods=['POST'])
def evaluar():
    nombre1 = request.form.get('nombre1')
    nombre2 = request.form.get('nombre2')
    archivo = request.files.get('video')

    if not archivo or not allowed_file(archivo.filename):
        return "Formato de video inválido", 400

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{archivo.filename}"
    ruta_video = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(ruta_video)

    nuevo = {
        "id": timestamp,
        "nombre1": nombre1,
        "nombre2": nombre2,
        "video": ruta_video.replace("\\", "/"),
        "puntos": 0,
        "votos": 0
    }

    resultados = cargar_datos(RESULTS_FILE)
    resultados.append(nuevo)
    guardar_datos(RESULTS_FILE, resultados)

    return redirect(url_for('teamwork_awards'))


@app.route('/votar', methods=['GET', 'POST'])
def votar():
    if request.method == 'GET':
        videos = cargar_datos(RESULTS_FILE)
        return render_template('teamwork_awards.html', resultados=videos)

    email = request.form.get('email')
    if not email:
        return "Email requerido", 400

    votos = cargar_datos(VOTES_FILE)
    if any(v['email'] == email for v in votos):
        return "Este correo ya ha votado", 403

    videos = cargar_datos(RESULTS_FILE)

    total_puntos = 0
    puntos_por_video = []

    for i in range(len(videos)):
        try:
            puntos = int(request.form.get(f'puntos_{i}', 0))
        except ValueError:
            puntos = 0
        total_puntos += puntos
        puntos_por_video.append(puntos)

    if total_puntos != 3:
        return "Debes asignar exactamente 3 puntos", 400

    for i, puntos in enumerate(puntos_por_video):
        videos[i]['puntos'] += puntos
        if puntos > 0:
            videos[i]['votos'] += 1

    guardar_datos(RESULTS_FILE, videos)
    votos.append({"email": email, "votado": puntos_por_video})
    guardar_datos(VOTES_FILE, votos)

    return redirect(url_for('resultados_votacion'))


@app.route('/resultados_votacion')
def resultados_votacion():
    resultados = cargar_datos(RESULTS_FILE)
    resultados.sort(key=lambda x: x['puntos'], reverse=True)
    return render_template("resultados_votacion.html", resultados=resultados)


@app.route('/limpiar_todo', methods=['POST'])
def limpiar_todo():
    guardar_datos(RESULTS_FILE, [])
    guardar_datos(VOTES_FILE, [])
    for archivo in os.listdir(UPLOAD_FOLDER):
        if archivo.endswith(tuple(ALLOWED_EXTENSIONS)):
            os.remove(os.path.join(UPLOAD_FOLDER, archivo))
    return "Sistema limpiado correctamente"


if __name__ == '__main__':
    app.run(debug=True)
