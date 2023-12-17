import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# PostgreSQL database connection parameters
url = os.environ.get("DATABASE_URL")

CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, Nama TEXT, Email TEXT, Password TEXT);"
)

GET_ALL = "SELECT * FROM users;"
GET_BY_ID = "SELECT * FROM users WHERE id = %s;"
INSERT_USER = "INSERT INTO users (nama, email, Password) VALUES (%s, %s, %s) RETURNING id;"
UPDATE_USER = "UPDATE users SET Nama = %s WHERE id = %s;"
DELETE_USER = "DELETE FROM users WHERE id = %s;"

# Flask application
app = Flask(__name__)

# Function to create a database connection


def create_connection():
    return psycopg2.connect(url)


# Flag to track whether the database is initialized
initialized = False

# Initialize the "users" table before the first request


@app.before_request
def before_request():
    global initialized
    if not initialized:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
        initialized = True


@app.route("/api/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        nama = data["nama"]
        email = data["email"]
        password = data["password"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_USER, (nama, email, password))
                user_id = cursor.fetchone()[0]

        return {"id": user_id, "message": f"User: {nama} created."}, 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Read all users


@app.route("/api/users", methods=["GET"])
def get_all():
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL)
                users = cursor.fetchall()

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Read a user by ID


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_by_id(user_id):
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_BY_ID, (user_id,))
                user = cursor.fetchone()

        if user:
            return jsonify(user)
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update a user by ID


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json()
        new_username = data["username"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_USER, (new_username, user_id))

        return {"message": f"User with ID {user_id} updated."}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a user by ID


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_USER, (user_id,))

        return {"message": f"User with ID {user_id} deleted."}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
