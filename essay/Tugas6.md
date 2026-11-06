# Tugas 6

## [Pertanyaan Reflektif](https://pbp.cs.ui.ac.id/assignments/individual/tugas-6.html#pertanyaan-reflektif)

> 1. Jelaskan apa yang dimaksud dengan REST dan mengapa mengembalikan JSON saja belum cukup untuk menyebut sebuah API sebagai RESTful! Jelaskan pula perbedaan PUT dan PATCH beserta contoh kapan masing-masing sebaiknya digunakan!

REST[^1] (*Representational State Transfer*) adalah gaya arsitektur untuk merancang web API, bukan library dan bukan format data. Karena itu, sebuah API tidak otomatis RESTful hanya karena responsnya JSON. Yang menentukan adalah cara API itu diatur. Tiga gagasan yang benar-benar saya praktikkan minggu ini:

- **Data diperlakukan sebagai resource.** URL menunjuk data, bukan tindakan: `/api/v1/education/` untuk kumpulan data dan `/api/v1/education/<uuid>/` untuk satu data.
- **HTTP method menyatakan tindakan.** `GET` membaca, `POST` membuat, `PUT`/`PATCH` mengubah, dan `DELETE` menghapus, sehingga kata kerja tidak perlu ditulis di URL.
- **Klien dan server bertukar representasi data.** Klien mengirim dan menerima JSON, dan status HTTP dipakai sesuai maknanya (`201` saat dibuat, `400` untuk input salah, `403` untuk tindakan yang tidak diizinkan, `404` untuk data yang tidak ada, `204` setelah dihapus).

Perbedaannya paling terasa jika dibandingkan dengan Tugas 5. Di sana saya memakai `POST /projects/add-ajax/` untuk menambah dan `POST /projects/<uuid>/delete/` untuk menghapus, jadi tindakannya tertulis di URL dan hampir semuanya lewat `POST`. Datanya memang JSON, tetapi bentuknya bukan REST. Sekarang tindakan yang sama menjadi `POST /api/v1/projects/` dan `DELETE /api/v1/projects/<uuid>/`. Intinya JSON hanya menjawab pertanyaan "format apa yang dipakai", sedangkan REST menjawab "bagaimana API itu disusun".

Saya juga perlu jujur bahwa API saya belum sepenuhnya RESTful menurut definisi aslinya. REST mensyaratkan *stateless*, sedangkan `SessionAuthentication` menyimpan sesi di server. Endpoint `/appreciate/` lebih mirip aksi (toggle) daripada resource. API saya juga tidak menyertakan tautan hypermedia di responsnya. Pilihan session ini tetap wajar untuk klien AJAX yang berjalan di website yang sama, dan yang terpenting kontrak API-nya jelas dan konsisten.

PUT dan PATCH sama-sama mengubah data, tetapi cakupannya berbeda. **PUT** mengirim representasi pengganti secara utuh, jadi semua field wajib ikut dikirim. **PATCH** hanya mengirim field yang ingin diubah, dan field lain dibiarkan seperti semula (di DRF, ini diatur lewat `partial=True`). Saya membuktikannya di test: `PUT` ke Project dengan isi `{"title": "Incomplete"}` menghasilkan `400` karena `description` dan `tags` wajib, sedangkan `PATCH` dengan isi yang sama menghasilkan `200` dan deskripsinya tetap utuh.

Dalam praktik, **PATCH** cocok untuk perubahan kecil. Contoh paling jelas ada di Songfess: ketika saya membalas lagu, yang dikirim hanya `{"reply": "..."}`, sehingga judul lagu dan pesan pengirim tidak tersentuh. **PUT** cocok ketika klien memang memegang data lengkap dan ingin menggantinya seluruhnya, misalnya menyinkronkan satu data dari form yang berisi semua kolom. Modal edit Education dan Experience saya tetap memakai PATCH walaupun semua kolom ikut dikirim, karena lebih aman: kalau suatu kolom tidak terkirim, nilainya tidak ikut terhapus.

