import sqlite3
import pandas as pd
import os
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = "mi_clave_segura"

# Ruta del archivo Excel
excel_path = 'data/Población 27-08-2024.xlsx'
# Ruta del archivo Excel
excel_path_uac = 'data/plan_de_estudios.xlsx'
excel_path_docentes = 'data/ADocentes.xlsx'

# Ruta de la base de datos
db_path = 'mi_base_de_datos.db'


# Función para borrar la tabla y volver a crearla
def resetear_tabla():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Borrar la tabla si existe
        cursor.execute("DROP TABLE IF EXISTS estudiantes;")
        
        # Crear la tabla nuevamente con la estructura correcta
        cursor.execute('''
            CREATE TABLE estudiantes (
                matricula TEXT PRIMARY KEY,
                nombre TEXT,
                sexo TEXT,
                curp TEXT,
                domicilio TEXT,
                colonia TEXT,
                cp TEXT,
                ciudad TEXT,
                municipio TEXT,
                tel_casa TEXT,
                tel_celular TEXT,
                email TEXT,
                grupo TEXT,
                nombre_padre TEXT,
                nombre_madre TEXT
            )
        ''')
        
        conn.commit()
        print("Tabla estudiantes reiniciada.")

# Función para cargar los datos de Excel en SQLite
def cargar_datos():
    df = pd.read_excel(excel_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO estudiantes (matricula, nombre, sexo, curp, domicilio, colonia, cp, ciudad, municipio, tel_casa, tel_celular, email, grupo, 
                nombre_padre, nombre_madre)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Matricula'], row['Nombre completo del Alumno (a)'], row['Sexo'], row['CURP'], row['Domicilio'],
                row['Colonia'], row['CP'], row['Ciudad'], row['Municipio'], row['Tel Casa'], row['Tel Celular'], row['E-Mail'],
                row['Grupo'], row['Nombre del padre'], row['Nombre de la madre']
            ))

        conn.commit()
        print("Datos cargados correctamente.")


# Función para borrar la tabla y volver a crearla
def resetear_tabla_asignatura():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Borrar la tabla si existe
        cursor.execute("DROP TABLE IF EXISTS uac;")
        
        # Crear la tabla con la estructura del Excel
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uac (
                id INTEGER PRIMARY KEY,
                clave TEXT,
                asignatura TEXT,
                hsm REAL,
                semestre INTEGER,
                componente TEXT,
                capacitacion TEXT,
                plan_estudios TEXT,
                hsm_paraesc REAL
            )
        ''')
        
        conn.commit()
        print("Tabla uac reiniciada.")

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_uac():
    if request.method == 'POST':
        clave = request.form['clave']
        asignatura = request.form['asignatura']
        hsm = request.form['hsm']
        semestre = request.form['semestre']
        componente = request.form['componente']
        capacitacion = request.form['capacitacion']
        plan_estudios = request.form['plan_estudios']
        hsm_paraesc = request.form['hsm_paraesc']

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO uac (clave, asignatura, hsm, semestre, componente, capacitacion, plan_estudios, hsm_paraesc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (clave, asignatura, hsm, semestre, componente, capacitacion, plan_estudios, hsm_paraesc))
            conn.commit()
        
        flash('UAC agregada correctamente.')
        return redirect(url_for('formulario_docentes'))


    return render_template('agregar_uac.html')

# Función para cargar los datos de Excel en SQLite
def cargar_datos_asignatura():
    df = pd.read_excel(excel_path_uac)

    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO uac (id, clave, asignatura, hsm, semestre, componente, capacitacion, plan_estudios, hsm_paraesc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Id'], row['Clave'], row['Asignatura'], row['HSM'], row['Semestre'], row['Componente'], 
                row['Capacitación'], row['Plan de Estudios'], row['HSM Paraesc']
            ))
        
        conn.commit()
        print("Datos cargados correctamente.")

# Función para borrar la tabla y volver a crearla
def resetear_tabla_docentes():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Borrar la tabla si existe
        cursor.execute("DROP TABLE IF EXISTS docentes;")
        
        # Crear la tabla con todos los HSM
        cursor.execute('''
            CREATE TABLE docentes (
                no_empleado TEXT PRIMARY KEY,
                apellidos TEXT,
                nombre TEXT,
                categoria TEXT,
                hsm_base Real
            )
        ''')
        
        conn.commit()
        print("Tabla docentes reiniciada.")


# Función para cargar los datos de Excel en SQLite
def cargar_datos_docentes():
    df = pd.read_excel(excel_path_docentes)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO docentes (no_empleado, apellidos, nombre, categoria, hsm_base)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                row['No_Empleado'], 
                row['Apellidos'],
                row['Nombre'],
                row['Categoría/Horario'], 
                row['HSM_Base']
            ))
        
        conn.commit()
        print("Datos cargados correctamente.")

@app.route("/agregar_docente", methods=["GET", "POST"])
def agregar_docente():
    if request.method == "POST":
        # Aquí capturas los datos del formulario y los agregas a la base de datos
        no_empleado = request.form["no_empleado"]
        apellidos = request.form["apellidos"]
        nombre = request.form["nombre"]
        categoria = request.form["categoria"]
        hsm_base = request.form["hsm_base"]

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO docentes (no_empleado, apellidos, nombre, categoria, hsm_base)
                VALUES (?, ?, ?, ?, ?)
            ''', (no_empleado, apellidos, nombre, categoria, hsm_base))
            conn.commit()

        return redirect(url_for('formulario_docentes'))

    return render_template("agregar_docente.html")


