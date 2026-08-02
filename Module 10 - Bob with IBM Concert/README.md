# 🚀 Workshop Guide — IBM Bob + Concert
## Perbanas Institute · Security Remediation Workshop

Selamat datang! Halaman ini adalah **titik mulai** kamu sebagai peserta workshop.

---

## ⏱️ Gambaran Sesi (±2 jam)

| Sesi | Lab | Mode | Durasi |
|------|-----|------|--------|
| Demo oleh presenter | Lab 1 — Java Modernization dengan Bob | 👀 Lihat saja | ~30 menit |
| Demo oleh presenter | Lab 2 — Concert Security Scanning | 👀 Lihat saja | ~20 menit |
| **Hands-on kamu** | **Lab 3 — Setup Bob + Concert** | 💻 Kerjain sendiri | ~20 menit |
| **Hands-on kamu** | **Lab 4 — Automated Remediation** | 💻 Kerjain sendiri | ~45 menit |

> **Kamu cukup fokus di Lab 3 dan Lab 4.** Lab 1 dan Lab 2 akan didemonstrasikan oleh presenter.

---

## ✅ Yang Harus Disiapkan SEBELUM Workshop

Pastikan semua ini sudah beres sebelum hari-H:

### 1. IBM Bob — Install & Login
- Download Bob extension di VS Code
- Login dengan akun IBM kamu
- Pastikan Bob sudah aktif (ikon Bob muncul di sidebar VS Code)

### 2. Clone Workshop Repo
```bash
git clone https://github.com/Client-Engineering-Indonesia/Bob-Workshop-IBM-Indonesia.git
```
Lalu buka folder `Bob-Workshop-IBM-Indonesia/Module 10 - Bob with IBM Concert` di VS Code.

### 3. `jq` — JSON processor
```bash
# macOS
brew install jq

# Linux/WSL
sudo apt install jq

# Windows (via Chocolatey)
choco install jq
```
Verifikasi: `jq --version`

### 4. VS Code — Versi terbaru
Download di [code.visualstudio.com](https://code.visualstudio.com)

---

## 📋 Yang Akan Diberikan Presenter Saat Workshop

Kamu **tidak perlu** setup Concert sendiri. Presenter akan membagikan:

| Yang dibagikan | Cara penggunaannya |
|----------------|-------------------|
| `CONCERT_BASE_URL` | Diisi ke file `.env` di Lab 3 |
| `CONCERT_API_KEY` | Diisi ke file `.env` di Lab 3 |
| `CONCERT_INSTANCE_ID` | Diisi ke file `.env` di Lab 3 |

Simpan ketiga nilai ini saat presenter membagikannya — kamu akan membutuhkannya di Lab 3 Step 3.

---

## 🗂️ Repo yang Digunakan

| Repo | URL | Kegunaannya |
|------|-----|-------------|
| Workshop Materials | [Bob-Workshop-IBM-Indonesia](https://github.com/Client-Engineering-Indonesia/Bob-Workshop-IBM-Indonesia) | Materi lengkap semua lab |
| Vulnerable App | [VulnerableSampleApp](https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp) | App yang akan kamu fork & remediate |

---

## 📖 Urutan Lab (Hands-on)

Saat tiba giliran hands-on kamu:

### → [Lab 3: Setup Bob-Concert Integration](Lab3-bob-mode-security-remediation/README.md)
Setup koneksi Bob ke Concert, copy mode config, buat `.env` dengan credentials dari presenter.

### → [Lab 4: Automated Vulnerability Remediation](Lab4-vulnerabilities-mitigation-using-bob/README.md)
Gunakan Bob Security Remediation mode untuk fix 14 SAST exposures secara otomatis, push ke GitHub, dan verifikasi hasilnya di Concert.

---

## 🆘 Troubleshooting Cepat

| Masalah | Solusi |
|---------|--------|
| Mode "🔒 Security Remediation" tidak muncul di Bob | Pastikan folder `.bob` sudah ada di root workspace → Reload VS Code |
| Bob tidak bisa connect ke Concert | Cek isi `.env` — pastikan 3 nilai sudah terisi dengan benar |
| `jq: command not found` | Install `jq` (lihat Step 4 di atas) |
| `git: command not found` | Install Git dari [git-scm.com](https://git-scm.com) |
| Bob error "Maven not found" | Lab 1 demo-only, tidak perlu Maven untuk Lab 3 & 4 |

---

*Ada pertanyaan? Tanyakan langsung ke presenter atau IBM team.* 🙌
