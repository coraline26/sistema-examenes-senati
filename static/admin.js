const API = window.location.origin;

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");

    // 🔐 Protección real: Corregido para usar la raíz "/" en lugar de index.html
    if (!token) {
        alert("Sesión expirada o acceso inválido");
        window.location.href = "/";
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

        // Aseguramos que los IDs coincidan con el HTML
        document.getElementById("total").innerText = data.total || 0;
        document.getElementById("promedio").innerText = data.promedio || 0;

        cargarTabla(data.historial);

    } catch (error) {
        console.error("Error en dashboard:", error);
        alert("Sesión expirada o acceso inválido");
        logout();
    }
}

/* ============================
   TABLA
============================ */
function cargarTabla(datos) {
    const tbody = document.getElementById("tabla");
    if (!tbody) return;
    
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
            <td><span class="badge ${d.nota >= 10.5 ? 'bg-success' : 'bg-danger'}">${d.nota}</span></td>
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
    
    // Limpiar campos tras registrar
    document.getElementById("dni").value = "";
    document.getElementById("nombres").value = "";
    document.getElementById("password").value = "";
    
    cargarDashboard(token);
}

/* ============================
   LOGOUT
============================ */
function logout() {
    localStorage.clear();
    window.location.href = "/";
}