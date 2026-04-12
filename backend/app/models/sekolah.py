from . import db

class SekolahInfo(db.Model):
    __tablename__ = "sekolah_info"

    id_sekolah = db.Column(db.Integer, primary_key=True, default=1)
    nama_sekolah = db.Column(db.String(150), nullable=False)
    alamat = db.Column(db.Text)
    no_telp = db.Column(db.String(20))
    email = db.Column(db.String(100))
    logo_path = db.Column(db.String(255))
    foto_masjid_path = db.Column(db.String(255))
    updated_at = db.Column(
        db.DateTime,
        onupdate=db.func.now(),
    )

    def __repr__(self) -> str:
        return f"<SekolahInfo {self.nama_sekolah}>"