# Ruta para mostrar y procesar el formulario
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    mensaje = ""
    estudiante = None
    matricula = ""

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM estudiantes WHERE matricula = ?", (matricula,))
            estudiante = cursor.fetchone()
            if estudiante:
                mensaje = "Estudiante encontrado."
            else:
                mensaje = "Estudiante no encontrado."

    return render_template('formulario.html', mensaje=mensaje, estudiante=estudiante,matricula=matricula)


def tabla_reporte_docente():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes_docentes (
                folio INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT NOT NULL,
                periodo TEXT NOT NULL,
                fecha_reporte TEXT,
                nombre_docente INTEGER NOT NULL,
                asignatura INTEGER NOT NULL,
                motivo TEXT NOT NULL,
                otro_motivo TEXT,
                reportes_cantidad INTEGER,
                observaciones TEXT,
                FOREIGN KEY (nombre_docente) REFERENCES docentes(no_empleado),
                FOREIGN KEY (matricula) REFERENCES estudiantes(matricula)
                FOREIGN KEY (asignatura) REFERENCES uac(id)
            )
        ''')
        conn.commit()
        print("✅ Tabla reportes_docentes creada correctamente.")

@app.route("/formulario_docentes", methods=["GET", "POST"])
def formulario_docentes():
    mensaje = ""
    estudiante = None
    matricula = ""
    docentes = []  # Asegurar que la variable exista
    asignaturas = []  # Asegurar que la variable exista
    reportes_cantidad = 0
    nuevo_folio = 1  # Valor por defecto

    if request.method == 'POST':
        matricula = request.form.get('matricula')

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Buscar al estudiante
            cursor.execute("SELECT * FROM estudiantes WHERE matricula = ?", (matricula,))
            estudiante = cursor.fetchone()
            if estudiante:
                mensaje = "Estudiante encontrado."

                # Contar reportes del estudiante
                cursor.execute("SELECT COUNT(*) FROM reportes_docentes WHERE matricula = ?", (matricula,))
                reportes_cantidad = cursor.fetchone()[0]

                # Obtener el siguiente folio automáticamente
                cursor.execute("SELECT MAX(folio) FROM reportes_docentes")
                max_folio = cursor.fetchone()[0]
                nuevo_folio = int(max_folio) + 1 if max_folio else 1  # Si no hay folios, empieza en 1

            else:
                mensaje = "Estudiante no encontrado."

            # Obtener la lista de docentes
            cursor.execute("SELECT no_empleado, apellidos, nombre FROM docentes")
            docentes = cursor.fetchall()

            # Obtener la lista de asignaturas
            cursor.execute("SELECT id, asignatura FROM uac")
            asignaturas = cursor.fetchall()

    return render_template('formulario_docentes.html', mensaje=mensaje, estudiante=estudiante, matricula=matricula, 
                           docentes=docentes, asignaturas=asignaturas, 
                           reportes_cantidad=reportes_cantidad, nuevo_folio=nuevo_folio)

@app.route("/guardar_reporte", methods=["POST"])
def guardar_reporte():
    folio = request.form.get('folio')
    matricula = request.form.get('matricula')
    periodo = request.form.get('periodo')
    fecha = request.form.get('fecha')
    docente_id = request.form.get('nombre_docente')  # Asegurar que llega un valor correcto
    asignatura_id = request.form.get('asignatura')
    motivo = request.form.get('motivo')
    otro_motivo = request.form.get('otro_motivo')
    observaciones = request.form.get('observaciones')

    print(f"Docente ID recibido: {docente_id}")  # Debug

    if not docente_id:
        return "Error: No se seleccionó un docente", 400  # Evitar insertar valores nulos

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reportes_docentes 
            (folio, matricula, periodo, fecha_reporte, nombre_docente, asignatura, motivo, otro_motivo, observaciones,reportes_cantidad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        ''', (folio, matricula, periodo,fecha, docente_id, asignatura_id, motivo, otro_motivo, observaciones,request.form.get('reportes_cantidad', 0)))
        conn.commit()

    return redirect(f'/generar_reporte/{folio}')

