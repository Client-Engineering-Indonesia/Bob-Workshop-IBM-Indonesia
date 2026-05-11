# Panduan Setup Bank Loan Application

## Prasyarat

Sebelum menjalankan aplikasi, pastikan Anda sudah menginstall:

1. **Node.js** (v14 atau lebih tinggi)
   - Download dari: https://nodejs.org/
   - Cek versi: `node --version`

2. **MySQL** (v5.7 atau lebih tinggi)
   - Download dari: https://dev.mysql.com/downloads/mysql/
   - Atau gunakan XAMPP/WAMP yang sudah include MySQL
   - Cek versi: `mysql --version`

3. **npm** (biasanya sudah terinstall bersama Node.js)
   - Cek versi: `npm --version`

## Langkah-langkah Instalasi

### 1. Install Dependencies

Buka terminal/command prompt di folder `bank-loan-app`, lalu jalankan:

```bash
npm install
```

Perintah ini akan menginstall semua dependencies yang dibutuhkan:
- express
- body-parser
- mysql
- bcrypt
- jsonwebtoken
- dotenv
- nodemon (dev dependency)

### 2. Setup Database

#### Opsi A: Menggunakan MySQL Command Line

1. Buka MySQL command line atau terminal
2. Login ke MySQL:
   ```bash
   mysql -u root -p
   ```
3. Jalankan script database:
   ```bash
   source database.sql
   ```
   Atau jika di Windows:
   ```bash
   mysql -u root -p < database.sql
   ```

#### Opsi B: Menggunakan phpMyAdmin (jika pakai XAMPP/WAMP)

1. Buka phpMyAdmin di browser: http://localhost/phpmyadmin
2. Klik tab "SQL"
3. Copy-paste isi file `database.sql`
4. Klik "Go" atau "Jalankan"

#### Opsi C: Menggunakan MySQL Workbench

1. Buka MySQL Workbench
2. Connect ke MySQL server
3. File → Open SQL Script → Pilih `database.sql`
4. Klik icon petir (Execute) untuk menjalankan script

### 3. Konfigurasi Environment Variables

File `.env` sudah dibuat dengan konfigurasi default. Jika perlu, sesuaikan dengan setup MySQL Anda:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=          # Kosongkan jika tidak ada password
DB_NAME=bank_loan_db
PORT=3000
```

**Catatan:** 
- Jika MySQL Anda memiliki password, isi `DB_PASSWORD` dengan password Anda
- Jika menggunakan port MySQL non-standard, tambahkan `DB_PORT=3307` (sesuaikan)

### 4. Jalankan Aplikasi

#### Mode Development (dengan auto-reload):
```bash
npm run dev
```

#### Mode Production:
```bash
npm start
```

### 5. Akses Aplikasi

Buka browser dan akses:
```
http://localhost:3000
```

Anda akan melihat halaman utama Bank Nusantara dengan:
- Hero section
- Produk pinjaman
- Kalkulator pinjaman
- Form pengajuan

## Troubleshooting

### Error: "Cannot connect to database"

**Solusi:**
1. Pastikan MySQL service sudah berjalan
   - Windows: Cek di Services (services.msc)
   - Mac/Linux: `sudo service mysql status`
2. Cek username dan password di file `.env`
3. Pastikan database `bank_loan_db` sudah dibuat

### Error: "Port 3000 already in use"

**Solusi:**
1. Ubah PORT di file `.env` menjadi port lain (misal: 3001)
2. Atau matikan aplikasi lain yang menggunakan port 3000

### Error: "Cannot find module 'express'"

**Solusi:**
1. Hapus folder `node_modules`
2. Jalankan `npm install` lagi

### Error: "Access denied for user 'root'@'localhost'"

**Solusi:**
1. Cek password MySQL Anda
2. Update `DB_PASSWORD` di file `.env`
3. Atau buat user MySQL baru:
   ```sql
   CREATE USER 'bankuser'@'localhost' IDENTIFIED BY 'password123';
   GRANT ALL PRIVILEGES ON bank_loan_db.* TO 'bankuser'@'localhost';
   FLUSH PRIVILEGES;
   ```
   Lalu update `.env`:
   ```
   DB_USER=bankuser
   DB_PASSWORD=password123
   ```

### MySQL tidak terinstall

**Solusi untuk Windows:**
1. Download XAMPP: https://www.apachefriends.org/
2. Install XAMPP
3. Buka XAMPP Control Panel
4. Start Apache dan MySQL
5. Gunakan phpMyAdmin untuk setup database

**Solusi untuk Mac:**
```bash
brew install mysql
brew services start mysql
```

**Solusi untuk Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

## Testing Aplikasi

### 1. Test Frontend
- Buka http://localhost:3000
- Klik tombol "Hitung Pinjaman Anda"
- Isi kalkulator dan lihat hasilnya
- Klik "Ajukan Sekarang" pada salah satu produk

### 2. Test Backend API (Opsional)

Gunakan Postman atau curl untuk test API:

**Register User:**
```bash
curl -X POST http://localhost:3000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123"}'
```

**Login:**
```bash
curl -X POST http://localhost:3000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

**Get Loan Applications:**
```bash
curl http://localhost:3000/api/loan-applications
```

## Fitur yang Berfungsi

✅ Frontend UI (100% berfungsi)
✅ Kalkulator pinjaman
✅ Form pengajuan (data tersimpan di localStorage)
✅ Modal login/register
✅ Responsive design

⚠️ Backend API (berfungsi jika database terkoneksi)
⚠️ Authentication (basic implementation)
⚠️ Data persistence (tergantung database)

## Catatan Keamanan

⚠️ **PERINGATAN:** Aplikasi ini dibuat untuk pembelajaran dan memiliki banyak security issues:
- SQL Injection vulnerabilities
- XSS vulnerabilities
- Hardcoded secrets
- No input validation
- No proper authentication

**JANGAN GUNAKAN UNTUK PRODUCTION!**

## Struktur Database

### Tabel `users`
- id (Primary Key)
- name
- email (Unique)
- password (Hashed)
- created_at
- updated_at

### Tabel `loan_applications`
- id (Primary Key)
- user_id (Foreign Key)
- full_name
- nik
- email
- phone
- address
- occupation
- income
- loan_type
- amount
- purpose
- status (pending/approved/rejected)
- created_at
- updated_at

## Bantuan Lebih Lanjut

Jika masih ada masalah:
1. Cek log error di terminal
2. Cek console browser (F12)
3. Pastikan semua prasyarat sudah terinstall
4. Restart MySQL service
5. Restart aplikasi Node.js

## Cara Menghentikan Aplikasi

Tekan `Ctrl + C` di terminal tempat aplikasi berjalan.

---

**Selamat mencoba!** 🚀