from . import db


JENIS_KELAMIN_VALUES = ("L", "P")


class Siswa(db.Model):
    __tablename__ = "siswa"
    __table_args__ = (
        db.CheckConstraint(
            "jenis_kelamin IS NULL OR jenis_kelamin IN ('L', 'P')",
            name="ck_siswa_jenis_kelamin_valid",
        ),
    )

    id_siswa = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    nisn = db.Column(db.String(20), nullable=False, unique=True)
    nama = db.Column(db.String(100), nullable=False)
    jenis_kelamin = db.Column(db.String(10))
    alamat = db.Column(db.Text)
    no_telp_ortu = db.Column(db.String(20))
    id_card = db.Column(db.String(50), unique=True)
    id_kelas = db.Column(
        db.Integer,
        db.ForeignKey("kelas.id_kelas", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    user = db.relationship("User", back_populates="siswa_profile")
    kelas = db.relationship("Kelas", back_populates="siswa")
    absensi = db.relationship("Absensi", back_populates="siswa")

    def __repr__(self) -> str:
        return f"<Siswa {self.nisn}>"
