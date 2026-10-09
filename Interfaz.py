import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

index= tk.Tk()
index.title("Interfaz")
index.geometry("800x600")
index.minsize(600,500)
index.configure(bg="#1e1e2e")
index.columnconfigure(0, weight=1)
index.rowconfigure(1, weight=1)

ebz=tk.Frame(index,bg="#1e1e2e")
ebz.grid(row=0, column=0, sticky="ew", padx=30, pady=(25,10))

tk.Label(ebz, text="Detector de sellos NOM-051", bg="#1e1e2e", fg="#f1f1f5",
         font=("Segoe UI", 22, "bold")).pack(anchor="center")

target=tk.Frame(index, bg="#2a2a3c",highlightbackground="#3d3d55",
                highlightthickness=2)
target.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
target.columnconfigure(0, weight=1)
target.rowconfigure(0, weight=1)

etiqueta= tk.Label(target, bg="#2a2a3c", fg="#a0a0b5",
                    text="\n\nAún no hay imagen",
                    font=("Segoe UI", 14))
etiqueta.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

estado = tk.StringVar(value="Listo")
barra = tk.Label(index, textvariable=estado, bg="#16161f", fg="#a0a0b5",
                 anchor="w", padx=15, pady=5, font=("Segoe UI", 9))
barra.grid(row=3, column=0, sticky="ew")

def cargar_imagen():
    ruta = filedialog.askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png")]
    )
    if not ruta:
        return  

    try:
        img = Image.open(ruta)
        img.thumbnail((450, 350))        
        img_tk = ImageTk.PhotoImage(img)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")
        return

    etiqueta.config(image=img_tk, text="")
    etiqueta.image = img_tk           
    estado.set(f"Cargada: {ruta.split('/')[-1]}  ({img.width}x{img.height}px)")

def limpiar():
    etiqueta.config(image="", text="\n\nAún no hay imagen")
    etiqueta.image = None
    estado.set("Listo")

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

crear_boton(zona_botones, "📂  Cargar imagen", cargar_imagen,
            "#7c3aed", "#9d5cff").pack(side="left", padx=8)
crear_boton(zona_botones, "🗑️  Limpiar", limpiar,
            "#44445a", "#5a5a75").pack(side="left", padx=8)
index.mainloop()

