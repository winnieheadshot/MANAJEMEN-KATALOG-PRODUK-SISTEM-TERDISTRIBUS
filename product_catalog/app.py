from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from mysql.connector import Error
import database as db
import logging
from functools import wraps
from werkzeug.exceptions import BadRequest
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

class DatabaseConnectionError(Exception):
    pass

def db_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = None
        try:
            conn = db.get_db_connection()
            return f(conn, *args, **kwargs)
        except Error as e:
            logger.error(f"Database error: {e}")
            flash('An error occurred while accessing the database', 'error')
            return redirect(url_for('index'))
        finally:
            if conn and conn.is_connected():
                conn.close()
    return decorated_function

# Web Routes
@app.route('/')
@db_connection
def index(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    return render_template('index.html', products=products)

@app.route('/add', methods=['GET', 'POST'])
@db_connection
def add_product(conn):
    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            description = request.form['description']

            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO products (name, category, price, description) VALUES (%s, %s, %s, %s)',
                (name, category, price, description)
            )
            conn.commit()
            cursor.close()
            
            flash('Product added successfully!', 'success')
            return redirect(url_for('index'))
            
        except (ValueError, KeyError) as e:
            flash('Invalid input data', 'error')
            logger.error(f"Input error: {e}")
            return render_template('add.html'), 400
            
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@db_connection
def edit_product(conn, id):
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            category = request.form['category']
            price = float(request.form['price'])
            description = request.form['description']
            
            cursor.execute(
                'UPDATE products SET name = %s, category = %s, price = %s, description = %s WHERE id = %s',
                (name, category, price, description, id)
            )
            conn.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('index'))
            
        except ValueError as e:
            flash('Invalid input data', 'error')
            logger.error(f"Input error: {e}")
            return redirect(url_for('edit_product', id=id))
    
    cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
    product = cursor.fetchone()
    cursor.close()
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
        
    return render_template('edit.html', product=product)

@app.route('/delete/<int:id>')
@db_connection
def delete_product(conn, id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/search')
@db_connection
def search(conn):
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    
    cursor = conn.cursor(dictionary=True)
    
    if category:
        cursor.execute(
            'SELECT * FROM products WHERE category = %s AND name LIKE %s', 
            (category, f'%{query}%')
        )
    else:
        cursor.execute(
            'SELECT * FROM products WHERE name LIKE %s', 
            (f'%{query}%',)
        )
    
    products = cursor.fetchall()
    cursor.close()
    return render_template('index.html', products=products)

# API Routes
@app.route('/api/products', methods=['GET'])
@db_connection
def get_products(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    return jsonify({'products': products})

@app.route('/api/products/<int:id>', methods=['GET'])
@db_connection
def get_product(conn, id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
    product = cursor.fetchone()
    cursor.close()
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({'product': product})

@app.route('/api/products', methods=['POST'])
@db_connection
def create_product(conn):
    if not request.is_json:
        raise BadRequest("Content-Type must be application/json")
        
    data = request.get_json()
    required_fields = ['name', 'category', 'price']
    
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO products (name, category, price, description) VALUES (%s, %s, %s, %s)',
            (data['name'], data['category'], float(data['price']), data.get('description', ''))
        )
        product_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({
            'message': 'Product created successfully',
            'product_id': product_id
        }), 201
        
    except ValueError:
        return jsonify({'error': 'Invalid price value'}), 400

@app.route('/api/products/<int:id>', methods=['PUT'])
@db_connection
def update_product_api(conn, id):
    if not request.is_json:
        raise BadRequest("Content-Type must be application/json")
        
    data = request.get_json()
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
    
    if not cursor.fetchone():
        cursor.close()
        return jsonify({'error': 'Product not found'}), 404
        
    update_fields = []
    update_values = []
    
    for field in ['name', 'category', 'price', 'description']:
        if field in data:
            update_fields.append(f"{field} = %s")
            update_values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
        
    update_values.append(id)
    query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
    
    cursor.execute(query, update_values)
    conn.commit()
    cursor.close()
    
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:id>', methods=['DELETE'])
@db_connection
def delete_product_api(conn, id):
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM products WHERE id = %s', (id,))
    
    if not cursor.fetchone():
        cursor.close()
        return jsonify({'error': 'Product not found'}), 404
        
    cursor.execute('DELETE FROM products WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    
    return jsonify({'message': 'Product deleted successfully'})

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')