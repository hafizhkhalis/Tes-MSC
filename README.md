# Program sederhana microservices python

Program ini dibuat untuk memenuhi UTS dari mata kuliah PL/SQL

Database yang digunakan ada postgree public dengan menggunakan ElephantSQL

Ada beberapa akses yang dapat digunakan pada API:

1. Create user
   Untuk membuat akun pada user yaitu : http://127.0.0.1:5000/api/users (POST)
   Json yang dibutuhkan adalah:
   {
   "nama": "nama",
   "email": "email",
   "password": "password"
   }

2. Get User Information
   Untuk mengambil data keseluruhan user yang ada pada database dapat menggunakan : http://127.0.0.1:5000/api/users (GET)

   Note: password di encrypt menggunakan aes-256 yang sudah dihapus

3. Get User by ID
   Untuk melakukan pencarian user berdasarkan ID dapat dilakukan dengan : http://127.0.0.1:5000/api/users/<"id"> (GET)

4. Update data user
   Untuk melakukan update data pada user dapat menggunakan : http://127.0.0.1:5000/api/users/<"id"> (PUT)
   Json yang dibutuhkan adalah:
   {
   "nama": "nama",
   "email": "email",
   "password": "password"
   }

   Note: pada fitur update tidak diperlukan untuk mengisi keseluruhan value, hanya data yang perlu diupdate saja yang diisi

5. Delete data user
   Untuk melakukan delete data user dapat menggunakan : http://127.0.0.1:5000/api/users/<"id"> (DELETED)

# BUG yang terdeteksi

Saat ini penyimpanan data menggunakan aes-256 yang masih dipisahkan menggunakan "/" tetapi sejauh ini tipe data yang dicoba belum ditemukan tipe data yang menyimpan "/" secara keseluruhan sehingga saat di decrypt, perintah tidak mengenali encrypt sebagai sebuah byte

sejauh ini untuk fitur yang aes-256 saya sudah mencoba mencari beberapa sumber termasuk menggunakan chat gpt karena keterbatasan ilmu saya dalam bahasa python maupun penggunaan database postgreSQL
