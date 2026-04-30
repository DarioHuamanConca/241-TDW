from flask import Flask, render_template, request, redirect, url_for, flash
import pymssql # Usamos pymssql para mejor compatibilidad con Docker/Linux
import os
import time

app = Flask(__name__)
app.secret_key = 'clave_secreta_docker'

# Configuración desde variables de entorno (Docker las pasará automáticamente)
DB_SERVER = os.environ.get('DB_SERVER', 'localhost')
DB_USER = os.environ.get('DB_USER', 'sa')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'TuPasswordFuerte123!')
DB_NAME = os.environ.get('DB_NAME', 'master')

def get_db_connection():
    # En Docker, a veces la DB tarda unos segundos en arrancar
    retries = 5
    while retries > 0:
        try:
            conn = pymssql.connect(
                server=DB_SERVER,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=True
            )
            return conn
        except Exception as e:
            print(f"Esperando a la base de datos... ({retries} intentos restantes)")
            time.sleep(5)
            retries -= 1
    raise Exception("No se pudo conectar a la base de datos después de varios intentos.")

@app.route('/')
def index():
    query = request.args.get('q')
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True) # as_dict facilita el uso en Jinja2
    
    if query:
        cursor.execute("SELECT id, name FROM items WHERE name LIKE %s", ('%' + query + '%',))
    else:
        cursor.execute("SELECT id, name FROM items")
    
    items = cursor.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    if name:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (name) VALUES (%s)", (name,))
        conn.close()
        flash('¡Agregado con éxito!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    
    if request.method == 'POST':
        name = request.form.get('name')
        cursor.execute("UPDATE items SET name = %s WHERE id = %d", (name, id))
        conn.close()
        flash('¡Actualizado!', 'info')
        return redirect(url_for('index'))
    
    cursor.execute("SELECT id, name FROM items WHERE id = %d", (id,))
    item = cursor.fetchone()
    conn.close()
    
    if item:
        return render_template('form.html', item=item)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = %d", (id,))
    conn.close()
    flash('Eliminado correctamente.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Inicialización de la tabla
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Verificamos si existe la tabla
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='items' AND xtype='U')
            CREATE TABLE items (
                id INT PRIMARY KEY IDENTITY(1,1),
                name NVARCHAR(255)
            )
        """)
        conn.close()
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")

    app.run(host='0.0.0.0', port=5000, debug=True)
