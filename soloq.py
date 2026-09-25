# Instal dependensi: pip install flask
# Jalankan: python app.py
# Buka: http://127.0.0.1:5000

from pathlib import Path
import os
import sqlite3
import uuid

from flask import Flask, abort, redirect, render_template_string, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # Maksimal 50 MB

FOLDER_APP = Path(__file__).parent
FOLDER_BUKU = FOLDER_APP / "buku"
DATABASE = FOLDER_APP / "soloq.db"
FOLDER_BUKU.mkdir(exist_ok=True)


def siapkan_database():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                penulis TEXT NOT NULL,
                nama_file TEXT NOT NULL
            )
        """)


def ambil_buku():
    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        return db.execute("SELECT * FROM buku ORDER BY id DESC").fetchall()


HALAMAN = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SOLOQ — Perpustakaan Komunitas</title>
    <style>
        :root {
            --cream: #f5f0e6;
            --ink: #20352f;
            --green: #355b4a;
            --muted: #64736b;
            --line: rgba(32, 53, 47, .14);
        }

        * { box-sizing: border-box; }

        html { scroll-behavior: smooth; }

        body {
            margin: 0;
            color: var(--ink);
            background:
                radial-gradient(ellipse at 10% 5%, rgba(227, 143, 93, .23), transparent 24rem),
                radial-gradient(ellipse at 90% 28%, rgba(103, 159, 177, .21), transparent 28rem),
                radial-gradient(ellipse at 10% 85%, rgba(105, 143, 101, .20), transparent 26rem),
                var(--cream);
            font-family: Georgia, "Times New Roman", serif;
        }

        a { color: inherit; }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px 7%;
            border-bottom: 1px solid var(--line);
            font-family: Arial, sans-serif;
        }

        .brand {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: .22em;
            text-decoration: none;
        }

        nav { display: flex; gap: 28px; }

        nav a {
            font-size: .9rem;
            text-decoration: none;
            color: var(--muted);
        }

        nav a:hover { color: var(--green); }

        .hero {
            min-height: 520px;
            padding: 105px 7% 90px;
            display: flex;
            align-items: center;
            position: relative;
            overflow: hidden;
        }

        .hero-copy { max-width: 720px; position: relative; z-index: 1; }

        .eyebrow {
            color: var(--green);
            font: 700 .75rem Arial, sans-serif;
            letter-spacing: .2em;
            text-transform: uppercase;
        }

        h1 {
            margin: 20px 0;
            max-width: 700px;
            font-size: clamp(3.4rem, 8vw, 7rem);
            line-height: .95;
            font-weight: 400;
            letter-spacing: -.055em;
        }

        .hero p {
            max-width: 510px;
            color: var(--muted);
            font-size: 1.15rem;
            line-height: 1.7;
        }

        .elements {
            position: absolute;
            right: 8%;
            top: 95px;
            display: grid;
            grid-template-columns: 110px 110px;
            gap: 14px;
            transform: rotate(7deg);
        }

        .element {
            width: 110px;
            height: 110px;
            display: grid;
            place-items: center;
            border: 1px solid rgba(255,255,255,.65);
            border-radius: 50%;
            color: white;
            font: 700 .8rem Arial, sans-serif;
            letter-spacing: .13em;
            box-shadow: 0 12px 35px rgba(32, 53, 47, .12);
        }

        .api { background: linear-gradient(145deg, #7eb4c0, #477e8a); }
        .udara { background: linear-gradient(145deg, #d9e2d8, #91a99b); }
        .api.udara { color: #345248; }
        .api2 { background: linear-gradient(145deg, #f1b078, #c9603d); }
        .tanah { background: linear-gradient(145deg, #a5a66c, #5d704d); }

        .button {
            display: inline-block;
            margin-top: 14px;
            padding: 14px 22px;
            border-radius: 99px;
            background: var(--green);
            color: white;
            font: 700 .9rem Arial, sans-serif;
            text-decoration: none;
        }

        section { padding: 80px 7%; }

        .section-heading {
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 24px;
            margin-bottom: 32px;
        }

        h2 {
            margin: 10px 0 0;
            font-size: clamp(2.2rem, 5vw, 4rem);
            font-weight: 400;
            letter-spacing: -.04em;
        }

        .section-note {
            max-width: 360px;
            color: var(--muted);
            font: .95rem/1.6 Arial, sans-serif;
        }

        .shelf {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 22px;
        }

        .book {
            min-height: 280px;
            padding: 25px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid var(--line);
            border-radius: 6px 18px 18px 6px;
            background: rgba(255,255,255,.56);
            box-shadow: 8px 10px 0 rgba(53, 91, 74, .08);
        }

        .book-cover {
            height: 130px;
            margin: -25px -25px 20px;
            border-radius: 5px 16px 0 0;
            background:
                radial-gradient(circle at 70% 20%, rgba(255,255,255,.55), transparent 35%),
                linear-gradient(145deg, #73917a, #355b4a);
        }

        .book h3 { margin: 0 0 8px; font-size: 1.55rem; }
        .book p { margin: 0; color: var(--muted); font: .9rem Arial, sans-serif; }
        .book a { margin-top: 22px; color: var(--green); font: 700 .9rem Arial, sans-serif; }

        .empty, .form-card {
            padding: 28px;
            border: 1px solid var(--line);
            border-radius: 16px;
            background: rgba(255,255,255,.52);
        }

        .empty { color: var(--muted); line-height: 1.7; }

        .form-card { max-width: 760px; }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        label {
            display: block;
            margin-bottom: 7px;
            font: 700 .85rem Arial, sans-serif;
        }

        input {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--line);
            border-radius: 9px;
            background: rgba(255,255,255,.8);
            font: 1rem Arial, sans-serif;
        }

        input[type="file"] { grid-column: 1 / -1; }

        button {
            margin-top: 18px;
            padding: 13px 20px;
            border: 0;
            border-radius: 99px;
            background: var(--green);
            color: white;
            cursor: pointer;
            font: 700 .9rem Arial, sans-serif;
        }

        .about {
            background: rgba(53, 91, 74, .08);
        }

        .about-text {
            max-width: 820px;
            font-size: clamp(1.25rem, 2.3vw, 1.8rem);
            line-height: 1.7;
        }

        .about-text strong { color: var(--green); }

        footer {
            padding: 28px 7%;
            border-top: 1px solid var(--line);
            color: var(--muted);
            font: .85rem Arial, sans-serif;
        }

        @media (max-width: 760px) {
            .topbar { padding: 20px 6%; align-items: flex-start; }
            nav { gap: 14px; flex-wrap: wrap; justify-content: flex-end; }
            .hero { min-height: 570px; padding: 75px 6%; align-items: flex-start; }
            .elements { right: 8%; top: 340px; transform: scale(.72) rotate(7deg); transform-origin: top right; }
            section { padding: 64px 6%; }
            .section-heading { display: block; }
            .section-note { margin-top: 15px; }
            .form-grid { grid-template-columns: 1fr; }
            input[type="file"] { grid-column: auto; }
        }
    </style>
</head>
<body>
    <header class="topbar">
        <a class="brand" href="#">SOLOQ</a>
        <nav>
            <a href="#perpustakaan">Perpustakaan</a>
            <a href="#isi-buku">Isi buku</a>
            <a href="#tentang">Tentang Soloq</a>
        </nav>
    </header>

    <main>
        <section class="hero">
            <div class="hero-copy">
                <div class="eyebrow">Ruang baca bersama</div>
                <h1>Pengetahuan tumbuh saat dibagikan.</h1>
                <p>
                    Perpustakaan komunitas SOLOQ. Sebuah ruang untuk menyimpan,
                    membaca, dan merawat pengetahuan bersama.
                </p>
                <a class="button" href="#perpustakaan">Jelajahi perpustakaan</a>
            </div>
            <div class="elements" aria-label="Api, air, udara, dan tanah">
                <div class="element api2">API</div>
                <div class="element api">AIR</div>
                <div class="element udara">UDARA</div>
                <div class="element tanah">TANAH</div>
            </div>
        </section>

        <section id="perpustakaan">
            <div class="section-heading">
                <div>
                    <div class="eyebrow">Koleksi komunitas</div>
                    <h2>Perpustakaan SOLOQ</h2>
                </div>
                <p class="section-note">
                    Buku-buku di sini diisi dan dirawat oleh komunitas.
                    Unggah berkas PDF untuk menambahkan bacaan.
                </p>
            </div>

            {% if buku %}
                <div class="shelf">
                    {% for item in buku %}
                        <article class="book">
                            <div>
                                <div class="book-cover"></div>
                                <h3>{{ item["judul"] }}</h3>
                                <p>Oleh {{ item["penulis"] }}</p>
                            </div>
                            <a href="{{ url_for('lihat_buku', nama_file=item['nama_file']) }}" target="_blank">
                                Baca buku ↗
                            </a>
                        </article>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty">
                    Belum ada buku di rak. Tambahkan buku pertama komunitas di bawah.
                </div>
            {% endif %}
        </section>

        <section id="isi-buku">
            <div class="section-heading">
                <div>
                    <div class="eyebrow">Kontribusi</div>
                    <h2>Isi rak buku</h2>
                </div>
            </div>

            <form class="form-card" action="{{ url_for('tambah_buku') }}" method="post" enctype="multipart/form-data">
                <div class="form-grid">
                    <div>
                        <label for="judul">Judul buku</label>
                        <input id="judul" name="judul" required maxlength="150" placeholder="Contoh: Semesta dan Kita">
                    </div>
                    <div>
                        <label for="penulis">Nama penulis</label>
                        <input id="penulis" name="penulis" required maxlength="100" placeholder="Nama penulis">
                    </div>
                    <div>
                        <label for="file_buku">Berkas buku (PDF, maks. 50 MB)</label>
                        <input id="file_buku" name="file_buku" type="file" accept=".pdf,application/pdf" required>
                    </div>
                </div>
                <button type="submit">Tambahkan ke perpustakaan</button>
            </form>
        </section>

        <section class="about" id="tentang">
            <div class="eyebrow">Tentang komunitas</div>
            <h2>Tentang Soloq</h2>
            <div class="about-text">
                <p><strong>SOLOQ</strong> adalah suatu komunitas literasi yang dikerjakan secara bergandengan tangan. Ia lahir bukan karena keresahan, melainkan karena cinta akan pengetahuan tanah, air, api dan udara di semesta raya.</p>
                <p>Ia adalah sebuah upaya akar rumput untuk mencipta masyarakat dengan kesadaran yang lebih segar dan kaya akan pengertian-pengertian.</p>
            </div>
        </section>
    </main>

    <footer>© SOLOQ — Pengetahuan tumbuh bersama.</footer>
</body>
</html>
"""


