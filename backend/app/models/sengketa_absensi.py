from . import db

class SengketaAbsensi(db.Model):
    __tablename__ = "sengketa_absensi"

    id_sengketa = db.Column(db.Integer, primary_key=True)
    id_siswa = db.Column(
        db.Integer,
        db.ForeignKey("siswa.id_siswa", ondelete="CASCADE"),
        nullable=False,
    )
    id_sesi = db.Column(
        db.Integer,
        db.ForeignKey("sesi_sholat.id_sesi", ondelete="CASCADE"),
        nullable=False,
    )
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
    verified_at = db.Column(db.DateTime)

    siswa = db.relationship("Siswa", backref=db.backref("sengketa_absensi", lazy="dynamic"))
    sesi = db.relationship("SesiSholat", backref=db.backref("sengketa", lazy="dynamic"))
    verifikator = db.relationship("User", backref=db.backref("klaim_diverifikasi", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<SengketaAbsensi id_sengketa={self.id_sengketa}>"
