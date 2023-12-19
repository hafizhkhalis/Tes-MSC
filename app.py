import os
import psycopg2
import secrets
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session


load_dotenv()

url = os.environ.get("DATABASE_URL")

CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, Nama TEXT, Email TEXT, Password CHAR(255), isAdmin BOOLEAN DEFAULT FALSE);"
)
GET_ALL = "SELECT * FROM users;"
GET_BY_ID = "SELECT * FROM users WHERE id = %s;"
INSERT_USER = "INSERT INTO users (nama, email, Password, isAdmin) VALUES (%s, %s, PGP_SYM_ENCRYPT(%s, 'AES-KEY'), %s) RETURNING id;"
DELETE_USER = "DELETE FROM users WHERE id = %s;"
GET_LOGIN = "SELECT email, PGP_SYM_DECRYPT(CAST(password AS BYTEA), 'AES-KEY'), isAdmin nama FROM users WHERE email = %s;"
GET_EMAIL = "SELECT email FROM users WHERE email = %s;"
GET_PROFILE_DETAILS = "SELECT nama, isAdmin FROM users WHERE email = %s"

app = Flask(__name__)


def create_connection():
    return psycopg2.connect(url)


initialized = False


def checking_auth():
    if session.get('login_status'):
        email = session.get('email')

        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_PROFILE_DETAILS, (email,))
                details = cursor.fetchone()[1]
            return True if details else False

    else:
        return False


@app.before_request
def before_request():
    global initialized
    if not initialized:
        with create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_USERS_TABLE)
        initialized = True


@app.route("/api/create_user", methods=["POST"])
def create_user():
    try:
        if checking_auth():
            data = request.get_json()
            nama = data["nama"]
            email = data["email"]
            password = data["password"]
            isAdmin = data.get("isAdmin", False)

            with create_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(GET_EMAIL, (email,))
                    get_email = cursor.fetchone()

            if get_email:
                return {"message": "Akun dengan email tersebut sudah pernah dibuat"}, 400

            with create_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        INSERT_USER, (nama, email, password, isAdmin))
                    user_id = cursor.fetchone()[0]
                    return {"id": user_id, "message": f"Pengguna: {nama} berhasil dibuat."}, 201

        else:
            return {"message:" "Hanya admin yang dapat membuat akun"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users", methods=["GET"])
def get_all():
    try:
        if checking_auth():
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(GET_ALL)
                    users = cursor.fetchall()

            columns = [column[0] for column in cursor.description]

            users_data = [dict(zip(columns, user)) for user in users]

            return jsonify(users_data)
        else:
            return {"message": "Hanya admin yang dapat mengakses"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_by_id(user_id):
    try:
        if checking_auth():
            with create_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(GET_BY_ID, (user_id,))
                    user = cursor.fetchone()

            if user:
                return jsonify({"id": user[0], "nama": user[1], "email": user[2], "password": user[3]})
            else:
                return jsonify({"error": "Pengguna tidak ditemukan!"}), 404

        else:
            return {"message": "Hanya admin yang dapat mengakses"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/edit_user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        if checking_auth():
            data = request.get_json()
            new_name = data.get("nama")
            new_email = data.get("email")
            new_password = data.get("password")
            new_role = data.get("isAdmin")

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

                    if new_role is not None:
                        update_query += "isAdmin = %s, "
                        update_values.append(new_role)

                    update_query = update_query.rstrip(
                        ", ") + " WHERE id = %s;"
                    update_values.append(user_id)

                    cursor.execute(update_query, tuple(update_values))

                    connection.commit()

            return {"message": f"Pengguna dengan ID {user_id} berhasil di update."}

        else:
            return {"message": "Anda tidak memiliki akses pada aksi ini"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def admin_rejected_delete(id):
    with create_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_BY_ID, (id,))
            details = cursor.fetchone()
            return True if details[3] else False


@app.route("/api/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        if checking_auth():
            if admin_rejected_delete(user_id):
                return {"message": "Akun dengan role Admin hanya dapat dihapus dengan mengakses database"}

            else:
                with create_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(DELETE_USER, (user_id,))
                        return {"message": f"Pengguna dengan ID {user_id} berhasil dihapus."}

        else:
            return {"message": "Anda tidak memiliki akses pada aksi ini"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


app.secret_key = os.urandom(32)


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

        if session.get('login_status') == True:
            return {"message": "Anda sudah login, Logout terlebih dahulu"}
        else:
            if user:
                if user[1] == password:
                    session['login_status'] = True
                    session['email'] = email
                    return {"message": "Login Berhasil"}
                else:
                    return {"error": "Email atau Kata sandi salah"}
            else:
                return {"error": "Pengguna tidak ditemukan"}, 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile", methods=["GET"])
def check_profile():
    try:
        if session.get('login_status') == True:
            email = session.get('email')

            with create_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(GET_PROFILE_DETAILS, (email,))
                    details = cursor.fetchone()
                    isAdmin = "Admin" if details[1] else "User"
                    return {"message": f"Anda login menggunakan akun dengan nama {details[0]} sebagai {isAdmin}"}

        else:
            return {"message": "Anda belum login, login terlebih dahulu"}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/logout", methods=["GET"])
def logout():
    if session.get('login_status') == True:
        session.pop('login_status', None)
        session.pop('email', None)
        session.pop('nama', None)
        return {"message": "Logout berhasil"}
    else:
        return {"message": "Anda belum login"}


if __name__ == "__main__":
    app.run(debug=True)
