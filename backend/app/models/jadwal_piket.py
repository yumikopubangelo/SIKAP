from . import db

class JadwalPiket(db.Model):
    __tablename__ = "jadwal_piket"

    id_jadwal = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=False,
    )
    hari = db.Column(db.String(10), nullable=False)
    jam_mulai = db.Column(db.Time, nullable=False)
    jam_selesai = db.Column(db.Time, nullable=False)

    user = db.relationship("User", backref=db.backref("jadwal_piket", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<JadwalPiket hari={self.hari}>"
