# ==============================================================================
# GESTOR ACADÉMICO - INTERFAZ GRÁFICA (FRONTEND)
# ==============================================================================
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry 
import BackendProyecto as db 

# ------------------------------------------------------------------------------
# 🔧 PARCHE DE COMPATIBILIDAD PARA TKCALENDAR EN PYTHON 3.12+
# ------------------------------------------------------------------------------
def _on_motion_fixed(self, event):
    try:
        if self.identify(event.x, event.y) == self._downarrow_name:
            self.state(['hover'])
        else:
            self.state(['!hover'])
    except AttributeError:
        pass

DateEntry._on_motion = _on_motion_fixed
# ------------------------------------------------------------------------------

# Asegurar que las tablas existen
db.crear_tablas_iniciales()

# --- PALETA DE COLORES ---
COLOR_SIDEBAR      = "#1e293b"   # Azul Noche
COLOR_FONDO        = "#f1f5f9"   # Gris muy claro
COLOR_BLANCO       = "#ffffff"   # Blanco puro
COLOR_TEXTO_MAIN   = "#334155"   # Gris oscuro
COLOR_TEXTO_SIDE   = "#ffffff"   # Blanco sidebar
COLOR_ACCENT       = "#1e293b"   # Azul Noche (Igual al sidebar)
COLOR_ACCENT_HOVER = "#334155"   # Hover grisaceo
COLOR_DANGER       = "#ef4444"   # Rojo

# --- VARIABLES DE ESTILO ---
BORDER_COLOR = "#cbd5e1"
FOCUS_COLOR  = "#2563eb"

# ==============================================================================
# II. SISTEMA DE MENSAJES Y UTILIDADES
# ==============================================================================

def centrar_ventana(ventana, ancho, alto):
    ventana.update_idletasks() 
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = int((pantalla_ancho / 2) - (ancho / 2))
    y = int((pantalla_alto / 2) - (alto / 2))
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def mostrar_mensaje(titulo, mensaje, tipo="info"):
    popup = tk.Toplevel()
    popup.withdraw() 
    popup.title(titulo)
    popup.config(bg=COLOR_BLANCO)
    # Las alertas SÍ pueden ser transitorias
    popup.transient(popup.master)
    
    centrar_ventana(popup, 400, 200)
    popup.resizable(False, False)
    popup.deiconify() 
    
    icono = "⚠️" if tipo == "error" else "ℹ️"
    color_icono = "#dc2626" if tipo == "error" else "#0284c7"

    tk.Label(popup, text=icono, font=("Arial", 30), bg=COLOR_BLANCO, fg=color_icono).pack(pady=(15, 5))
    tk.Label(popup, text=mensaje, font=("Segoe UI", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, wraplength=350).pack(pady=5)

    btn_frame = tk.Frame(popup, bg=COLOR_BLANCO)
    btn_frame.pack(pady=15)
    
    tk.Button(btn_frame, text="Entendido", command=popup.destroy, cursor="hand2",
              bg="#e2e8f0", fg="#334155", bd=0, padx=20, pady=6,
              font=("Segoe UI", 9, "bold")).pack()

    popup.grab_set()
    popup.wait_window()

def preguntar_si_no(titulo, mensaje):
    respuesta = {"valor": False}
    
    popup = tk.Toplevel()
    popup.withdraw()
    popup.title(titulo)
    popup.config(bg=COLOR_BLANCO)
    popup.transient(popup.master)
    
    centrar_ventana(popup, 350, 180)
    popup.resizable(False, False)
    popup.deiconify()

    tk.Label(popup, text="❓", font=("Arial", 30), bg=COLOR_BLANCO, fg="#eab308").pack(pady=(15, 5))
    tk.Label(popup, text=mensaje, font=("Segoe UI", 10), bg=COLOR_BLANCO, fg=COLOR_TEXTO_MAIN, wraplength=300).pack(pady=5)

    def click_si(): respuesta["valor"] = True; popup.destroy()
    def click_no(): respuesta["valor"] = False; popup.destroy()

    btn_frame = tk.Frame(popup, bg=COLOR_BLANCO)
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="Sí, confirmar", command=click_si, cursor="hand2",
              bg="#16a34a", fg="white", bd=0, padx=15, pady=6, font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancelar", command=click_no, cursor="hand2",
              bg="#dc2626", fg="white", bd=0, padx=15, pady=6, font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)

    popup.grab_set()
    popup.wait_window()
    return respuesta["valor"]

