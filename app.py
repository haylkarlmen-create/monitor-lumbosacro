# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 22:24:43 2026

@author: Usuario
"""

from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Monitor Lumbosacro</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #081522;
    color: #eaf6ff;
}

header {
    padding: 26px;
    text-align: center;
    background: linear-gradient(120deg, #10283e, #164965);
    border-bottom: 3px solid #00c8ff;
}

h1 {
    color: #67e8f9;
    margin: 0;
    font-size: 29px;
}

h2 {
    color: #9ddfff;
    font-size: 21px;
}

.subtitulo {
    color: #c3d9e8;
    margin-top: 10px;
}

.contenedor {
    max-width: 1250px;
    margin: auto;
    padding: 22px;
}

.panel {
    background: #142b40;
    border: 1px solid #30516a;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 22px;
}

.tarjetas {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.tarjeta {
    background: #1b3b55;
    padding: 22px;
    border-radius: 14px;
    text-align: center;
}

.numero {
    font-size: 46px;
    font-weight: bold;
    margin: 15px 0;
}

.barra {
    height: 15px;
    background: #071522;
    border-radius: 12px;
    overflow: hidden;
}

.progreso {
    height: 100%;
    width: 0%;
    transition: width 0.3s;
}

.estado {
    margin-top: 12px;
    font-weight: bold;
}

.fila {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.control {
    background: #1b3b55;
    padding: 17px;
    border-radius: 12px;
    margin-bottom: 15px;
}

.control label {
    display: block;
    margin-bottom: 12px;
    font-weight: bold;
}

input[type=range] {
    width: 100%;
    cursor: pointer;
    accent-color: #00c8ff;
}

.mapa {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    padding: 35px 10px;
    background: #091b2b;
    border-radius: 14px;
}

.zona {
    width: 95px;
    height: 125px;
    border-radius: 40px;
    background: #22c55e;
    color: #061522;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    text-align: center;
    transition: background 0.3s;
}

.central {
    height: 150px;
}

canvas {
    width: 100%;
    height: 260px;
    background: #091b2b;
    border-radius: 12px;
}

.alerta {
    background: #123d35;
    border: 2px solid #22c55e;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

.alerta.activa {
    background: #711c30;
    border-color: #fb7185;
    animation: parpadeo 1s infinite;
}

@keyframes parpadeo {
    50% { opacity: 0.65; }
}

button {
    background: #00b8e6;
    color: #061522;
    padding: 12px 18px;
    border: none;
    border-radius: 9px;
    font-weight: bold;
    cursor: pointer;
    margin: 5px;
}

button:hover {
    background: #67e8f9;
}

.registro {
    background: #091b2b;
    padding: 15px;
    border-radius: 10px;
    height: 160px;
    overflow-y: auto;
    font-size: 14px;
    color: #c1d9e8;
}

.verde { color: #4ade80; }
.amarillo { color: #facc15; }
.rojo { color: #fb7185; }

footer {
    text-align: center;
    color: #91a9bb;
    padding: 20px;
}

@media(max-width: 750px) {
    .tarjetas, .fila {
        grid-template-columns: 1fr;
    }

    h1 { font-size: 23px; }
}
</style>
</head>

<body>

<header>
    <h1>SISTEMA DE MONITOREO LUMBOSACRO</h1>
    <p class="subtitulo">
        Proyecto Integrador - Ingenieria Biomedica
    </p>
    <p class="verde">● SISTEMA ACTIVO - MODO SIMULACION</p>
</header>

<div class="contenedor">

<section class="panel">
    <h2>Monitoreo de sensores FSR402</h2>

    <div class="tarjetas">

        <div class="tarjeta">
            <h3>Sensor 1 - Izquierdo</h3>
            <div class="numero" id="valor0">20%</div>
            <div class="barra">
                <div class="progreso" id="barra0"></div>
            </div>
            <div class="estado" id="estado0">BAJO</div>
        </div>

        <div class="tarjeta">
            <h3>Sensor 2 - Central</h3>
            <div class="numero" id="valor1">30%</div>
            <div class="barra">
                <div class="progreso" id="barra1"></div>
            </div>
            <div class="estado" id="estado1">BAJO</div>
        </div>

        <div class="tarjeta">
            <h3>Sensor 3 - Derecho</h3>
            <div class="numero" id="valor2">20%</div>
            <div class="barra">
                <div class="progreso" id="barra2"></div>
            </div>
            <div class="estado" id="estado2">BAJO</div>
        </div>

    </div>
</section>

<section class="panel">
    <h2>Control manual de presiones simuladas</h2>

    <p>
        Mueve las barras para simular diferentes niveles
        de presion sobre la region lumbosacra.
    </p>

    <div class="control">
        <label>Sensor izquierdo:
            <span id="controlValor0">20%</span>
        </label>
        <input type="range" min="0" max="100"
               value="20" id="slider0">
    </div>

    <div class="control">
        <label>Sensor central:
            <span id="controlValor1">30%</span>
        </label>
        <input type="range" min="0" max="100"
               value="30" id="slider1">
    </div>

    <div class="control">
        <label>Sensor derecho:
            <span id="controlValor2">20%</span>
        </label>
        <input type="range" min="0" max="100"
               value="20" id="slider2">
    </div>

    <button onclick="restablecer()">
        Restablecer presiones
    </button>
</section>

<div class="fila">

<section class="panel">
    <h2>Mapa de distribucion de presion</h2>

    <div class="mapa">
        <div class="zona" id="zona0">IZQ.</div>
        <div class="zona central" id="zona1">CENTRO</div>
        <div class="zona" id="zona2">DER.</div>
    </div>

    <p class="verde">● Verde: presion baja</p>
    <p class="amarillo">● Amarillo: presion media</p>
    <p class="rojo">● Rojo: presion alta</p>
</section>

<section class="panel">
    <h2>Estado del sistema</h2>

    <p>Modo: <strong>SIMULACION MANUAL</strong></p>
    <p>Tiempo de monitoreo:
        <strong id="tiempo">0 s</strong>
    </p>
    <p>Presion maxima:
        <strong id="maximo">0%</strong>
    </p>
    <p>Frecuencia: 1 lectura por segundo</p>

    <button onclick="activarSonido()">
        Activar sonido
    </button>

    <button onclick="silenciar()">
        Silenciar alarma
    </button>

    <p id="estadoSonido">Sonido desactivado</p>
</section>

</div>

<section class="panel">
    <h2>Grafica de monitoreo en tiempo real</h2>
    <canvas id="grafica" width="900" height="260"></canvas>

    <p>
        <span class="verde">● Sensor izquierdo</span> |
        <span class="amarillo">● Sensor central</span> |
        <span class="rojo">● Sensor derecho</span>
    </p>
</section>

<section class="panel">
    <h2>Sistema de alarmas</h2>

    <div class="alerta" id="alerta">
        MONITOREO NORMAL
    </div>

    <p>
        La alarma se activa si un sensor permanece
        en 70% o mas durante 10 segundos consecutivos.
    </p>

    <p id="contadorAlarma">
        Tiempo de presion alta: 0 segundos
    </p>
</section>

<section class="panel">
    <h2>Registro de eventos</h2>

    <div class="registro" id="registro">
        Sistema iniciado en modo simulacion.
    </div>
</section>

</div>

<footer>
    Prototipo academico - Valores simulados
    - No apto para diagnostico clinico
</footer>

<script>

// Valores iniciales
let presiones = [20, 30, 20];

// Historial de cada sensor
let historiales = [[], [], []];

// Segundos consecutivos en presion alta
let contadores = [0, 0, 0];

let tiempo = 0;
let alarmaActiva = false;
let sonidoHabilitado = false;
let silenciada = false;
let audioCtx = null;

const canvas = document.getElementById("grafica");
const ctx = canvas.getContext("2d");

const coloresGrafica = [
    "#4ade80",
    "#facc15",
    "#fb7185"
];

// Configurar controles deslizantes
for (let i = 0; i < 3; i++) {
    document.getElementById("slider" + i)
        .addEventListener("input", function() {

        presiones[i] = Number(this.value);

        document.getElementById(
            "controlValor" + i
        ).textContent = this.value + "%";

        actualizarPantalla();
    });
}

function clasificar(valor) {
    if (valor >= 70) {
        return ["ALTO", "#fb7185"];
    }

    if (valor >= 40) {
        return ["MEDIO", "#facc15"];
    }

    return ["BAJO", "#22c55e"];
}

function registrar(mensaje) {
    const registro = document.getElementById("registro");
    const linea = document.createElement("div");
    const hora = new Date().toLocaleTimeString();

    linea.textContent = hora + " - " + mensaje;
    registro.prepend(linea);

    while (registro.children.length > 40) {
        registro.lastElementChild.remove();
    }
}

function actualizarPantalla() {
    presiones.forEach((valor, i) => {
        const [estado, color] = clasificar(valor);

        const numero = document.getElementById("valor" + i);
        numero.textContent = valor + "%";
        numero.style.color = color;

        const barra = document.getElementById("barra" + i);
        barra.style.width = valor + "%";
        barra.style.background = color;

        const texto = document.getElementById("estado" + i);
        texto.textContent = estado;
        texto.style.color = color;

        document.getElementById(
            "zona" + i
        ).style.background = color;
    });

    document.getElementById("maximo").textContent =
        Math.max(...presiones) + "%";
}

function activarSonido() {
    try {
        audioCtx = audioCtx || new (
            window.AudioContext || window.webkitAudioContext
        )();

        audioCtx.resume();
        sonidoHabilitado = true;
        silenciada = false;

        document.getElementById("estadoSonido")
            .textContent = "Sonido activado";

        registrar("Sonido de alarma activado");

        // Pitido de prueba
        beep();

    } catch(error) {
        registrar("Error al activar sonido");
    }
}

function silenciar() {
    silenciada = true;

    document.getElementById("estadoSonido")
        .textContent = "Alarma silenciada";

    registrar("Alarma silenciada");
}

function beep() {
    if (!sonidoHabilitado || silenciada || !audioCtx) {
        return;
    }

    const oscilador = audioCtx.createOscillator();
    const volumen = audioCtx.createGain();

    oscilador.type = "sine";
    oscilador.frequency.value = 850;

    volumen.gain.value = 0.12;

    oscilador.connect(volumen);
    volumen.connect(audioCtx.destination);

    oscilador.start();
    oscilador.stop(audioCtx.currentTime + 0.25);
}

function restablecer() {
    presiones = [20, 30, 20];
    contadores = [0, 0, 0];
    alarmaActiva = false;
    silenciada = false;

    for (let i = 0; i < 3; i++) {
        document.getElementById(
            "slider" + i
        ).value = presiones[i];

        document.getElementById(
            "controlValor" + i
        ).textContent = presiones[i] + "%";
    }

    actualizarPantalla();
    actualizarAlarma();
    registrar("Presiones restablecidas");
}

function dibujarGrafica() {
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    // Cuadricula
    ctx.strokeStyle = "#29465e";
    ctx.lineWidth = 1;

    for (let i = 0; i <= 4; i++) {
        const y = 15 + i * (h - 30) / 4;

        ctx.beginPath();
        ctx.moveTo(38, y);
        ctx.lineTo(w - 10, y);
        ctx.stroke();

        ctx.fillStyle = "#b8d0e0";
        ctx.font = "12px Arial";

        ctx.fillText(
            (100 - i * 25) + "%",
            2,
            y + 4
        );
    }

    historiales.forEach((datos, sensor) => {
        ctx.beginPath();
        ctx.strokeStyle = coloresGrafica[sensor];
        ctx.lineWidth = 3;

        datos.forEach((valor, i) => {
            const x = 38 + i * (w - 50) / 59;
            const y = 15 + (100 - valor) *
                      (h - 30) / 100;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
    });
}

function actualizarAlarma() {
    const alerta = document.getElementById("alerta");

    const sensoresEnAlarma = contadores
        .map((contador, i) => contador >= 10 ? i + 1 : null)
        .filter(x => x !== null);

    const nuevaAlarma = sensoresEnAlarma.length > 0;

    if (nuevaAlarma) {
        alerta.textContent =
            "ALERTA: PRESION SOSTENIDA - SENSOR " +
            sensoresEnAlarma.join(", ");

        alerta.classList.add("activa");

        if (!alarmaActiva) {
            registrar(
                "Alerta de presion sostenida en sensor " +
                sensoresEnAlarma.join(", ")
            );
        }

    } else {
        alerta.textContent = "MONITOREO NORMAL";
        alerta.classList.remove("activa");
    }

    alarmaActiva = nuevaAlarma;

    document.getElementById("contadorAlarma")
        .textContent =
        "Tiempo de presion alta: " +
        Math.max(...contadores) + " segundos";
}

function cicloMonitoreo() {
    tiempo++;

    document.getElementById("tiempo")
        .textContent = tiempo + " s";

    presiones.forEach((valor, i) => {
        historiales[i].push(valor);

        if (historiales[i].length > 60) {
            historiales[i].shift();
        }

        if (valor >= 70) {
            contadores[i]++;
        } else {
            contadores[i] = 0;
        }
    });

    dibujarGrafica();
    actualizarAlarma();

    if (alarmaActiva) {
        // Pitido repetido cada 2 segundos
        if (tiempo % 2 === 0) {
            beep();
        }
    }
}

// Inicializar
actualizarPantalla();
dibujarGrafica();

// Una actualizacion por segundo
setInterval(cicloMonitoreo, 1000);

</script>

</body>
</html>
"""

@app.route("/")
def inicio():
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )
