#####################################################################################
######            NOTE: Running the test will CLEAR the database               ######
#####################################################################################

import pytest
import sqlite3
from flask_sql import app, init_db, query_db, DATABASE

# Fixture to set up and tear down the database
@pytest.fixture(scope='function', autouse=True)
def setup_database():
    # Reinitialize the database before each test
    init_db()
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("DELETE FROM books")  # Truncate database
        conn.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='books';")  # Reset primary key

# Test the home route
def test_home():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert response.data.decode() == 'Hello, World!'

# Test GET /api/books with an empty database
def test_get_books_empty():
    with app.test_client() as client:
        response = client.get('/api/books')
        data = response.get_json()
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data'] == []
        assert data['total'] == 0

# Test POST /api/books
def test_create_book():
    with app.test_client() as client:
        response = client.post('/api/books', json={
            'title': 'test',
            'author': 'test',
            'year': 1234
        })
        data = response.get_json()
        assert response.status_code == 201
        assert data['success'] is True
        assert data['message'] == 'Book created successfully'

        books = query_db('SELECT * FROM books')
        assert len(books) == 1
        assert books[0]['title'] == 'test'
        assert books[0]['author'] == 'test'
        assert books[0]['year'] == 1234

# Test GET /api/books/<book_id>
def test_get_book():
    with app.test_client() as client:
        query_db('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', 
                 ['test', 'test', 1234])


        response = client.get('/api/books/1')
        data = response.get_json()
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['title'] == 'test'

# Test PUT /api/books/<book_id>
def test_update_book():
    with app.test_client() as client:
        query_db('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', 
                 ['test', 'test', 1234])

        response = client.put('/api/books/1', json={
            'title': 'test: Updated',
            'author': 'test',
            'year': 1234
        })
        data = response.get_json()
        assert response.status_code == 200
        assert data['success'] is True
        assert data['message'] == 'Book updated successfully'

        book = query_db('SELECT * FROM books WHERE id = 1', one=True)
        assert book['title'] == 'test: Updated'
        assert book['year'] == 1234

# Test DELETE /api/books/<book_id>
def test_delete_book():
    with app.test_client() as client:
        query_db('INSERT INTO books (title, author, year) VALUES (?, ?, ?)', 
                 ['test', 'test', 1234])

        response = client.delete('/api/books/1')
        data = response.get_json()
        assert response.status_code == 200
        assert data['success'] is True
        assert data['message'] == 'Book deleted successfully'

        books = query_db('SELECT * FROM books')
        assert len(books) == 0

# Test error handling for GET /api/books/<book_id> when book does not exist
def test_get_nonexistent_book():
    with app.test_client() as client:
        response = client.get('/api/books/999')
        data = response.get_json()
        assert response.status_code == 404
        assert data['success'] is False
        assert data['error'] == 'Book not found'

# Test error handling for POST /api/books with missing fields
def test_create_book_missing_fields():
    with app.test_client() as client:
        response = client.post('/api/books', json={'title': '1984'})
        data = response.get_json()
        assert response.status_code == 400
        assert data['success'] is False
        assert 'Missing fields' in data['error']