# ==============================================================================
# III. LÓGICA DE CONTROL (CRUD)
# ==============================================================================

# --- ALUMNO ---
def limpiar_campos(n_var, c_var): n_var.set(""); c_var.set("")
def cargar_alumnos(tree):
    for item in tree.get_children(): tree.delete(item)
    for a in db.seleccionar_alumnos(): tree.insert('', tk.END, iid=a[0], values=a)

def registrar_alumno(n_var, c_var, tree, limpiar):
    nom = n_var.get(); corr = c_var.get()
    if not nom or not corr: mostrar_mensaje("Error", "Los campos son obligatorios.", "error"); return
    res = db.insertar_alumno(nom, corr) 
    if res == "UNIQUE_ERROR": mostrar_mensaje("Duplicado", f"El correo '{corr}' ya está registrado.", "error"); return
    elif res is None: mostrar_mensaje("Error", "Fallo de conexión BD.", "error"); return 
    mostrar_mensaje("Éxito", "Alumno registrado correctamente."); limpiar(n_var, c_var); cargar_alumnos(tree)

def borrar_alumno(tree):
    sel = tree.selection() 
    if not sel: mostrar_mensaje("Aviso", "Selecciona un alumno de la lista.", "error"); return
    if preguntar_si_no("Confirmar", "¿Estás seguro de borrar este alumno?"):
        res = db.borrar_alumno(int(sel[0]))
        if res == True:
            tree.delete(sel[0])
            mostrar_mensaje("Listo", "Alumno eliminado.")
        elif res == "FK_ERROR":
            mostrar_mensaje("No se puede borrar", "Este alumno tiene entregas registradas.\nPor integridad de datos, borra primero sus registros en 'Gestor de Entregas'.", "error")
        else:
            mostrar_mensaje("Error", "Error desconocido en la BD.", "error")

# --- CURSO ---
def limpiar_campos_curso(n, d): n.set(""); d.delete('1.0', tk.END)
def cargar_cursos(tree):
    for item in tree.get_children(): tree.delete(item)
    for c in db.seleccionar_cursos(): tree.insert('', tk.END, iid=c[0], values=c)

def registrar_curso(n, d, tree, limp):
    nom = n.get(); desc = d.get('1.0', tk.END).strip()
    if not nom or not desc: mostrar_mensaje("Error", "Nombre y descripción obligatorios.", "error"); return
    res = db.insertar_curso(nom, desc)
    if res == "UNIQUE_ERROR": mostrar_mensaje("Error", "Ya existe un curso con ese nombre.", "error"); return
    if res: mostrar_mensaje("Éxito", "Curso creado."); limp(n, d); cargar_cursos(tree)
    else: mostrar_mensaje("Error", "Fallo BD.", "error")

def borrar_curso(tree):
    sel = tree.selection()
    if not sel: mostrar_mensaje("Aviso", "Selecciona curso.", "error"); return
    if preguntar_si_no("Borrar", "¿Eliminar curso?"):
        res = db.borrar_curso(int(sel[0]))
        if res == True:
            tree.delete(sel[0]); mostrar_mensaje("Listo", "Borrado.")
        elif res == "FK_ERROR":
            mostrar_mensaje("Error", "No puedes borrar este curso porque tiene Tareas asociadas.", "error")
        else: mostrar_mensaje("Error", "Fallo BD.", "error")

# --- TAREA ---
def obt_cursos(): return [f"{c[0]} - {c[1]}" for c in db.seleccionar_cursos()]
def limp_tarea(t, f, c): t.set(""); f.set(""); c.set("")
def cargar_tareas(tr):
    for i in tr.get_children(): tr.delete(i)
    for t in db.seleccionar_tareas(): tr.insert('', tk.END, iid=t[0], values=t)

def reg_tarea(t, f, c, tr, limp):
    if not t.get() or not f.get() or not c.get(): mostrar_mensaje("Error", "Campos vacíos.", "error"); return
    try: id_c = int(c.get().split(' - ')[0])
    except: mostrar_mensaje("Error", "Curso inválido.", "error"); return
    if db.insertar_tarea(t.get(), f.get(), id_c): 
        mostrar_mensaje("Éxito", "Registrada.")
        limp(t, f, c)
        cargar_tareas(tr)
        # Recuperar foco a la ventana de Tareas
        try: tr.winfo_toplevel().lift()
        except: pass
    else: mostrar_mensaje("Error", "Fallo BD.", "error")

