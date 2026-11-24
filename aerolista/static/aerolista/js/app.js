// ==============================================================
// app.js · El JavaScript de la página
// --------------------------------------------------------------
// Dibuja el avión, pide los datos a Django con fetch() y actualiza
// los colores de los asientos después de cada cambio.
// ==============================================================

// Forma del avión (la misma que en vuelo.py)
const FILAS = 12;
const FILAS_EJECUTIVA = 2;
const LETRAS_EJECUTIVA = ["A", "C", "D", "F"];
const LETRAS_ECONOMICA = ["A", "B", "C", "D", "E", "F"];

// Estado de la página
let vueloActual = "";      // código del vuelo elegido
let reservados = {};       // {"7D": {datos del pasajero}, ...}
let seleccionado = "";     // asiento en amarillo
let clase = "";            // filtro de la pestaña Listar
let reservaCargada = null; // reserva que se está modificando

// Atajo para buscar un elemento por su id
function $(id) { return document.getElementById(id); }

// ---------------- Comunicación con Django ----------------

// Hace el pedido y devuelve la respuesta JSON ({ok, datos, mensaje})
async function pedir(url, metodo = "GET", datos = null) {
  const opciones = {
    method: metodo,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
    },
  };
  if (datos !== null) opciones.body = JSON.stringify(datos);
  const respuesta = await fetch(url, opciones);
  return await respuesta.json();
}

function urlVuelo(final = "") {
  return "/api/vuelos/" + encodeURIComponent(vueloActual) + final;
}

// Muestra un mensaje de Bootstrap que desaparece solo
function mensaje(texto, tipo = "success") {
  const caja = document.createElement("div");
  caja.className = "alert alert-" + tipo;
  caja.textContent = texto;
  $("mensajes").appendChild(caja);
  setTimeout(() => caja.remove(), 4000);
}

// ---------------- Vuelo y tablero ----------------

async function mostrarVuelo() {
  const r = await pedir(urlVuelo());
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  const v = r.datos;
  $("info-vuelo").innerHTML = "";
  const linea = document.createElement("div");
  linea.className = "fw-semibold";
  linea.textContent = `${v.codigo} · ${v.origen} → ${v.destino} · ${v.fecha} · ${v.hora}`;
  $("info-vuelo").appendChild(linea);
}

async function actualizarTodo() {
  seleccionado = "";
  $("res-asiento").value = "";
  reservaCargada = null;
  $("form-modificar").classList.add("d-none");
  $("resultado-busqueda").innerHTML = "";

  await mostrarVuelo();
  const r = await pedir(urlVuelo("/reservas"));         // listar() de la lista enlazada
  reservados = {};
  for (const p of r.datos) reservados[p.asiento] = p;
  dibujarAvion();
  const total = FILAS_EJECUTIVA * LETRAS_EJECUTIVA.length + (FILAS - FILAS_EJECUTIVA) * LETRAS_ECONOMICA.length;
  const n = r.datos.length;
  $("tablero").textContent = `${n} reservados · ${total - n} libres · ${total} en total`;
  listar();
}

// ---------------- El avión ----------------

function crearAsiento(codigo) {
  const boton = document.createElement("button");
  boton.type = "button";
  boton.textContent = codigo;
  boton.title = codigo;
  if (reservados[codigo]) boton.className = "asiento reservado";
  else if (codigo === seleccionado) boton.className = "asiento seleccionado";
  else boton.className = "asiento libre";
  boton.addEventListener("click", () => clicAsiento(codigo));
  return boton;
}

function dibujarAvion() {
  const avion = $("avion");
  avion.innerHTML = "";
  for (let fila = 1; fila <= FILAS; fila++) {
    const esEjecutiva = fila <= FILAS_EJECUTIVA;
    const letras = esEjecutiva ? LETRAS_EJECUTIVA : LETRAS_ECONOMICA;
    const div = document.createElement("div");
    div.className = "fila" + (esEjecutiva ? " ejecutiva" : "");
    const mitad = letras.length / 2;                    // pasillo en el centro
    letras.forEach((letra, i) => {
      if (i === mitad) {
        const pasillo = document.createElement("span");
        pasillo.className = "pasillo";
        pasillo.textContent = fila;
        div.appendChild(pasillo);
      }
      div.appendChild(crearAsiento(fila + letra));
    });
    avion.appendChild(div);
  }
}

function clicAsiento(codigo) {
  if (reservados[codigo]) {                             // asiento rojo: mostrar quién viaja
    mostrarPasajero(reservados[codigo]);
    new bootstrap.Tab(document.querySelector('[data-bs-target="#tab-buscar"]')).show();
    return;
  }
  seleccionado = codigo;                                // asiento verde: seleccionarlo
  $("res-asiento").value = codigo;
  if (reservaCargada) $("mod-asiento").value = codigo;  // si se está modificando, también cambia aquí
  dibujarAvion();
}

// ---------------- Registrar vuelo ----------------