> 2. Jelaskan peran serializer pada Django REST Framework! Apa keuntungannya dibandingkan merakit dictionary secara manual dengan JsonResponse seperti pada Tutorial 05?

Serializer[^2] adalah lapisan yang menerjemahkan data dua arah. Pada `GET`, ia mengubah objek model menjadi tipe data Python yang siap dirender menjadi JSON (*serialization*). Pada `POST`/`PUT`/`PATCH`, ia mengubah input klien menjadi data yang sudah divalidasi dan siap disimpan (*deserialization*). Hasil serializer belum berupa string JSON, karena renderer DRF yang mengubahnya jadi isi response.

Di Tugas 5, `get_projects_json` merakit dictionary satu per satu di dalam perulangan, lalu validasi input dikerjakan terpisah oleh `ProjectForm` dan `form.errors.get_json_data()`. Pola itu berfungsi, tetapi pekerjaannya berulang untuk setiap model. Dengan `ModelSerializer`, satu class menggantikan keduanya. Contohnya `EducationSerializer` mendefinisikan daftar `fields` secara eksplisit (bukan `"__all__"`), validasi lewat `validate_institution` dan `validate_degree` yang memakai `strip_tags`, serta field hasil hitungan lewat `SerializerMethodField`.

Beberapa keuntungan yang saya rasakan langsung:

- **Kontrak data satu tempat.** Field yang keluar masuk tertulis di `Meta.fields`, jadi password dan email akun tidak mungkin ikut terkirim. Untuk nama pemberi apresiasi, hanya `username` yang diambil.
- **Field hasil hitungan bersifat read-only.** `appreciation_count`, `is_appreciated`, dan `appreciated_by_names` dihitung server. Di test, saya mengirim `appreciation_count: 99` dan `appreciated_by_names: "forged"`, dan nilainya tetap diabaikan.
- **Bentuk data bisa menyesuaikan siapa yang melihat.** Pada Songfess saya memakai dua serializer: `PublicSongfessSerializer` (tanpa `message` dan tanpa akun pengirim) untuk pengunjung, dan `SongfessSerializer` untuk pengirim, pemilik, serta Editor. Di dalam `SongfessSerializer`, `get_fields()` mengunci `reply` menjadi read-only untuk siapa pun yang bukan pemilik atau Editor, sehingga pengirim tidak bisa menulis balasannya sendiri walaupun mengirim field itu.
- **Error validasi konsisten.** `is_valid(raise_exception=True)` otomatis membalas `400` beserta error per field, tanpa saya menulis percabangan `if` di setiap view.

Ada dua hal yang saya pelajari dengan cara yang agak menyakitkan. Pertama, di langkah awal serializer saya langsung error `ImproperlyConfigured: Field name tech_stack is not valid for model Project`. Penyebabnya, tutorial memakai nama field `tech_stack`, sedangkan model saya memakai `tags` (ditambah `meta` dan `order` yang wajib diisi). Dari situ saya sadar bahwa serializer membaca definisi model saya sendiri, bukan contoh di tutorial. Kedua, serializer punya jalur validasi yang terpisah dari form: `ProjectForm.clean_title` tidak ikut berjalan di API, jadi aturan seperti pembersihan tag HTML harus ditulis ulang di `validate_<field>`.

> 3. Jelaskan perbedaan autentikasi dan otorisasi pada Django REST Framework! Mengapa hak akses harus diperiksa dengan permission class di server, bukan hanya dengan menyembunyikan tombol di template?

**Autentikasi** menjawab pertanyaan "siapa kamu?", sedangkan **otorisasi** menjawab "apa yang boleh kamu lakukan?". DRF memisahkan keduanya. *Authentication class* (di proyek ini `SessionAuthentication`) mengenali sesi login Django dan mengisi `request.user`. Setelah itu *permission class* memutuskan apakah request boleh diteruskan. Pengunjung yang belum login tidak ditolak di tahap autentikasi, ia hanya diperlakukan sebagai anonim, dan penolakan `403` baru terjadi di tahap permission.

Aturan akses minggu ini saya tulis sebagai permission class terpisah, bukan `if` di dalam view:

- `IsPortfolioOwnerOrReadOnly` untuk Project: semua orang boleh membaca, hanya superuser yang boleh menulis.
- `IsPortfolioOwnerOrEditorOrReadOnly` untuk Education dan Experience: sama, tetapi anggota grup `Editor` juga boleh `PUT` dan `PATCH`, sedangkan `POST` dan `DELETE` tetap ditolak.
- `IsAuthenticated` untuk endpoint star/apresiasi, dan akun pemberi selalu diambil dari `request.user`, bukan dari input.
- `IsSongfessSenderOrStaffOrReadOnly` untuk Songfess, yang juga memeriksa level objek: pengirim hanya boleh mengubah kirimannya sendiri selama belum dibalas, dan boleh menghapusnya kapan saja.

Hak akses harus diperiksa di server karena tombol di template hanyalah kenyamanan tampilan, bukan penjagaan. Siapa pun bisa membuka DevTools dan memanggil `fetch()` langsung ke `/api/v1/...` tanpa melewati tombol apa pun. Saya mengujinya sendiri: dengan akun Editor, saya menjalankan tiga `fetch()` dari Console ke data uji, dan hasilnya `DELETE` `403`, `POST` `403`, dan `PATCH` `200`. Itu membuktikan pembatasan ada di server. Menariknya, Browsable API juga menyembunyikan form POST di halaman daftar dan tombol DELETE di halaman detail untuk akun Editor itu, karena ia memeriksa permission untuk setiap method. Tetapi tombol yang hilang itu hanya bukti tidak langsung, angka status dari Console-lah bukti yang sebenarnya.

Urutan pemeriksaannya juga berpengaruh pada status yang muncul. Permission diperiksa sebelum objek dicari, jadi pengguna biasa yang mencoba mengubah data yang tidak ada mendapat `403`, bukan `404`. Untuk Songfess saya sengaja membuat kiriman yang belum dibalas menjawab `404` (bukan `403`) bagi orang yang tidak berhak melihatnya, supaya orang luar tidak bisa mengetahui ada atau tidaknya kiriman tertentu. Satu catatan kecil: saya tidak memakai `IsAdminUser` bawaan DRF karena ia memeriksa `is_staff`, sedangkan aturan portofolio saya memakai `is_superuser`.

> 4. Jelaskan mengapa permintaan yang mengubah data tetap memerlukan token CSRF ketika API memakai SessionAuthentication! Mengapa test yang memakai force_authenticate tidak cukup untuk membuktikan bahwa perlindungan CSRF berjalan?

CSRF[^3] (*Cross-Site Request Forgery*) memanfaatkan fakta bahwa browser otomatis menyertakan cookie sesi pada setiap request ke domain yang sama. Jika saya sedang login di website saya, halaman jahat di tab lain bisa memicu request `DELETE` atau `POST` ke website saya, dan browser akan ikut mengirim cookie sesi saya. Dari sisi server, request itu tampak sah karena `SessionAuthentication` hanya melihat cookie sesi. Token CSRF menutup celah ini: halaman jahat tidak bisa membaca token milik website saya, sehingga tidak bisa menyertakannya. Karena itu, untuk `POST`, `PUT`, `PATCH`, dan `DELETE` dari pengguna yang terautentikasi lewat sesi, DRF memeriksa token CSRF, dan `403` muncul bila token tidak ada atau salah. Hal ini tidak berlaku untuk autentikasi berbasis token header, karena header itu tidak dikirim otomatis oleh browser.

Di sisi frontend, setiap request tulis saya menyertakan header `X-CSRFToken` yang nilainya dibaca dari cookie `csrftoken` lewat `getCookie()`. Saya sempat belajar bahwa cookie itu tidak selalu ada. Skrip Tugas 5 dulu "kebetulan" membuat cookie lewat `{% csrf_token %}` di dalam form star dan hapus. Setelah form itu diganti `fetch()`, saya harus menaruh `{% csrf_token %}` secara eksplisit di template, kalau tidak, pengguna biasa bisa mendapat `403 CSRF Failed: CSRF cookie not set`. Tentu saya tidak memakai `@csrf_exempt` sebagai jalan pintas.