def del_tarea(tr):
    sel = tr.selection()
    if not sel: mostrar_mensaje("Aviso", "Selecciona tarea.", "error"); return
    if preguntar_si_no("Borrar", "¿Eliminar tarea?"):
        res = db.borrar_tarea(int(sel[0]))
        if res == True:
            tr.delete(sel[0]); mostrar_mensaje("Listo", "Borrada.")
        elif res == "FK_ERROR":
            mostrar_mensaje("Error", "No puedes borrar esta tarea porque tiene Entregas (notas) asociadas.", "error")
        else: mostrar_mensaje("Error", "Fallo BD.", "error")
        
    # Recuperar foco a la ventana de Tareas tras cerrar el popup
    try: tr.winfo_toplevel().lift()
    except: pass

# --- ENTREGA ---
def limp_ent(f, n, a, t): f.set(""); n.set(""); a.set(""); t.set("")
def obt_alum(): return [f"{a[0]} - {a[1]}" for a in db.seleccionar_alumnos()]
def obt_tar(): return [f"{t[0]} - {t[1]}" for t in db.seleccionar_tareas()]
def carg_ent(tr):
    for i in tr.get_children(): tr.delete(i)
    for r in db.seleccionar_entregas(): tr.insert('', tk.END, iid=r[0], values=r)

def reg_ent(f, n, a, t, tr):
    if not f.get() or not n.get() or not a.get() or not t.get(): mostrar_mensaje("Error", "Todos los campos obligatorios.", "error"); return
    try: nota = float(n.get()); ida = int(a.get().split(' - ')[0]); idt = int(t.get().split(' - ')[0])
    except: mostrar_mensaje("Error", "La nota debe ser numérica.", "error"); return
    
    if db.insertar_entrega(f.get(), nota, ida, idt): 
        mostrar_mensaje("Éxito", "Entrega guardada.")
        limp_ent(f, n, a, t)
        carg_ent(tr)
        # Recuperar foco
        try: tr.winfo_toplevel().lift()
        except: pass
    else: mostrar_mensaje("Error", "Fallo BD.", "error")

def del_ent(tr):
    sel = tr.selection()
    if not sel: mostrar_mensaje("Aviso", "Selecciona entrega.", "error"); return
    if preguntar_si_no("Borrar", "¿Borrar entrega?"):
        if db.borrar_entrega(int(sel[0])): tr.delete(sel[0]); mostrar_mensaje("Listo", "Borrada.")
        else: mostrar_mensaje("Error", "Fallo BD.", "error")
    
    try: tr.winfo_toplevel().lift()
    except: pass

# ==============================================================================
# IV. ESTILOS Y APARIENCIA
# ==============================================================================

def configurar_estilos_tema():
    style = ttk.Style()
    style.theme_use('clam')

    style.configure("TFrame", background=COLOR_FONDO)
    style.configure("TLabel", background=COLOR_FONDO, foreground=COLOR_TEXTO_MAIN, font=('Segoe UI', 10))
    
    # ENTRY Y COMBOBOX
    style.configure("TEntry", 
                    fieldbackground=COLOR_BLANCO, 
                    foreground="#000000", 
                    bordercolor=BORDER_COLOR,
                    lightcolor=BORDER_COLOR,
                    darkcolor=BORDER_COLOR,
                    relief="flat", padding=5)
    style.map("TEntry", bordercolor=[('focus', FOCUS_COLOR)], lightcolor=[('focus', FOCUS_COLOR)], darkcolor=[('focus', FOCUS_COLOR)])
    
    style.configure("TCombobox",
                    fieldbackground=COLOR_BLANCO,
                    background=COLOR_BLANCO,
                    foreground="#000000",
                    bordercolor=BORDER_COLOR,
                    lightcolor=BORDER_COLOR,
                    darkcolor=BORDER_COLOR,
                    arrowcolor="#334155",
                    relief="flat", padding=5)
    style.map("TCombobox", fieldbackground=[('readonly', COLOR_BLANCO)], bordercolor=[('focus', FOCUS_COLOR)], lightcolor=[('focus', FOCUS_COLOR)], darkcolor=[('focus', FOCUS_COLOR)])
    
    # BOTONES
    style.configure("Accion.TButton",
                    background=COLOR_ACCENT, foreground="#ffffff",
                    borderwidth=0, font=('Segoe UI', 10, 'bold'), padding=6)
    style.map("Accion.TButton", background=[('active', COLOR_ACCENT_HOVER)])

    style.configure("Cerrar.TButton",
                    background=COLOR_DANGER, foreground="white",
                    borderwidth=0, font=('Segoe UI', 10, 'bold'), padding=6)
    style.map("Cerrar.TButton", background=[('active', "#dc2626")])

    # TABLAS
    style.configure("Treeview", background=COLOR_BLANCO, foreground="#334155", fieldbackground=COLOR_BLANCO, rowheight=28, borderwidth=0)
    style.configure("Treeview.Heading", background="#e2e8f0", foreground="#1e293b", font=('Segoe UI', 10, 'bold'), relief="flat")
    style.map("Treeview.Heading", background=[('active', '#cbd5e1')])

