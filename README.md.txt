# 🎓 Gestor Académico

Sistema de gestión académica de escritorio desarrollado en **Python**. Diseñado con una interfaz gráfica moderna estilo **SaaS** (Software as a Service), priorizando la usabilidad (UX), la estética corporativa y la integridad de datos.

## 🚀 Descripción

Este proyecto es una solución **CRUD** (Create, Read, Update, Delete) completa para administrar entidades educativas. Permite gestionar el ciclo de vida de:
* **Alumnos**
* **Cursos**
* **Tareas**
* **Entregas y Calificaciones**

A diferencia de gestores básicos, este sistema implementa **restricciones SQL estrictas** y una interfaz reactiva que guía al usuario, evitando errores comunes y corrupción de datos.

## ✨ Características Clave

### 🎨 Interfaz de Usuario (UI/UX)
* **Estilo Corporativo:** Paleta de colores `Slate Blue` & `White` para un entorno de trabajo profesional y limpio.
* **Calendarios Integrados:** Uso de `tkcalendar` para selección de fechas intuitiva sin errores de formato.
* **Navegación Fluida:** Menú lateral tipo Dashboard y ventanas modales que se auto-centran en pantalla.
* **Feedback Visual:** Sistema de alertas personalizadas (no nativas del SO) que respetan la línea gráfica.

### 🛡️ Arquitectura y Datos
* **Backend SQL:** Base de datos SQLite3 optimizada.
* **Integridad Referencial:** El sistema protege los datos mediante `Foreign Keys`.
    * *Ejemplo:* No se puede borrar un alumno si tiene notas registradas. El sistema intercepta el error SQL y muestra un mensaje amigable al usuario explicándole la razón.
* **Arquitectura Modular:** Separación estricta entre Frontend (`FrontendProyecto.py`) y Backend (`BackendProyecto.py`).

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
| :--- | :--- |
| **Python 3.12+** | Lenguaje principal |
| **Tkinter** | Framework GUI estándar |
| **tkcalendar** | Librería de gestión de fechas |
| **SQLite3** | Motor de Base de Datos Relacional |

## ⚙️ Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/Gestor-Academico.git](https://github.com/TU_USUARIO/Gestor-Academico.git)
    cd Gestor-Academico
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Ejecutar la aplicación:**
    ```bash
    python FrontendProyecto.py
    ```
    *(La base de datos se generará automáticamente en la primera ejecución)*.

## 📄 Estructura de Datos

El sistema utiliza un modelo relacional para garantizar la consistencia:



* **Relaciones:**
    * Un **Curso** tiene muchas **Tareas**.
    * Una **Tarea** pertenece a un **Curso**.
    * Una **Entrega** vincula a un **Alumno** y una **Tarea**.

---
Desarrollado con ❤️ y Python.
