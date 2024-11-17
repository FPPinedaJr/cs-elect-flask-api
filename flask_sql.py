from flask import Flask, jsonify, request
from http import HTTPStatus
import sqlite3

app = Flask(__name__)
DATABASE = 'data.sql'

# Initialize database schema
def initialize_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL
            )
        ''')
        conn.commit()

# Helper function to query database
def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        conn.commit()
    return (rv[0] if rv else None) if one else rv

# Home route
@app.route('/')
def hello_world():
    return 'Hello, World!'

# GET all books
@app.route('/api/books', methods=['GET'])
def get_books():
    books = query_db('SELECT * FROM books')
    data = [dict(book) for book in books]
    return jsonify({'success': True, 'data': data, 'total': len(data)}), HTTPStatus.OK

# GET a single book by ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = query_db('SELECT * FROM books WHERE id = ?', [book_id], one=True)
    if book:
        return jsonify({'success': True, 'data': dict(book)}), HTTPStatus.OK
    return jsonify({'success': False, 'error': 'Book not found'}), HTTPStatus.NOT_FOUND

# POST - Create a new book
@app.route('/api/books', methods=['POST'])
def create_book():
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['title', 'author', 'year']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': 'Missing fields'}), HTTPStatus.BAD_REQUEST

    query_db('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', 
             [data['title'], data['author'], data['year']])
    return jsonify({'success': True, 'message': 'Book created successfully'}), HTTPStatus.CREATED

# PUT - Update a book
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = query_db('SELECT * FROM books WHERE id = ?', [book_id], one=True)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), HTTPStatus.NOT_FOUND

    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    query_db('''
        UPDATE books
        SET title = ?, author = ?, year = ?
        WHERE id = ?
    ''', [data.get('title', book['title']), data.get('author', book['author']), data.get('year', book['year']), book_id])

    return jsonify({'success': True, 'message': 'Book updated successfully'}), HTTPStatus.OK

# DELETE - Remove a book
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = query_db('SELECT * FROM books WHERE id = ?', [book_id], one=True)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), HTTPStatus.NOT_FOUND

    query_db('DELETE FROM books WHERE id = ?', [book_id])
    return jsonify({'success': True, 'message': f'Book deleted successfully'}), HTTPStatus.OK

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True)
