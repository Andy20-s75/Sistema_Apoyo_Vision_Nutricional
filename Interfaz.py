import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

MODOS = ["contener", "llenar", "estirar"]
NOMBRES = {"contener": "Contener", "llenar": "Llenar", "estirar": "Estirar"}
ZOOM_MIN, ZOOM_MAX, PASO_ZOOM = 0.1, 8.0, 1.15

datos = {
    "original": None,     # imagen PIL sin modificar
    "tk": None,           # PhotoImage actual
    "id": None,           # id del dibujo dentro del canvas
    "zoom": 1.0,
    "x": 0, "y": 0,       # centro de la imagen en el canvas
    "nombre": "",
    "modo": "contener",
    "auto": True,         # True = se adapta sola al frame
}

index = tk.Tk()
index.title("Interfaz")
index.geometry("800x600")
index.minsize(600, 500)
index.configure(bg="#1e1e2e")
index.columnconfigure(0, weight=1)
index.rowconfigure(1, weight=1)

ebz = tk.Frame(index, bg="#1e1e2e")
ebz.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

titulo = tk.Label(ebz, text="Detector de sellos NOM-051", bg="#1e1e2e",
                  fg="#f1f1f5", font=("Segoe UI", 22, "bold"))
titulo.pack(anchor="center")

target = tk.Frame(index, bg="#2a2a3c", highlightbackground="#3d3d55",
                  highlightthickness=2)
target.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
target.columnconfigure(0, weight=1)
target.rowconfigure(0, weight=1)

# Canvas sin márgenes: ocupa TODO el frame
lienzo = tk.Canvas(target, bg="#2a2a3c", highlightthickness=0)
lienzo.grid(row=0, column=0, sticky="nsew")

estado = tk.StringVar(value="Listo")
barra = tk.Label(index, textvariable=estado, bg="#16161f", fg="#a0a0b5",
                 anchor="w", padx=15, pady=5, font=("Segoe UI", 9))
barra.grid(row=3, column=0, sticky="ew")


# ---------- Dibujo ----------
def mensaje_vacio():
    lienzo.delete("all")
    lienzo.create_text(lienzo.winfo_width() / 2, lienzo.winfo_height() / 2,
                       text="Aún no hay imagen", fill="#a0a0b5",
                       font=("Segoe UI", 14))


def dibujar():
    orig = datos["original"]
    if orig is None:
        return
    w, h = lienzo.winfo_width(), lienzo.winfo_height()

    if datos["auto"] and datos["modo"] == "estirar":
        tam = (w, h)                                   # ocupa todo el frame
    else:
        tam = (max(1, int(orig.width * datos["zoom"])),
               max(1, int(orig.height * datos["zoom"])))

    img = orig.resize(tam, Image.Resampling.BILINEAR)
    datos["tk"] = ImageTk.PhotoImage(img)              # guardar referencia
    lienzo.delete("all")
    datos["id"] = lienzo.create_image(datos["x"], datos["y"],
                                      image=datos["tk"], anchor="center")
    pct = tam[0] / orig.width * 100
    estado.set(f"{datos['nombre']}  |  {orig.width}x{orig.height}px  |  "
               f"Zoom: {pct:.0f}%  |  Modo: {NOMBRES[datos['modo']]}")


def ajustar(event=None):
    """Adapta la imagen al frame según el modo elegido."""
    orig = datos["original"]
    if orig is None:
        return
    w, h = lienzo.winfo_width(), lienzo.winfo_height()
    if w < 2 or h < 2:
        return
    ex, ey = w / orig.width, h / orig.height

    if datos["modo"] == "llenar":
        datos["zoom"] = max(ex, ey)     # cubre todo el frame
    elif datos["modo"] == "estirar":
        datos["zoom"] = ex              # (el ancho real se calcula en dibujar)
    else:
        datos["zoom"] = min(ex, ey)     # cabe completa

    datos["x"], datos["y"] = w / 2, h / 2
    datos["auto"] = True
    dibujar()


def cambiar_modo():
    i = (MODOS.index(datos["modo"]) + 1) % len(MODOS)
    datos["modo"] = MODOS[i]
    boton_modo.config(text=f"⛶ Modo: {NOMBRES[datos['modo']]}")
    ajustar()


