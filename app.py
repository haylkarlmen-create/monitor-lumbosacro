# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 22:24:43 2026

@author: Usuario
"""

from flask import Flask, request, jsonify, render_template_string
import os
import time
import threading
import math
import hmac

app = Flask(__name__)

# ==========================================
# CONFIGURACION DEL SERVIDOR
# ==========================================

TOKEN = os.environ.get("MONITOR_TOKEN", "")

lock = threading.Lock()

latest = {
    "sensores": [],
    "ultima": 0,
    "secuencia": 0
}

# ==========================================
# RECIBIR DATOS REALES DE LA ESP32
# ==========================================

@app.route("/api/datos", methods=["POST"])
def recibir():

    if not TOKEN or not hmac.compare_digest(
        request.headers.get("X-Token", ""), TOKEN
    ):
        return jsonify(error="No autorizado"), 401

    body = request.get_json(silent=True)

    rows = body.get("sensores") if isinstance(
        body, dict
    ) else None

    if not isinstance(rows, list) or len(rows) != 4:
        return jsonify(
            error="Se requieren cuatro sensores"
        ), 400

    try:
        clean = []

        for i, s in enumerate(rows):

            if not isinstance(s, dict):
                raise ValueError()

            if s["sensor"] != i + 1:
                raise ValueError()

            nivel = float(s["nivel"])
            resistencia = s["resistencia"]
            adc = int(s["adc"])

            permanencia = int(s["permanencia"])
            tiempo_alto = int(s["tiempo_alto"])

            if not math.isfinite(nivel):
                raise ValueError()

            if not 0 <= nivel <= 100:
                raise ValueError()

            if not 0 <= adc <= 4095:
                raise ValueError()

            if min(permanencia, tiempo_alto) < 0:
                raise ValueError()

            if resistencia is not None:

                resistencia = float(resistencia)

                if not math.isfinite(resistencia):
                    raise ValueError()

                if resistencia < 0:
                    raise ValueError()

            estado = s["estado"]
            alarma = s["alarma"]

            if estado not in (
                "NORMAL", "PREVENTIVO", "RIESGO"
            ):
                raise ValueError()

            if type(alarma) is not bool:
                raise ValueError()

            clean.append({
                "sensor": i + 1,
                "nivel": nivel,
                "resistencia": resistencia,
                "adc": adc,
                "permanencia": permanencia,
                "tiempo_alto": tiempo_alto,
                "estado": estado,
                "alarma": alarma
            })

    except (
        KeyError, TypeError,
        ValueError, OverflowError
    ):
        return jsonify(
            error="Lecturas invalidas"
        ), 400

    with lock:

        latest.update(
            sensores=clean,
            ultima=time.time(),
            secuencia=latest["secuencia"] + 1
        )

    return jsonify(
        estado="Datos recibidos correctamente"
    )


# ==========================================
# ENVIAR DATOS A LA INTERFAZ
# ==========================================

@app.route("/api/datos", methods=["GET"])
def datos():

    with lock:
        result = dict(latest)

    result["conectado"] = (
        time.time() - result["ultima"]
    ) < 15

    response = jsonify(result)

    response.headers["Cache-Control"] = "no-store"

    return response


# ==========================================
# INTERFAZ GRAFICA
# ==========================================

HTML = """
<!DOCTYPE html>
<html lang="es">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Monitor Lumbosacro</title>

<style>

/* =====================================
   ESTILO GENERAL
===================================== */

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #eef7fb;
    color: #164e63;
    font-family: Arial, sans-serif;
}

header {
    background: linear-gradient(
        120deg, #e0f2fe, #ccfbf1
    );
    padding: 32px 20px;
    border-bottom: 1px solid #b6e4ed;
}

header > div {
    max-width: 1180px;
    margin: auto;
}

h1 {
    margin: 0;
    font-size: 36px;
    color: #155e75;
}

h2 {
    font-size: 21px;
    margin: 0 0 16px;
    color: #155e75;
}

h3 {
    font-size: 16px;
    margin: 8px 0;
}

p {
    line-height: 1.5;
}

main {
    max-width: 1180px;
    margin: auto;
    padding: 24px 16px;
}

.muted {
    color: #526c7d;
    font-size: 14px;
}

/* =====================================
   PANELES Y TARJETAS
===================================== */

.panel,
.sensor {

    background: white;
    border: 1px solid #d5e8ef;
    border-radius: 18px;
    padding: 20px;

    box-shadow:
    0 4px 16px rgba(22,78,99,0.06);
}