async function registrarVuelo() {
  const datos = {
    codigo: $("v-codigo").value, origen: $("v-origen").value, destino: $("v-destino").value,
    fecha: $("v-fecha").value, hora: $("v-hora").value,
  };
  const r = await pedir("/api/vuelos", "POST", datos);
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  mensaje(r.mensaje);
  const opcion = document.createElement("option");
  opcion.value = r.datos.codigo;
  opcion.textContent = `${r.datos.codigo} · ${r.datos.origen} → ${r.datos.destino}`;
  $("selector-vuelo").appendChild(opcion);
  $("selector-vuelo").value = r.datos.codigo;
  vueloActual = r.datos.codigo;
  ["v-codigo", "v-origen", "v-destino", "v-fecha", "v-hora"].forEach(id => $(id).value = "");
  actualizarTodo();
}

// ---------------- Reservar ----------------

async function reservar() {
  const datos = {
    asiento: $("res-asiento").value, nombre: $("res-nombre").value,
    cedula: $("res-cedula").value, edad: $("res-edad").value,
  };
  if (datos.asiento === "") { mensaje("Primero elige un asiento verde en el avión", "warning"); return; }
  const r = await pedir(urlVuelo("/reservas"), "POST", datos);
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  mensaje(r.mensaje);
  ["res-nombre", "res-cedula", "res-edad"].forEach(id => $(id).value = "");
  actualizarTodo();
}

// ---------------- Buscar ----------------

function mostrarPasajero(p) {
  const caja = $("resultado-busqueda");
  caja.innerHTML = "";
  const tarjeta = document.createElement("div");
  tarjeta.className = "border rounded p-3 bg-white";
  tarjeta.innerHTML = "<b></b><br><span></span>";
  tarjeta.querySelector("b").textContent = `Reserva #${p.numero} · ${p.nombre}`;
  tarjeta.querySelector("span").textContent =
    `Cédula ${p.cedula} · ${p.edad} años · asiento ${p.asiento} · ${p.clase}`;
  caja.appendChild(tarjeta);
}

async function buscar() {
  const tipo = $("bus-tipo").value;
  const valor = $("bus-valor").value.trim();
  if (valor === "") { mensaje("Escribe qué quieres buscar", "warning"); return; }
  let url;
  if (tipo === "numero") url = urlVuelo("/reservas/" + encodeURIComponent(valor));
  else if (tipo === "asiento") url = urlVuelo("/asientos/" + encodeURIComponent(valor));
  else url = urlVuelo("/cedulas/" + encodeURIComponent(valor));

  const r = await pedir(url);
  $("resultado-busqueda").innerHTML = "";
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  if (r.datos === null) { mensaje(r.mensaje, "info"); return; }   // asiento libre
  mostrarPasajero(r.datos);
}

// ---------------- Modificar y cancelar ----------------

async function cargarReserva() {
  const numero = $("mod-numero").value;
  const r = await pedir(urlVuelo("/reservas/" + encodeURIComponent(numero)));
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  reservaCargada = r.datos;
  $("mod-nombre").value = r.datos.nombre;
  $("mod-edad").value = r.datos.edad;
  $("mod-asiento").value = r.datos.asiento;
  $("form-modificar").classList.remove("d-none");
}

async function guardarCambios() {
  const datos = { nombre: $("mod-nombre").value, edad: $("mod-edad").value, asiento: $("mod-asiento").value };
  const r = await pedir(urlVuelo("/reservas/" + reservaCargada.numero), "PUT", datos);
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  mensaje(r.mensaje);
  actualizarTodo();
}

async function cancelarReserva() {
  if (!confirm(`¿Cancelar la reserva #${reservaCargada.numero}?`)) return;
  const r = await pedir(urlVuelo("/reservas/" + reservaCargada.numero), "DELETE");
  if (!r.ok) { mensaje(r.mensaje, "danger"); return; }
  mensaje(r.mensaje);
  actualizarTodo();
}

// ---------------- Listar ----------------

async function listar() {
  const url = urlVuelo("/reservas") + (clase ? "?clase=" + encodeURIComponent(clase) : "");
  const r = await pedir(url);
  const cuerpo = $("tabla-pasajeros");
  cuerpo.innerHTML = "";
  for (const p of r.datos) {
    const fila = document.createElement("tr");
    [p.numero, p.nombre, p.cedula, p.edad, p.asiento].forEach(valor => {
      const celda = document.createElement("td");
      celda.textContent = valor;
      fila.appendChild(celda);
    });
    cuerpo.appendChild(fila);
  }
  if (r.datos.length === 0) {
    cuerpo.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Sin reservas</td></tr>';
  }
}

// ---------------- Conectar los botones ----------------

$("selector-vuelo").addEventListener("change", () => { vueloActual = $("selector-vuelo").value; actualizarTodo(); });
$("btn-registrar-vuelo").addEventListener("click", registrarVuelo);
$("btn-reservar").addEventListener("click", reservar);
$("btn-buscar").addEventListener("click", buscar);
$("btn-cargar").addEventListener("click", cargarReserva);
$("btn-guardar-cambios").addEventListener("click", guardarCambios);
$("btn-cancelar-reserva").addEventListener("click", cancelarReserva);
document.querySelectorAll(".filtro").forEach(boton => {
  boton.addEventListener("click", () => {
    document.querySelectorAll(".filtro").forEach(b => b.classList.remove("active"));
    boton.classList.add("active");
    clase = boton.dataset.clase;
    listar();
  });
});

// Al abrir la página: tomar el primer vuelo y dibujar todo
vueloActual = $("selector-vuelo").value;
if (vueloActual !== "") actualizarTodo();
