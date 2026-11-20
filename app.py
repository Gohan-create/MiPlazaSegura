import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(24))
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024
CSRFProtect(app)

# Punto de referencia verificado (Wikipedia: Las Heras, 32°51′S 68°49′W / 32.850°S 68.817°W).
CENTRO_LAS_HERAS = {"lat": -32.850, "lng": -68.817}

# Plazas con nombre y dirección tomados de fuentes oficiales (mendoza.gov.ar, medios locales).
# Las coordenadas NO se inventaron: están en None hasta que las confirmes (por ejemplo,
# haciendo clic derecho sobre la plaza en openstreetmap.org y copiando lat/lng).
# Al completar "lat" y "lng", el marcador aparece solo en el mapa.
PLAZAS = [
    {"id": 1, "nombre": "Plaza Departamental Marcos Burgos",
     "direccion": "Casco histórico de Las Heras", "lat": None, "lng": None,
     "descripcion": "Plaza central del departamento, renovada junto con el casco histórico."},
    {"id": 2, "nombre": "Plaza Las Heras (Panquehua)",
     "direccion": "Entre Avellaneda, Río Negro, Juan Gualberto Godoy y Víctor Hugo, Panquehua",
     "lat": None, "lng": None,
     "descripcion": "Espacio verde de unos 12.500 m² incluido en un plan de remodelación integral."},
    {"id": 3, "nombre": "Plaza 2 de Abril",
     "direccion": "Barrio Municipal", "lat": None, "lng": None,
     "descripcion": "Plaza de casi 4 hectáreas, reinaugurada con homenaje a excombatientes."},
]

CATEGORIAS = ["Limpieza", "Seguridad", "Iluminación", "Juegos infantiles",
              "Mantenimiento", "Espacios verdes", "Sugerencias generales"]

OPINIONES = []
PROPUESTAS = []

MAX_NOMBRE, MAX_MENSAJE, MAX_TITULO = 60, 600, 100


def ahora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def nombres_plazas():
    return [p["nombre"] for p in PLAZAS]


@app.route("/")
def inicio():
    stats = {"opiniones": len(OPINIONES), "plazas": len(PLAZAS), "propuestas": len(PROPUESTAS)}
    return render_template("index.html", stats=stats)


@app.route("/opiniones", methods=["GET", "POST"])
def opiniones():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        plaza = request.form.get("plaza", "")
        categoria = request.form.get("categoria", "")
        mensaje = request.form.get("mensaje", "").strip()
        if not nombre or not mensaje:
            flash("Completá tu nombre y el mensaje.", "error")
        elif plaza not in nombres_plazas() or categoria not in CATEGORIAS:
            flash("Elegí una plaza y una categoría de la lista.", "error")
        elif len(nombre) > MAX_NOMBRE or len(mensaje) > MAX_MENSAJE:
            flash(f"Máximo {MAX_NOMBRE} caracteres en el nombre y {MAX_MENSAJE} en el mensaje.", "error")
        else:
            OPINIONES.insert(0, {"nombre": nombre, "plaza": plaza, "categoria": categoria,
                                 "mensaje": mensaje, "fecha": ahora()})
            flash("¡Gracias! Tu opinión ya está publicada.", "ok")
        return redirect(url_for("opiniones") + "#lista")

    q = request.args.get("q", "").strip().lower()
    f_plaza = request.args.get("plaza", "")
    f_cat = request.args.get("categoria", "")
    lista = [o for o in OPINIONES
             if (not f_plaza or o["plaza"] == f_plaza)
             and (not f_cat or o["categoria"] == f_cat)
             and (not q or q in o["mensaje"].lower() or q in o["nombre"].lower())]
    return render_template("opiniones.html", opiniones=lista, plazas=nombres_plazas(),
                           categorias=CATEGORIAS, q=q, f_plaza=f_plaza, f_cat=f_cat,
                           total=len(OPINIONES), max_mensaje=MAX_MENSAJE)


@app.route("/mapa")
def mapa():
    return render_template("mapa.html", plazas=PLAZAS)


@app.route("/api/plazas")
def api_plazas():
    return jsonify({"centro": CENTRO_LAS_HERAS, "plazas": PLAZAS})


@app.route("/propuestas", methods=["GET", "POST"])
def propuestas():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        plaza = request.form.get("plaza", "")
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        if not nombre or not titulo or not descripcion:
            flash("Completá nombre, título y descripción.", "error")
        elif plaza not in nombres_plazas():
            flash("Elegí una plaza de la lista.", "error")
        elif len(nombre) > MAX_NOMBRE or len(titulo) > MAX_TITULO or len(descripcion) > MAX_MENSAJE:
            flash("Alguno de los campos supera la longitud permitida.", "error")
        else:
            PROPUESTAS.insert(0, {"nombre": nombre, "plaza": plaza, "titulo": titulo,
                                  "descripcion": descripcion, "fecha": ahora()})
            flash("¡Propuesta publicada!", "ok")
        return redirect(url_for("propuestas") + "#lista")
    return render_template("propuestas.html", propuestas=PROPUESTAS, plazas=nombres_plazas(),
                           max_titulo=MAX_TITULO, max_mensaje=MAX_MENSAJE)


@app.route("/consejos")
def consejos():
    items = [("🗑️", "No arrojes basura al suelo", "Llevá tus residuos hasta el cesto más cercano o a tu casa."),
             ("🌳", "Cuidá árboles y plantas", "No quiebres ramas ni pises canteros: dan sombra y oxígeno."),
             ("🛝", "Respetá los juegos infantiles", "Usalos según su edad y avisá si ves una pieza rota."),
             ("♻️", "Usá bien los cestos", "Separá lo que puedas y no dejes bolsas fuera del cesto."),
             ("🏞️", "Cuidá los espacios públicos", "Bancos, luminarias y senderos son de todos."),
             ("📣", "Denunciá daños", "Informá los problemas de mantenimiento a la Municipalidad de Las Heras.")]
    return render_template("consejos.html", items=items)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