@app.route("/generar_reporte/<folio>", methods=["GET"])
def generar_reporte(folio):
    # Conectar a la base de datos y obtener los datos necesarios
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Obtener el reporte
        cursor.execute("SELECT * FROM reportes_docentes WHERE folio = ?", (folio,))
        reporte = cursor.fetchone()

        if reporte:
            # Extraer datos del reporte
            folio = reporte[0]
            matricula = reporte[1]
            periodo = reporte[2]
            fecha = reporte[3]
            id_docente = reporte[4]  # Esto es el ID del docente, no el nombre
            id_asignatura = reporte[5]  # Esto es el ID de la asignatura, no el nombre
            motivo = reporte[6]
            otro_motivo = reporte[7] if motivo == "Otros" else ""
            observaciones = reporte[8]

            # Obtener el nombre del estudiante
            cursor.execute("SELECT nombre FROM estudiantes WHERE matricula = ?", (matricula,))
            estudiante = cursor.fetchone()
            estudiante = estudiante[0] if estudiante else "No encontrado"

            # Obtener el nombre del docente
            cursor.execute("SELECT nombre, apellidos FROM docentes WHERE no_empleado = ?", (id_docente,))
            docente = cursor.fetchone()
            nombre_docente = f"{docente[0]} {docente[1]}" if docente else "No encontrado"


            # Obtener el nombre de la asignatura
            cursor.execute("SELECT asignatura FROM uac WHERE id = ?", (id_asignatura,))
            asignatura = cursor.fetchone()
            nombre_asignatura = asignatura[0] if asignatura else "No encontrada"

            return render_template("reporte_docente.html", 
                                   folio=folio, 
                                   estudiante=estudiante, 
                                   matricula=matricula,
                                   nombre_docente=nombre_docente, 
                                   asignatura=nombre_asignatura, 
                                   periodo=periodo, 
                                   fecha=fecha,
                                   motivo=motivo, 
                                   otro_motivo=otro_motivo,
                                   observaciones=observaciones)
        else:
            return "Reporte no encontrado", 404


def eliminar_tabla_reporte_docente():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS reportes_docentes;")
        conn.commit()
        print("❌ Tabla reportes_docentes eliminada correctamente.")
# Ruta para guardar el justificante
@app.route('/justificante', methods=['POST'])
def justificante():
    matricula = request.form.get('matricula')
    fecha_justificar = request.form.get('fecha_justificar')
    motivo = request.form.get('motivo')
    documentos=request.form.get('documentos')
    motivo_otros = request.form.get('motivo_otros', '')
    documento_otros=request.form.get('documento_otros','')
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM estudiantes WHERE matricula = ?", (matricula,))
        estudiante = cursor.fetchone()

    if estudiante:
       nombre_estudiante = estudiante[0]
    else:
        nombre_estudiante = "Desconocido"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS justificantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT,
                fecha_justificar TEXT,
                motivo TEXT,
                documentos TEXT,
                motivo_otros TEXT,
                documento_otros TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO justificantes (matricula, fecha_justificar, motivo, documentos, motivo_otros, documento_otros)
            VALUES (?, ?, ?, ?, ?,?)
        ''', (matricula, fecha_justificar, motivo, documentos, motivo_otros,documento_otros))
        conn.commit()

    return render_template('justificante.html', 
                            nombre_estudiante=nombre_estudiante, 
                            matricula=matricula, 
                            fecha_justificar=fecha_justificar, 
                            motivo=motivo, 
                            documentos=documentos, 
                            motivo_otros=motivo_otros,
                            documento_otros=documento_otros)


@app.route('/')
def menu():
    return render_template('menu.html')

# Crear la tabla de reportes si no existe
def crear_tabla_reportes():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT,
                grado TEXT,
                grupo TEXT,
                motivo TEXT,
                sancion TEXT,
                detalles TEXT,
                FOREIGN KEY (matricula) REFERENCES estudiantes(matricula)
            )
        ''')
        conn.commit()

# Ruta principal para buscar estudiante
@app.route("/reportes", methods=["GET", "POST"])
def reportes():
    mensaje = ""
    estudiante = None
    matricula = ""

    if request.method == "POST":
        if "buscar_matricula" in request.form:
            matricula = request.form["matricula"]
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM estudiantes WHERE matricula = ?", (matricula,))
                estudiante = cursor.fetchone()
                mensaje = "Estudiante encontrado." if estudiante else "Estudiante no encontrado."
        elif "guardar_reporte" in request.form:
            matricula = request.form["matricula"]
            grado = request.form["grado"]
            grupo = request.form["grupo"]
            motivo = request.form.getlist("motivo[]")  # Lista de motivos seleccionados
            motivo_str = ", ".join(motivo)  # Convertir la lista en una cadena de texto
            sancion = request.form["sancion"]
            detalles = request.form.get("detalles","")

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reportes (matricula, grado, grupo, motivo, sancion, detalles)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (matricula, grado, grupo, motivo_str, sancion, detalles))
                conn.commit()
            flash("Reporte guardado exitosamente.", "success")
            return redirect(url_for("reportes"))

    return render_template("reportes.html", mensaje=mensaje, estudiante=estudiante, matricula=matricula)

