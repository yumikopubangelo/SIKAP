from . import db

class Guru(db.Model):
    __tablename__ = "guru"

    id_guru = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    nip = db.Column(db.String(30), unique=True)
    nama = db.Column(db.String(100), nullable=False)
    jabatan = db.Column(db.String(50))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    user = db.relationship("User", backref=db.backref("guru_profile", uselist=False))

    def __repr__(self) -> str:
        return f"<Guru {self.nama}>"
