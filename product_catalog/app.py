from flask import Flask, render_template, request, redirect, url_for, flash
import database as db

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        description = request.form['description']
        
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, category, price, description) VALUES (%s, %s, %s, %s)',
                      (name, category, price, description))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product added successfully!')
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        description = request.form['description']
        
        cursor.execute('UPDATE products SET name = %s, category = %s, price = %s, description = %s WHERE id = %s',
                      (name, category, price, description, id))
        conn.commit()
        flash('Product updated successfully!')
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit.html', product=product)

@app.route('/delete/<int:id>')
def delete_product(id):
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Product deleted successfully!')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    
    conn = db.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if category:
        cursor.execute('SELECT * FROM products WHERE category = %s AND name LIKE %s', 
                      (category, f'%{query}%'))
    else:
        cursor.execute('SELECT * FROM products WHERE name LIKE %s', (f'%{query}%',))
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)