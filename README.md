## UAS Microservice CRUD API PLSQL UNSIA

Mata Kuliah : Pemrograman PL/SQL

Kelas : IT302

Prodi : PJJ Informatika

Dosen : Abdul Azzam Ajhari, S.Kom., M.Kom

Anggota :

- Hafizh Khalis Majid

## Microservice CRUD USER API with Python and PostgreSQL

Role yang ada saat ini pada table user:

- Admin
- User

Ada beberapa akses yang dapat digunakan pada API:

1. Action: Create Account\
   Method: POST\
   API: /api/create_user\
   Auth: Admin\
   Body:\
    {\
    “nama”: “nama”,\
    “email”: “email”,\
    “password”: “password”,\
    “isAdmin”: True/False (Jika dikosongkan valuenya false)\
    }

   Response:

   - 201: Pengguna berhasil dibuat
   - 400: Email pernah dibuat pada akun lain
   - 402: Hanya admin yang dapat membuat akun
   - 500: Eror

2. Action: Get Data All Account\
   Method: GET\
   API: /api/users\
   Auth: Admin\
   Response:

   - 200: Data akun tampil
   - 402: Hanya admin yang dapat mengakses
   - 500: Eror

3. Action: Get Data Users by ID\
   Method: GET\
   API: /api/users/”user_id”\
   Auth: Admin\
   Response:

   - 200: Data akun tampil
   - 402: Hanya admin yang dapat mengakses
   - 500: Eror

4. Action: Update user
   Method: PUT
   API: /api/edit_user/”user_id”
   Auth: Admin
   Body:\
    {\
    "email": "email",\
    "isadmin": true/false,\
    "nama": "nama",\
    "password": ”password,\
    }
   Note: Request bisa di isi dengan beberapa parameter update, tidak perlu semua detail akun perlu di update.

   - Response:

   * 200: Update berhasil
   * 402: Tidak memiliki akses pada aksi ini
   * 500: Eror

   Note: pada fitur update tidak diperlukan untuk mengisi keseluruhan value, hanya data yang perlu diupdate saja yang diisi

5. Action: Delete User\
   Method: DELETE\
   API: /api/delete_user/”user_id”\
   Auth: Admin\
   Response:

   - 200: Akun berhasil di delete
   - 402: Tidak memiliki akses pada aksi ini, akun admin hanya dapat dihapus
     dengan mengakses database
   - 500: Eror

6. Action: Login\
   Method: POST\
   API: /api/login\
   Auth: All\
   Body:\
    {\
    “email”: “email”,\
    “password”: “password”,\
    }
   Response:

   - 200: Login berhasil
   - 409: Sudah login, logout terlebih dahulu
   - 404: Pengguna tidak ditemukan
   - 400: Email atau kata sandi salah
   - 500: Eror

7. Action: Cek Profile\
   Method: GET\
   API: /api/profile\
   Auth: All\
   Response:

   - 200: Detail akun login
   - 402: Anda belum login, login terlebih dahulu
   - 500: Eror

8. Action: Logout\
   Method: GET\
   API: api/logout\
   Auth: All\
   Response:

   - 200: Logout berhasil
   - 400: Anda belum login
   - 500: Eror

9. Action: Cek Log Aktivitas akun\
   Method: GET\
   API: /api/log\
   Auth: All\
   Response:

   - 200: Detail log apa saja yang terjadi pada akun
   - 402: Anda belum login, login terlebih dahulu
   - 500: Eror

Trigger aplikasi untuk melakukan duplikasi data dari dari table user_login ke user_log, dan setiap log nantinya dapat dipanggil dengan menggunakan action log pada api request

# Detail Trigger

Script:
create trigger user_log_login after insert on user_login
for each row execute procedure user_log_login_func();

Note: trigger akan terjadi saat terjadi tambahan data pada table user_login

create trigger user_log_logout after update on user_login
for each row execute procedure user_log_login_func();

Note: trigger akan terjadi saat terjadi perubahan data pada table user_login, pada kasus kali ini dilakukan pengecekan pada status login dari user_login dengan tujuan ketika user sudah logout maka data user log akan otomatis bertambah
