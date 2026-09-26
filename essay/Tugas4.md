# Tugas 4

## Table of Contents

- [Overview](#overview)
- [Weekly Progress](#weekly-progress)
- [Role and Access Control](#role-and-access-control)
- [Authentication, Session, and Cookies](#authentication-session-and-cookies)
- [AI Disclosure](#ai-disclosure)
- [Installation and Local Setup](#installation-and-local-setup)
- [Deployment](#deployment)
- [Testing Checklist](#testing-checklist)
- [References](#references)

---

## Overview

Website ini merupakan portfolio yang menampilkan beberapa bagian utama:

- Profile dan informasi pribadi
- Experience
- Education
- Projects
- Gallery
- Project starring
- Songfess

Data pada bagian **Experience, Education, dan Projects** dikelola menggunakan model Django dan ditampilkan melalui template. Pengguna yang telah login juga dapat melakukan aksi tertentu sesuai dengan role yang dimilikinya.

Implementasi minggu ini menggunakan:

- **Django** sebagai web framework
- **Django Authentication** untuk registrasi, login, logout, dan user management
- **Django Groups** sebagai penanda role `Editor`
- **Django session** untuk mempertahankan status autentikasi pengguna
- **Cookies** untuk menyimpan informasi `last_login`
- **Django decorators dan permission checks** untuk membatasi akses ke endpoint yang membutuhkan autentikasi atau role tertentu

---

## Weekly Progress

### Authentication

Implementasi authentication mencakup:

1. Registrasi akun menggunakan `UserCreationForm`.
2. Login menggunakan `AuthenticationForm`.
3. Logout menggunakan Django authentication system.
4. Halaman dan aksi tertentu dilindungi dengan `@login_required`.
5. User yang belum login tidak dapat mengakses fitur yang membutuhkan autentikasi.

### Session

Setelah login berhasil, Django membuat authentication session untuk pengguna. Status `request.user.is_authenticated` kemudian digunakan oleh aplikasi untuk membedakan pengguna yang sudah login dengan guest.

Session juga memungkinkan aplikasi mengetahui user yang sedang melakukan suatu aksi, misalnya ketika pengguna melakukan star terhadap project atau mengirim Songfess.

### Cookies

Aplikasi menyimpan waktu login pada cookie `last_login`.

Saat login berhasil:

```python
response.set_cookie(
    'last_login',
    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
)
```

Nilai tersebut kemudian dibaca pada halaman utama melalui:

```python
request.COOKIES.get(
    'last_login',
    'No previous login session or cookie found.'
)
```

Cookie dihapus ketika pengguna logout:

```python
response.delete_cookie('last_login')
```

Dengan demikian, implementasi ini sekaligus menunjukkan penggunaan cookie secara eksplisit dalam aplikasi Django.

### Role-Based Access Control

Minggu ini ditambahkan role **Editor** menggunakan Django Group.

Helper yang digunakan:

```python
def is_editor(user):
    return user.groups.filter(name="Editor").exists()
```

Group `Editor` digunakan sebagai role marker. Tidak ada permission Django model yang perlu dicentang pada group tersebut karena hak akses Editor ditentukan secara eksplisit pada view yang membutuhkan kemampuan update.

Pembagian akses yang diterapkan:

| Role | Read | Star | Create | Update | Delete |
|---|---:|---:|---:|---:|---:|
| Guest | Yes | No | No | No | No |
| User | Yes | Yes | No | No | No |
| Editor | Yes | Yes | No | Yes | No |
| Superuser | Yes | Yes | Yes | Yes | Yes |

Untuk **Editor**, hak update diterapkan pada:

- Projects
- Education
- Experience

Sedangkan aksi create dan delete tetap dibatasi untuk superuser.

---

## Role and Access Control

### Guest

Guest dapat membaca konten portfolio, tetapi tidak dapat melakukan aksi yang membutuhkan autentikasi seperti starring project.

### User

User yang telah login dapat:

- Membaca konten
- Melakukan star/unstar pada project
- Menggunakan fitur yang membutuhkan authentication

User biasa tidak mendapatkan akses untuk membuat, mengubah, atau menghapus data portfolio.

### Editor

Editor merupakan custom role yang dibuat menggunakan Django Group.

Editor dapat:

- Membaca konten
- Melakukan star/unstar
- Mengedit Project
- Mengedit Education
- Mengedit Experience

Editor **tidak** dapat:

- Membuat Project baru
- Membuat Education baru
- Membuat Experience baru
- Menghapus Project
- Menghapus Education
- Menghapus Experience

Contoh pengecekan pada endpoint update:

```python
if not (request.user.is_superuser or is_editor(request.user)):
    raise PermissionDenied
```

Pengecekan dilakukan di backend sehingga pembatasan akses tidak hanya bergantung pada apakah tombol tertentu terlihat di template.

### Superuser

Superuser memiliki akses penuh terhadap data portfolio:

- Create
- Read
- Update
- Delete
- Star

Tombol create dan delete pada template juga hanya ditampilkan kepada superuser.

---

## Authentication, Session, and Cookies

### Register

Registrasi menggunakan Django `UserCreationForm`.

Alur:

```text
Guest
  |
  v
Register
  |
  v
User account created
  |
  v
Login
```

### Login

Login menggunakan Django `AuthenticationForm`.

Setelah kredensial valid:

```python
user = form.get_user()
login(request, user)
```

Kemudian aplikasi mengarahkan user kembali ke halaman utama dan menyimpan timestamp login pada cookie `last_login`.

### Logout

Logout menggunakan:

```python
logout(request)
```

Cookie `last_login` juga dihapus setelah logout.

### Protected Views

Endpoint yang membutuhkan autentikasi menggunakan:

```python
@login_required(login_url="/login/")
```

Untuk endpoint yang membutuhkan role tertentu, view melakukan pengecekan tambahan dan melempar `PermissionDenied` jika user tidak memiliki akses.

Contoh:

```python
@login_required(login_url="/login/")
def update_project(request, project_id):
    if not (request.user.is_superuser or is_editor(request.user)):
        raise PermissionDenied
```

---

## AI Disclosure

AI digunakan sebagai **asisten teknis**, bukan sebagai pengganti proses implementasi dan pengujian.

### AI Tool

Tool AI yang digunakan pada minggu ini adalah **ChatGPT (OpenAI)**.

AI digunakan terutama untuk:

1. Meninjau struktur permission pada `views.py`.
2. Memeriksa konsistensi implementasi role pada `Projects`, `Education`, dan `Experience`.
3. Membantu meninjau dokumentasi README agar setup dan implementasi dapat dijelaskan secara terstruktur.

### Bagian yang Dibantu AI

AI terutama membantu pada:

- Penulisan helper `is_editor()`.
- Penyesuaian conditional pada view update.
- Penyesuaian conditional pada template.
- Review konsistensi permission antara Projects, Education, dan Experience.

Implementasi kemudian disesuaikan dengan struktur project yang sudah ada dan diuji secara manual.

### Keterbatasan

Implementasi role saat ini menggunakan nama group `"Editor"` sebagai penanda role. Artinya, perubahan nama group atau kebutuhan role yang jauh lebih kompleks akan membutuhkan perubahan pada kode.

Selain itu, permission belum diabstraksikan menjadi decorator atau permission class khusus karena kebutuhan saat ini masih relatif sederhana. Jika jumlah role dan aturan akses bertambah pada iterasi berikutnya, authorization layer dapat direfactor menjadi sistem permission yang lebih terstruktur.

## Manual Improvements and Limitations

AI membantu mempercepat proses implementasi, tetapi beberapa keputusan tetap dilakukan secara manual berdasarkan struktur project dan hasil pengujian.

### Keputusan implementasi manual

Saya memilih menggunakan **Django Group sebagai role marker** untuk `Editor` karena kebutuhan tugas hanya memerlukan satu custom role dengan pola akses yang jelas. Pendekatan ini lebih sederhana daripada membuat sistem permission baru yang lebih kompleks.

Saya juga mempertahankan create/delete sebagai superuser-only. Dengan demikian, role Editor memiliki tanggung jawab yang lebih terbatas dan sesuai requirement: **dapat melakukan update tetapi tidak dapat mengubah struktur data melalui create/delete**.

---

## Installation and Local Setup

### Requirements

- Python 3.10+
- pip
- Git
- Django
- Dependencies yang tercantum pada `requirements.txt`

### Clone Repository

```bash
git clone https://github.com/<username>/myportofolio.git
cd myportofolio
```

### Create Virtual Environment

Windows:

```bash
python -m venv env
env\Scripts\activate
```

Unix/macOS/Linux:

```bash
python -m venv env
source env/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Configuration

Buat file `.env` pada root project:

```env
PRODUCTION=False
```

Untuk konfigurasi production, gunakan environment variables yang sesuai dengan deployment.

### Database Migration

```bash
python manage.py migrate
```

Untuk local development, database SQLite digunakan sebagai database default sesuai konfigurasi project.

### Run Development Server

```bash
python manage.py runserver
```

Kemudian buka:

```text
http://127.0.0.1:8000/
```

---

## Initial Role Setup

Role `Editor` dikonfigurasi melalui Django Admin.

### Membuat Group Editor

1. Login sebagai superuser.
2. Buka Django Admin.
3. Masuk ke **Groups**.
4. Buat group dengan nama:

```text
Editor
```

5. Tambahkan user yang ingin dijadikan Editor ke group tersebut.

Pada implementasi ini, group digunakan sebagai **role marker**, sehingga tidak diperlukan pemilihan model permission pada group.

### Membuat Superuser

Jika belum tersedia:

```bash
python manage.py createsuperuser
```

Ikuti instruksi Django untuk menentukan username, email, dan password.

---

## Deployment

Production menggunakan PostgreSQL dan dideploy melalui PWS.

Buat project baru pada PWS, kemudian konfigurasi environment variables melalui tab **Environs**:

```env
PRODUCTION=True

DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=<database-port>
SCHEMA=tutorial
```

Pastikan URL deployment PWS ditambahkan ke `ALLOWED_HOSTS` pada `settings.py`.

`WhiteNoiseMiddleware` juga perlu tetap aktif agar static files dapat disajikan pada production.

Untuk melakukan deployment:

```bash
git add .
git commit -m "feat(auth): add editor role for update permissions"
git push pws main:master
```

---

## Testing Checklist

Testing dilakukan berdasarkan matriks role yang ditentukan pada tugas.

### Guest

- [x] Dapat membuka halaman portfolio.
- [x] Dapat melihat Projects, Education, dan Experience.
- [x] Tidak dapat melakukan star.
- [x] Tidak dapat mengakses endpoint update.
- [x] Tidak dapat create/delete.

### User

- [x] Dapat login.
- [x] Dapat melihat portfolio.
- [x] Dapat melakukan star/unstar.
- [x] Tidak mendapatkan tombol Edit.
- [x] Tidak dapat create/delete.

### Editor

- [x] Dapat login sebagai user yang berada di group `Editor`.
- [x] Dapat melakukan star.
- [x] Mendapatkan tombol Edit pada Projects.
- [x] Mendapatkan tombol Edit pada Education.
- [x] Mendapatkan tombol Edit pada Experience.
- [x] Dapat melakukan update data.
- [x] Tidak mendapatkan tombol Add/Create.
- [x] Tidak mendapatkan tombol Delete.
- [x] Endpoint update melakukan pengecekan `is_editor()` di backend.

### Superuser

- [x] Dapat melihat tombol Add/Create.
- [x] Dapat melihat tombol Edit.
- [x] Dapat melihat tombol Delete.
- [x] Dapat create, update, dan delete.
- [x] Dapat melakukan star.

---

## References

- [Django Authentication](https://docs.djangoproject.com/en/stable/topics/auth/)
- [Django Groups](https://docs.djangoproject.com/en/stable/topics/auth/default/#groups)
- [Django Login Required](https://docs.djangoproject.com/en/stable/topics/auth/default/#the-login-required-decorator)
- [Django Sessions](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
- [Django Request and Response Objects](https://docs.djangoproject.com/en/stable/ref/request-response/)
- [MDN — HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [PWS — Pacil Web Service](https://pws.cs.ui.ac.id)