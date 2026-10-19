import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import subprocess
import os
import requests
import threading
import asyncio
import edge_tts
import pygame


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_IMAGEN = os.path.join(BASE_DIR, "Runny.jpeg")
RUTA_FONDO = os.path.join(BASE_DIR, "Fondo.png")

CARPETA_IMAGENES = r"C:\Users\Family\Desktop\Software Robot Pro\imagenesRimas"
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


ESP32_IP = "192.168.4.2"
ESP32_PORT = 80
CONTROL_PASSWORD = "Motores123"

# ============================================================
# COLORES
# ============================================================

BG = "#101820"
PANEL = "#17232d"
PANEL2 = "#0b1117"

GREEN = "#00ff88"
WHITE = "#ffffff"
GRAY = "#cccccc"
BLUE = "#1769aa"

COLOR_INTERACCION = "#eef5ff"
COLOR_NUMEROS = "#1769aa"
COLOR_COLORES = "#7b1fa2"
COLOR_LETRAS = "#00897b"


# ============================================================
# VOZ
# ============================================================

VOZ_RUNNY = "es-MX-DaliaNeural"

CARPETA_AUDIO = os.path.join(
    os.environ.get("TEMP", "."),
    "runny_audio"
)

os.makedirs(
    CARPETA_AUDIO,
    exist_ok=True
)


# ============================================================
# AUDIO
# ============================================================

try:
    pygame.mixer.init()
except Exception as error:
    print("No se pudo iniciar pygame:", error)


audios_preparados = {}
audio_generation_lock = threading.Lock()

# Identificador del audio actualmente solicitado.
# Sirve para impedir que un audio viejo vuelva a sonar.
audio_id_actual = 0

audio_id_lock = threading.Lock()

contador_audio = 0


def obtener_audio_id():

    global audio_id_actual

    with audio_id_lock:
        audio_id_actual += 1
        return audio_id_actual


def detener_audio():

    try:
        pygame.mixer.music.stop()
    except Exception:
        pass


# ============================================================
# VENTANA
# ============================================================

ventana = tk.Tk()

ventana.title(
    "CONTROL DEL ROBOT - RUNNY"
)

ventana.geometry(
    "1350x760"
)

ventana.minsize(
    950,
    650
)

ventana.resizable(
    True,
    True
)

ventana.configure(
    bg=BG
)


# ============================================================
# VARIABLES
# ============================================================

lista_wifi = None
estado_wifi = None
estado_comando = None

etiqueta_mano_derecha = None
etiqueta_muneca_derecha = None
etiqueta_codo_derecho = None

etiqueta_mano_izquierda = None
etiqueta_muneca_izquierda = None
etiqueta_codo_izquierdo = None

contenido = None


# ============================================================
# GENERAR AUDIO
# ============================================================

def generar_audio(texto, archivo):

    async def generar():

        comunicador = edge_tts.Communicate(
            text=texto,
            voice=VOZ_RUNNY,
            rate="-20%",
            pitch="+45Hz",
            volume="+0%"
        )

        await comunicador.save(
            archivo
        )

    asyncio.run(
        generar()
    )


# ============================================================
# PREPARAR AUDIO
# ============================================================

def preparar_audio(nombre, texto):

    try:

        archivo = os.path.join(
            CARPETA_AUDIO,
            nombre + ".mp3"
        )

        if not os.path.exists(archivo):

            generar_audio(
                texto,
                archivo
            )

        audios_preparados[texto] = archivo

        return True

    except Exception as error:

        print(
            "Error preparando audio:",
            texto,
            error
        )

        return False


# ============================================================
# DATOS DE INTERACCIÓN
# ============================================================

NUMEROS = {

    "0": (
        "cero",
        "Cero, cero, redondito, parece un huevito.",
        "0",
        "cero.png"
    ),

    "1": (
        "uno",
        "Uno, uno, mira qué bonito, es el primero y está solito.",
        "1",
        "uno.png"
    ),

    "2": (
        "dos",
        "Dos, dos, son dos amiguitos, juntos son muy divertidos.",
        "2",
        "dos.png"
    ),

    "3": (
        "tres",
        "Tres, tres, cuenta otra vez, uno, dos y tres.",
        "3",
        "tres.png"
    ),

    "4": (
        "cuatro",
        "Cuatro, cuatro, vamos a contar, uno, dos, tres y cuatro al final.",
        "4",
        "cuatro.png"
    ),

    "5": (
        "cinco",
        "Cinco, cinco, abre tu mano, cinco deditos saludan temprano.",
        "5",
        "cinco.png"
    ),

    "6": (
        "seis",
        "Seis, seis, vamos a aprender, cuenta conmigo, lo vas a entender.",
        "6",
        "seis.png"
    ),

    "7": (
        "siete",
        "Siete, siete, qué divertido, ya lo aprendiste, qué buen amigo.",
        "7",
        "siete.png"
    ),

    "8": (
        "ocho",
        "Ocho, ocho, parece un moñito, míralo bien, es muy bonito.",
        "8",
        "ocho.png"
    ),

    "9": (
        "nueve",
        "Nueve, nueve, vamos a cantar, otro numerito vamos a aprender.",
        "9",
        "nueve.png"
    )
}


COLORES = {

    "ROJO": (
        "#e53935",
        "Rojo, rojo, como una manzana, es un color bonito que brilla en la mañana.",
        "ROJO", "manzana.png"
    ),

    "AZUL": (
        "#1e88e5",
        "Azul, azul, como el cielo y el mar, es un color hermoso que podemos mirar.",
        "AZUL", "nubes.png"  
    ),

    "VERDE": (
        "#43a047",
        "Verde, verde, como una hoja, es el color que a la naturaleza le encanta.",
        "VERDE",
        "hoja.png"
    ),

    "AMARILLO": (
        "#fdd835",
        "Amarillo, amarillo, como el sol, brilla brillante con mucho color.",
        "AMARILLO",
        "sol.png"
    ),

    "BLANCO": (
        "#ffffff",
        "Blanco, blanco, como una nube, suave y bonito hasta el cielo sube.",
        "BLANCO",
        "nube.png"
    ),

    "NEGRO": (
        "#000000",
        "Negro, negro, como la noche, cuando aparece se duerme el coche.",
        "NEGRO",
        "noche.png"
    ),

    "NARANJA": (
        "#fb8c00",
        "Naranja, naranja, como una naranja, qué rico color que a todos nos encanta.",
        "NARANJA",
        "naranja.png"
    ),

    "MORADO": (
        "#8e24aa",
        "Morado, morado, como una flor, es un bonito y mágico color.",
        "MORADO",
        "flor.png"
    ),

    "ROSADO": (
        "#ec407a",
        "Rosado, rosado, suave y bonito, parece el color de un dulce pastelito.",
        "ROSADO",
        "pastelito.png"
    ),

    "CAFÉ": (
        "#6d4c41",
        "Café, café, como la tierra, es un color que la naturaleza encierra.",
        "CAFÉ",
        "tierra.png"
    ),

    "GRIS": (
        "#757575",
        "Gris, gris, como una nube, cuando aparece lentamente sube.",
        "GRIS",
        "nube_gris.png"
    ),

    "CELESTE": (
        "#29b6f6",
        "Celeste, celeste, como el cielo, es un color que parece un sueño.",
        "CELESTE",
        "cielo.png"
    )
}


