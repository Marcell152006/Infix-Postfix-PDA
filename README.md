# Expression Automata — PDA Infix & Postfix

Aplikasi Streamlit untuk mengenali ekspresi Infix dan Postfix menggunakan simulasi PDA.

## Fitur
- Pilih mode Infix atau Postfix.
- Validasi ekspresi.
- Menampilkan status diterima/ditolak.
- Menampilkan log state, input yang dibaca, aksi, stack, dan input tersisa.
- Infix menggunakan CFG dan satu state pemrosesan `q1` dengan self-loop.
- Postfix menggunakan state `q0`, `q1`, `q2`, `q3`, `q4`, dan `q5`.

## Persyaratan
- Python 3.10 atau lebih baru.

## Instalasi Windows

Buka terminal pada folder proyek:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan aplikasi

```bash
streamlit run app.py
```

Browser akan membuka aplikasi Streamlit. Jika tidak terbuka otomatis, kunjungi alamat lokal yang ditampilkan terminal (biasanya `http://localhost:8501`).

## Aturan Infix
```text
E  -> T E'
E' -> + T E' | - T E' | ε
T  -> F T'
T' -> * F T' | / F T' | ε
F  -> ( E ) | A | B | ... | Z
```

Operand adalah satu huruf kapital A–Z. Operator yang didukung `+ - * /` dan tanda kurung `(` `)`.

## Catatan implementasi
- Pada diagram Infix, top of stack berada di sebelah kiri.
- Ekspansi CFG bersifat nondeterministik. Program mencari jalur yang berhasil mencapai konfigurasi penerimaan.
- `$` adalah penanda akhir internal yang ditambahkan oleh simulasi, bukan karakter yang perlu diketik pengguna.
- Program hanya mengenali struktur ekspresi, tidak menghitung nilai aritmetikanya.
