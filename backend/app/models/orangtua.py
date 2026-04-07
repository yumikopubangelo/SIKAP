from . import db

class OrangTua(db.Model):
    __tablename__ = "orangtua"

    id_ortu = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    id_siswa = db.Column(
        db.Integer,
        db.ForeignKey("siswa.id_siswa", ondelete="CASCADE"),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    user = db.relationship("User", backref=db.backref("orangtua_profile", uselist=False))
    siswa = db.relationship("Siswa", backref=db.backref("orangtua", uselist=False))

    def __repr__(self) -> str:
        return f"<OrangTua id_ortu={self.id_ortu}>"