# ==============================================================================
# V. VENTANAS SECUNDARIAS
# ==============================================================================

def abrir_añadir_alumno(root):
    w = tk.Toplevel(root); w.withdraw(); w.title("Gestor de Alumnos"); w.config(bg=COLOR_FONDO)
    # ALUMNOS NO TIENE CALENDARIO -> PUEDE SER MODAL (GRAB_SET)
    w.transient(root); w.grab_set(); w.focus_force()
    centrar_ventana(w, 700, 550); w.resizable(False, False)

    ttk.Label(w, text="👨‍🎓 GESTOR DE ALUMNOS", font=('Segoe UI', 16, 'bold'), foreground="#1e293b").pack(pady=20)
    frame = ttk.Frame(w, padding=20); frame.pack(fill='both', padx=10); frame.grid_columnconfigure(1, weight=1)

    n_var = tk.StringVar(); c_var = tk.StringVar(); ancho = 30 
    ttk.Label(frame, text='Nombre:').grid(row=0, column=0, pady=10, sticky='w')
    ttk.Entry(frame, textvariable=n_var, width=ancho).grid(row=0, column=1, pady=10, padx=(20, 0), sticky='ew')
    ttk.Label(frame, text='Correo:').grid(row=1, column=0, pady=10, sticky='w')
    ttk.Entry(frame, textvariable=c_var, width=ancho).grid(row=1, column=1, pady=10, padx=(20, 0), sticky='ew')

    bts = ttk.Frame(frame); bts.grid(row=2, column=0, columnspan=2, pady=30)
    
    ttk.Button(bts, text="Registrar", style="Accion.TButton", cursor="hand2", command=lambda: registrar_alumno(n_var, c_var, tree, limpiar_campos)).pack(side='left', padx=5)
    ttk.Button(bts, text="Borrar", style="Accion.TButton", cursor="hand2", command=lambda: borrar_alumno(tree)).pack(side='left', padx=5)
    ttk.Button(bts, text="Limpiar", style="Accion.TButton", cursor="hand2", command=lambda: limpiar_campos(n_var, c_var)).pack(side='left', padx=5)
    ttk.Button(bts, text="Cerrar", style="Cerrar.TButton", cursor="hand2", command=w.destroy).pack(side='left', padx=5)

    tf = ttk.Frame(w, padding=10); tf.pack(fill='both', expand=True)
    sb = ttk.Scrollbar(tf, orient=tk.VERTICAL); sb.pack(side=tk.RIGHT, fill='y')
    tree = ttk.Treeview(tf, columns=("ID", "Nombre", "Correo"), show='headings', yscrollcommand=sb.set)
    tree.pack(fill='both', expand=True); sb.config(command=tree.yview)
    tree.column("ID", width=50, anchor='center'); tree.column("Nombre", width=280); tree.column("Correo", width=280)
    tree.heading("ID", text="ID"); tree.heading("Nombre", text="Nombre"); tree.heading("Correo", text="Correo")
    cargar_alumnos(tree)
    w.deiconify()

