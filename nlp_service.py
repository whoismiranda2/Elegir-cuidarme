import re
import unicodedata


STOPWORDS = {
    "yo", "me", "mi", "mis", "tu", "tus", "el", "la", "los", "las",
    "un", "una", "unos", "unas", "de", "del", "que", "y", "o", "en",
    "a", "con", "por", "para", "es", "soy", "estoy", "muy", "mas",
    "más", "pero", "porque", "como", "hoy"
}


DICCIONARIO_EMOCIONES = {
    "ansioso": {
        "palabras": ["ansiedad", "ansioso", "nervioso", "miedo", "preocupado", "estresado", "panico", "pánico"],
        "recomendacion": "Prueba la técnica de respiración 4-7-8."
    },
    "triste": {
        "palabras": ["triste", "solo", "sola", "llorar", "vacio", "vacío", "deprimido", "cansado"],
        "recomendacion": "Prueba escribir una carta a ti mismo o hacer la técnica de las 5 cosas positivas."
    },
    "enojado": {
        "palabras": ["enojo", "enojado", "molesto", "coraje", "rabia", "odio", "furioso"],
        "recomendacion": "Prueba moverte 3 minutos o hacer respiración profunda."
    },
    "bien": {
        "palabras": ["bien", "feliz", "contento", "tranquilo", "alegre", "motivado"],
        "recomendacion": "Sigue haciendo actividades que te cuiden."
    }
}


PALABRAS_RIESGO = [
    "suicidio", "suicidarme", "morirme", "matarme",
    "hacerme daño", "no quiero vivir", "ya no quiero vivir",
    "desaparecer", "lastimarme"
]


def quitar_acentos(texto):
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto


def limpiar_texto(texto):
    texto = texto.lower().strip()
    texto = quitar_acentos(texto)
    texto = re.sub(r"[^a-zñáéíóúü\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def tokenizar(texto):
    palabras = texto.split()
    return [p for p in palabras if p not in STOPWORDS]


def detectar_riesgo(texto_limpio):
    for frase in PALABRAS_RIESGO:
        frase_limpia = quitar_acentos(frase.lower())
        if frase_limpia in texto_limpio:
            return True
    return False


def analizar_emocion_texto(texto):
    if not texto or not texto.strip():
        return {
            "ok": False,
            "mensaje": "No se recibió texto para analizar."
        }

    texto_limpio = limpiar_texto(texto)
    tokens = tokenizar(texto_limpio)

    riesgo = detectar_riesgo(texto_limpio)

    puntajes = {}

    for emocion, datos in DICCIONARIO_EMOCIONES.items():
        puntaje = 0

        for palabra in datos["palabras"]:
            palabra_limpia = quitar_acentos(palabra.lower())

            if palabra_limpia in tokens:
                puntaje += 2

            if palabra_limpia in texto_limpio:
                puntaje += 1

        puntajes[emocion] = puntaje

    emocion_detectada = max(puntajes, key=puntajes.get)
    puntaje_maximo = puntajes[emocion_detectada]
    total_puntajes = sum(puntajes.values())

    if puntaje_maximo == 0:
        emocion_detectada = "normal"
        confianza = 0.0
        recomendacion = "No se detectó una emoción clara. Puedes revisar las técnicas generales de autocuidado."
    else:
        confianza = round(puntaje_maximo / total_puntajes, 2)
        recomendacion = DICCIONARIO_EMOCIONES[emocion_detectada]["recomendacion"]

    if riesgo:
        emocion_detectada = "riesgo"
        confianza = 1.0
        recomendacion = (
            "El texto contiene señales de posible riesgo. "
            "Se recomienda hablar inmediatamente con un orientador, maestro o adulto de confianza."
        )

    return {
        "ok": True,
        "texto_limpio": texto_limpio,
        "tokens": tokens,
        "emocion_detectada": emocion_detectada,
        "puntajes": puntajes,
        "confianza": confianza,
        "riesgo": riesgo,
        "recomendacion": recomendacion
    }