LETRAS = {

    "A": (
        "avión",
        "A, A, la primera letra, A de avión que vuela y vuela.",
        "A",
        "A.png"
    ),

    "B": (
        "barco",
        "B, B, suena muy bien, B de barco que navega también.",
        "B",
        "barco.png"
    ),

    "C": (
        "casa",
        "C, C, vamos a aprender, C de casa, qué bonito es leer.",
        "C",
        "casa.png"
    ),

    "D": (
        "dado",
        "D, D, qué emoción, D de dado y de diversión.",
        "D",
        "dado.png"
    ),

    "E": (
        "estrella",
        "E, E, vamos a cantar, E de estrella que podemos mirar.",
        "E",
        "estrella.png"
    ),

    "F": (
        "flor",
        "F, F, qué emoción, F de flor y de diversión.",
        "F",
        "flor.png"
    ),

    "G": (
        "gato",
        "G, G, suena genial, G de gato, animal especial.",
        "G",
        "gato.png"
    ),

    "H": (
        "helado",
        "H, H, aunque no suena, H de helado que vale la pena.",
        "H",
        "helado.png"
    ),

    "I": (
        "iguana",
        "I, I, vamos a aprender, I de iguana, la puedes conocer.",
        "I",
        "iguana.png"
    ),

    "J": (
        "jirafa",
        "J, J, qué diversión, J de jirafa de gran tamaño.",
        "J",
        "jirafa.png"
    ),

    "K": (
        "kilo",
        "K, K, vamos a cantar, K de kilo, fácil de recordar.",
        "K",
        "kilo.png"
    ),

    "L": (
        "luna",
        "L, L, qué bonito es, L de luna que aparece después.",
        "L",
        "luna.png"
    ),

    "M": (
        "mamá",
        "M, M, vamos a aprender, M de mamá, qué bonito es querer.",
        "M",
        "mama.png"
    ),

    "N": (
        "nube",
        "N, N, suena muy bien, N de nube que vemos también.",
        "N",
        "nube.png"
    ),

    "Ñ": (
        "niño",
        "Ñ, Ñ, letra especial, Ñ de niño, ¡qué genial!",
        "Ñ",
        "nino.png"
    ),

    "O": (
        "oso",
        "O, O, redonda como el sol, O de oso, qué lindo animal.",
        "O",
        "oso.png"
    ),

    "P": (
        "perro",
        "P, P, vamos a cantar, P de perro que nos puede acompañar.",
        "P",
        "perro.png"
    ),

    "Q": (
        "queso",
        "Q, Q, qué emoción, Q de queso, qué rico sabor.",
        "Q",
        "queso.png"
    ),

    "R": (
        "robot",
        "R, R, vamos a aprender, R de robot, ¡como Runny también!",
        "R",
        "robot.png"
    ),

    "S": (
        "sapo",
        "S, S, suena genial, S de sapo, animal especial.",
        "S",
        "sapo.png"
    ),

    "T": (
        "tren",
        "T, T, vamos a cantar, T de tren que comienza a andar.",
        "T",
        "tren.png"
    ),

    "U": (
        "uva",
        "U, U, qué divertido, U de uva, un fruto delicioso.",
        "U",
        "uva.png"
    ),

    "V": (
        "vaca",
        "V, V, vamos a aprender, V de vaca que podemos conocer.",
        "V",
        "vaca.png"
    ),

    "W": (
        "uve doble",
        "W, W, uve doble se llama, aprendemos juntos con mucha calma.",
        "W",
        "uve_doble.png"
    ),

    "X": (
        "xilófono",
        "X, X, vamos a aprender, X de xilófono que podemos tocar.",
        "X",
        "xilofono.png"
    ),

    "Y": (
        "yoyo",
        "Y, Y, qué emoción, Y de yoyo que sube y baja un montón.",
        "Y",
        "yoyo.png"
    ),

    "Z": (
        "zapato",
        "Z, Z, vamos a terminar, Z de zapato para caminar.",
        "Z",
        "zapato.png"
    )
}


# ============================================================
# FUENTES
# ============================================================

def obtener_fuente(tamano=80):

    rutas = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf"
    ]

    for ruta in rutas:

        try:
            return ImageFont.truetype(
                ruta,
                tamano
            )
        except Exception:
            pass

    return ImageFont.load_default()


# ============================================================
# IMAGEN ILUSTRATIVA
# ============================================================

  # ============================================================
# IMAGEN ILUSTRATIVA
# ============================================================

def crear_imagen_ilustrativa(
    titulo,
    subtitulo,
    simbolo,
    fondo,
    archivo_imagen=None,
    
    tipo="normal"
):

    ancho = 700
    alto = 500

    imagen = Image.new("RGB", (ancho, alto), fondo)
    dibujo = ImageDraw.Draw(imagen)

    # --- DECORACIÓN ---
    decoraciones = [(45, 50, 18), (655, 55, 25), (70, 430, 22), (630, 425, 18)]
    for x, y, radio in decoraciones:
        dibujo.ellipse((x - radio, y - radio, x + radio, y + radio), fill="#ffffff")

    # --- TÍTULO ---
    fuente_titulo = obtener_fuente(38)
    fuente_sub = obtener_fuente(27)

    caja = dibujo.textbbox((0, 0), titulo, font=fuente_titulo)
    ancho_titulo = caja[2] - caja[0]

    if ancho_titulo > 620:
        fuente_titulo = obtener_fuente(28)
        caja = dibujo.textbbox((0, 0), titulo, font=fuente_titulo)
        ancho_titulo = caja[2] - caja[0]

    dibujo.text(((ancho - ancho_titulo) / 2, 28), titulo, fill="#ffffff", font=fuente_titulo)

    # --- CÍRCULO CENTRAL ---
    dibujo.ellipse((165, 105, 535, 375), fill="#ffffff")

    # --- AQUÍ SE METE LA IMAGEN AL COLOR ---
    imagen_colocada = False
    if archivo_imagen:
        ruta_completa = os.path.join(CARPETA_IMAGENES, archivo_imagen)
        if os.path.exists(ruta_completa):
            try:
                # Abrimos la imagen de la rima (ej. manzana.png)
                img_centro = Image.open(ruta_completa).convert("RGBA")
                # La achicamos para que quepa dentro del círculo blanco
                img_centro.thumbnail((320, 240), Image.Resampling.LANCZOS)
                
                # Calculamos el centro exacto del círculo para pegarla
                pos_x = 165 + (370 - img_centro.width) // 2
                pos_y = 105 + (270 - img_centro.height) // 2
                
                # Pegamos la imagen sobre el fondo de color
                imagen.paste(img_centro, (int(pos_x), int(pos_y)), img_centro)
                imagen_colocada = True
            except Exception as e:
                print(f"Error cargando la imagen {archivo_imagen}:", e)

    # --- SÍMBOLO (Si por algún motivo no hay foto, pone la letra/número normal) ---
    if not imagen_colocada:
        fuente_grande = obtener_fuente(150)
        simbolo = str(simbolo)
        caja = dibujo.textbbox((0, 0), simbolo, font=fuente_grande)
        sw = caja[2] - caja[0]
        sh = caja[3] - caja[1]

        if sw > 300:
            fuente_grande = obtener_fuente(75)
            caja = dibujo.textbbox((0, 0), simbolo, font=fuente_grande)
            sw = caja[2] - caja[0]
            sh = caja[3] - caja[1]

        dibujo.text(
            ((ancho - sw) / 2, 175),
            simbolo,
            fill=fondo if fondo != "#ffffff" else "#222222",
            font=fuente_grande
        )

    # --- SUBTÍTULO ---
    subtitulo = str(subtitulo)
    caja = dibujo.textbbox((0, 0), subtitulo, font=fuente_sub)
    tw = caja[2] - caja[0]

    if tw > 620:
        fuente_sub = obtener_fuente(21)
        caja = dibujo.textbbox((0, 0), subtitulo, font=fuente_sub)
        tw = caja[2] - caja[0]

    dibujo.text(((ancho - tw) / 2, 425), subtitulo, fill="#ffffff", font=fuente_sub)

    return imagen

    # --------------------------------------------------------
    # DECORACIÓN
    # --------------------------------------------------------

    decoraciones = [
        (45, 50, 18),
        (655, 55, 25),
        (70, 430, 22),
        (630, 425, 18)
    ]

    for x, y, radio in decoraciones:

        dibujo.ellipse(
            (
                x - radio,
                y - radio,
                x + radio,
                y + radio
            ),
            fill="#ffffff"
        )

    # --------------------------------------------------------
    # TÍTULO
    # --------------------------------------------------------

    fuente_titulo = obtener_fuente(38)
    fuente_grande = obtener_fuente(150)
    fuente_sub = obtener_fuente(27)

    caja = dibujo.textbbox(
        (0, 0),
        titulo,
        font=fuente_titulo
    )

    ancho_titulo = caja[2] - caja[0]

    # Si el título es muy grande, reducirlo
    if ancho_titulo > 620:

        fuente_titulo = obtener_fuente(28)

        caja = dibujo.textbbox(
            (0, 0),
            titulo,
            font=fuente_titulo
        )

        ancho_titulo = caja[2] - caja[0]

    dibujo.text(
        (
            (ancho - ancho_titulo) / 2,
            28
        ),
        titulo,
        fill="#ffffff",
        font=fuente_titulo
    )

    # --------------------------------------------------------
    # CÍRCULO CENTRAL
    # --------------------------------------------------------

    dibujo.ellipse(
        (165, 105, 535, 375),
        fill="#ffffff"
    )

    # --------------------------------------------------------
    # SÍMBOLO
    # --------------------------------------------------------

    simbolo = str(simbolo)

    caja = dibujo.textbbox(
        (0, 0),
        simbolo,
        font=fuente_grande
    )

    sw = caja[2] - caja[0]
    sh = caja[3] - caja[1]

    # Si es un texto largo, usamos fuente más pequeña
    if sw > 300:

        fuente_grande = obtener_fuente(75)

        caja = dibujo.textbbox(
            (0, 0),
            simbolo,
            font=fuente_grande
        )

        sw = caja[2] - caja[0]
        sh = caja[3] - caja[1]

    dibujo.text(
        (
            (ancho - sw) / 2,
            175
        ),
        simbolo,
        fill=fondo if fondo != "#ffffff" else "#222222",
        font=fuente_grande
    )

    # --------------------------------------------------------
    # SUBTÍTULO
    # --------------------------------------------------------

    subtitulo = str(subtitulo)

    caja = dibujo.textbbox(
        (0, 0),
        subtitulo,
        font=fuente_sub
    )

    tw = caja[2] - caja[0]

    if tw > 620:

        fuente_sub = obtener_fuente(21)

        caja = dibujo.textbbox(
            (0, 0),
            subtitulo,
            font=fuente_sub
        )

        tw = caja[2] - caja[0]

    dibujo.text(
        (
            (ancho - tw) / 2,
            425
        ),
        subtitulo,
        fill="#ffffff",
        font=fuente_sub
    )

    return imagen