`force_authenticate` tidak cukup karena ia melewati proses autentikasi sama sekali. Dengan `force_authenticate`, `request.user` langsung diisi tanpa melalui `SessionAuthentication`, sehingga pemeriksaan CSRF yang menjadi bagian dari autentikasi sesi tidak pernah berjalan. Test dengan `force_authenticate` memang berguna untuk menguji permission (siapa boleh melakukan apa), tetapi tidak menguji login maupun CSRF. Selain itu, test client bawaan Django mematikan pemeriksaan CSRF secara default, jadi test yang tampak lulus bisa saja menyembunyikan celah.

Karena itu saya menulis test terpisah dengan `APIClient(enforce_csrf_checks=True)` dan `.login()` yang membuat sesi sungguhan. Untuk Project, Education, Experience, dan Songfess, masing-masing ada test yang membuktikan `POST` tanpa token CSRF ditolak dengan `403` dan tidak ada data yang tersimpan (saya memeriksa `Model.objects.count()`, bukan hanya status HTTP). Untuk Project ada satu test tambahan yang membuktikan sebaliknya: token CSRF yang valid, diambil dari Browsable API, membuat `POST` berhasil dengan `201`.

## AI Disclosure

Minggu ini saya menggunakan **Claude (Anthropic)** sebagai pemandu pengerjaan. Saya juga mengirim screenshot DevTools dan seluruh output terminal (termasuk *traceback*) setiap kali ada error, supaya penjelasannya sesuai kondisi proyek saya dan bukan contoh umum.

### Keputusan dan perbaikan yang saya lakukan sendiri

- **Nama field.** Saya menyadari model saya berbeda dari model di tutorial (`tags`, `meta`, `order`), dan saya yang mencocokkannya setelah error `ImproperlyConfigured`.
- **Penamaan `appreciated_by`.** AI awalnya mengusulkan `starred_by`. Saya menilai itu tidak masuk akal untuk riwayat pendidikan, jadi saya memilih `appreciated_by`.
- **Arah Songfess.** Saya mengubah konsepnya: pengunjung mengirim lagu untuk saya, dengan Editor setara pemilik. Saya juga memutuskan menyembunyikan tampilannya sementara, sambil mempertahankan API dan test-nya.
- **Cakupan model.** Atas arahan asisten dosen (kata kak Vazha), saya mengerjakan seluruh model, bukan hanya satu.
- **Verifikasi.** Saya menguji setiap langkah di Browsable API dan DevTools sebelum lanjut, dan hanya meng-*commit* setelah `python manage.py test main` lulus.

### Keterbatasan AI yang saya temui

AI tidak selalu benar, dan beberapa kesalahannya ketahuan dari pengujian dan pembacaan saya sendiri:

- AI sempat menganggap akun `admin` saya adalah superuser, padahal itu akun Editor. Tombol POST dan DELETE yang tidak muncul di Browsable API ternyata justru bukti permission Editor bekerja.
- Satu test Songfess yang ditulis AI (`test_songfess_page_roles`) gagal karena memeriksa kata `reply-modal` yang ternyata juga muncul di dalam JavaScript halaman. Yang benar adalah memeriksa elemen `id="reply-modal"`. Perilaku halamannya sudah benar, test-nya yang perlu diperbaiki.

Dari semua itu, saya belajar bahwa kode dari AI tetap harus diuji dan dibaca ulang. Sebuah saran yang terdengar meyakinkan bisa saja menggeser langkah yang wajib, salah menebak peran akun, atau menulis test yang salah sasaran.

## Installation and Deployment

*(Ada perubahan `models.py`, migrasi baru, dan satu dependency baru minggu ini. Selebihnya langkah instalasi sama seperti minggu-minggu sebelumnya.)*

### Requirements

- Python 3.10+
- pip
- Git
- Django `~=5.2`
- `djangorestframework~=3.18.3` (dependency baru, sudah tercatat di `requirements.txt`)

### Local Preview

