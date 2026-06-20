import json
import os
from nlp_service import analizar_emocion_texto


BASE_DIR = os.path.dirname(__file__)


def cargar_json(nombre_archivo):
    path = os.path.join(BASE_DIR, "data", nombre_archivo)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def tecnicas_para_emocion(emocion):
    tecnicas = cargar_json("tecnicas.json")
    return [
        {
            "nombre": t["nombre"],
            "descripcion": t["descripcion"]
        }
        for t in tecnicas
        if emocion in t.get("para", [])
    ][:2]


def actividades_sugeridas():
    actividades = cargar_json("actividades.json")
    sugerencias = []

    for categoria in actividades:
        for opcion in categoria.get("opciones", [])[:1]:
            sugerencias.append({
                "categoria": categoria["categoria"],
                "nombre": opcion["nombre"],
                "descripcion": opcion["descripcion"]
            })

    return sugerencias[:3]


def videos_sugeridos(emocion):
    videos = cargar_json("videos.json")

    if emocion == "ansioso":
        claves = ["ansiedad", "emociones"]
    elif emocion == "triste":
        claves = ["autoestima", "emociones"]
    elif emocion == "enojado":
        claves = ["emociones", "presión"]
    else:
        claves = ["salud", "autoestima"]

    resultado = []
    for video in videos:
        texto = f"{video['titulo']} {video['descripcion']} {video['categoria']}".lower()
        if any(c in texto for c in claves):
            resultado.append({
                "titulo": video["titulo"],
                "descripcion": video["descripcion"],
                "categoria": video["categoria"],
                "duracion": video["duracion"]
            })

    return resultado[:2]


def construir_respuesta_base(emocion, mensaje_usuario):
    if emocion == "ansioso":
        return (
            "Parece que tu mensaje expresa ansiedad o preocupación. "
            "Tiene sentido sentirse así cuando hay presión o incertidumbre. "
            "Podemos empezar con una técnica breve para calmar el cuerpo."
        )

    if emocion == "triste":
        return (
            "Parece que tu mensaje expresa tristeza o cansancio emocional. "
            "Gracias por escribirlo. Nombrarlo ya es una forma de cuidarte."
        )

    if emocion == "enojado":
        return (
            "Parece que tu mensaje expresa enojo o frustración. "
            "El enojo no es malo; suele aparecer cuando algo importa o cuando sentimos que algo fue injusto."
        )

    if emocion == "bien":
        return (
            "Tu mensaje parece expresar bienestar o tranquilidad. "
            "Es buen momento para reforzar hábitos que te ayudan a seguir cuidándote."
        )

    return (
        "Leí tu mensaje. No detecté una emoción dominante con suficiente claridad, "
        "pero puedo sugerirte algunas opciones generales de autocuidado."
    )


def responder_flora(mensaje):
    if not mensaje or not mensaje.strip():
        return {
            "ok": False,
            "respuesta": "Escribe algo para que Flora pueda acompañarte.",
            "emocion_detectada": "normal",
            "riesgo": False,
            "tecnicas": [],
            "actividades": [],
            "videos": []
        }

    analisis = analizar_emocion_texto(mensaje)
    emocion = analisis.get("emocion_detectada", "normal")
    riesgo = analisis.get("riesgo", False)

    if riesgo:
        return {
            "ok": True,
            "emocion_detectada": "riesgo",
            "confianza": 1.0,
            "riesgo": True,
            "respuesta": (
                "Me preocupa lo que escribiste. No tienes que manejar esto a solas. "
                "Busca ahora mismo a un adulto de confianza, orientador escolar, maestro o familiar. "
                "Si sientes que puedes hacerte daño, pide ayuda inmediata."
            ),
            "tecnicas": [],
            "actividades": [],
            "videos": [],
            "acciones": ["mostrar_alerta_riesgo"]
        }

    tecnicas = tecnicas_para_emocion(emocion)
    actividades = actividades_sugeridas()
    videos = videos_sugeridos(emocion)

    respuesta = construir_respuesta_base(emocion, mensaje)

    if tecnicas:
        respuesta += f" Te sugiero empezar con: {tecnicas[0]['nombre']}."

    return {
        "ok": True,
        "emocion_detectada": emocion,
        "confianza": analisis.get("confianza", 0),
        "riesgo": False,
        "respuesta": respuesta,
        "tecnicas": tecnicas,
        "actividades": actividades,
        "videos": videos,
        "tokens": analisis.get("tokens", []),
        "puntajes": analisis.get("puntajes", {}),
        "acciones": [f"filtrar_tecnicas:{emocion}"] if emocion != "normal" else []
    }