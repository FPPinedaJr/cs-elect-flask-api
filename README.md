# Book API


This is a simple Flask-based API to manage a collection of books. The API supports the basic CRUD operations: Create, Read, Update, and Delete. It uses SQLite as the database backend.


## Testing with Postman

You can test the API using Postman by sending requests to the following endpoints:

```json
POST /api/books
Content-Type: application/json

{
    "title": "POST_SOMETHING",
    "author": "POST_SOMETHING",
    "year": 1234
}

-------------------------------------

GET /api/books

-------------------------------------

GET /api/books/<id>

-------------------------------------

PUT /api/books/1
Content-Type: application/json

{
    "title": "PUT_SOMETHING",
    "year": 1234
}

-------------------------------------

DELETE /api/books/1

```