@app.route('/base_datos')
def mostrar_base_datos():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudiantes")
        estudiantes = cursor.fetchall()
    
    return render_template('base_datos.html', estudiantes=estudiantes)

@app.route('/cargar_archivo', methods=['POST'])
def cargar_archivo():
    archivo = request.files['archivo']
    if archivo:
        # Crear carpeta de uploads si no existe
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        # Guardar el archivo temporalmente
        filename = secure_filename(archivo.filename)
        temp_path = os.path.join('uploads', filename)
        archivo.save(temp_path)

        # Cargar datos en la base de datos
        df = pd.read_excel(temp_path, engine='xlrd')

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for _, row in df.iterrows():
                matricula = row['Matricula']
                cursor.execute("SELECT COUNT(*) FROM estudiantes WHERE matricula = ?", (matricula,))
                existe = cursor.fetchone()[0]

                if existe:
                    # Si la matrícula ya existe, actualizar los datos
                    cursor.execute('''
                        UPDATE estudiantes
                        SET nombre = ?, sexo = ?, curp = ?, domicilio = ?, colonia = ?, cp = ?, ciudad = ?, municipio = ?, 
                            tel_casa = ?, tel_celular = ?, email = ?, grupo = ?, nombre_padre = ?, nombre_madre = ?
                        WHERE matricula = ?
                    ''', (
                        row['Nombre completo del Alumno (a)'], row['Sexo'], row['CURP'], row['Domicilio'], row['Colonia'],
                        row['CP'], row['Ciudad'], row['Municipio'], row['Tel Casa'], row['Tel Celular'], row['E-Mail'], row['Grupo'],
                        row['Nombre del padre'], row['Nombre de la madre'], matricula
                    ))
                else:
                    # Si no existe, insertar los nuevos datos
                    cursor.execute('''
                        INSERT INTO estudiantes (matricula, nombre, sexo, curp, domicilio, colonia, cp, ciudad, municipio, 
                        tel_casa, tel_celular, email, grupo, nombre_padre, nombre_madre)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        matricula, row['Nombre completo del Alumno (a)'], row['Sexo'], row['CURP'], row['Domicilio'],
                        row['Colonia'], row['CP'], row['Ciudad'], row['Municipio'], row['Tel Casa'], row['Tel Celular'], row['E-Mail'],
                        row['Grupo'], row['Nombre del padre'], row['Nombre de la madre']
                    ))

            conn.commit()

        # Eliminar el archivo temporal
        os.remove(temp_path)
        flash("Archivo procesado correctamente. Datos actualizados/agregados en la base de datos.", "success")
        return redirect(url_for("mostrar_base_datos"))

    flash("Error al cargar el archivo.", "danger")
    return redirect(url_for("menu"))


@app.route('/listar_justificantes')
def listar_justificantes():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, matricula, fecha_justificar, motivo, documentos, motivo_otros, documento_otros FROM justificantes")
        justificantes = cursor.fetchall()  # Trae todos los justificantes guardados

    return render_template('listar_justificantes.html', justificantes=justificantes)

@app.route('/editar_justificante/<int:id>', methods=['GET', 'POST'])
def editar_justificante(id):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        if request.method == 'POST':
            # Recoger los datos del formulario
            fecha_justificar = request.form.get('fecha_justificar')
            motivo = request.form.get('motivo')
            documentos = request.form.get('documentos')
            motivo_otros = request.form.get('motivo_otros', '')
            documento_otros = request.form.get('documento_otros', '')

            # Actualizar los datos en la base de datos
            cursor.execute('''
                UPDATE justificantes
                SET fecha_justificar = ?, motivo = ?, documentos = ?, motivo_otros = ?, documento_otros = ?
                WHERE id = ?
            ''', (fecha_justificar, motivo, documentos, motivo_otros, documento_otros, id))

            conn.commit()
            return "Justificante actualizado con éxito. <a href='/listar_justificantes'>Volver</a>"

        # Si es GET, mostrar los datos actuales
        cursor.execute("SELECT * FROM justificantes WHERE id = ?", (id,))
        justificante = cursor.fetchone()

    return render_template('editar_justificante.html', justificante=justificante)

@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_justificante(id):
    conn = sqlite3.connect('mi_base_de_datos.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM justificantes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/listar_justificantes')

@app.route('/cargar_y_mostrar')
def cargar_y_mostrar():
    return render_template('cargar_y_mostrar.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
