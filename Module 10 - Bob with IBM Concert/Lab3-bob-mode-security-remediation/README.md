# Lab 3 — Setup Bob Security Remediation Mode

Hubungkan Bob ke IBM Concert dalam 4 langkah.

---

## Kredensial Workshop

> **Peserta:** Tiga nilai berikut akan dibagikan oleh presenter pada saat sesi ini dimulai. **Jangan di-commit ke GitHub.**

| Variabel | Deskripsi |
|----------|-----------|
| `CONCERT_BASE_URL` | URL Concert instance + `/concert/core/api/v1` |
| `CONCERT_API_KEY` | API key dalam format base64 |
| `CONCERT_INSTANCE_ID` | Instance ID Concert (umumnya `0000-0000-0000-0000`) |

---

## Langkah-Langkah

### Langkah 1: Buka Folder `Module 10` di VS Code

Buka VS Code, lalu:
- **File → Open Folder**
- Pilih folder `Module 10 - Bob with IBM Concert`
- Klik **Open**

> Folder `.bob` sudah tersedia di dalam folder ini — tidak diperlukan konfigurasi tambahan.

---

### Langkah 2: Buat File `.env` dengan Kredensial

Buka terminal di VS Code (`Ctrl+`` ` atau `Cmd+`` `), lalu jalankan perintah berikut. **Ganti ketiga nilai** dengan kredensial dari presenter:

```bash
cat > .env << EOF
CONCERT_BASE_URL=<DIISI_DARI_PRESENTER>
CONCERT_API_KEY=<DIISI_DARI_PRESENTER>
CONCERT_INSTANCE_ID=<DIISI_DARI_PRESENTER>
EOF
```

Contoh file `.env` yang telah terisi:
```
CONCERT_BASE_URL=https://your-concert-host:12443/concert/core/api/v1
CONCERT_API_KEY=Y29uY2VydHVzZXI6...
CONCERT_INSTANCE_ID=0000-0000-0000-0000
```

> File `.env` sudah terdaftar di `.gitignore` — tidak akan ter-push ke GitHub.

---

### Langkah 3: Import Custom Mode ke Bob

Bob membaca `custom_modes.yaml` dari folder `.bob` di workspace yang sedang dibuka. Lakukan langkah berikut agar mode terdaftar:

1. Klik ikon **Settings** (⚙️) di panel Bob
2. Pilih tab **Modes**
3. Klik **Edit Project Modes**

Bob akan membuka file `.bob/custom_modes.yaml` yang sudah tersedia di folder ini. Mode **🔒 Security Remediation** akan otomatis terdaftar.

Alternatif — reload VS Code agar Bob membaca ulang konfigurasi:

- **Mac:** `Cmd+Shift+P` → ketik `Reload Window` → Enter
- **Windows/Linux:** `Ctrl+Shift+P` → ketik `Reload Window` → Enter

---

### Langkah 4: Verifikasi Mode dan Uji Koneksi

1. Buka Bob, klik **mode selector**
2. Pastikan **🔒 Security Remediation** muncul pada daftar mode

![Bob Security Remediation mode muncul](image/2-modes.png)

3. Klik **🔒 Security Remediation** untuk mengaktifkan mode tersebut, lalu ketik perintah berikut di chat Bob:

```
Check Concert for vulnerabilities
```

![Ketik Check Concert for vulnerabilities](image/3-testing-bob.png)

Bob akan secara otomatis menguji koneksi dan menampilkan daftar aplikasi yang terdaftar di Concert:

![Bob test Concert API connection](image/3.1-testing-bob.png)

Klik **Approve** saat Bob meminta izin untuk menjalankan perintah curl:

![Bob meminta approval](image/3.2-testing-bob.png)

![Bob konfirmasi .env terbaca](image/3.3-testing-bob.png)

Koneksi berhasil:

![Concert API connection success](image/3.4-testing-bob.png)

Daftar aplikasi di Concert ditampilkan:

![Daftar aplikasi di Concert](image/3.5-testing-bob.png)

---

## Checklist Sebelum Melanjutkan ke Lab 4

- [ ] Folder `Module 10 - Bob with IBM Concert` terbuka di VS Code
- [ ] File `.env` sudah berisi ketiga kredensial yang diberikan presenter
- [ ] Mode **🔒 Security Remediation** muncul di Bob
- [ ] Bob berhasil terhubung ke Concert dan menampilkan daftar aplikasi

---

## Langkah Selanjutnya

Lanjutkan ke **[Lab 4 → Automated Vulnerability Remediation](../Lab4-vulnerabilities-mitigation-using-bob/README.md)**
