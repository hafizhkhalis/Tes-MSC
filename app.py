import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request, jsonify


load_dotenv()

url = os.environ.get("DATABASE_URL")

CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, Nama TEXT, Email TEXT, Password CHAR(255));"
)
GET_ALL = "SELECT * FROM users;"
GET_BY_ID = "SELECT * FROM users WHERE id = %s;"
# GET_BY_ID = "SELECT PGP_SYM_DECRYPT(CAST(password AS BYTEA), 'AES-KEY') FROM users WHERE id = %s;"
INSERT_USER = "INSERT INTO users (nama, email, Password) VALUES (%s, %s, PGP_SYM_ENCRYPT(%s, 'AES-KEY')) RETURNING id;"
UPDATE_USER = "UPDATE users SET nama = %s, email = %s, password = PGP_SYM_ENCRYPT(%s, 'AES-KEY') WHERE id = %s;"
DELETE_USER = "DELETE FROM users WHERE id = %s;"
GET_LOGIN = "SELECT email, PGP_SYM_DECRYPT(CAST(password AS BYTEA), 'AES-KEY') FROM users WHERE email = %s;"

app = Flask(__name__)


def create_connection():
    return psycopg2.connect(url)


initialized = False


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

        return {"id": user_id, "message": f"Pengguna: {nama} berhasil dibuat."}, 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            return jsonify({"error": "Pengguna tidak ditemukan!"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        data = request.get_json()
        new_name = data.get("nama")
        new_email = data.get("email")
        new_password = data.get("password")

        with create_connection() as connection:
            with connection.cursor() as cursor:
                update_query = "UPDATE users SET "
                update_values = []

                if new_name is not None:
                    update_query += "nama = %s, "
                    update_values.append(new_name)

                if new_email is not None:
                    update_query += "email = %s, "
                    update_values.append(new_email)

                if new_password is not None:
                    update_query += "password = PGP_SYM_ENCRYPT(%s, 'AES-KEY'), "
                    update_values.append(new_password)

                update_query = update_query.rstrip(", ") + " WHERE id = %s;"
                update_values.append(user_id)

                cursor.execute(update_query, tuple(update_values))

                connection.commit()

        return {"message": f"Pengguna dengan ID {user_id} berhasil di update."}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(DELETE_USER, (user_id,))

        return {"message": f"Pengguna dengan ID {user_id} berhasil dihapus."}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def get_login():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_LOGIN, (email,))
                user = cursor.fetchone()

        if user:
            if user[1] == password:
                return {"message": "Login Berhasil"}
            else:
                return {"error": "Email atau Kata sandi salah"}
        else:
            return {"error": "Pengguna tidak ditemukan"}, 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
