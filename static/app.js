let authHeader = "";

const BASE = "http://127.0.0.1:5000";

// ---------- Registro ----------
async function registrar() {
  const usuario = document.getElementById("regUser").value;
  const contraseña = document.getElementById("regPass").value;

  try {
    const res = await fetch(BASE + "/registro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, contraseña })
    });
    const data = await res.json();
    document.getElementById("outRegistro").textContent = data.message || data.error;
  } catch (err) {
    console.error(err);
    document.getElementById("outRegistro").textContent = "Error al registrar";
  }
}

// ---------- Login ----------
async function login() {
  const usuario = document.getElementById("loginUser").value;
  const contraseña = document.getElementById("loginPass").value;

  try {
    const res = await fetch(BASE + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, contraseña })
    });
    const data = await res.json();
    if (res.ok) {
      authHeader = "Basic " + btoa(usuario + ":" + contraseña);
    }
    document.getElementById("outLogin").textContent = data.message || data.error;
  } catch (err) {
    console.error(err);
    document.getElementById("outLogin").textContent = "Error al iniciar sesión";
  }
}

// ---------- Listar tareas ----------
async function tareas() {
  if (!authHeader) {
    alert("Primero iniciá sesión");
    return;
  }

  try {
    const res = await fetch(BASE + "/tareas", {
      method: "GET",
      headers: { "Authorization": authHeader }
    });
    const tareas = await res.json();

    let html = "<table border='1'><tr><th>ID</th><th>Título</th><th>Descripción</th><th>Acciones</th></tr>";
    tareas.forEach(t => {
      html += `<tr>
                 <td>${t.id}</td>
                 <td>${t.titulo}</td>
                 <td>${t.descripcion}</td>
                 <td>
                    <button onclick="editarTarea(${t.id}, '${t.titulo}', '${t.descripcion}')">Editar</button>
                    <button onclick="eliminarTarea(${t.id})">Eliminar</button>
                 </td>
               </tr>`;
    });
    html += "</table>";
    document.getElementById("outTareas").innerHTML = html;
  } catch (err) {
    console.error(err);
    document.getElementById("outTareas").textContent = "Error al obtener tareas";
  }
}

// ---------- Crear tarea ----------
async function crearTarea() {
  if (!authHeader) {
    alert("Primero iniciá sesión");
    return;
  }

  const titulo = document.getElementById("titulo").value;
  const descripcion = document.getElementById("descripcion").value;

  if (!titulo) {
    alert("El título es obligatorio");
    return;
  }

  try {
    const res = await fetch(BASE + "/tareas", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authHeader
      },
      body: JSON.stringify({ titulo, descripcion })
    });
    const data = await res.json();
    if (res.ok) {
      alert(data.message);
      document.getElementById("titulo").value = "";
      document.getElementById("descripcion").value = "";
      tareas(); // refrescar la tabla de tareas
    } else {
      alert(data.error);
    }
  } catch (err) {
    console.error(err);
  }
}

// ---------- Editar tarea ----------
async function editarTarea(id, tituloActual, descripcionActual) {
  const nuevoTitulo = prompt("Nuevo título:", tituloActual);
  const nuevaDescripcion = prompt("Nueva descripción:", descripcionActual);

  if (!nuevoTitulo) return;

  try {
    const res = await fetch(BASE + `/tareas/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authHeader
      },
      body: JSON.stringify({ titulo: nuevoTitulo, descripcion: nuevaDescripcion })
    });
    const data = await res.json();
    if (res.ok) {
      alert(data.message);
      tareas(); // refrescar la tabla de tareas
    } else {
      alert(data.error);
    }
  } catch (err) {
    console.error(err);
  }
}

// ---------- Eliminar tarea ----------
async function eliminarTarea(id) {
  if (!confirm("¿Seguro que querés eliminar esta tarea?")) return;

  try {
    const res = await fetch(BASE + `/tareas/${id}`, {
      method: "DELETE",
      headers: { "Authorization": authHeader }
    });
    const data = await res.json();
    if (res.ok) {
      alert(data.message);
      tareas(); // refrescar la tabla de tareas
    } else {
      alert(data.error);
    }
  } catch (err) {
    console.error(err);
  }
}

// ---------- Event Listeners ----------
document.getElementById("btnRegistrar").addEventListener("click", registrar);
document.getElementById("btnLogin").addEventListener("click", login);
document.getElementById("btnTareas").addEventListener("click", tareas);
document.getElementById("crearBtn").addEventListener("click", crearTarea);
