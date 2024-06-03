import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
import mysql.connector
import base64
import io

# Configuración de la conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="negocio"
)

def guardar_producto(nombre, precio, imagen_path):
    cursor = db.cursor()
    
    with open(imagen_path, 'rb') as file:
        imagen = file.read()
    
    # Convertir la imagen a base64 para almacenarla en la base de datos
    imagen_base64 = base64.b64encode(imagen)
    
    query = "INSERT INTO productos (nombre, precio, imagen) VALUES (%s, %s, %s)"
    values = (nombre, precio, imagen_base64)
    
    cursor.execute(query, values)
    db.commit()
    cursor.close()

def seleccionar_imagen():
    global imagen_path
    imagen_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if imagen_path:
        imagen = Image.open(imagen_path)
        imagen = imagen.resize((150, 150), Image.Resampling.LANCZOS)
        imagen_tk = ImageTk.PhotoImage(imagen)
        lbl_imagen.config(image=imagen_tk)
        lbl_imagen.image = imagen_tk

def guardar():
    global imagen_path
    nombre = entry_nombre.get()
    precio = entry_precio.get()
    if not nombre or not precio or not imagen_path:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return
    
    try:
        precio = float(precio)
    except ValueError:
        messagebox.showerror("Error", "El precio debe ser un número.")
        return

    guardar_producto(nombre, precio, imagen_path)
    messagebox.showinfo("Éxito", "Producto guardado exitosamente.")
    entry_nombre.delete(0, tk.END)
    entry_precio.delete(0, tk.END)
    lbl_imagen.config(image='')
    imagen_path = None
    listar_productos()

def eliminar_producto(nombre):
    respuesta = messagebox.askyesno("Confirmar", f"¿Estás seguro de que quieres eliminar el producto '{nombre}'?")
    if respuesta:
        cursor = db.cursor()
        query = "DELETE FROM productos WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        db.commit()
        cursor.close()
        listar_productos()

def listar_productos():
    for widget in frame_lista.winfo_children():
        widget.destroy()

    cursor = db.cursor()
    cursor.execute("SELECT nombre, precio, imagen FROM productos")
    productos = cursor.fetchall()
    cursor.close()
    
    for nombre, precio, imagen_base64 in productos:
        frame_producto = tk.Frame(frame_lista)
        frame_producto.pack(fill=tk.X, padx=10, pady=5)

        imagen_data = base64.b64decode(imagen_base64)
        imagen = Image.open(io.BytesIO(imagen_data))
        imagen = imagen.resize((200, 200), Image.Resampling.LANCZOS)
        imagen_tk = ImageTk.PhotoImage(imagen)
        
        lbl_imagen = tk.Label(frame_producto, image=imagen_tk)
        lbl_imagen.image = imagen_tk
        lbl_imagen.pack(side=tk.LEFT, padx=5)
        
        lbl_nombre = tk.Label(frame_producto, text=nombre)
        lbl_nombre.pack(side=tk.LEFT, padx=5)
        
        lbl_precio = tk.Label(frame_producto, text=f"${precio}")
        lbl_precio.pack(side=tk.LEFT, padx=5)

        btn_eliminar = tk.Button(frame_producto, text="Eliminar", command=lambda n=nombre: eliminar_producto(n))
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        # Configuración del desplazamiento en el lienzo
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Negocio")
ventana.geometry("800x600")  # Establecer el tamaño inicial de la ventana a 800x600 píxeles


tk.Label(ventana, text="Nombre del producto:").grid(row=0, column=0, padx=10, pady=10)
entry_nombre = tk.Entry(ventana)
entry_nombre.grid(row=0, column=1, padx=10, pady=10)

tk.Label(ventana, text="Precio del producto:").grid(row=1, column=0, padx=10, pady=10)
entry_precio = tk.Entry(ventana)
entry_precio.grid(row=1, column=1, padx=10, pady=10)

tk.Button(ventana, text="Seleccionar imagen", command=seleccionar_imagen).grid(row=2, column=0, padx=10, pady=10)

lbl_imagen = tk.Label(ventana)
lbl_imagen.grid(row=2, column=1, padx=10, pady=10)

tk.Button(ventana, text="Guardar producto", command=guardar).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Marco para listar los productos
frame_scrollbar = tk.Frame(ventana)
frame_scrollbar.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

canvas = tk.Canvas(frame_scrollbar)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_scrollbar, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

frame_lista = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_lista, anchor="nw")

ventana.grid_rowconfigure(4, weight=1)
ventana.grid_columnconfigure(1, weight=1)

imagen_path = None

listar_productos()  # Listar productos al iniciar la aplicación

ventana.mainloop()

# Cerrar la conexión a la base de datos al final
db.close()