@app.route("/")
def beranda():
    return render_template_string(HALAMAN, buku=ambil_buku())


@app.route("/tambah-buku", methods=["POST"])
def tambah_buku():
    judul = request.form.get("judul", "").strip()
    penulis = request.form.get("penulis", "").strip()
    file = request.files.get("file_buku")

    if not judul or not penulis or not file or not file.filename:
        abort(400, "Judul, penulis, dan berkas buku wajib diisi.")

    nama_asli = secure_filename(file.filename)
    if not nama_asli.lower().endswith(".pdf"):
        abort(400, "Berkas yang dapat diunggah hanya PDF.")

    nama_simpan = f"{uuid.uuid4().hex}.pdf"
    file.save(FOLDER_BUKU / nama_simpan)

    with sqlite3.connect(DATABASE) as db:
        db.execute(
            "INSERT INTO buku (judul, penulis, nama_file) VALUES (?, ?, ?)",
            (judul, penulis, nama_simpan),
        )

    return redirect(url_for("beranda") + "#perpustakaan")


@app.route("/buku/<nama_file>")
def lihat_buku(nama_file):
    # Hanya izinkan berkas PDF yang tercatat di database.
    with sqlite3.connect(DATABASE) as db:
        ditemukan = db.execute(
            "SELECT 1 FROM buku WHERE nama_file = ?",
            (nama_file,),
        ).fetchone()

    if not ditemukan:
        abort(404)

    return send_from_directory(FOLDER_BUKU, nama_file, mimetype="application/pdf")


siapkan_database()

if __name__ == "__main__":
    app.run(debug=True)