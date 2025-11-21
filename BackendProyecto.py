import sqlite3

# Nombre de la base de datos
DB_NAME = 'ProyectoTkinter4.db'

def conectar_bd():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error BD: {e}")
        return None

def crear_tablas_iniciales():
    conn = conectar_bd()
    if conn is None: return
    try:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS ALUMNO (
            idalumno INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(150) NOT NULL,
            correo VARCHAR(150) NOT NULL UNIQUE
        );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS CURSO (
            idcurso INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(150) NOT NULL UNIQUE,
            descripcion TEXT
        );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS TAREA (
            idtarea INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo VARCHAR(100) NOT NULL,
            fecha_entrega DATE NOT NULL,
            cursoid INTEGER NOT NULL,
            FOREIGN KEY (cursoid) REFERENCES CURSO(idcurso)
        );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS ENTREGA (
            identrega INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_entrega DATE NOT NULL,
            nota DECIMAL(4, 2) NOT NULL,
            alumnoid INTEGER NOT NULL,
            tareaid INTEGER NOT NULL,
            FOREIGN KEY (alumnoid) REFERENCES ALUMNO(idalumno),
            FOREIGN KEY (tareaid) REFERENCES TAREA(idtarea)
        );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS CURSO_ALUMNO (
            fk_idalumno INTEGER NOT NULL,
            fk_idcurso INTEGER NOT NULL,
            PRIMARY KEY (fk_idalumno, fk_idcurso),
            FOREIGN KEY (fk_idalumno) REFERENCES ALUMNO(idalumno),
            FOREIGN KEY (fk_idcurso) REFERENCES CURSO(idcurso)
        );""")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creando tablas: {e}")
    finally:
        conn.close()

# --- CRUD ALUMNO ---
def insertar_alumno(nombre, correo):
    conn = conectar_bd()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("INSERT INTO ALUMNO (nombre, correo) VALUES (?, ?)", (nombre, correo))
        conn.commit()
        return c.lastrowid
    except: return None
    finally: conn.close()

def seleccionar_alumnos():
    conn = conectar_bd()
    if not conn: return []
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM ALUMNO")
        return c.fetchall()
    except: return []
    finally: conn.close()

def borrar_alumno(id_):
    conn = conectar_bd()
    if not conn: return False
    try:
        conn.execute("DELETE FROM ALUMNO WHERE idalumno=?", (id_,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- CRUD CURSO ---
def insertar_curso(nombre, desc):
    conn = conectar_bd()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("INSERT INTO CURSO (nombre, descripcion) VALUES (?, ?)", (nombre, desc))
        conn.commit()
        return c.lastrowid
    except: return None
    finally: conn.close()

def seleccionar_cursos():
    conn = conectar_bd()
    if not conn: return []
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM CURSO")
        return c.fetchall()
    except: return []
    finally: conn.close()

def borrar_curso(id_):
    conn = conectar_bd()
    if not conn: return False
    try:
        conn.execute("DELETE FROM CURSO WHERE idcurso=?", (id_,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- CRUD TAREA ---
def insertar_tarea(titulo, fecha, cursoid):
    conn = conectar_bd()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("INSERT INTO TAREA (titulo, fecha_entrega, cursoid) VALUES (?, ?, ?)", (titulo, fecha, cursoid))
        conn.commit()
        return c.lastrowid
    except: return None
    finally: conn.close()

def seleccionar_tareas():
    conn = conectar_bd()
    if not conn: return []
    try:
        c = conn.cursor()
        c.execute("SELECT T.idtarea, T.titulo, T.fecha_entrega, C.nombre FROM TAREA T INNER JOIN CURSO C ON T.cursoid = C.idcurso")
        return c.fetchall()
    except: return []
    finally: conn.close()

def borrar_tarea(id_):
    conn = conectar_bd()
    if not conn: return False
    try:
        conn.execute("DELETE FROM TAREA WHERE idtarea=?", (id_,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

# --- CRUD ENTREGA ---
def insertar_entrega(fecha, nota, alumnoid, tareaid):
    conn = conectar_bd()
    if not conn: return None
    try:
        c = conn.cursor()
        c.execute("INSERT INTO ENTREGA (fecha_entrega, nota, alumnoid, tareaid) VALUES (?, ?, ?, ?)", (fecha, nota, alumnoid, tareaid))
        conn.commit()
        return c.lastrowid
    except sqlite3.Error as e:
        print(f"Error insert entrega: {e}")
        return None
    finally: conn.close()

def seleccionar_entregas():
    conn = conectar_bd()
    if not conn: return []
    try:
        c = conn.cursor()
        sql = """SELECT E.identrega, E.fecha_entrega, E.nota, A.nombre, T.titulo 
                 FROM ENTREGA E 
                 INNER JOIN ALUMNO A ON E.alumnoid = A.idalumno
                 INNER JOIN TAREA T ON E.tareaid = T.idtarea"""
        c.execute(sql)
        return c.fetchall()
    except: return []
    finally: conn.close()

def borrar_entrega(id_):
    conn = conectar_bd()
    if not conn: return False
    try:
        conn.execute("DELETE FROM ENTREGA WHERE identrega=?", (id_,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()
