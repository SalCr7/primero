import sqlite3
import pandas as pd
import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename


app = Flask(__name__)

# Ruta del archivo Excel
excel_path = 'data/Población 27-08-2024.xlsx'

# Ruta de la base de datos
db_path = 'mi_base_de_datos.db'

# Función para cargar los datos de Excel en SQLite
def cargar_datos():
    if not os.path.exists(db_path):
        # Cargar datos del archivo Excel
        df = pd.read_excel(excel_path)

        # Crear la base de datos SQLite y la tabla
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
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
                    email TEXT
                )
            ''')

            # Insertar los datos de Excel en la tabla
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO estudiantes (matricula, nombre, sexo, curp, domicilio, colonia, cp, ciudad, municipio, tel_casa, tel_celular, email)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Matricula'], row['Nombre completo del Alumno (a)'], row['Sexo'], row['CURP'], row['Domicilio'],
                    row['Colonia'], row['CP'], row['Ciudad'], row['Municipio'], row['Tel Casa'], row['Tel Celular'], row['E-Mail']
                ))

            conn.commit()
        print("Datos cargados en la base de datos.")

# Llamar a la función para cargar los datos si la base de datos no existe
cargar_datos()

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

    return "Justificante registrado con éxito."

@app.route('/')
def menu():
    return render_template('menu.html')

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
        # Guardar el archivo temporalmente
        filename = secure_filename(archivo.filename)
        temp_path = os.path.join('uploads', filename)
        archivo.save(temp_path)

        # Cargar datos en la base de datos
        df = pd.read_excel(temp_path)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute('''
                    SELECT COUNT(*) FROM estudiantes WHERE matricula = ?
                ''', (row['Matricula'],))
                existe = cursor.fetchone()[0]

                if existe:
                    # Si la matrícula ya existe, actualizar los datos
                    cursor.execute('''
                        UPDATE estudiantes
                        SET nombre = ?, sexo = ?, curp = ?, domicilio = ?, colonia = ?, cp = ?, ciudad = ?, municipio = ?, tel_casa = ?, tel_celular = ?, email = ?
                        WHERE matricula = ?
                    ''', (
                        row['Nombre completo del Alumno (a)'], row['Sexo'], row['CURP'], row['Domicilio'], row['Colonia'],
                        row['CP'], row['Ciudad'], row['Municipio'], row['Tel Casa'], row['Tel Celular'], row['E-Mail'],
                        row['Matricula']
                    ))
                else:
                    # Si no existe, insertar los nuevos datos
                    cursor.execute('''
                        INSERT INTO estudiantes (matricula, nombre, sexo, curp, domicilio, colonia, cp, ciudad, municipio, tel_casa, tel_celular, email)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        row['Matricula'], row['Nombre completo del Alumno (a)'], row['Sexo'], row['CURP'], row['Domicilio'],
                        row['Colonia'], row['CP'], row['Ciudad'], row['Municipio'], row['Tel Casa'], row['Tel Celular'], row['E-Mail']
                    ))

            conn.commit()

        # Eliminar el archivo temporal
        os.remove(temp_path)
        return "Archivo cargado y datos actualizados en la base de datos."
    return "Error al cargar el archivo."

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
