# Workshop Guide — IBM Bob + IBM Concert
## Perbanas Institute · Security Remediation Workshop

Selamat datang di workshop IBM Bob + Concert. Dokumen ini merupakan **panduan utama** bagi peserta workshop.

---

## Gambaran Sesi (±2 jam)

| Sesi | Lab | Keterangan | Durasi |
|------|-----|------------|--------|
| Demonstrasi | Lab 1 — Java Modernization dengan Bob | Dibawakan oleh presenter | ±30 menit |
| Demonstrasi | Lab 2 — Concert Security Scanning | Dibawakan oleh presenter | ±20 menit |
| **Praktik Mandiri** | **Lab 3 — Setup Bob + Concert** | Dikerjakan oleh peserta | ±20 menit |
| **Praktik Mandiri** | **Lab 4 — Automated Remediation** | Dikerjakan oleh peserta | ±45 menit |

> **Peserta cukup mengikuti Lab 3 dan Lab 4.** Lab 1 dan Lab 2 akan didemonstrasikan oleh presenter.

---

## Persiapan Sebelum Workshop

Pastikan seluruh komponen berikut telah terpasang sebelum hari pelaksanaan:

### 1. IBM Bob — Instalasi & Login
- Pasang ekstensi Bob di VS Code
- Masuk menggunakan akun IBM yang telah diberikan
- Verifikasi bahwa Bob telah aktif (ikon Bob muncul di sidebar VS Code)

### 2. Clone Repository Workshop
```bash
git clone https://github.com/Client-Engineering-Indonesia/Bob-Workshop-IBM-Indonesia.git
```
Selanjutnya buka folder `Bob-Workshop-IBM-Indonesia/Module 10 - Bob with IBM Concert` di VS Code.

### 3. `jq` — JSON Command-Line Processor
```bash
# macOS
brew install jq

# Linux / WSL
sudo apt install jq

# Windows (via Chocolatey)
choco install jq
```
Verifikasi instalasi: `jq --version`

### 4. VS Code — Versi Terbaru
Unduh di [code.visualstudio.com](https://code.visualstudio.com)

---

## Kredensial yang Akan Diberikan oleh Presenter

Peserta **tidak perlu** melakukan konfigurasi IBM Concert secara mandiri. Presenter akan membagikan kredensial berikut pada saat sesi berlangsung:

| Variabel | Penggunaan |
|----------|-----------|
| `CONCERT_BASE_URL` | Diisikan ke file `.env` pada Lab 3 |
| `CONCERT_API_KEY` | Diisikan ke file `.env` pada Lab 3 |
| `CONCERT_INSTANCE_ID` | Diisikan ke file `.env` pada Lab 3 |

Harap simpan ketiga nilai tersebut saat presenter membagikannya — akan digunakan pada Lab 3 Langkah 2.

---

## Repository yang Digunakan

| Repository | URL | Keterangan |
|------------|-----|------------|
| Materi Workshop | [Bob-Workshop-IBM-Indonesia](https://github.com/Client-Engineering-Indonesia/Bob-Workshop-IBM-Indonesia) | Seluruh materi lab |
| Aplikasi Sampel | [VulnerableSampleApp](https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp) | Aplikasi Java yang akan dianalisis dan diperbaiki |

---

## Panduan Praktik Mandiri

### [Lab 3 — Setup Bob-Concert Integration](Lab3-bob-mode-security-remediation/README.md)
Konfigurasi koneksi Bob ke IBM Concert menggunakan kredensial yang diberikan presenter, lalu verifikasi koneksi berhasil.

### [Lab 4 — Automated Vulnerability Remediation](Lab4-vulnerabilities-mitigation-using-bob/README.md)
Gunakan Bob Security Remediation mode untuk mendeteksi dan memperbaiki 14 SAST exposures secara otomatis, melakukan push ke GitHub, serta memverifikasi hasilnya melalui dasbor IBM Concert.

---

## Panduan Pemecahan Masalah

| Masalah | Solusi |
|---------|--------|
| Mode "🔒 Security Remediation" tidak muncul di Bob | Pastikan folder `.bob` tersedia di root workspace, kemudian lakukan Reload Window di VS Code |
| Bob tidak dapat terhubung ke Concert | Periksa isi file `.env` — pastikan ketiga variabel telah terisi dengan benar |
| Pesan error `jq: command not found` | Lakukan instalasi `jq` (lihat Langkah 3 di atas) |
| Pesan error `git: command not found` | Lakukan instalasi Git melalui [git-scm.com](https://git-scm.com) |
| Bob menampilkan error "Maven not found" | Lab 1 bersifat demonstrasi; Maven tidak diperlukan untuk Lab 3 dan Lab 4 |

---

*Apabila terdapat pertanyaan, silakan menghubungi presenter atau tim IBM yang bertugas.*
