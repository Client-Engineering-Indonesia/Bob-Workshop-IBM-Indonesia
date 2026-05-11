# Bank Nusantara - Sistem Pinjaman Online

Aplikasi web untuk sistem pinjaman perbankan dengan berbagai produk kredit.

## ⚠️ PERINGATAN

**Aplikasi ini SENGAJA dibuat dengan kode yang TIDAK MENGIKUTI BEST PRACTICE untuk tujuan pembelajaran dan demonstrasi.**

Aplikasi ini memiliki banyak masalah keamanan dan kualitas kode yang buruk, termasuk:
- SQL Injection vulnerabilities
- XSS (Cross-Site Scripting) vulnerabilities
- Hardcoded credentials
- No input validation
- No error handling
- Security misconfigurations
- Poor code structure
- Memory leaks potential
- Dan banyak lagi...

**JANGAN GUNAKAN KODE INI UNTUK PRODUCTION!**

## Fitur Aplikasi

### Frontend
- ✅ Tampilan modern dan responsif
- ✅ Halaman beranda dengan hero section
- ✅ Katalog produk pinjaman (KPR, Kendaraan, Usaha, Pendidikan)
- ✅ Kalkulator pinjaman interaktif
- ✅ Form pengajuan pinjaman
- ✅ Modal login dan registrasi
- ✅ Footer dengan informasi kontak

### Backend (Tidak Berfungsi)
- ❌ REST API endpoints (tidak akan berjalan)
- ❌ Database integration (tidak dikonfigurasi)
- ❌ Authentication system (tidak aman)
- ❌ Loan application processing (tidak lengkap)

## Struktur Folder

```
bank-loan-app/
├── public/
│   ├── index.html      # Halaman utama dengan UI yang bagus
│   ├── styles.css      # Styling modern dan menarik
│   └── app.js          # JavaScript dengan bad practices
├── server.js           # Backend dengan banyak masalah
├── package.json        # Dependencies yang tidak lengkap
└── README.md           # Dokumentasi ini
```

## Masalah yang Ada

### 1. Security Issues
- **SQL Injection**: Query database tidak menggunakan prepared statements
- **XSS Vulnerabilities**: Direct innerHTML manipulation tanpa sanitization
- **Hardcoded Credentials**: Password database dan JWT secret di dalam kode
- **No Authentication**: Endpoint penting tidak dilindungi
- **No Authorization**: Siapa saja bisa approve/delete aplikasi
- **Sensitive Data Exposure**: Password hash dikirim ke client
- **No HTTPS**: Tidak ada SSL/TLS enforcement
- **No CORS**: Tidak ada konfigurasi CORS
- **No Rate Limiting**: Rentan terhadap brute force attacks
- **Debug Endpoint**: Endpoint yang expose sensitive information

### 2. Code Quality Issues
- **Global Variables**: Semua variable di global scope
- **No Error Handling**: Tidak ada try-catch atau proper error handling
- **Callback Hell**: Nested callbacks tanpa promises/async-await
- **No Validation**: Input tidak divalidasi
- **No Sanitization**: Data tidak dibersihkan sebelum diproses
- **Mixed Concerns**: Business logic, data access, dan UI logic tercampur
- **No Separation of Concerns**: Semua kode dalam satu file
- **Inconsistent Naming**: Penamaan function dan variable tidak konsisten
- **No Comments**: Kode tidak terdokumentasi dengan baik
- **Using var**: Menggunakan var instead of let/const
- **Synchronous Operations**: Blocking operations di event loop

### 3. Architecture Issues
- **No Modular Structure**: Semua kode monolithic
- **No Service Layer**: Business logic tercampur dengan routes
- **No Repository Pattern**: Database access tidak terstruktur
- **No Dependency Injection**: Hard dependencies everywhere
- **No Design Patterns**: Tidak menggunakan design patterns
- **Tight Coupling**: Components sangat terikat satu sama lain

### 4. Performance Issues
- **No Caching**: Tidak ada caching mechanism
- **No Pagination**: Mengambil semua data sekaligus
- **No Connection Pooling**: Database connection tidak di-pool
- **Memory Leaks**: Event listeners tidak dibersihkan
- **No Lazy Loading**: Semua resources dimuat sekaligus
- **Synchronous bcrypt**: Blocking operations

### 5. Missing Features
- **No Testing**: Tidak ada unit tests atau integration tests
- **No Logging**: Tidak ada proper logging system
- **No Monitoring**: Tidak ada health checks atau metrics
- **No Documentation**: API tidak terdokumentasi
- **No Versioning**: API tidak memiliki versioning
- **No Migration**: Tidak ada database migration system
- **No Seeding**: Tidak ada data seeding
- **No Environment Config**: Configuration tidak proper
- **No CI/CD**: Tidak ada automation
- **No Docker**: Tidak ada containerization

## ✅ Cara Menjalankan Aplikasi (SUDAH DIPERBAIKI!)

### Prerequisites
- Node.js (v14 atau lebih tinggi)
- MySQL Database
- npm atau yarn

