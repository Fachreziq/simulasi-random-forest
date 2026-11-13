"""Konfigurasi studi kasus. Ubah file ini untuk mengganti atribut/data."""
CONFIG = {
    "title": "Prediksi Pelanggan Berlangganan Internet Rumah",
    "label": "Berlangganan",
    "classes": ["Tidak", "Ya"],
    "attributes": [
        {"key": "Usia", "name": "Usia", "values": ["Muda", "Dewasa", "Senior"]},
        {"key": "Penghasilan", "name": "Penghasilan", "values": ["Tinggi", "Sedang", "Rendah"]},
        {"key": "Aktif", "name": "Pengguna Aktif", "values": ["Ya", "Tidak"]},
        {"key": "Sinyal", "name": "Kualitas Sinyal", "values": ["Baik", "Buruk"]},
    ],
    # [No, Usia, Penghasilan, Pengguna Aktif, Kualitas Sinyal, Berlangganan]
    "rows": [
        [1, "Muda", "Rendah", "Ya", "Buruk", "Ya"],
        [2, "Muda", "Tinggi", "Ya", "Baik", "Ya"],
        [3, "Muda", "Sedang", "Tidak", "Baik", "Tidak"],
        [4, "Muda", "Rendah", "Tidak", "Buruk", "Tidak"],
        [5, "Dewasa", "Tinggi", "Ya", "Buruk", "Ya"],
        [6, "Dewasa", "Sedang", "Ya", "Baik", "Ya"],
        [7, "Dewasa", "Rendah", "Tidak", "Baik", "Tidak"],
        [8, "Dewasa", "Tinggi", "Tidak", "Buruk", "Ya"],
        [9, "Senior", "Sedang", "Tidak", "Baik", "Tidak"],
        [10, "Senior", "Rendah", "Ya", "Buruk", "Tidak"],
        [11, "Senior", "Tinggi", "Ya", "Baik", "Ya"],
        [12, "Senior", "Sedang", "Ya", "Buruk", "Ya"],
        [13, "Muda", "Sedang", "Ya", "Buruk", "Ya"],
        [14, "Dewasa", "Rendah", "Tidak", "Buruk", "Tidak"],
    ],
    "test": {"Usia": "Muda", "Penghasilan": "Sedang", "Aktif": "Ya", "Sinyal": "Buruk"},
    # Bootstrap dan atribut acak yang dipakai pada laporan (m = 2)
    "preset": {
        "trees": [
            {
                "bootstrap": [6, 3, 7, 11, 1, 2, 14, 9, 2, 6, 10, 1, 9, 4],
                "candidates": {
                    "Root": ["Usia", "Sinyal"],
                    "Root/Usia=Dewasa": ["Aktif", "Sinyal"],
                    "Root/Usia=Muda": ["Penghasilan", "Sinyal"],
                    "Root/Usia=Muda/Penghasilan=Rendah": ["Aktif", "Sinyal"],
                    "Root/Usia=Senior": ["Penghasilan", "Sinyal"],
                },
            },
            {
                "bootstrap": [4, 11, 11, 10, 1, 10, 10, 7, 1, 4, 1, 9, 14, 3],
                "candidates": {
                    "Root": ["Aktif", "Penghasilan"],
                    "Root/Aktif=Ya": ["Usia", "Sinyal"],
                    "Root/Aktif=Ya/Usia=Senior": ["Sinyal", "Penghasilan"],
                },
            },
            {
                "bootstrap": [2, 10, 10, 11, 4, 6, 2, 9, 12, 2, 10, 1, 10, 4],
                "candidates": {
                    "Root": ["Sinyal", "Aktif"],
                    "Root/Aktif=Ya": ["Sinyal", "Penghasilan"],
                    "Root/Aktif=Ya/Sinyal=Buruk": ["Penghasilan", "Usia"],
                    "Root/Aktif=Ya/Sinyal=Buruk/Penghasilan=Rendah": ["Usia"],
                },
            },
        ]
    },
}