Clone repositori ini
```bash
git clone https://github.com/<username>/myportofolio.git
cd myportofolio
```

Buat virtual environment
```bash
python -m venv env

# Windows (cmd/PowerShell)
env\Scripts\activate

# Unix (macOS/Linux)
source env/bin/activate
```

Install dependencies
```bash
pip install -r requirements.txt
```

Buat file `.env` di root proyek untuk konfigurasi lokal:
```
PRODUCTION=False
```

Jalankan migrasi dan server
```bash
python manage.py migrate
python manage.py runserver
```

Lalu buka `http://127.0.0.1:8000/`. Browsable API tersedia di `http://127.0.0.1:8000/api/v1/projects/`, `/api/v1/education/`, `/api/v1/experience/`, dan `/api/v1/songfess/`.

### Perubahan Skema Database

Migrasi minggu ini menambahkan:

- `appreciated_by` (`ManyToManyField` ke `User`) pada `Education` dan `Experience`.
- Perubahan pada `Songfess`: `requester` dari `OneToOneField` menjadi `ForeignKey`, `song_title` kini wajib, serta field baru `reply` dan `created_at`.

Data `Songfess` lama memakai arti yang terbalik (dulu `song_title` diisi pemilik), jadi sebaiknya dirapikan atau dihapus lewat Django Admin setelah migrasi.

### Role Setup

Peran Editor masih memakai grup Django bernama persis `Editor` (lihat Tugas 4). Buat grup itu lewat Django Admin, lalu masukkan akun yang ingin dijadikan Editor.

### Running Tests

```bash
python manage.py test main
```

Hasil terakhir: **82 test lulus**. Rinciannya: 13 test lama di `main/tests.py`, ditambah test API di `main/tests_api.py` untuk Project (13), Education (15, termasuk apresiasi), Experience (15), dan Songfess (26). Test mencakup setiap peran, pemeriksaan isi database pada test penolakan, validasi input, star/apresiasi, dan pemeriksaan CSRF dengan `APIClient(enforce_csrf_checks=True)`.

Gunakan `python manage.py test main`, bukan `python manage.py test` tanpa nama app, agar `test_e2e.py` (Selenium) dari Tugas 4 tidak ikut dijalankan.

### Deployment

Produksi memakai PostgreSQL dan dideploy melalui [PWS](https://pws.cs.ui.ac.id) dengan environment variable yang sama seperti minggu lalu (`PRODUCTION`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `SCHEMA`).

Hal yang perlu diperhatikan untuk deployment minggu ini:

- `CSRF_TRUSTED_ORIGINS` harus sama persis dengan origin HTTPS PWS, karena request tulis dari `fetch()` sekarang diperiksa token CSRF-nya.
- Migrasi baru harus diterapkan ke database produksi sebelum fitur apresiasi dan Songfess dipakai.
- Setelah deploy, uji membaca, login, dan satu operasi tulis.

Untuk push perubahan ke PWS:
```bash
git add .
git commit -m "chore: deploy"
git push pws main:master
```

## Referensi

- https://www.django-rest-framework.org/api-guide/serializers/
- https://www.django-rest-framework.org/api-guide/permissions/
- https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication
- https://www.django-rest-framework.org/topics/ajax-csrf-cors/
- https://www.django-rest-framework.org/api-guide/testing/
- https://docs.djangoproject.com/en/5.2/ref/csrf/
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PUT
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/PATCH
- https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm

[^1]: REST: *Representational State Transfer*, gaya arsitektur untuk merancang web API yang memperlakukan data sebagai resource, memakai method HTTP untuk menyatakan tindakan, dan menukar representasi data antara klien dan server.
[^2]: Serializer: komponen DRF yang mengubah objek model menjadi tipe data Python yang dapat dirender ke JSON, dan sebaliknya memvalidasi serta mengubah input klien menjadi data yang siap disimpan.
[^3]: CSRF: *Cross-Site Request Forgery*, serangan yang membuat browser pengguna yang sedang login mengirim request tidak sah ke sebuah website, dengan memanfaatkan cookie sesi yang dikirim otomatis oleh browser.