const API = "http://127.0.0.1:5000";

// ---------------- PROTECCIÓN DE RUTAS ----------------
if (
    (location.pathname.includes("admin.html") ||
     location.pathname.includes("examen.html")) &&
    !localStorage.getItem("token")
) {
    window.location = "index.html";
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

    // 🔁 REDIRECCIÓN SEGÚN ROL
    if (data.carrera === "ADMIN") {
        window.location.href = "admin.html";
    } else {
        window.location.href = "examen.html";
    }
}


// ---------------- EXAMEN ----------------
let totalPreguntas = 0;
let respondidas = 0;
let respondidasSet = new Set();

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

    document.getElementById("titulo").innerText =
        `Carrera: ${data.carrera} | Preguntas: ${data.total}`;

    totalPreguntas = data.total;
    respondidas = 0;
    respondidasSet.clear();

    actualizarProgreso(0, totalPreguntas);
    mostrarPreguntas(data.preguntas);
    iniciarTemporizador(20 * 60);
}

// ---------------- PROGRESO ----------------
function actualizarProgreso(actual, total) {
    const porcentaje = Math.round((actual / total) * 100);
    document.getElementById("barraProgreso").style.width = porcentaje + "%";
}

// ---------------- PREGUNTAS ----------------
function mostrarPreguntas(preguntas) {
    const form = document.getElementById("formExamen");
    form.innerHTML = "";

    preguntas.forEach((p, i) => {
        form.innerHTML += `
        <div class="card card-pregunta">
            <div class="card-body">
                <div class="pregunta">${i + 1}. ${p.pregunta}</div>
                <div class="opciones">
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
    <label>
        <input type="radio"
               name="${idPregunta}"
               value="${letra}"
               onchange="marcarRespuesta(${idPregunta})">
        ${texto}
    </label>`;
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
        Swal.fire("Error", "Sesión no válida", "error");
        return;
    }

    const respuestas = [];

    document.querySelectorAll("input[type=radio]:checked").forEach(r => {
        respuestas.push({
            id_pregunta: r.name,   // ✅ ahora es ID real
            respuesta: r.value
        });
    });

    if (respuestas.length < totalPreguntas) {
        Swal.fire("Atención", "Debes responder todas las preguntas", "warning");
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
            Swal.fire(
                "🎓 Examen enviado",
                `Puntaje: ${data.puntaje}/${data.total}<br>Nota final: <b>${data.nota}</b>`,
                "success"
            ).then(() => {
                localStorage.removeItem("token");
                window.location = "index.html";
            });
        } else {
            Swal.fire("Error", data.mensaje || "Error desconocido", "error");
        }
    })
    .catch(err => {
        console.error(err);
        Swal.fire("Error", "No se pudo enviar el examen", "error");
    });
}

// ---------------- LOGOUT ----------------
function logout() {
    localStorage.removeItem("token");
    window.location = "index.html";
}

// ---------------- AUTOLOAD ----------------
if (location.pathname.includes("examen.html")) {
    cargarExamen();
}
