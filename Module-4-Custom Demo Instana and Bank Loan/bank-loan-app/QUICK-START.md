# 🚀 Quick Start - Bank Loan App

Panduan cepat untuk menjalankan aplikasi dalam 5 menit!

## ⚡ Langkah Cepat

### 1️⃣ Install Dependencies (1 menit)
```bash
npm install
```

### 2️⃣ Setup Database (2 menit)

**Pastikan MySQL sudah berjalan!**

Pilih salah satu cara:

#### Cara A: Command Line
```bash
mysql -u root -p < database.sql
```

#### Cara B: Jika pakai XAMPP/WAMP
1. Buka phpMyAdmin: http://localhost/phpmyadmin
2. Klik tab "SQL"
3. Copy-paste isi file `database.sql`
4. Klik "Go"

### 3️⃣ Sesuaikan Konfigurasi (30 detik)

Edit file `.env` jika perlu (terutama password MySQL):
```env
DB_PASSWORD=     # Isi jika MySQL Anda pakai password
```

### 4️⃣ Jalankan Aplikasi (30 detik)
```bash
npm start
```

### 5️⃣ Buka Browser (30 detik)
```
http://localhost:3000
```

## ✅ Selesai!

Aplikasi sudah berjalan! Anda bisa:
- Lihat produk pinjaman
- Gunakan kalkulator
- Isi form pengajuan
- Test login/register

## ❌ Troubleshooting Cepat

### MySQL tidak jalan?
**Windows (XAMPP):**
1. Buka XAMPP Control Panel
2. Klik "Start" pada MySQL

**Mac:**
```bash
brew services start mysql
```

**Linux:**
```bash
sudo systemctl start mysql
```

### Port 3000 sudah dipakai?
Edit `.env`:
```env
PORT=3001
```

### Error "Cannot connect to database"?
1. Cek MySQL sudah jalan
2. Cek password di `.env`
3. Pastikan database sudah dibuat

## 📝 Catatan

- Frontend akan tetap berfungsi meskipun database error
- Data form akan tersimpan di localStorage browser
- Untuk panduan lengkap, baca `SETUP-GUIDE.md`

## 🎯 Test Cepat

1. Buka http://localhost:3000
2. Scroll ke "Kalkulator Pinjaman"
3. Ubah jumlah pinjaman
4. Klik "Ajukan Sekarang" pada produk KPR
5. Isi form dan submit

Jika semua berjalan lancar, aplikasi sudah siap! 🎉