# ============================================================
# IMAGEN MENÚ NÚMEROS
# ============================================================

def imagen_menu_numeros():

    return crear_imagen_ilustrativa(
        "¡VAMOS A CONTAR!",
        "Aprendamos los números",
        "123",
        COLOR_NUMEROS
    )


# ============================================================
# IMAGEN MENÚ COLORES
# ============================================================

def imagen_menu_colores():

    imagen = Image.new(
        "RGB",
        (700, 500),
        COLOR_COLORES
    )

    dibujo = ImageDraw.Draw(
        imagen
    )

    fuente = obtener_fuente(35)

    texto = "¡DESCUBRAMOS LOS COLORES!"

    caja = dibujo.textbbox(
        (0, 0),
        texto,
        font=fuente
    )

    dibujo.text(
        (
            (700 - (caja[2] - caja[0])) / 2,
            30
        ),
        texto,
        fill="white",
        font=fuente
    )

    colores = [
        "#e53935",
        "#fb8c00",
        "#fdd835",
        "#43a047",
        "#1e88e5",
        "#8e24aa",
        "#ec407a"
    ]

    for i, color in enumerate(colores):

        x = 60 + i * 90

        dibujo.ellipse(
            (
                x,
                145,
                x + 65,
                210
            ),
            fill=color
        )

    dibujo.arc(
        (180, 180, 520, 360),
        180,
        180,
        fill="white",
        width=12
    )

    fuente2 = obtener_fuente(25)

    texto2 = "¡Los colores están por todas partes!"

    caja2 = dibujo.textbbox(
        (0, 0),
        texto2,
        font=fuente2
    )

    dibujo.text(
        (
            (700 - (caja2[2] - caja2[0])) / 2,
            425
        ),
        texto2,
        fill="white",
        font=fuente2
    )

    return imagen


# ============================================================
# IMAGEN MENÚ ABECEDARIO
# ============================================================