def abrir_añadir_curso(root):
    w = tk.Toplevel(root); w.withdraw(); w.title("Gestor de Cursos"); w.config(bg=COLOR_FONDO)
    w.transient(root); w.grab_set(); w.focus_force()
    centrar_ventana(w, 750, 550); w.resizable(False, False)

    ttk.Label(w, text="📚 GESTOR DE CURSOS", font=('Segoe UI', 16, 'bold'), foreground="#1e293b").pack(pady=20)
    frame = ttk.Frame(w, padding=20); frame.pack(fill='both', padx=10); frame.grid_columnconfigure(1, weight=1)

    n_var = tk.StringVar()
    # TEXT ESTILIZADO
    d_txt = tk.Text(frame, height=4, width=30, font=('Segoe UI', 10),
                    bd=0, relief="flat", highlightthickness=1, 
                    highlightbackground=BORDER_COLOR, highlightcolor=FOCUS_COLOR,
                    padx=5, pady=5)

    def on_focus_in(e): e.widget.config(highlightbackground=FOCUS_COLOR)
    def on_focus_out(e): e.widget.config(highlightbackground=BORDER_COLOR)
    d_txt.bind("<FocusIn>", on_focus_in); d_txt.bind("<FocusOut>", on_focus_out)

    ttk.Label(frame, text='Nombre:').grid(row=0, column=0, pady=10, sticky='w')
    ttk.Entry(frame, textvariable=n_var).grid(row=0, column=1, pady=10, padx=(20, 0), sticky='ew') 
    ttk.Label(frame, text='Descripción:').grid(row=1, column=0, pady=10, sticky='nw')
    d_txt.grid(row=1, column=1, pady=10, padx=(20, 0), sticky='ew')

    bts = ttk.Frame(frame); bts.grid(row=2, column=0, columnspan=2, pady=30)
    ttk.Button(bts, text="Registrar", style="Accion.TButton", cursor="hand2", command=lambda: registrar_curso(n_var, d_txt, tree, limpiar_campos_curso)).pack(side='left', padx=5)
    ttk.Button(bts, text="Borrar", style="Accion.TButton", cursor="hand2", command=lambda: borrar_curso(tree)).pack(side='left', padx=5)
    ttk.Button(bts, text="Limpiar", style="Accion.TButton", cursor="hand2", command=lambda: limpiar_campos_curso(n_var, d_txt)).pack(side='left', padx=5)
    ttk.Button(bts, text="Cerrar", style="Cerrar.TButton", cursor="hand2", command=w.destroy).pack(side='left', padx=5)

    tf = ttk.Frame(w, padding=10); tf.pack(fill='both', expand=True)
    sb = ttk.Scrollbar(tf, orient=tk.VERTICAL); sb.pack(side=tk.RIGHT, fill='y')
    tree = ttk.Treeview(tf, columns=("ID", "Nombre", "Desc"), show='headings', yscrollcommand=sb.set)
    tree.pack(fill='both', expand=True); sb.config(command=tree.yview)
    tree.column("ID", width=50, anchor='center'); tree.column("Nombre", width=200); tree.column("Desc", width=450)
    tree.heading("ID", text="ID"); tree.heading("Nombre", text="Nombre"); tree.heading("Desc", text="Descripción")
    cargar_cursos(tree)
    w.deiconify()