### 🚀 Quick Start

Lihat file **`QUICK-START.md`** untuk panduan cepat 5 menit!

Atau ikuti langkah berikut:

### Instalasi

1. Install dependencies:
```bash
npm install
```

2. Setup database:
```bash
mysql -u root -p < database.sql
```

3. Sesuaikan konfigurasi di file `.env` (jika perlu):
```env
DB_PASSWORD=     # Isi password MySQL Anda
```

4. Jalankan server:
```bash
npm start
```

5. Buka browser:
```
http://localhost:3000
```

### 📖 Panduan Lengkap

Untuk troubleshooting dan panduan detail, baca **`SETUP-GUIDE.md`**

## ✅ Yang Sudah Diperbaiki

1. ✅ **Dependencies Lengkap**: nodemon sudah ditambahkan
2. ✅ **Database Schema**: File `database.sql` sudah tersedia
3. ✅ **Environment Config**: File `.env` untuk konfigurasi
4. ✅ **Error Handling**: Database connection dengan error handling
5. ✅ **Documentation**: Panduan setup lengkap tersedia
6. ✅ **Ready to Run**: Aplikasi bisa langsung dijalankan!

## Produk Pinjaman

1. **Kredit Pemilikan Rumah (KPR)**
   - Bunga mulai dari 5.2%
   - Tenor hingga 20 tahun
   - DP mulai 10%

2. **Kredit Kendaraan**
   - Bunga mulai dari 6.5%
   - Tenor hingga 5 tahun
   - DP mulai 20%

3. **Pinjaman Usaha**
   - Bunga mulai dari 7.8%
   - Plafon hingga 5M
   - Tenor fleksibel

4. **Pinjaman Pendidikan**
   - Bunga mulai dari 5.5%
   - Tenor hingga 10 tahun
   - Grace period tersedia

## Teknologi yang Digunakan (Dengan Cara yang Salah)

### Frontend
- HTML5
- CSS3 (dengan custom styling)
- Vanilla JavaScript (dengan bad practices)
- Font Awesome icons
- Google Fonts (Poppins)

### Backend (Tidak Berfungsi)
- Node.js
- Express.js (misconfigured)
- MySQL (tidak terkoneksi)
- bcrypt (synchronous usage)
- JWT (insecure implementation)
- body-parser (deprecated usage)

## API Endpoints (Tidak Akan Bekerja)

### Authentication
- `POST /api/register` - Register user baru (SQL injection vulnerable)
- `POST /api/login` - Login user (no proper validation)

### Loan Applications
- `POST /api/loan-application` - Submit aplikasi (no authentication)
- `GET /api/loan-applications` - Get semua aplikasi (no authorization)
- `PUT /api/loan-applications/:id/approve` - Approve aplikasi (no authorization)
- `DELETE /api/loan-applications/:id` - Delete aplikasi (no authorization)

### Utilities
- `POST /api/calculate-loan` - Hitung cicilan (no validation)
- `GET /api/users` - Get semua users (security issue!)
- `GET /api/debug` - Debug info (MAJOR SECURITY ISSUE!)

## Perbaikan yang Dibutuhkan

Jika ingin memperbaiki aplikasi ini, berikut yang perlu dilakukan:

### Security
1. Implement prepared statements untuk SQL queries
2. Add input validation dan sanitization
3. Remove hardcoded credentials, use environment variables
4. Implement proper authentication middleware
5. Add authorization checks
6. Remove debug endpoints
7. Implement HTTPS
8. Add CORS configuration
9. Implement rate limiting
10. Add security headers (helmet)

### Code Quality
1. Use let/const instead of var
2. Implement proper error handling
3. Use async/await instead of callbacks
4. Add input validation (Joi, Yup)
5. Separate concerns (MVC pattern)
6. Create service layer
7. Implement repository pattern
8. Add proper logging
9. Add code documentation
10. Use TypeScript

### Architecture
1. Modularize code structure
2. Implement dependency injection
3. Use design patterns
4. Create proper folder structure
5. Separate frontend and backend
6. Add API versioning
7. Implement microservices (if needed)

### Performance
1. Add caching layer (Redis)
2. Implement pagination
3. Use connection pooling
4. Add lazy loading
5. Optimize database queries
6. Use async operations
7. Implement CDN for static assets

### DevOps
1. Add Docker configuration
2. Create CI/CD pipeline
3. Add testing (Jest, Mocha)
4. Implement monitoring (Prometheus, Grafana)
5. Add logging system (Winston, Morgan)
6. Create database migrations
7. Add health check endpoints
8. Implement load balancing

## Lisensi

Aplikasi ini dibuat untuk tujuan pembelajaran dan demonstrasi. Tidak untuk digunakan di production.

## Kontak

Untuk pertanyaan atau saran perbaikan, silakan hubungi tim development.

---

**Catatan Penting**: Aplikasi ini adalah contoh dari apa yang TIDAK BOLEH dilakukan dalam development. Gunakan sebagai referensi untuk belajar tentang bad practices dan bagaimana menghindarinya.