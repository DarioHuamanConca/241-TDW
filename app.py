from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash_messages'

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    query = request.args.get('q')
    conn = get_db_connection()
    if query:
        items = conn.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + query + '%',)).fetchall()
    else:
        items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    if name:
        conn = get_db_connection()
        conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        flash('¡Ítem agregado con éxito!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()
    
    if item is None:
        conn.close()
        flash('Error: El ítem no existe.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            conn.execute("UPDATE items SET name = ? WHERE id = ?", (name, id))
            conn.commit()
            conn.close()
            flash('¡Ítem actualizado!', 'info')
            return redirect(url_for('index'))
    
    conn.close()
    return render_template('form.html', item=item)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM items WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('Ítem eliminado.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Inicializar base de datos si no existe
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)')
    
    # Agregar datos de ejemplo si está vacía
    count = conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO items (name) VALUES ('Ejemplo 1: Aprender Flask')")
        conn.execute("INSERT INTO items (name) VALUES ('Ejemplo 2: Dominar Tailwind')")
        conn.commit()
    
    conn.close()
    app.run(debug=True)
