fetch("/api/plazas").then(r => r.json()).then(({ centro, plazas }) => {
  const mapa = L.map("mapa").setView([centro.lat, centro.lng], 13);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19, attribution: "&copy; colaboradores de OpenStreetMap"
  }).addTo(mapa);
  L.marker([centro.lat, centro.lng]).addTo(mapa)
    .bindPopup("<strong>Las Heras</strong><br>Punto de referencia del departamento");

  const marcadores = {};
  const txt = s => { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; };
  plazas.forEach(p => {
    if (p.lat === null || p.lng === null) return;
    marcadores[p.id] = L.marker([p.lat, p.lng]).addTo(mapa).bindPopup(
      `<strong>${txt(p.nombre)}</strong><br>${txt(p.direccion)}<br>${txt(p.descripcion)}`);
  });

  const aviso = document.getElementById("aviso-mapa");
  document.getElementById("localizar").addEventListener("click", () => {
    const id = document.getElementById("selector").value;
    aviso.hidden = true;
    if (!id) { aviso.textContent = "Elegí una plaza de la lista."; aviso.hidden = false; return; }
    const p = plazas.find(x => String(x.id) === id);
    if (marcadores[id]) {
      mapa.flyTo([p.lat, p.lng], 17);
      marcadores[id].openPopup();
    } else {
      mapa.flyTo([centro.lat, centro.lng], 13);
      aviso.textContent = `${p.nombre} (${p.direccion}): todavía no tiene coordenadas verificadas, por eso no hay marcador.`;
      aviso.hidden = false;
    }
  });
});
