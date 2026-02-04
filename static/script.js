const API = window.location.origin;

// ---------------- PROTECCIÓN DE RUTAS ----------------
// Corregido: Ahora busca las rutas de Flask (/examen y /admin_panel) en lugar de archivos .html
if (
    (window.location.pathname === "/admin_panel" || 
     window.location.pathname === "/examen") && 
    !localStorage.getItem("token")
) {
    window.location.href = "/";
}

// ---------------- LOGIN ----------------
function cambiarRol() {
    const rol = document.querySelector("input[name=rol]:checked").value;
    const pass = document.getElementById("password");

    if (rol === "admin") {
        pass.type = "password";
        pass.placeholder = "Contraseña administrador";
    } else {
        pass.type = "date";
        pass.placeholder = "";
    }
}

async function login() {
    const dni = document.getElementById("dni").value;
    const password = document.getElementById("password").value;

    if (!dni || !password) {
        alert("Complete todos los campos");
        return;
    }

    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dni, password })
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.mensaje || "Credenciales incorrectas");
        return;
    }

    // 🔐 GUARDAR SESIÓN
    localStorage.setItem("token", data.token);
    localStorage.setItem("carrera", data.carrera);

    // 🔁 REDIRECCIÓN SEGÚN ROL (Corregido a rutas de Flask)
    if (data.carrera === "ADMIN") {
        window.location.href = "/admin_panel";
    } else {
        window.location.href = "/examen";
    }
}


// ---------------- EXAMEN ----------------
let totalPreguntas = 0;
let respondidas = 0;
let respondidasSet = new Set();
let examenIniciado = false;
let intervaloTiempo = null;
const TIEMPO_EXAMEN = 45 * 60;



async function cargarExamen() {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API}/examen_auto`, {
        headers: { Authorization: `Bearer ${token}` }
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.mensaje);
        return;
    }

    totalPreguntas = data.total;
    respondidas = 0;
    respondidasSet.clear();

    actualizarProgreso(0, totalPreguntas);
    mostrarPreguntas(data.preguntas);

    // ❌ NO iniciar temporizador aquí
    // iniciarTemporizador(45 * 60);

    // Bloquear preguntas hasta empezar
    document.querySelectorAll("input[type=radio]").forEach(r => r.disabled = true);
}


function empezarExamen() {
    Swal.fire({
        title: "Examen de conocimientos",
        html: `
            <p>El examen tiene una duración de <b>45 minutos</b>.</p>
            <p>Una vez iniciado, el tiempo comenzará a correr.</p>
            <p><b>No podrás pausar el examen.</b></p>
        `,
        icon: "info",
        confirmButtonText: "Empezar examen",
        allowOutsideClick: false
    }).then(() => {
        examenIniciado = true;

        document.querySelectorAll("input[type=radio]").forEach(r => r.disabled = false);

        document.getElementById("btnEmpezar").style.display = "none";
        document.getElementById("btnEnviar").style.display = "block";

        iniciarTemporizador(TIEMPO_EXAMEN);
    });
}


function iniciarTemporizador(segundos) {
    const timer = document.getElementById("timer");
    if (!timer) return;

    // Evitar doble intervalo
    if (intervaloTiempo) clearInterval(intervaloTiempo);

    let avisoMostrado = false;

    intervaloTiempo = setInterval(() => {
        let min = Math.floor(segundos / 60);
        let seg = segundos % 60;

        timer.innerText =
            `${min.toString().padStart(2, '0')}:${seg.toString().padStart(2, '0')}`;

        if (segundos === 180 && !avisoMostrado) {
            avisoMostrado = true;
            Swal.fire({
                icon: "warning",
                title: "¡Atención!",
                text: "Faltan 3 minutos para terminar el examen",
                confirmButtonText: "Entendido"
            });
        }

        if (segundos <= 0) {
            clearInterval(intervaloTiempo);
            enviarExamen();
        }
        segundos--;
    }, 1000);
}


// ---------------- PROGRESO ----------------
function actualizarProgreso(actual, total) {
    const barra = document.getElementById("barraProgreso");
    if(barra) {
        const porcentaje = Math.round((actual / total) * 100);
        barra.style.width = porcentaje + "%";
    }
}

// ---------------- PREGUNTAS ----------------
function mostrarPreguntas(preguntas) {
    const form = document.getElementById("formExamen");
    if(!form) return;
    
    form.innerHTML = "";

    preguntas.forEach((p, i) => {
        form.innerHTML += `
        <div class="card card-pregunta mb-3">
            <div class="card-body">
                <div class="pregunta"><b>${i + 1}. ${p.pregunta}</b></div>
                <div class="opciones mt-2">
                    ${crearOpcion(p.id, p.opcion_a, "A")}
                    ${crearOpcion(p.id, p.opcion_b, "B")}
                    ${crearOpcion(p.id, p.opcion_c, "C")}
                    ${crearOpcion(p.id, p.opcion_d, "D")}
                </div>
            </div>
        </div>`;
    });
}

function crearOpcion(idPregunta, texto, letra) {
    return `
    <div class="form-check">
        <input class="form-check-input" type="radio"
               name="${idPregunta}"
               id="opt_${idPregunta}_${letra}"
               value="${letra}"
               onchange="marcarRespuesta(${idPregunta})">
        <label class="form-check-label" for="opt_${idPregunta}_${letra}">
            ${letra}) ${texto}
        </label>
    </div>`;
}

function marcarRespuesta(idPregunta) {
    if (!respondidasSet.has(idPregunta)) {
        respondidasSet.add(idPregunta);
        respondidas++;
        actualizarProgreso(respondidas, totalPreguntas);
    }
}

// ---------------- TEMPORIZADOR ----------------
function iniciarTemporizador(segundos) {
    const timer = document.getElementById("timer");
    if(!timer) return;

    const intervalo = setInterval(() => {
        let min = Math.floor(segundos / 60);
        let seg = segundos % 60;

        timer.innerText =
            `${min.toString().padStart(2, '0')}:${seg.toString().padStart(2, '0')}`;

        if (segundos <= 0) {
            clearInterval(intervalo);
            enviarExamen();
        }
        segundos--;
    }, 1000);
}

// ---------------- ENVIAR EXAMEN ----------------
function enviarExamen() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Sesión no válida");
        return;
    }

    const respuestas = [];

    document.querySelectorAll("input[type=radio]:checked").forEach(r => {
        respuestas.push({
            id_pregunta: r.name,
            respuesta: r.value
        });
    });

    if (respuestas.length < totalPreguntas) {
        alert("Debes responder todas las preguntas");
        return;
    }

    fetch(`${API}/enviar_examen`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ respuestas })
    })
    .then(res => res.json())
    .then(data => {
        if (data.nota !== undefined) {
            alert(`🎓 Examen enviado\nPuntaje: ${data.puntaje}/${data.total}\nNota final: ${data.nota}`);
            localStorage.removeItem("token");
            window.location.href = "/";
        } else {
            alert(data.mensaje || "Error desconocido");
        }
    })
    .catch(err => {
        console.error(err);
        alert("No se pudo enviar el examen");
    });
}

// ---------------- LOGOUT ----------------
function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

// ---------------- AUTOLOAD (Corregido para Flask) ----------------
// Se ejecuta cargarExamen() solo si la URL es la del examen
if (window.location.pathname === "/examen") {
    document.addEventListener("DOMContentLoaded", cargarExamen);
}