def abrir_gestion_tareas(root):
    w = tk.Toplevel(root); w.withdraw(); w.title("Gestor de Tareas"); w.config(bg=COLOR_FONDO)
    
    # --- CORRECCIÓN CALENDARIO ---
    # Para evitar que el calendario se cierre al clickar,
    # esta ventana NO DEBE TENER grab_set() ni transient().
    # Es una ventana independiente.
    w.focus_force() 
    
    centrar_ventana(w, 800, 600); w.resizable(False, False)

    ttk.Label(w, text="📝 GESTOR DE TAREAS", font=('Segoe UI', 16, 'bold'), foreground="#1e293b").pack(pady=20)
    t_var = tk.StringVar(); f_var = tk.StringVar(); c_var = tk.StringVar()
    frame = ttk.Frame(w, padding=20); frame.pack(fill='both', padx=10)
    gf = ttk.Frame(frame); gf.pack(fill='x'); gf.grid_columnconfigure(1, weight=1)

    ttk.Label(gf, text='Título:').grid(row=0, column=0, pady=10, sticky='e')
    ttk.Entry(gf, textvariable=t_var).grid(row=0, column=1, pady=10, sticky='ew', padx=10)
    
    # CALENDARIO
    ttk.Label(gf, text='Fecha (Y-M-D):').grid(row=1, column=0, pady=10, sticky='e')
    cal = DateEntry(gf, textvariable=f_var, width=12, background=COLOR_ACCENT,
                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    cal.grid(row=1, column=1, pady=10, sticky='ew', padx=10)

    ttk.Label(gf, text='Curso:').grid(row=2, column=0, pady=10, sticky='e')
    lst = obt_cursos(); cb = ttk.Combobox(gf, textvariable=c_var, values=lst, state='readonly')
    cb.grid(row=2, column=1, pady=10, sticky='ew', padx=10); 
    if lst: cb.current(0)

    bts = ttk.Frame(frame); bts.pack(pady=30)
    ttk.Button(bts, text="Registrar", style="Accion.TButton", cursor="hand2", command=lambda: reg_tarea(t_var, f_var, c_var, tree, limp_tarea)).pack(side='left', padx=5)
    ttk.Button(bts, text="Borrar", style="Accion.TButton", cursor="hand2", command=lambda: del_tarea(tree)).pack(side='left', padx=5)
    ttk.Button(bts, text="Limpiar", style="Accion.TButton", cursor="hand2", command=lambda: limp_tarea(t_var, f_var, c_var)).pack(side='left', padx=5)
    ttk.Button(bts, text="Cerrar", style="Cerrar.TButton", cursor="hand2", command=w.destroy).pack(side='left', padx=5)

    tf = ttk.Frame(w, padding=10); tf.pack(fill='both', expand=True)
    sb = ttk.Scrollbar(tf, orient=tk.VERTICAL); sb.pack(side=tk.RIGHT, fill='y')
    tree = ttk.Treeview(tf, columns=("ID", "Tit", "Fec", "Cur"), show='headings', yscrollcommand=sb.set)
    tree.pack(fill='both', expand=True); sb.config(command=tree.yview)
    tree.column("ID", width=50, anchor='center'); tree.column("Tit", width=300); tree.column("Fec", width=120); tree.column("Cur", width=280)
    tree.heading("ID", text="ID"); tree.heading("Tit", text="Título"); tree.heading("Fec", text="Fecha"); tree.heading("Cur", text="Curso")
    cargar_tareas(tree)
    w.deiconify()

def abrir_gestion_entregas(root):
    w = tk.Toplevel(root); w.withdraw(); w.title("Gestor de Entregas"); w.config(bg=COLOR_FONDO)
    
    w.focus_force()
    
    centrar_ventana(w, 900, 600); w.resizable(False, False)

    ttk.Label(w, text="📦 GESTOR DE ENTREGAS", font=('Segoe UI', 16, 'bold'), foreground="#1e293b").pack(pady=20)
    f_var = tk.StringVar(); n_var = tk.StringVar(); a_var = tk.StringVar(); t_var = tk.StringVar()
    frame = ttk.Frame(w, padding=20); frame.pack(fill='both', padx=10)
    gf = ttk.Frame(frame); gf.pack(fill='x'); gf.grid_columnconfigure(1, weight=1)

    ttk.Label(gf, text='Alumno:').grid(row=0, column=0, pady=10, sticky='e')
    la = obt_alum(); ca = ttk.Combobox(gf, textvariable=a_var, values=la, state='readonly')
    ca.grid(row=0, column=1, pady=10, sticky='ew', padx=10); 
    if la: ca.current(0)
    ttk.Label(gf, text='Tarea:').grid(row=1, column=0, pady=10, sticky='e')
    lt = obt_tar(); ct = ttk.Combobox(gf, textvariable=t_var, values=lt, state='readonly')
    ct.grid(row=1, column=1, pady=10, sticky='ew', padx=10); 
    if lt: ct.current(0)
    
    # CALENDARIO
    ttk.Label(gf, text='Fecha:').grid(row=2, column=0, pady=10, sticky='e')
    cal = DateEntry(gf, textvariable=f_var, width=12, background=COLOR_ACCENT,
                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    cal.grid(row=2, column=1, pady=10, sticky='ew', padx=10)

    ttk.Label(gf, text='Nota:').grid(row=3, column=0, pady=10, sticky='e')
    ttk.Entry(gf, textvariable=n_var).grid(row=3, column=1, pady=10, sticky='ew', padx=10)

    bts = ttk.Frame(frame); bts.pack(pady=30)
    ttk.Button(bts, text="Registrar", style="Accion.TButton", cursor="hand2", command=lambda: reg_ent(f_var, n_var, a_var, t_var, tree)).pack(side='left', padx=5)
    ttk.Button(bts, text="Borrar", style="Accion.TButton", cursor="hand2", command=lambda: del_ent(tree)).pack(side='left', padx=5)
    ttk.Button(bts, text="Limpiar", style="Accion.TButton", cursor="hand2", command=lambda: limp_ent(f_var, n_var, a_var, t_var)).pack(side='left', padx=5)
    ttk.Button(bts, text="Cerrar", style="Cerrar.TButton", cursor="hand2", command=w.destroy).pack(side='left', padx=5)

    tf = ttk.Frame(w, padding=10); tf.pack(fill='both', expand=True)
    sb = ttk.Scrollbar(tf, orient=tk.VERTICAL); sb.pack(side=tk.RIGHT, fill='y')
    tree = ttk.Treeview(tf, columns=("ID","Fec","Not","Alu","Tar"), show='headings', yscrollcommand=sb.set)
    tree.pack(fill='both', expand=True); sb.config(command=tree.yview)
    tree.column("ID", width=50, anchor='center'); tree.column("Fec", width=100, anchor='center'); tree.column("Not", width=60, anchor='center')
    tree.column("Alu", width=280); tree.column("Tar", width=350)
    tree.heading("ID", text="ID"); tree.heading("Fec", text="Fecha"); tree.heading("Not", text="Nota"); tree.heading("Alu", text="Alumno"); tree.heading("Tar", text="Tarea")
    carg_ent(tree)
    w.deiconify()

# ==============================================================================
# VI. VENTANA PRINCIPAL
# ==============================================================================

def crear_boton_sidebar(parent, text, icon, command):
    btn_frame = tk.Frame(parent, bg=COLOR_SIDEBAR); btn_frame.pack(fill='x', pady=5)
    btn = tk.Button(btn_frame, text=f"  {icon}   {text}", font=("Segoe UI", 11),
                    bg=COLOR_SIDEBAR, fg=COLOR_TEXTO_SIDE, bd=0, anchor="w", cursor="hand2",
                    padx=20, pady=10, command=command)
    btn.pack(fill='x')
    btn.bind("<Enter>", lambda e: btn.config(bg="#334155")) 
    btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_SIDEBAR))
    return btn