.panel {
    margin-bottom: 18px;
}

.cards {

    display: grid;

    grid-template-columns:
    repeat(4, minmax(0, 1fr));

    gap: 14px;
    margin-bottom: 18px;
}

.number {

    font-size: 38px;
    font-weight: bold;
    margin: 14px 0;

    color: #0891b2;
}

.bar {

    height: 9px;
    background: #e0f2fe;
    border-radius: 10px;
    overflow: hidden;
}

.fill {

    height: 100%;
    width: 0%;

    background: #14b8a6;

    transition: width 0.3s;
}

.state {

    font-size: 13px;
    font-weight: bold;
    margin-top: 14px;
}

.two {

    display: grid;

    grid-template-columns: 1fr 1fr;

    gap: 18px;
}

/* =====================================
   BOTONES
===================================== */

.controls {

    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

button {

    border: 1px solid #a5d8e4;

    background: #e6f9fb;
    color: #155e75;

    border-radius: 10px;

    padding: 12px 15px;

    font-size: 14px;
    font-weight: bold;

    cursor: pointer;

    transition: background 0.2s;
}

button:hover {
    background: #c5f2f4;
}

button:disabled {
    opacity: 0.5;
    cursor: default;
}

.status {

    display: inline-block;

    background: white;

    border-radius: 30px;

    padding: 9px 16px;

    font-weight: bold;

    margin-top: 12px;

    color: #0d9488;
}

/* =====================================
   ALARMAS
===================================== */

.alert {

    padding: 18px;

    border-radius: 12px;

    background: #edf6fa;

    border: 1px solid #c9e1eb;

    font-weight: bold;
}

.alert.high {

    background: #fff1f2;

    color: #be123c;

    border-color: #fda4af;

    animation: parpadeo 1s infinite;
}

.alert.ok {

    background: #ecfdf5;

    color: #047857;

    border-color: #99f6e4;
}

@keyframes parpadeo {

    50% {
        opacity: 0.65;
    }
}

/* =====================================
   GRAFICAS Y MAPA
===================================== */

canvas {

    width: 100%;
    height: 280px;

    display: block;
}

svg {

    width: 100%;

    max-height: 270px;

    display: block;
}

.legend {

    display: flex;

    flex-wrap: wrap;

    gap: 15px;

    font-size: 13px;

    margin-top: 12px;
}

/* =====================================
   REGISTRO DE EVENTOS
===================================== */

.log {

    max-height: 190px;

    overflow: auto;

    font-size: 14px;

    background: #f4fafc;

    border-radius: 10px;

    padding: 10px;
}

.log div {

    padding: 9px;

    border-bottom: 1px solid #e5eef3;
}

footer {

    text-align: center;

    padding: 20px;

    color: #526c7d;

    font-size: 13px;
}

/* =====================================
   ADAPTACION PARA CELULARES
===================================== */

@media(max-width: 850px) {

    .cards {

        grid-template-columns:
        repeat(2, minmax(0, 1fr));
    }

    .two {

        grid-template-columns: 1fr;
    }

    h1 {
        font-size: 28px;
    }
}

@media(max-width: 400px) {

    .sensor {
        padding: 12px;
    }

    .number {
        font-size: 30px;
    }
}

</style>

</head>

<body>

<!-- ==================================
     ENCABEZADO
=================================== -->

<header>

<div>

    <h1>Monitor Lumbosacro</h1>

    <p>
        Sistema de monitoreo biomecánico
        mediante sensores FSR402
    </p>

    <p class="muted">
        Ingeniería Biomédica |
        Proyecto Integrador |
        TESI
    </p>

    <span class="status" id="conexion">
        ● Esperando ESP32
    </span>

</div>

</header>

<main>

<!-- ==================================
     CONTROLES DEL SISTEMA
=================================== -->

<section class="panel">

    <h2>Monitoreo de cuatro sensores FSR402</h2>

    <p class="muted">
        Lecturas físicas recibidas mediante Wi-Fi.
        El porcentaje representa el nivel relativo
        de la señal del sensor, no presión clínica.
    </p>

    <div class="controls">

        <button id="start">
            Iniciar visualización
        </button>

        <button id="stop">
            Detener visualización
        </button>

        <button id="reset">
            Reiniciar gráfica y registro
        </button>

        <button id="sound">
            Activar sonido
        </button>

        <button id="mute">
            Silenciar alarma
        </button>

    </div>

    <p class="muted" id="info">
        Esperando datos reales.
    </p>

</section>

<!-- ==================================
     TARJETAS DE LOS CUATRO SENSORES
=================================== -->

<div class="cards" id="cards"></div>

<div class="two">

<!-- ==================================
     MAPA LUMBOSACRO
=================================== -->

<section class="panel">

    <h2>Distribución lumbosacra</h2>

    <p class="muted">

        Vista posterior esquemática.
        Cuatro sensores colocados horizontalmente.

    </p>

    <svg viewBox="0 0 340 230"
    role="img"
    aria-label="Espalda baja con cuatro sensores">

        <!-- Contorno de espalda -->

        <path

        d="M107 13
        Q170 0 233 13
        L267 48
        Q240 84 240 112
        L255 169
        Q266 198 248 220
        L92 220
        Q74 198 85 169
        L100 112
        Q100 84 73 48 Z"

        fill="#e0f2fe"

        stroke="#94c8dc"

        stroke-width="2"/>

        <!-- Columna vertebral -->

        <path

        d="M170 15
        Q166 70 170 112
        T170 184"

        stroke="#7db7cd"

        stroke-width="2"

        stroke-dasharray="4 5"

        fill="none"/>

        <!-- Region de monitoreo -->

        <rect

        x="86"
        y="135"

        width="168"
        height="48"

        rx="13"

        fill="#cffafe"

        stroke="#67e8f9"/>

        <!-- Sensores dinamicos -->

        <g id="zones"></g>

    </svg>

    <div class="legend">

        <span style="color:#0d9488">
            ● Normal
        </span>

        <span style="color:#b45309">
            ● Preventivo
        </span>

        <span style="color:#be123c">
            ● Riesgo
        </span>

        <span style="color:#64748b">
            ● Sin datos
        </span>

    </div>

</section>

<!-- ==================================
     ESTADO Y ALARMAS
=================================== -->

<section class="panel">

    <h2>Estado y alertas</h2>

    <div class="alert" id="alert">

        Esperando datos reales

    </div>

    <p id="max">
        Nivel máximo: —
    </p>

    <p id="duration">
        Mayor permanencia: —
    </p>

    <p id="high">
        Tiempo de nivel alto: —
    </p>

    <p class="muted">

        Condiciones experimentales:

        <br><br>

        Normal: menor a 40%.

        <br>

        Preventivo: de 40% a menos de 70%.

        <br>

        Riesgo experimental: 70% o más.

        <br><br>

        La alarma se activa después de
        10 segundos de nivel alto.

        <br>

        El tiempo de permanencia comienza
        desde un nivel de carga del 5%.

    </p>

    <p class="muted" id="audioState">

        Sonido desactivado

    </p>

</section>

</div>

<!-- ==================================
     GRAFICA EN TIEMPO REAL
=================================== -->

<section class="panel">

    <h2>Gráfica de monitoreo en tiempo real</h2>

    <p class="muted">

        Nivel relativo (%) contra tiempo (s).
        Últimas 60 muestras recibidas.

    </p>

    <canvas id="chart"></canvas>

    <div class="legend" id="legend"></div>

</section>

<!-- ==================================
     REGISTRO DE EVENTOS
=================================== -->

<section class="panel">

    <h2>Registro de eventos</h2>

    <div class="log" id="log">

        Sin eventos registrados.

    </div>

</section>

</main>

<footer>

    Prototipo académico de Ingeniería Biomédica.

    <br>

    No apto para diagnóstico clínico.
    No ingresar datos identificables de pacientes.

</footer>

<!-- ==================================
     JAVASCRIPT
=================================== -->

<script>

// Nombres de las cuatro zonas

const names = [

    "Lateral izquierdo",

    "Medial izquierdo",

    "Medial derecho",

    "Lateral derecho"

];

// Colores de las cuatro curvas

const colors = [

    "#0891b2",

    "#0d9488",

    "#e11d48",

    "#6366f1"

];

const $ = id => document.getElementById(id);

// Variables de monitoreo

let running = true;

let history = [];

let lastSeq = null;

let lastStamp = 0;

let origin = 0;

let prevStates = [];

let prevAlarm = "";

let connected = null;

let audio = null;

let muted = true;

let lastBeep = 0;

let busy = false;

let generation = 0;


// =====================================
// CREAR CUATRO TARJETAS
// =====================================

const cards = $("cards");

for (let i = 0; i < 4; i++) {

    cards.insertAdjacentHTML(

        "beforeend",

        `
        <article class="sensor">

            <div class="muted">

                SENSOR 0${i+1}

            </div>

            <h3>${names[i]}</h3>

            <div class="number" id="n${i}">

                —

            </div>

            <div class="bar">

                <div class="fill" id="b${i}">

                </div>

            </div>

            <p class="muted" id="r${i}">

                Resistencia: —

            </p>

            <p class="muted" id="adc${i}">

                ADC: —

            </p>

            <p class="muted" id="t${i}">

                Permanencia: —

            </p>

            <p class="muted" id="a${i}">

                Nivel alto: —

            </p>

            <div class="state" id="s${i}">

                SIN DATOS

            </div>

        </article>
        `
    );

    // Crear los cuatro sensores horizontales

    $("zones").insertAdjacentHTML(

        "beforeend",

        `
        <circle

            id="z${i}"

            cx="${110 + 40*i}"

            cy="159"

            r="16"

            fill="#94a3b8"

            stroke="white"

            stroke-width="2"

        />

        <text

            x="${110 + 40*i}"

            y="163"

            text-anchor="middle"

            font-size="11"

            font-weight="bold"

            fill="#164e63"

        >

            S${i+1}

        </text>
        `
    );

    // Crear leyenda de grafica

    $("legend").insertAdjacentHTML(

        "beforeend",

        `
        <span style="color:${colors[i]}">

            ● S${i+1} ${names[i]}

        </span>
        `
    );
}


// =====================================
// REGISTRO DE EVENTOS
// =====================================

function log(msg) {

    const el = document.createElement("div");

    el.textContent =

        new Date().toLocaleTimeString()

        + " — " + msg;

    if (!$("log").children.length) {

        $("log").textContent = "";
    }

    $("log").prepend(el);

    while ($("log").children.length > 40) {

        $("log").lastElementChild.remove();
    }
}


// =====================================
// COLORES SEGUN ESTADO
// =====================================

function color(estado) {

    if (estado === "RIESGO") {

        return "#e11d48";
    }

    if (estado === "PREVENTIVO") {

        return "#b45309";
    }

    return "#0d9488";
}


// =====================================
// LIMPIAR LECTURAS
// =====================================

function clearReadings(message) {

    for (let i = 0; i < 4; i++) {

        $("n"+i).textContent = "—";

        $("n"+i).style.color = "#64748b";

        $("b"+i).style.width = "0%";

        $("r"+i).textContent =

            "Resistencia: —";

        $("adc"+i).textContent =

            "ADC: —";

        $("t"+i).textContent =

            "Permanencia: —";

        $("a"+i).textContent =

            "Nivel alto: —";

        $("s"+i).textContent =

            "SIN DATOS";

        $("s"+i).style.color = "#64748b";

        $("z"+i).setAttribute(

            "fill", "#94a3b8"

        );
    }

    $("alert").className = "alert";

    $("alert").textContent = message;

    $("max").textContent =

        "Nivel máximo: —";

    $("duration").textContent =

        "Mayor permanencia: —";

    $("high").textContent =

        "Tiempo de nivel alto: —";
}


// =====================================
// ALARMA AUDIBLE
// =====================================

function beep() {

    if (

        muted ||

        !audio ||

        audio.state !== "running"

    ) {

        return;
    }

    const oscillator = audio.createOscillator();

    const gain = audio.createGain();

    oscillator.frequency.value = 850;

    gain.gain.value = 0.12;

    oscillator.connect(gain);

    gain.connect(audio.destination);

    oscillator.start();

    oscillator.stop(

        audio.currentTime + 0.25

    );
}


// =====================================
// BOTON ACTIVAR SONIDO
// =====================================

$("sound").onclick = async () => {

    try {

        audio = audio || new (

            window.AudioContext ||

            window.webkitAudioContext

        )();

        await audio.resume();

        muted = false;

        $("audioState").textContent =

            "Sonido activado";

        log("Sonido de alarma activado");

        beep();

    } catch (error) {

        $("audioState").textContent =

            "No se pudo activar el sonido";
    }
};


// =====================================
// BOTON SILENCIAR
// =====================================

$("mute").onclick = () => {

    muted = true;

    $("audioState").textContent =

        "Alarma silenciada";

    log("Alarma audible silenciada");
};


// =====================================
// BOTON DETENER
// =====================================

$("stop").onclick = () => {

    running = false;

    generation++;

    $("conexion").textContent =

        "● Visualización detenida";

    $("info").textContent =

        "La ESP32 continúa midiendo. " +

        "Solo se detuvo esta pantalla.";

    clearReadings(

        "Visualización detenida"

    );

    log("Visualización detenida");
};


// =====================================
// BOTON INICIAR
// =====================================

$("start").onclick = () => {

    if (!running) {

        running = true;

        generation++;

        connected = null;

        log("Visualización iniciada");

        poll();
    }
};


// =====================================
// BOTON REINICIAR
// =====================================

$("reset").onclick = () => {

    history = [];

    origin = 0;

    lastSeq = null;

    lastStamp = 0;

    prevStates = [];

    prevAlarm = "";

    $("log").textContent = "";

    log(

        "Gráfica y registro reiniciados. " +

        "Temporizadores de ESP32 no modificados."

    );

    draw();
};


// =====================================
// DIBUJAR GRAFICA
// =====================================

function draw() {

    const canvas = $("chart");

    const width = canvas.clientWidth;

    const height = canvas.clientHeight;

    const pixelRatio =

        window.devicePixelRatio || 1;

    if (!width || !height) {

        return;
    }

    canvas.width = width * pixelRatio;

    canvas.height = height * pixelRatio;

    const ctx = canvas.getContext("2d");

    ctx.scale(pixelRatio, pixelRatio);

    const left = 44;

    const right = width - 14;

    const top = 15;

    const bottom = height - 32;

    ctx.font = "11px Arial";

    ctx.strokeStyle = "#dceaf0";

    ctx.fillStyle = "#526c7d";

    // Eje vertical

    for (let v = 0; v <= 100; v += 25) {

        let y = bottom -

            (bottom - top) * v / 100;

        ctx.beginPath();

        ctx.moveTo(left, y);

        ctx.lineTo(right, y);

        ctx.stroke();

        ctx.fillText(

            v + "%", 3, y + 4

        );
    }

    // Eje horizontal

    const first = history.length ?

        history[0].t : 0;

    const end = history.length ?

        Math.max(

            first + 1,

            history[history.length-1].t

        ) : 60;

    for (let i = 0; i <= 4; i++) {

        let x = left +

            (right-left) * i / 4;

        ctx.fillText(

            Math.round(

                first + (end-first)*i/4

            ) + "s",

            x-8,

            height-9

        );
    }

    // Dibujar cuatro curvas

    colors.forEach((col, sensor) => {

        ctx.strokeStyle = col;

        ctx.lineWidth = 2.5;

        ctx.beginPath();

        let started = false;

        history.forEach(point => {

            if (point.v === null) {

                started = false;

                return;
            }

            let x = left +

                (right-left) *

                (point.t-first) /

                (end-first);

            let y = bottom -

                (bottom-top) *

                point.v[sensor] / 100;

            if (started) {

                ctx.lineTo(x,y);

            } else {

                ctx.moveTo(x,y);
            }

            started = true;
        });

        ctx.stroke();
    });

    // Mostrar primer punto recibido

    if (

        history.length === 1 &&

        history[0].v

    ) {

        colors.forEach((col,i) => {

            ctx.fillStyle = col;

            ctx.beginPath();

            ctx.arc(

                left,

                bottom -

                (bottom-top) *

                history[0].v[i] / 100,

                3,

                0,

                Math.PI*2

            );

            ctx.fill();
        });
    }
}


// =====================================
// DETECTAR DESCONEXION
// =====================================

function offline(message) {

    if (connected !== false) {

        log(message);

        if (history.length) {

            history.push({

                t: history[history.length-1].t + 1,

                v: null

            });

            if (history.length > 60) {

                history.shift();
            }

            draw();
        }
    }

    connected = false;

    prevStates = [];

    prevAlarm = "";

    $("conexion").textContent =

        "● ESP32 sin conexión";

    $("info").textContent = message;

    clearReadings(

        "Sin datos recientes. " +

        "No se puede evaluar la carga."

    );
}


// =====================================
// RECIBIR DATOS REALES DEL SERVIDOR
// =====================================

async function poll() {

    if (!running || busy) {

        return;
    }

    busy = true;

    const gen = generation;

    try {

        const response = await fetch(

            "/api/datos",

            {

                cache: "no-store",

                signal: AbortSignal.timeout(5000)

            }
        );

        if (!response.ok) {

            throw Error(

                "HTTP " + response.status

            );
        }

        const data = await response.json();

        if (!running || gen !== generation) {

            return;
        }

        if (

            !data.conectado ||

            data.sensores.length !== 4

        ) {

            offline(

                "Esperando mediciones recientes " +

                "de la ESP32"

            );

            return;
        }

        if (connected !== true) {

            log("ESP32 conectada");
        }

        connected = true;

        $("conexion").textContent =

            "● ESP32 conectada";

        $("info").textContent =

            "Última lectura: " +

            new Date(

                data.ultima * 1000

            ).toLocaleTimeString();

        const rows = data.sensores;


        // Actualizar las cuatro tarjetas

        rows.forEach((sensor,i) => {

            const c = color(sensor.estado);

            $("n"+i).textContent =

                sensor.nivel.toFixed(1) + "%";

            $("n"+i).style.color = c;

            $("b"+i).style.width =

                sensor.nivel + "%";

            $("b"+i).style.background = c;

            $("r"+i).textContent =

                "Resistencia: " +

                (

                    sensor.resistencia === null ?

                    "Fuera de rango" :

                    sensor.resistencia.toFixed(3)

                    + " kΩ"

                );

            $("adc"+i).textContent =

                "ADC: " + sensor.adc;

            $("t"+i).textContent =

                "Permanencia: " +

                sensor.permanencia + " s";

            $("a"+i).textContent =

                "Nivel alto: " +

                sensor.tiempo_alto + " s";

            $("s"+i).textContent =

                sensor.estado === "RIESGO" ?

                "RIESGO EXPERIMENTAL" :

                sensor.estado;

            $("s"+i).style.color = c;

            // Actualizar mapa de espalda

            $("z"+i).setAttribute(

                "fill", c

            );

            // Registrar cambio de estado

            if (

                prevStates[i] !== sensor.estado

            ) {

                log(

                    "S" + (i+1) +

                    " — " + sensor.estado

                );
            }

            prevStates[i] = sensor.estado;
        });


        // Actualizar valores maximos

        $("max").textContent =

            "Nivel máximo: " +

            Math.max(

                ...rows.map(s => s.nivel)

            ).toFixed(1) + "%";

        $("duration").textContent =

            "Mayor permanencia: " +

            Math.max(

                ...rows.map(s => s.permanencia)

            ) + " s";

        $("high").textContent =

            "Tiempo de nivel alto: " +

            Math.max(

                ...rows.map(s => s.tiempo_alto)

            ) + " s";


        // Detectar sensores en alarma

        const alarms = rows

            .filter(s => s.alarma)

            .map(s => "S" + s.sensor)

            .join(", ");

        $("alert").className =

            "alert " +

            (alarms ? "high" : "ok");

        $("alert").textContent =

            alarms ?

            "ALERTA DE CARGA SOSTENIDA — "

            + alarms :

            "Sin alarma de carga sostenida";


        // Registrar activacion de alarma

        if (alarms !== prevAlarm) {

            log(

                alarms ?

                "Alerta activada: " + alarms :

                "Alerta desactivada"

            );

            prevAlarm = alarms;
        }


        // Activar pitido cada dos segundos

        if (

            alarms &&

            Date.now()-lastBeep >= 2000

        ) {

            beep();

            lastBeep = Date.now();
        }


        // Guardar datos nuevos en grafica

        if (

            data.secuencia !== lastSeq ||

            data.ultima !== lastStamp

        ) {

            if (!origin) {

                origin = data.ultima;
            }

            history.push({

                t: Math.max(

                    0,

                    data.ultima-origin

                ),

                v: rows.map(s => s.nivel)

            });

            if (history.length > 60) {

                history.shift();
            }

            lastSeq = data.secuencia;

            lastStamp = data.ultima;

            draw();
        }

    } catch (error) {

        if (running && gen === generation) {

            offline(

                "No se pudo consultar el servidor"

            );
        }

    } finally {

        busy = false;
    }
}


// =====================================
// INICIAR INTERFAZ
// =====================================

window.addEventListener(

    "resize", draw

);

draw();

poll();

setInterval(poll, 1000);

</script>

</body>

</html>
"""


# ==========================================
# PAGINA PRINCIPAL
# ==========================================

@app.route("/")
def inicio():

    return render_template_string(HTML)


# ==========================================
# EJECUTAR FLASK EN SPYDER
# ==========================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        use_reloader=False

    )
