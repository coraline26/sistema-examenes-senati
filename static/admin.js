const API = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");

    // 🔐 Protección real
    if (!token) {
        alert("Sesión expirada o acceso inválido");
        window.location.href = "index.html";
        return;
    }

    cargarDashboard(token);
});

/* ============================
   DASHBOARD
============================ */
async function cargarDashboard(token) {
    try {
        const res = await fetch(`${API}/admin/dashboard`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (res.status === 401 || res.status === 403) {
            throw new Error("Token inválido");
        }

        const data = await res.json();

        document.getElementById("total").innerText = data.total;
        document.getElementById("promedio").innerText = data.promedio;

        cargarTabla(data.historial);

    } catch (error) {
        alert("Sesión expirada o acceso inválido");
        logout();
    }
}

/* ============================
   TABLA
============================ */
function cargarTabla(datos) {
    const tbody = document.getElementById("tabla");
    tbody.innerHTML = "";

    if (!datos || datos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    No existen registros
                </td>
            </tr>`;
        return;
    }

    datos.forEach(d => {
        tbody.innerHTML += `
        <tr>
            <td>${d.dni}</td>
            <td>${d.nombres}</td>
            <td>${d.carrera}</td>
            <td>${d.puntaje}</td>
            <td>${d.nota}</td>
            <td>${d.fecha}</td>
        </tr>`;
    });
}

/* ============================
   EXPORTAR EXCEL
============================ */
async function exportar() {
    const token = localStorage.getItem("token");

    const res = await fetch(`${API}/admin/exportar_excel`, {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        alert("Error al exportar");
        return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "reporte_examenes.xlsx";
    a.click();
}

/* ============================
   CREAR ALUMNO
============================ */
async function crearAlumno() {
    const token = localStorage.getItem("token");

    const dni = document.getElementById("dni").value;
    const nombres = document.getElementById("nombres").value;
    const password = document.getElementById("password").value;
    const carrera = document.getElementById("carrera").value;

    if (!dni || !nombres || !password) {
        alert("Complete todos los campos");
        return;
    }

    const res = await fetch(`${API}/admin/alumno`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ dni, password, nombres, carrera })
    });

    const data = await res.json();
    alert(data.mensaje);
    cargarDashboard(token);
}

/* ============================
   LOGOUT
============================ */
function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}
