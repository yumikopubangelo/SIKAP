Tempatkan public key RFID per perangkat di folder ini.

Format file:
- Nama file harus sama dengan `device_id` perangkat, misalnya `ESP-001.pem`
- Isi file adalah public key PEM

Alur yang didukung:
1. Perangkat RFID menyimpan private key.
2. Perangkat menandatangani payload absensi.
3. Backend memverifikasi signature memakai public key dari folder ini.

Header yang dipakai backend:
- `X-API-Key`
- `X-RFID-Signature`
- `X-RFID-Signature-Timestamp`
