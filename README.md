# Simulasi Random Forest (Streamlit) – Prediksi Pelanggan Berlangganan Internet

Web simulasi Random Forest (Gain Ratio / C4.5) untuk tugas Pembelajaran Mesin, ditulis dengan Python.

## Fitur
1. **Data** – 14 data pelanggan, bisa diedit.
2. **Hutan** – bootstrap sampling, jumlah pohon, m atribut acak, seed. Mode "Sesuai laporan" menghasilkan angka yang sama dengan laporan perhitungan manual.
3. **Pohon** – diagram pohon + detail Entropy, Gain, Split Info, Gain Ratio per node.
4. **Prediksi** – voting mayoritas untuk data baru, lengkap dengan jalur pada tiap pohon.

## Struktur
| File | Isi |
|---|---|
| `app.py` | Tampilan Streamlit |
| `rf_engine.py` | Mesin Random Forest (Python murni) |
| `data_config.py` | Konfigurasi studi kasus (atribut, data, preset laporan) |
| `test_engine.py` | Uji mesin (`python test_engine.py`) |
| `requirements.txt` | Dependensi |

## Menjalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy ke Streamlit Community Cloud (gratis)
1. Upload semua file ke repository GitHub **public**.
2. Buka https://share.streamlit.io lalu login dengan akun GitHub.
3. Klik **Create app**, pilih repository, branch `main`, dan **Main file path** = `app.py`.
4. Klik **Deploy**. Link akan berbentuk `https://<nama-app>.streamlit.app`.

## Link
- Repository: (isi link GitHub)
- Web simulasi: (isi link Streamlit)
- Video tutorial: (isi link YouTube)
