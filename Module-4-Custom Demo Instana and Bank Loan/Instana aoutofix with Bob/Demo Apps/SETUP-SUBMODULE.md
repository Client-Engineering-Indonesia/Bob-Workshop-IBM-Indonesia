# Setup Golang Error Simulator Submodule

## 📋 Masalah
Repository GitLab di `http://162.133.131.244/root/golang-error-simulator.git` masih kosong, sehingga tidak bisa ditambahkan sebagai submodule.

## ✅ Solusi: Push Code ke GitLab Terlebih Dahulu

### Langkah 1: Siapkan Code Golang Error Simulator

Pastikan Anda memiliki code golang-error-simulator dengan struktur:
```
golang-error-simulator/
├── go.mod
├── main.go
└── README.md
```

### Langkah 2: Initialize Git Repository Lokal

```bash
cd /path/to/golang-error-simulator
git init
git add .
git commit -m "Initial commit: Golang error simulator demo app"
```

### Langkah 3: Push ke GitLab

```bash
# Tambahkan remote GitLab
git remote add origin http://162.133.131.244/root/golang-error-simulator.git

# Push ke GitLab
git push -u origin main
# atau jika branch default adalah master:
# git push -u origin master
```

### Langkah 4: Tambahkan sebagai Submodule

Setelah repository GitLab terisi, kembali ke repository Tutorial dan jalankan:

```bash
cd /path/to/Tutorial

# Tambahkan submodule
git submodule add http://162.133.131.244/root/golang-error-simulator.git "Custom Demos/Instana aoutofix with Bob/Demo Apps/golang-error-simulator"

# Initialize dan update submodule
git submodule update --init --recursive

# Commit perubahan
git add .gitmodules "Custom Demos/Instana aoutofix with Bob/Demo Apps/golang-error-simulator"
git commit -m "Add golang-error-simulator as submodule"
```

## 🔍 Verifikasi

Setelah berhasil, struktur .gitmodules akan seperti ini:

```ini
[submodule "Event Automation"]
	path = Event Automation
	url = git@github.com:5112100070/Event-Automation-Tutorial.git
[submodule "Liberty WAS"]
	path = Liberty WAS
	url = git@github.com:5112100070/Liberty-Tutorial.git
[submodule "Custom Demos/Instana aoutofix with Bob/Demo Apps/golang-error-simulator"]
	path = Custom Demos/Instana aoutofix with Bob/Demo Apps/golang-error-simulator
	url = http://162.133.131.244/root/golang-error-simulator.git
```

## 📝 Catatan

- Pastikan Anda memiliki akses ke GitLab server (http://162.133.131.244)
- Jika menggunakan HTTPS, Anda mungkin perlu memasukkan username dan password
- Untuk akses yang lebih mudah, pertimbangkan untuk setup SSH key

## 🔗 Referensi

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitLab Submodules](https://docs.gitlab.com/ee/user/project/repository/submodules.html)

---

**Created**: 2026-02-05