def main():
    root = tk.Tk(); root.withdraw(); root.title("Codearts Solutions - Dashboard")
    centrar_ventana(root, 800, 450)
    configurar_estilos_tema()

    sidebar = tk.Frame(root, bg=COLOR_SIDEBAR, width=250)
    sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)
    content = tk.Frame(root, bg=COLOR_FONDO)
    content.pack(side="right", fill="both", expand=True)

    tk.Label(sidebar, text="CODEARTS", font=("Arial", 16, "bold"), bg=COLOR_SIDEBAR, fg="white").pack(pady=40)
    crear_boton_sidebar(sidebar, "Alumnos", "👨‍🎓", lambda: abrir_añadir_alumno(root))
    crear_boton_sidebar(sidebar, "Cursos", "📚", lambda: abrir_añadir_curso(root))
    crear_boton_sidebar(sidebar, "Tareas", "📝", lambda: abrir_gestion_tareas(root))
    crear_boton_sidebar(sidebar, "Entregas", "📤", lambda: abrir_gestion_entregas(root))
    
    tk.Label(sidebar, bg=COLOR_SIDEBAR).pack(expand=True, fill='both') 
    
    btn_salir = tk.Button(sidebar, text="  ❌   Salir", font=("Segoe UI", 11, "bold"),
                          bg=COLOR_DANGER, fg="white", bd=0, anchor="w", padx=20, pady=10,
                          cursor="hand2", command=root.destroy)
    btn_salir.pack(fill='x', side="bottom")
    btn_salir.bind("<Enter>", lambda e: btn_salir.config(bg="#dc2626"))
    btn_salir.bind("<Leave>", lambda e: btn_salir.config(bg=COLOR_DANGER))

    tk.Label(content, text="Bienvenido al Gestor Académico", font=("Segoe UI", 24, "bold"), bg=COLOR_FONDO, fg="#1e293b").pack(pady=(100, 20))
    tk.Label(content, text="Selecciona una opción del menú lateral para comenzar.", font=("Segoe UI", 12), bg=COLOR_FONDO, fg="#64748b").pack()

    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()
