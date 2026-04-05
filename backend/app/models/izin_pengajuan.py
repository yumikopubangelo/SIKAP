from . import db

class IzinPengajuan(db.Model):
    __tablename__ = "izin_pengajuan"

    id_izin = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(
        db.Integer,
        db.ForeignKey("siswa.id_siswa", ondelete="CASCADE"),
        nullable=False,
    )
    tanggal_mulai = db.Column(db.Date, nullable=False)
    tanggal_selesai = db.Column(db.Date, nullable=False)
    alasan = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), server_default="pending")
    id_verifikator = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="SET NULL"),
    )
    catatan_verifikator = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )
    updated_at = db.Column(
        db.DateTime,
        onupdate=db.func.now(),
    )

    siswa = db.relationship("Siswa", backref=db.backref("izin_pengajuan", lazy="dynamic"))
    verifikator = db.relationship("User", backref=db.backref("izin_diverifikasi", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<IzinPengajuan id_izin={self.id_izin}>"