def imagen_menu_abecedario():

    imagen = Image.new(
        "RGB",
        (700, 500),
        COLOR_LETRAS
    )

    dibujo = ImageDraw.Draw(
        imagen
    )

    fuente = obtener_fuente(35)

    texto = "¡VAMOS A APRENDER LETRAS!"

    caja = dibujo.textbbox(
        (0, 0),
        texto,
        font=fuente
    )

    dibujo.text(
        (
            (700 - (caja[2] - caja[0])) / 2,
            25
        ),
        texto,
        fill="white",
        font=fuente
    )

    letras = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G"
    ]

    fuente_letra = obtener_fuente(58)

    for i, letra in enumerate(letras):

        x = 55 + (i % 4) * 150
        y = 125 + (i // 4) * 115

        dibujo.rounded_rectangle(
            (
                x,
                y,
                x + 105,
                y + 85
            ),
            radius=20,
            fill="white"
        )

        dibujo.text(
            (
                x + 32,
                y + 8
            ),
            letra,
            fill=COLOR_LETRAS,
            font=fuente_letra
        )

    return imagen


# ============================================================
# REPRODUCCIÓN DE AUDIO
# ============================================================

def reproducir_audio(texto, etiqueta_voz=None):

    """
    Detiene inmediatamente el audio anterior.

    Si el audio ya está preparado, comienza inmediatamente.

    Si todavía no existe, se genera en segundo plano.
    Si durante la generación el usuario pulsa otro botón,
    el audio anterior NO se reproducirá.
    """

    global contador_audio

    # --------------------------------------------------------
    # NUEVO ID
    # --------------------------------------------------------

    mi_id = obtener_audio_id()

    # --------------------------------------------------------
    # DETENER AUDIO ACTUAL INMEDIATAMENTE
    # --------------------------------------------------------

    detener_audio()

    if etiqueta_voz is not None:

        try:
            etiqueta_voz.config(
                text="🔊 PREPARANDO VOZ..."
            )
        except Exception:
            pass

    # --------------------------------------------------------
    # AUDIO YA EXISTENTE
    # --------------------------------------------------------

    if texto in audios_preparados:

        archivo = audios_preparados[texto]

        def reproducir_preparado():

            try:

                with audio_id_lock:

                    if mi_id != audio_id_actual:
                        return

                pygame.mixer.music.load(
                    archivo
                )

                with audio_id_lock:

                    if mi_id != audio_id_actual:
                        return

                pygame.mixer.music.play()

                if etiqueta_voz is not None:

                    ventana.after(
                        0,
                        lambda:
                        etiqueta_voz.config(
                            text="🔊 RUNNY ESTÁ HABLANDO..."
                        )
                    )

            except Exception as error:

                print(
                    "Error reproduciendo:",
                    error
                )

        threading.Thread(
            target=reproducir_preparado,
            daemon=True
        ).start()

        return

    # --------------------------------------------------------
    # GENERAR AUDIO SI NO EXISTE
    # --------------------------------------------------------

    def generar_y_reproducir():

        global contador_audio

        try:

            with audio_generation_lock:

                if texto in audios_preparados:

                    archivo = audios_preparados[texto]

                else:

                    contador_audio += 1

                    archivo = os.path.join(
                        CARPETA_AUDIO,
                        "runny_extra_"
                        + str(contador_audio)
                        + ".mp3"
                    )

                    generar_audio(
                        texto,
                        archivo
                    )

                    audios_preparados[
                        texto
                    ] = archivo

            # ------------------------------------------------
            # COMPROBAR SI SIGUE SIENDO EL AUDIO ACTUAL
            # ------------------------------------------------

            with audio_id_lock:

                if mi_id != audio_id_actual:

                    return

            pygame.mixer.music.load(
                archivo
            )

            with audio_id_lock:

                if mi_id != audio_id_actual:

                    return

            pygame.mixer.music.play()

            if etiqueta_voz is not None:

                ventana.after(
                    0,
                    lambda:
                    etiqueta_voz.config(
                        text="🔊 RUNNY ESTÁ HABLANDO..."
                    )
                )

        except Exception as error:

            print(
                "Error generando audio:",
                error
            )

            if etiqueta_voz is not None:

                ventana.after(
                    0,
                    lambda:
                    etiqueta_voz.config(
                        text="⚠️ NO SE PUDO REPRODUCIR LA VOZ"
                    )
                )

    threading.Thread(
        target=generar_y_reproducir,
        daemon=True
    ).start()


# ============================================================
# PRECARGAR AUDIOS
# ============================================================

def precargar_audios():

    try:

        preparar_audio(
            "saludo_runny",
            "¡Hola! Soy Runny. Estoy muy feliz de interactuar contigo. ¡Vamos a jugar!"
        )

        preparar_audio(
            "bienvenida_interaccion",
            "Bienvenidos a todos los niños y niñas que van a aprender conmigo jugando. Conoceremos números, colores y abecedario. Selecciona el que desees empezar a aprender."
        )

        preparar_audio(
            "seleccion_numeros",
            "Seleccionaste números. ¡Bienvenido! Vamos a aprender los números jugando."
        )

        preparar_audio(
            "seleccion_colores",
            "Seleccionaste colores. ¡Bienvenido! Vamos a aprender los colores jugando."
        )

        preparar_audio(
            "seleccion_abecedario",
            "Seleccionaste el abecedario. ¡Bienvenido! Vamos a aprender las letras jugando."
        )

        # ----------------------------------------------------
        # NÚMEROS
        # ----------------------------------------------------

        for numero, datos in NUMEROS.items():

            nombre = datos[0]
            frase = datos[1]

            texto = (
                "Seleccionaste el número "
                + nombre
                + ". "
                + frase
            )

            preparar_audio(
                "numero_rima_" + numero,
                texto
            )

        # ----------------------------------------------------
        # COLORES
        # ----------------------------------------------------

        for color, datos in COLORES.items():

            frase = datos[1]

            texto = (
                "Seleccionaste el color "
                + color.lower()
                + ". "
                + frase
            )

            preparar_audio(
                "color_rima_" + color,
                texto
            )

        # ----------------------------------------------------
        # LETRAS
        # ----------------------------------------------------

        for letra, datos in LETRAS.items():

            frase = datos[1]

            texto = (
                "Seleccionaste la letra "
                + letra
                + ". "
                + frase
            )

            preparar_audio(
                "letra_rima_" + letra,
                texto
            )

        print(
            "AUDIOS DE RUNNY PREPARADOS"
        )

    except Exception as error:

        print(
            "Error precargando audios:",
            error
        )


# ============================================================
# SALUDO
# ============================================================

def saludo_inicial():

    reproducir_audio(
        "¡Hola! Soy Runny. Estoy muy feliz de interactuar contigo. ¡Vamos a jugar!"
    )


# ============================================================
# WIFI
# ============================================================

def escanear_wifi():

    if lista_wifi is None:
        return

    lista_wifi.delete(
        0,
        tk.END
    )

    estado_wifi.config(
        text="Escaneando redes WiFi..."
    )

    ventana.update()

    try:

        resultado = subprocess.check_output(
            [
                "netsh",
                "wlan",
                "show",
                "networks"
            ],
            encoding="cp850",
            errors="ignore"
        )

        redes = []

        for linea in resultado.splitlines():

            linea = linea.strip()

            if (
                linea.startswith("SSID ")
                and ":" in linea
            ):

                nombre = linea.split(
                    ":",
                    1
                )[1].strip()

                if (
                    nombre != ""
                    and nombre not in redes
                ):

                    redes.append(
                        nombre
                    )

        if len(redes) == 0:

            estado_wifi.config(
                text="No se encontraron redes"
            )

            return

        for red in redes:

            lista_wifi.insert(
                tk.END,
                red
            )

        estado_wifi.config(
            text=str(len(redes))
            + " red(es) encontrada(s)"
        )

    except Exception as error:

        estado_wifi.config(
            text="Error al escanear"
        )

        messagebox.showerror(
            "Error WiFi",
            str(error)
        )


def conectar_wifi():

    if lista_wifi is None:
        return

    seleccion = lista_wifi.curselection()

    if not seleccion:

        messagebox.showwarning(
            "WiFi",
            "Selecciona primero una red."
        )

        return

    ssid = lista_wifi.get(
        seleccion[0]
    )

    ventana_password = tk.Toplevel(
        ventana
    )

    ventana_password.title(
        "CONTRASEÑA WIFI"
    )

    ventana_password.geometry(
        "420x230"
    )

    ventana_password.resizable(
        False,
        False
    )

    ventana_password.configure(
        bg=PANEL
    )

    tk.Label(
        ventana_password,
        text="RED WIFI",
        font=("Arial", 15, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(
        pady=(20, 5)
    )

    tk.Label(
        ventana_password,
        text=ssid,
        font=("Arial", 12),
        fg=GREEN,
        bg=PANEL
    ).pack(
        pady=5
    )

    entrada_password = tk.Entry(
        ventana_password,
        show="*",
        font=("Arial", 13),
        width=30
    )

    entrada_password.pack(
        pady=10
    )

    def realizar_conexion():

        password = entrada_password.get()

        if password == "":

            messagebox.showwarning(
                "WiFi",
                "Introduce la contraseña."
            )

            return

        ventana_password.destroy()

        estado_wifi.config(
            text="Conectando a "
            + ssid
            + "..."
        )

        try:

            perfil_wifi = """<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>SSID_AQUI</name>
    <SSIDConfig>
        <SSID>
            <name>SSID_AQUI</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>PASSWORD_AQUI</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
"""

            perfil_wifi = perfil_wifi.replace(
                "SSID_AQUI",
                ssid
            )

            perfil_wifi = perfil_wifi.replace(
                "PASSWORD_AQUI",
                password
            )

            archivo_temporal = os.path.join(
                os.environ["TEMP"],
                "wifi_esp32.xml"
            )

            with open(
                archivo_temporal,
                "w",
                encoding="utf-8"
            ) as archivo:

                archivo.write(
                    perfil_wifi
                )

            subprocess.run(
                [
                    "netsh",
                    "wlan",
                    "add",
                    "profile",
                    "filename="
                    + archivo_temporal
                ],
                capture_output=True,
                text=True
            )

            resultado = subprocess.run(
                [
                    "netsh",
                    "wlan",
                    "connect",
                    "name="
                    + ssid
                ],
                capture_output=True,
                text=True
            )

            if resultado.returncode == 0:

                estado_wifi.config(
                    text="Conectado a: "
                    + ssid
                )

                messagebox.showinfo(
                    "WiFi",
                    "Conectado correctamente a:\n\n"
                    + ssid
                    + "\n\nIP de la ESP32:\n"
                    + ESP32_IP
                )

            else:

                estado_wifi.config(
                    text="No se pudo conectar"
                )

                messagebox.showerror(
                    "WiFi",
                    "Windows no pudo conectarse a la red."
                )

        except Exception as error:

            messagebox.showerror(
                "Error WiFi",
                str(error)
            )

    tk.Button(
        ventana_password,
        text="CONECTAR",
        font=("Arial", 12, "bold"),
        width=18,
        height=2,
        command=realizar_conexion
    ).pack(
        pady=10
    )


# ============================================================
# COMANDO SERVO
# ============================================================

def enviar_comando(motor, grados):

    global estado_comando

    try:

        grados = int(
            float(grados)
        )

    except Exception:

        return

    grados = max(
        0,
        min(
            180,
            grados
        )
    )

    comando = (
        motor
        + ":"
        + str(grados)
    )

    if estado_comando is not None:

        estado_comando.config(
            text="Enviando -> "
            + comando
        )

    def enviar():

        try:

            url = (
                "http://"
                + ESP32_IP
                + ":"
                + str(ESP32_PORT)
                + "/servo"
            )

            respuesta = requests.get(
                url,
                params={
                    "motor": motor,
                    "grados": grados
                },
                timeout=2
            )

            if respuesta.status_code == 200:

                ventana.after(
                    0,
                    lambda c=comando:
                    estado_comando.config(
                        text="Enviado correctamente -> "
                        + c
                    )
                )

            else:

                ventana.after(
                    0,
                    lambda codigo=respuesta.status_code:
                    estado_comando.config(
                        text="Error ESP32: "
                        + str(codigo)
                    )
                )

        except Exception:

            ventana.after(
                0,
                lambda c=comando:
                estado_comando.config(
                    text="ESP32 no responde -> "
                    + c
                )
            )

    threading.Thread(
        target=enviar,
        daemon=True
    ).start()


# ============================================================
# MOVIMIENTO
# ============================================================

def enviar_movimiento(caracter):
    global estado_comando

    if caracter not in ("F", "B", "L", "R"):
        return

    # Traducir los caracteres de los botones a las direcciones que espera el C++
    traduccion_direcciones = {
        "F": "arriba",     # Adelante -> Arriba (Y-, Z-)
        "B": "abajo",      # Atrás -> Abajo (Y+, Z+)
        "L": "izquierda",  # Izquierda -> Izquierda (X-, Y+, Z-)
        "R": "derecha"     # Derecha -> Derecha (X+, Y-, Z+)
    }

    direccion_cpp = traduccion_direcciones[caracter]

    if estado_comando is not None:
        estado_comando.config(
            text=f"Enviando movimiento: {direccion_cpp.upper()}"
        )

    def enviar():
        try:
            url = f"http://{ESP32_IP}:{ESP32_PORT}/move"
            
            # Parámetros exactos que pide el código C++ de tu ESP32
            parametros = {
                "clave": CONTROL_PASSWORD,
                "eje": "ALL",
                "direccion": direccion_cpp,
                "pasos": 200,          # Cantidad de pasos por pulsación
                "velocidad": 80      # Velocidad dentro del rango permitido (50 a 1500)
            }

            respuesta = requests.get(url, params=parametros, timeout=2)

            if respuesta.status_code == 200:
                ventana.after(
                    0,
                    lambda: estado_comando.config(
                        text=f"¡Movimiento iniciado!: {direccion_cpp.upper()}"
                    )
                )
            else:
                ventana.after(
                    0,
                    lambda: estado_comando.config(
                        text=f"Error ESP32 ({respuesta.status_code}): {respuesta.text}"
                    )
                )

        except Exception as error:
            ventana.after(
                0,
                lambda: estado_comando.config(
                    text="ESP32 no responde. ¿Estás conectado a su WiFi?"
                )
            )

    threading.Thread(target=enviar, daemon=True).start()



# ============================================================
# MOVIMIENTO
# ============================================================

def crear_frame_movimiento(parent):

    frame_movimiento = tk.LabelFrame(
        parent,
        text=" MOVIMIENTO DEL ROBOT ",
        font=("Arial", 13, "bold"),
        fg=WHITE,
        bg=PANEL,
        padx=10,
        pady=8
    )

    frame_movimiento.pack(
        padx=15,
        pady=8,
        fill="x"
    )

    tk.Label(
        frame_movimiento,
        text="Control de movimiento",
        font=("Arial", 12, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(
        pady=(0, 8)
    )

    flechas = tk.Frame(
        frame_movimiento,
        bg=PANEL
    )

    flechas.pack()

    botones = [
        ("↑", "F", 0, 1),
        ("←", "L", 1, 0),
        ("→", "R", 1, 2),
        ("↓", "B", 2, 1)
    ]

    for simbolo, caracter, fila, columna in botones:

        tk.Button(
            flechas,
            text=simbolo,
            font=("Arial", 25, "bold"),
            width=4,
            height=1,
            bg=BLUE,
            fg=WHITE,
            activebackground="#2585cc",
            relief="flat",
            cursor="hand2",
            command=lambda c=caracter:
            enviar_movimiento(c)
        ).grid(
            row=fila,
            column=columna,
            padx=5,
            pady=4
        )


# ============================================================
# SERVO
# ============================================================

def cambiar_servo(
    valor,
    motor,
    etiqueta
):

    grados = int(
        float(valor)
    )

    etiqueta.config(
        text=str(grados)
        + " grados"
    )

    enviar_comando(
        motor,
        grados
    )


def crear_control_servo(
    parent,
    nombre,
    motor,
    etiqueta_global
):

    tk.Label(
        parent,
        text=nombre,
        font=("Arial", 10, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(
        pady=(2, 0)
    )

    etiqueta = tk.Label(
        parent,
        text="90 grados",
        font=("Arial", 10, "bold"),
        fg=GREEN,
        bg=PANEL
    )

    etiqueta.pack()

    globals()[etiqueta_global] = etiqueta

    slider = tk.Scale(
        parent,
        from_=0,
        to=180,
        orient=tk.HORIZONTAL,
        length=250,
        resolution=1,
        showvalue=False,
        bg=PANEL,
        fg=WHITE,
        highlightthickness=0,
        troughcolor="#253542",
        command=lambda valor,
        m=motor,
        e=etiqueta:
        cambiar_servo(
            valor,
            m,
            e
        )
    )

    slider.set(90)

    slider.pack(
        fill="x",
        padx=5
    )


def crear_frame_servos(parent):

    global etiqueta_mano_derecha
    global etiqueta_muneca_derecha
    global etiqueta_codo_derecho

    global etiqueta_mano_izquierda
    global etiqueta_muneca_izquierda
    global etiqueta_codo_izquierdo

    frame = tk.LabelFrame(
        parent,
        text=" CONTROL DE SERVOMOTORES ",
        font=("Arial", 13, "bold"),
        fg=WHITE,
        bg=PANEL,
        padx=8,
        pady=6
    )

    frame.pack(
        padx=15,
        pady=8,
        fill="x"
    )

    brazos = tk.Frame(
        frame,
        bg=PANEL
    )

    brazos.pack(
        fill="x"
    )

    derecho = tk.LabelFrame(
        brazos,
        text=" BRAZO DERECHO ",
        fg=GREEN,
        bg=PANEL,
        font=("Arial", 11, "bold")
    )

    derecho.pack(
        side="left",
        fill="both",
        expand=True,
        padx=5
    )

    crear_control_servo(
        derecho,
        "MANO",
        "mano_derecha",
        "etiqueta_mano_derecha"
    )

    crear_control_servo(
        derecho,
        "MUÑECA",
        "muneca_derecha",
        "etiqueta_muneca_derecha"
    )

    crear_control_servo(
        derecho,
        "CODO",
        "codo_derecho",
        "etiqueta_codo_derecho"
    )

    izquierdo = tk.LabelFrame(
        brazos,
        text=" BRAZO IZQUIERDO ",
        fg=GREEN,
        bg=PANEL,
        font=("Arial", 11, "bold")
    )

    izquierdo.pack(
        side="right",
        fill="both",
        expand=True,
        padx=5
    )

    crear_control_servo(
        izquierdo,
        "MANO",
        "mano_izquierda",
        "etiqueta_mano_izquierda"
    )

    crear_control_servo(
        izquierdo,
        "MUÑECA",
        "muneca_izquierda",
        "etiqueta_muneca_izquierda"
    )

    crear_control_servo(
        izquierdo,
        "CODO",
        "codo_izquierdo",
        "etiqueta_codo_izquierdo"
    )


# ============================================================
# WIFI PANEL
# ============================================================

def crear_frame_wifi(parent):

    global lista_wifi
    global estado_wifi

    frame = tk.LabelFrame(
        parent,
        text=" CONEXIÓN WiFi ",
        font=("Arial", 13, "bold"),
        fg=WHITE,
        bg=PANEL
    )

    frame.pack(
        padx=15,
        fill="x"
    )

    tk.Button(
        frame,
        text="ESCANEAR REDES WiFi",
        command=escanear_wifi
    ).pack(
        pady=3
    )

    lista_wifi = tk.Listbox(
        frame,
        height=3
    )

    lista_wifi.pack(
        fill="x"
    )

    tk.Button(
        frame,
        text="CONECTAR A RED",
        command=conectar_wifi
    ).pack(
        pady=3
    )

    estado_wifi = tk.Label(
        frame,
        text="Esperando conexión...",
        fg=GREEN,
        bg=PANEL
    )

    estado_wifi.pack()


# ============================================================
# LIMPIAR
# ============================================================

def limpiar_contenido():

    global lista_wifi
    global estado_wifi
    global estado_comando

    # Al cambiar de pantalla también detenemos la voz.
    detener_audio()
    obtener_audio_id()

    lista_wifi = None
    estado_wifi = None
    estado_comando = None

    for widget in contenido.winfo_children():

        widget.destroy()


# ============================================================
# BOTÓN MENÚ
# ============================================================

def crear_boton_menu(
    parent,
    texto,
    comando,
    ancho=25
):

    return tk.Button(
        parent,
        text=texto,
        command=comando,
        font=("Arial", 16, "bold"),
        width=ancho,
        height=2,
        bg=BLUE,
        fg=WHITE,
        activebackground="#2585cc",
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2"
    )


# ============================================================
# INICIO
# ============================================================

def mostrar_inicio():

    limpiar_contenido()

    inicio = tk.Frame(
        contenido,
        bg=PANEL2
    )

    inicio.pack(
        fill="both",
        expand=True
    )

    try:

        fondo = Image.open(
            RUTA_FONDO
        ).convert("RGB")

        etiqueta = tk.Label(
            inicio
        )

        etiqueta.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )

        etiqueta.imagen_original = fondo

        def actualizar(event=None):

            ancho = inicio.winfo_width()
            alto = inicio.winfo_height()

            if ancho <= 1 or alto <= 1:
                return

            imagen = etiqueta.imagen_original.copy()

            proporcion = (
                imagen.width /
                imagen.height
            )

            ventana_prop = (
                ancho /
                alto
            )

            if proporcion > ventana_prop:

                nuevo_alto = alto
                nuevo_ancho = int(
                    alto * proporcion
                )

            else:

                nuevo_ancho = ancho
                nuevo_alto = int(
                    ancho / proporcion
                )

            imagen = imagen.resize(
                (
                    nuevo_ancho,
                    nuevo_alto
                ),
                Image.Resampling.LANCZOS
            )

            izquierda = max(
                0,
                (nuevo_ancho - ancho) // 2
            )

            arriba = max(
                0,
                (nuevo_alto - alto) // 2
            )

            imagen = imagen.crop(
                (
                    izquierda,
                    arriba,
                    izquierda + ancho,
                    arriba + alto
                )
            )

            foto = ImageTk.PhotoImage(
                imagen
            )

            etiqueta.configure(
                image=foto
            )

            etiqueta.image = foto

        inicio.bind(
            "<Configure>",
            actualizar
        )

        inicio.after(
            100,
            actualizar
        )

    except Exception as error:

        tk.Label(
            inicio,
            text=
            "RUNNY\n\n"
            "No se pudo cargar Fondo.png\n\n"
            + str(error),
            font=("Arial", 25, "bold"),
            fg=WHITE,
            bg=PANEL2
        ).pack(
            expand=True
        )


# ============================================================
# CONTROL DEL ROBOT
# ============================================================

def mostrar_robot():

    limpiar_contenido()

    tk.Label(
        contenido,
        text="CONTROL DEL ROBOT",
        font=("Arial", 28, "bold"),
        fg=WHITE,
        bg=PANEL2
    ).pack(
        pady=15
    )

    principal = tk.Frame(
        contenido,
        bg=PANEL2
    )

    principal.pack(
        fill="both",
        expand=True,
        padx=15
    )

    izquierda = tk.Frame(
        principal,
        bg=PANEL2
    )

    izquierda.pack(
        side="left",
        fill="both",
        expand=True
    )

    try:

        imagen = Image.open(
            RUTA_IMAGEN
        )

        imagen.thumbnail(
            (650, 520),
            Image.Resampling.LANCZOS
        )

        foto = ImageTk.PhotoImage(
            imagen
        )

        etiqueta = tk.Label(
            izquierda,
            image=foto,
            bg=PANEL2
        )

        etiqueta.image = foto

        etiqueta.pack(
            expand=True
        )

    except Exception as error:

        tk.Label(
            izquierda,
            text=
            "No se pudo cargar Runny.jpeg\n\n"
            + str(error),
            fg=WHITE,
            bg=PANEL2
        ).pack(
            expand=True
        )

    # PANEL DE CONTROLES CON DESPLAZAMIENTO VERTICAL
    # Permite acceder a los seis servos incluso en pantallas bajas.
    panel_controles = tk.Frame(
        principal,
        bg=PANEL2,
        width=610
    )

    panel_controles.pack(
        side="right",
        fill="y",
        padx=10
    )

    panel_controles.pack_propagate(False)

    lienzo_controles = tk.Canvas(
        panel_controles,
        bg=PANEL,
        highlightthickness=0,
        width=590
    )

    barra_vertical = tk.Scrollbar(
        panel_controles,
        orient="vertical",
        command=lienzo_controles.yview
    )

    lienzo_controles.configure(
        yscrollcommand=barra_vertical.set
    )

    barra_vertical.pack(
        side="right",
        fill="y"
    )

    lienzo_controles.pack(
        side="left",
        fill="both",
        expand=True
    )

    derecha = tk.Frame(
        lienzo_controles,
        bg=PANEL
    )

    ventana_controles = lienzo_controles.create_window(
        (0, 0),
        window=derecha,
        anchor="nw"
    )

    def actualizar_area_desplazamiento(event=None):
        lienzo_controles.configure(
            scrollregion=lienzo_controles.bbox("all")
        )

    def ajustar_ancho_controles(event):
        lienzo_controles.itemconfigure(
            ventana_controles,
            width=event.width
        )

    derecha.bind(
        "<Configure>",
        actualizar_area_desplazamiento
    )

    lienzo_controles.bind(
        "<Configure>",
        ajustar_ancho_controles
    )

    # La rueda del ratón desplaza el panel cuando el cursor está encima.
    def desplazar_controles(event):
        lienzo_controles.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    def activar_rueda(event):
        lienzo_controles.bind_all(
            "<MouseWheel>",
            desplazar_controles
        )

    def desactivar_rueda(event):
        lienzo_controles.unbind_all(
            "<MouseWheel>"
        )

    lienzo_controles.bind(
        "<Enter>",
        activar_rueda
    )
    lienzo_controles.bind(
        "<Leave>",
        desactivar_rueda
    )

    tk.Label(
        derecha,
        text="CONTROL DEL ROBOT",
        font=("Arial", 21, "bold"),
        fg=WHITE,
        bg=PANEL
    ).pack(
        pady=10
    )

    crear_frame_wifi(
        derecha
    )

    crear_frame_movimiento(
        derecha
    )

    crear_frame_servos(
        derecha
    )

    global estado_comando

    estado_comando = tk.Label(
        derecha,
        text="Último comando: ninguno",
        font=("Arial", 10, "bold"),
        fg=GREEN,
        bg=PANEL
    )

    estado_comando.pack(
        pady=5
    )


# ============================================================
# MOSTRAR IMAGEN SELECCIONADA
# ============================================================

def mostrar_imagen_seleccionada(
    imagen,
    etiqueta,
    panel,
    color
):

    try:

        ancho = panel.winfo_width()
        alto = panel.winfo_height()

        if ancho < 100:
            ancho = 600

        if alto < 100:
            alto = 500

        imagen = imagen.copy()

        proporcion = (
            imagen.width /
            imagen.height
        )

        ventana_prop = (
            ancho /
            alto
        )

        if proporcion > ventana_prop:

            nuevo_ancho = ancho - 30

            nuevo_alto = int(
                nuevo_ancho /
                proporcion
            )

        else:

            nuevo_alto = alto - 30

            nuevo_ancho = int(
                nuevo_alto *
                proporcion
            )

        imagen = imagen.resize(
            (
                max(100, nuevo_ancho),
                max(100, nuevo_alto)
            ),
            Image.Resampling.LANCZOS
        )

        foto = ImageTk.PhotoImage(
            imagen
        )

        etiqueta.configure(
            image=foto
        )

        etiqueta.image = foto

    except Exception as error:

        print(
            "Error mostrando imagen:",
            error
        )


# ============================================================
# PANEL INTERACTIVO
# ============================================================

def crear_panel_interactivo(
    titulo,
    subtitulo,
    imagen_menu,
    color_principal,
    botones,
    funcion_click,
    tipo
):

    limpiar_contenido()

    contenedor = tk.Frame(
        contenido,
        bg=COLOR_INTERACCION
    )

    contenedor.pack(
        fill="both",
        expand=True
    )

    # ========================================================
    # CABECERA
    # ========================================================

    cabecera = tk.Frame(
        contenedor,
        bg=color_principal,
        height=80
    )

    cabecera.pack(
        fill="x"
    )

    cabecera.pack_propagate(
        False
    )

    tk.Button(
        cabecera,
        text="← VOLVER",
        font=("Arial", 11, "bold"),
        bg="#ffffff",
        fg=color_principal,
        relief="flat",
        cursor="hand2",
        command=mostrar_interaccion
    ).pack(
        side="left",
        padx=20,
        pady=18
    )

    tk.Label(
        cabecera,
        text=titulo,
        font=("Arial", 25, "bold"),
        bg=color_principal,
        fg="white"
    ).pack(
        side="left",
        padx=20
    )

    # ========================================================
    # CUERPO
    # ========================================================

    cuerpo = tk.Frame(
        contenedor,
        bg=COLOR_INTERACCION
    )

    cuerpo.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=15
    )

    # ========================================================
    # PANEL IMAGEN
    # ========================================================

    panel_imagen = tk.Frame(
        cuerpo,
        bg="white",
        relief="flat",
        bd=0
    )

    panel_imagen.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 15)
    )

    etiqueta_imagen = tk.Label(
        panel_imagen,
        bg="white"
    )

    etiqueta_imagen.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    # ========================================================
    # PANEL DERECHO
    # ========================================================

    panel_derecho = tk.Frame(
        cuerpo,
        bg="#ffffff",
        width=500
    )

    panel_derecho.pack(
        side="right",
        fill="y"
    )

    panel_derecho.pack_propagate(
        False
    )

    tk.Label(
        panel_derecho,
        text=subtitulo,
        font=("Arial", 18, "bold"),
        fg=color_principal,
        bg="white"
    ).pack(
        pady=(12, 5)
    )

    # ========================================================
    # ELEMENTO SELECCIONADO
    # ========================================================

    seleccionado_label = tk.Label(
        panel_derecho,
        text="¡ELIGE UNO!",
        font=("Arial", 40, "bold"),
        fg=color_principal,
        bg="white"
    )

    seleccionado_label.pack(
        pady=(5, 2)
    )

    # ========================================================
    # ESTADO
    # ========================================================

    estado_label = tk.Label(
        panel_derecho,
        text="Pulsa un botón para comenzar",
        font=("Arial", 10, "bold"),
        fg="#555555",
        bg="white"
    )

    estado_label.pack(
        pady=3
    )

    # ========================================================
    # FRASE DE RUNNY
    # ========================================================

    tk.Label(
        panel_derecho,
        text="💬 FRASE DE RUNNY",
        font=("Arial", 11, "bold"),
        fg=color_principal,
        bg="white"
    ).pack(
        pady=(8, 2)
    )

    frase_frame = tk.Frame(
        panel_derecho,
        bg="#f2f6fa",
        bd=1,
        relief="solid"
    )

    frase_frame.pack(
        fill="x",
        padx=18,
        pady=5
    )

    frase_label = tk.Label(
        frase_frame,
        text=
        "Aquí aparecerá la frase de Runny.",
        font=("Arial", 12, "bold"),
        fg="#333333",
        bg="#f2f6fa",
        wraplength=430,
        justify="center",
        padx=12,
        pady=12
    )

    frase_label.pack(
        fill="x"
    )

    # ========================================================
    # VOZ
    # ========================================================

    voz_label = tk.Label(
        panel_derecho,
        text="🔊 LISTO PARA APRENDER",
        font=("Arial", 10, "bold"),
        fg="#00897b",
        bg="white"
    )

    voz_label.pack(
        pady=5
    )

    # ========================================================
    # GRID DE BOTONES
    # ========================================================

    grid = tk.Frame(
        panel_derecho,
        bg="white"
    )

    grid.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=4
    )

    # --------------------------------------------------------
    # CANTIDAD DE COLUMNAS
    # --------------------------------------------------------

    if tipo == "color":
        columnas = 3
    elif tipo == "letra":
        columnas = 6
    else:
        columnas = 5

    for columna in range(columnas):

        grid.columnconfigure(
            columna,
            weight=1
        )

    # ========================================================
    # BOTONES
    # ========================================================

    for i, elemento in enumerate(botones):

        if isinstance(elemento, tuple):

            nombre = elemento[0]
            color = elemento[1]

        else:

            nombre = elemento
            color = color_principal

        # ----------------------------------------------------
        # COLOR DE TEXTO
        # ----------------------------------------------------

        colores_oscuros = (
            "#000000",
            "#e53935",
            "#1e88e5",
            "#43a047",
            "#8e24aa",
            "#ec407a",
            "#fb8c00",
            "#6d4c41",
            "#757575",
            "#1769aa",
            "#7b1fa2",
            "#00897b"
        )

        if str(color).lower() in colores_oscuros:

            fg = "white"

        else:

            fg = "#222222"

        # ----------------------------------------------------
        # TAMAÑO
        # ----------------------------------------------------

        if tipo == "color":

            ancho_boton = 12

        elif tipo == "letra":

            ancho_boton = 5

        else:

            ancho_boton = 7

        boton = tk.Button(
            grid,
            text=nombre,
            font=("Arial", 11, "bold"),
            width=ancho_boton,
            height=2,
            bg=color,
            fg=fg,
            activebackground=color,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            bd=0,
            command=lambda x=nombre:
            funcion_click(
                x,
                etiqueta_imagen,
                panel_imagen,
                frase_label,
                seleccionado_label,
                estado_label,
                voz_label,
                color_principal,
                tipo
            )
        )

        fila = i // columnas
        columna = i % columnas

        boton.grid(
            row=fila,
            column=columna,
            padx=4,
            pady=4,
            sticky="ew"
        )

    # ========================================================
    # MOSTRAR IMAGEN DEL MENÚ
    # ========================================================

    def mostrar_imagen_menu():

        try:

            ancho = panel_imagen.winfo_width()
            alto = panel_imagen.winfo_height()

            if ancho < 100:
                ancho = 600

            if alto < 100:
                alto = 500

            imagen = imagen_menu.copy()

            proporcion = (
                imagen.width /
                imagen.height
            )

            ventana_prop = (
                ancho /
                alto
            )

            if proporcion > ventana_prop:

                nuevo_ancho = ancho - 30

                nuevo_alto = int(
                    nuevo_ancho /
                    proporcion
                )

            else:

                nuevo_alto = alto - 30

                nuevo_ancho = int(
                    nuevo_alto *
                    proporcion
                )

            imagen = imagen.resize(
                (
                    max(100, nuevo_ancho),
                    max(100, nuevo_alto)
                ),
                Image.Resampling.LANCZOS
            )

            foto = ImageTk.PhotoImage(
                imagen
            )

            etiqueta_imagen.configure(
                image=foto
            )

            etiqueta_imagen.image = foto

        except Exception as error:

            print(
                "Error imagen:",
                error
            )

    panel_imagen.bind(
        "<Configure>",
        lambda e:
        mostrar_imagen_menu()
    )

    ventana.after(
        100,
        mostrar_imagen_menu
    )


# ============================================================
# NÚMEROS
# ============================================================

def mostrar_numeros():

    crear_panel_interactivo(
        "🔢 APRENDAMOS LOS NÚMEROS",
        "Elige un número",
        imagen_menu_numeros(),
        COLOR_NUMEROS,
        list(NUMEROS.keys()),
        seleccionar_numero,
        "numero"
    )


def seleccionar_numero(
    numero,
    etiqueta_imagen,
    panel_imagen,
    frase_label,
    seleccionado_label,
    estado_label,
    voz_label,
    color_principal,
    tipo
):

    datos = NUMEROS[numero]

    nombre = datos[0]
    frase = datos[1]
    simbolo = datos[2]
    archivo_imagen = datos[3] if len(datos) > 3 else None

    # --------------------------------------------------------
    # IMAGEN
    # --------------------------------------------------------

    imagen = crear_imagen_ilustrativa(
        "NÚMERO " + numero,
        nombre.upper(),
        simbolo,
        COLOR_NUMEROS,
        archivo_imagen
    )

    mostrar_imagen_seleccionada(
        imagen,
        etiqueta_imagen,
        panel_imagen,
        COLOR_NUMEROS
    )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    seleccionado_label.config(
        text=numero,
        fg=COLOR_NUMEROS
    )

    frase_label.config(
        text=frase
    )

    estado_label.config(
        text=
        "✨ ¡MUY BIEN! SELECCIONASTE EL "
        + nombre.upper()
    )

    voz_label.config(
        text="🔊 RUNNY ESTÁ PREPARANDO LA FRASE..."
    )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    texto = (
        "Seleccionaste el número "
        + nombre
        + ". "
        + frase
    )

    reproducir_audio(
        texto,
        voz_label
    )


# ============================================================
# COLORES
# ============================================================

def mostrar_colores():

    botones = [
        (
            nombre,
            datos[0]
        )
        for nombre, datos in COLORES.items()
    ]

    crear_panel_interactivo(
        "🎨 DESCUBRAMOS LOS COLORES",
        "Elige un color",
        imagen_menu_colores(),
        COLOR_COLORES,
        botones,
        seleccionar_color,
        "color"
    )


def seleccionar_color(
    color,
    etiqueta_imagen,
    panel_imagen,
    frase_label,
    seleccionado_label,
    estado_label,
    voz_label,
    color_principal,
    tipo
):

    datos = COLORES[color]

    codigo = datos[0]
    frase = datos[1]
    simbolo = datos[2]
    archivo_imagen = datos[3] if len(datos) > 3 else None

    # --------------------------------------------------------
    # IMAGEN
    # --------------------------------------------------------

    imagen = crear_imagen_ilustrativa(
        color,
        "¡UN COLOR MUY BONITO!",
        simbolo,
        codigo,
        archivo_imagen
    )

    mostrar_imagen_seleccionada(
        imagen,
        etiqueta_imagen,
        panel_imagen,
        codigo
    )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    seleccionado_label.config(
        text=color,
        fg=(
            codigo
            if color != "BLANCO"
            else "#333333"
        )
    )

    frase_label.config(
        text=frase
    )

    estado_label.config(
        text=
        "🌈 ¡EXCELENTE! APRENDISTE EL COLOR "
        + color
    )

    voz_label.config(
        text="🔊 RUNNY ESTÁ PREPARANDO LA FRASE..."
    )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    texto = (
        "Seleccionaste el color "
        + color.lower()
        + ". "
        + frase
    )

    reproducir_audio(
        texto,
        voz_label
    )


# ============================================================
# ABECEDARIO
# ============================================================

def mostrar_abecedario():

    crear_panel_interactivo(
        "🔤 APRENDAMOS EL ABECEDARIO",
        "Elige una letra",
        imagen_menu_abecedario(),
        COLOR_LETRAS,
        list(LETRAS.keys()),
        seleccionar_letra,
        "letra"
    )


def seleccionar_letra(
    letra,
    etiqueta_imagen,
    panel_imagen,
    frase_label,
    seleccionado_label,
    estado_label,
    voz_label,
    color_principal,
    tipo
):

    datos = LETRAS[letra]

    palabra = datos[0]
    frase = datos[1]
    simbolo = datos[2]
    archivo_imagen = datos[3] if len(datos) > 3 else None

    # --------------------------------------------------------
    # IMAGEN
    # --------------------------------------------------------

    imagen = crear_imagen_ilustrativa(
        letra,
        palabra.upper(),
        simbolo,
        COLOR_LETRAS,
        archivo_imagen
    )

    mostrar_imagen_seleccionada(
        imagen,
        etiqueta_imagen,
        panel_imagen,
        COLOR_LETRAS
    )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    seleccionado_label.config(
        text=letra,
        fg=COLOR_LETRAS
    )

    frase_label.config(
        text=frase
    )

    estado_label.config(
        text=
        "⭐ ¡MUY BIEN! "
        + letra
        + " DE "
        + palabra.upper()
    )

    voz_label.config(
        text="🔊 RUNNY ESTÁ PREPARANDO LA FRASE..."
    )

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    texto = (
        "Seleccionaste la letra "
        + letra
        + ". "
        + frase
    )

    reproducir_audio(
        texto,
        voz_label
    )


# ============================================================
# MENÚ INTERACCIÓN
# ============================================================

def mostrar_interaccion():

    limpiar_contenido()

    reproducir_audio(
        "Bienvenidos a todos los niños y niñas que van a aprender conmigo jugando. Conoceremos números, colores y abecedario. Selecciona el que desees empezar a aprender."
    )

    contenedor = tk.Frame(
        contenido,
        bg="#eef5ff"
    )

    contenedor.pack(
        fill="both",
        expand=True
    )

    tk.Label(
        contenedor,
        text="🎮 ¡VAMOS A APRENDER JUGANDO!",
        font=("Arial", 30, "bold"),
        fg="#17232d",
        bg="#eef5ff"
    ).pack(
        pady=(30, 5)
    )

    tk.Label(
        contenedor,
        text="Selecciona una actividad",
        font=("Arial", 15),
        fg="#555555",
        bg="#eef5ff"
    ).pack(
        pady=5
    )

    tarjetas = tk.Frame(
        contenedor,
        bg="#eef5ff"
    )

    tarjetas.pack(
        expand=True
    )

    # ========================================================
    # TARJETA NÚMEROS
    # ========================================================

    tarjeta_numeros = tk.Frame(
        tarjetas,
        bg=COLOR_NUMEROS,
        width=270,
        height=300
    )

    tarjeta_numeros.grid(
        row=0,
        column=0,
        padx=15,
        pady=15
    )

    tarjeta_numeros.pack_propagate(
        False
    )

    tk.Label(
        tarjeta_numeros,
        text="123",
        font=("Arial", 50, "bold"),
        bg=COLOR_NUMEROS,
        fg="white"
    ).pack(
        pady=(25, 5)
    )

    tk.Label(
        tarjeta_numeros,
        text="NÚMEROS",
        font=("Arial", 21, "bold"),
        bg=COLOR_NUMEROS,
        fg="white"
    ).pack()

    tk.Label(
        tarjeta_numeros,
        text="0  1  2  3  4  5  6  7  8  9",
        font=("Arial", 11, "bold"),
        bg=COLOR_NUMEROS,
        fg="white"
    ).pack(
        pady=8
    )

    tk.Button(
        tarjeta_numeros,
        text="¡APRENDER!",
        font=("Arial", 12, "bold"),
        bg="white",
        fg=COLOR_NUMEROS,
        relief="flat",
        cursor="hand2",
        command=mostrar_numeros
    ).pack(
        pady=15
    )

    # ========================================================
    # TARJETA COLORES
    # ========================================================

    tarjeta_colores = tk.Frame(
        tarjetas,
        bg=COLOR_COLORES,
        width=270,
        height=300
    )

    tarjeta_colores.grid(
        row=0,
        column=1,
        padx=15,
        pady=15
    )

    tarjeta_colores.pack_propagate(
        False
    )

    tk.Label(
        tarjeta_colores,
        text="● ● ●",
        font=("Arial", 38, "bold"),
        bg=COLOR_COLORES,
        fg="white"
    ).pack(
        pady=(30, 5)
    )

    tk.Label(
        tarjeta_colores,
        text="COLORES",
        font=("Arial", 21, "bold"),
        bg=COLOR_COLORES,
        fg="white"
    ).pack()

    tk.Label(
        tarjeta_colores,
        text="Rojo • Azul • Verde • Amarillo",
        font=("Arial", 10, "bold"),
        bg=COLOR_COLORES,
        fg="white"
    ).pack(
        pady=8
    )

    tk.Button(
        tarjeta_colores,
        text="¡DESCUBRIR!",
        font=("Arial", 12, "bold"),
        bg="white",
        fg=COLOR_COLORES,
        relief="flat",
        cursor="hand2",
        command=mostrar_colores
    ).pack(
        pady=15
    )

    # ========================================================
    # TARJETA ABECEDARIO
    # ========================================================

    tarjeta_letras = tk.Frame(
        tarjetas,
        bg=COLOR_LETRAS,
        width=270,
        height=300
    )

    tarjeta_letras.grid(
        row=0,
        column=2,
        padx=15,
        pady=15
    )

    tarjeta_letras.pack_propagate(
        False
    )

    tk.Label(
        tarjeta_letras,
        text="ABC",
        font=("Arial", 48, "bold"),
        bg=COLOR_LETRAS,
        fg="white"
    ).pack(
        pady=(25, 5)
    )

    tk.Label(
        tarjeta_letras,
        text="ABECEDARIO",
        font=("Arial", 19, "bold"),
        bg=COLOR_LETRAS,
        fg="white"
    ).pack()

    tk.Label(
        tarjeta_letras,
        text="A • B • C • D • E • F...",
        font=("Arial", 11, "bold"),
        bg=COLOR_LETRAS,
        fg="white"
    ).pack(
        pady=8
    )

    tk.Button(
        tarjeta_letras,
        text="¡APRENDER!",
        font=("Arial", 12, "bold"),
        bg="white",
        fg=COLOR_LETRAS,
        relief="flat",
        cursor="hand2",
        command=mostrar_abecedario
    ).pack(
        pady=15
    )


# ============================================================
# MENU LATERAL
# ============================================================

menu_lateral = tk.Frame(
    ventana,
    bg="#081018",
    width=220
)

menu_lateral.pack(
    side="left",
    fill="y"
)

menu_lateral.pack_propagate(
    False
)


tk.Label(
    menu_lateral,
    text="RUNNY",
    font=("Arial", 25, "bold"),
    fg=GREEN,
    bg="#081018"
).pack(
    pady=(30, 5)
)


tk.Label(
    menu_lateral,
    text="CONTROL",
    font=("Arial", 12, "bold"),
    fg=WHITE,
    bg="#081018"
).pack(
    pady=(0, 25)
)


def boton_lateral(
    texto,
    comando
):

    return tk.Button(
        menu_lateral,
        text=texto,
        command=comando,
        font=("Arial", 12, "bold"),
        bg="#13202a",
        fg=WHITE,
        activebackground=BLUE,
        activeforeground=WHITE,
        relief="flat",
        height=2,
        cursor="hand2"
    )


boton_lateral(
    "INICIO",
    mostrar_inicio
).pack(
    fill="x",
    padx=15,
    pady=6
)


boton_lateral(
    "CONTROL DEL ROBOT",
    mostrar_robot
).pack(
    fill="x",
    padx=15,
    pady=6
)


boton_lateral(
    "INTERACCIÓN",
    mostrar_interaccion
).pack(
    fill="x",
    padx=15,
    pady=6
)


tk.Label(
    menu_lateral,
    text="",
    bg="#081018"
).pack(
    expand=True
)


tk.Label(
    menu_lateral,
    text=
    "RUNNY\n"
    "ESP32\n"
    "CONTROL ROBÓTICO",
    font=("Arial", 9),
    fg="#777777",
    bg="#081018",
    justify="center"
).pack(
    pady=20
)


# ============================================================
# CONTENIDO
# ============================================================

contenido = tk.Frame(
    ventana,
    bg=PANEL2
)

contenido.pack(
    side="right",
    fill="both",
    expand=True
)


# ============================================================
# MOSTRAR INICIO
# ============================================================

mostrar_inicio()


# ============================================================
# PREPARAR AUDIOS EN SEGUNDO PLANO
# ============================================================

threading.Thread(
    target=precargar_audios,
    daemon=True
).start()


# ============================================================
# SALUDO INICIAL
# ============================================================

ventana.after(
    2000,
    saludo_inicial
)


# ============================================================
# ACTUALIZAR ESTADO DE VOZ
# ============================================================

def comprobar_audio():

    try:

        if pygame.mixer.music.get_busy():

            # No hacemos nada; la etiqueta concreta
            # ya indica que Runny está hablando.

            pass

    except Exception:
        pass

    ventana.after(
        300,
        comprobar_audio
    )


ventana.after(
    500,
    comprobar_audio
)


# ============================================================
# INICIAR
# ============================================================

ventana.mainloop()