def al_redimensionar(event):
    if datos["original"] is None:
        mensaje_vacio()
    elif datos["auto"]:
        ajustar()                       # se re-adapta al nuevo tamaño


# ---------- Zoom y arrastre ----------
def cambiar_zoom(factor, cx=None, cy=None):
    orig = datos["original"]
    if orig is None:
        return
    if cx is None:
        cx, cy = lienzo.winfo_width() / 2, lienzo.winfo_height() / 2
    if datos["auto"] and datos["modo"] == "estirar":
        datos["zoom"] = lienzo.winfo_width() / orig.width
    datos["auto"] = False               # el usuario toma el control

    tope = max(min(ZOOM_MAX, 6000 / max(orig.size)), datos["zoom"])
    nuevo = max(ZOOM_MIN, min(tope, datos["zoom"] * factor))
    razon = nuevo / datos["zoom"]
    datos["x"] = cx + (datos["x"] - cx) * razon
    datos["y"] = cy + (datos["y"] - cy) * razon
    datos["zoom"] = nuevo
    dibujar()


def rueda(event):
    acercar = event.delta > 0 if event.num not in (4, 5) else event.num == 4
    cambiar_zoom(PASO_ZOOM if acercar else 1 / PASO_ZOOM, event.x, event.y)


def inicio_arrastre(event):
    datos["ult"] = (event.x, event.y)


def arrastrar(event):
    if datos["original"] is None:
        return
    if datos["auto"] and datos["modo"] == "estirar":
        datos["zoom"] = lienzo.winfo_width() / datos["original"].width
        dibujar()
    datos["auto"] = False
    ux, uy = datos["ult"]
    dx, dy = event.x - ux, event.y - uy
    datos["x"] += dx
    datos["y"] += dy
    lienzo.move(datos["id"], dx, dy)
    datos["ult"] = (event.x, event.y)


lienzo.bind("<Configure>", al_redimensionar)
lienzo.bind("<MouseWheel>", rueda)
lienzo.bind("<Button-4>", rueda)
lienzo.bind("<Button-5>", rueda)
lienzo.bind("<ButtonPress-1>", inicio_arrastre)
lienzo.bind("<B1-Motion>", arrastrar)
lienzo.bind("<Double-Button-1>", ajustar)


# ---------- Acciones ----------
def cargar_imagen():
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")]
    )
    if not ruta:
        return
    try:
        datos["original"] = Image.open(ruta).convert("RGBA")
        datos["nombre"] = os.path.basename(ruta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")
        return
    ajustar()


def limpiar():
    datos["original"] = None
    datos["tk"] = None
    mensaje_vacio()
    estado.set("Listo")


def detectar_sello():
    if datos["original"] is None:
        messagebox.showwarning("Sin imagen", "Primero carga una imagen.")
        return
    estado.set("Detectando sello...")
    messagebox.showinfo("Detectar sello", "Aquí irá la detección.")


def crear_boton(padre, texto, comando, color, color_hover):
    b = tk.Button(padre, text=texto, command=comando, bg=color, fg="white",
                  activebackground=color_hover, activeforeground="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", bd=0,
                  padx=22, pady=10, cursor="hand2")
    b.bind("<Enter>", lambda e: b.config(bg=color_hover))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


zona_botones = tk.Frame(index, bg="#1e1e2e")
zona_botones.grid(row=2, column=0, pady=(10, 20))

crear_boton(ebz, "🔍 Detectar sello", detectar_sello,
            "#10b981", "#34d399").pack(anchor="w", pady=(0, 12), before=titulo)
crear_boton(zona_botones, "📂  Cargar imagen", cargar_imagen,
            "#7c3aed", "#9d5cff").pack(side="left", padx=8)
boton_modo = crear_boton(zona_botones, "⛶ Modo: Contener", cambiar_modo,
                         "#3b82f6", "#60a5fa")
boton_modo.pack(side="left", padx=8)
crear_boton(zona_botones, "🗑️  Limpiar", limpiar,
            "#44445a", "#5a5a75").pack(side="left", padx=8)

index.mainloop()