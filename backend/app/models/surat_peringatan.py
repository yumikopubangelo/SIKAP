from . import db

class SuratPeringatan(db.Model):
    __tablename__ = "surat_peringatan"

    id_sp = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(
        db.Integer,
        db.ForeignKey("siswa.id_siswa", ondelete="CASCADE"),
        nullable=False,
    )
    sp_ke = db.Column(db.Integer, nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    jenis = db.Column(db.String(10), nullable=False)
    status_kirim = db.Column(db.String(20), server_default="belum_kirim")
    id_pengirim = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="SET NULL"),
    )
    alasan = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    siswa = db.relationship("Siswa", backref=db.backref("surat_peringatan", lazy="dynamic"))
    pengirim = db.relationship("User", backref=db.backref("sp_dikirim", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<SuratPeringatan id_sp={self.id_sp}>"
