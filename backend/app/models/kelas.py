from . import db


TINGKAT_VALUES = ("X", "XI", "XII")


class Kelas(db.Model):
    __tablename__ = "kelas"
    id_kelas = db.Column(db.Integer, primary_key=True)
    nama_kelas = db.Column(db.String(20), nullable=False)
    tingkat = db.Column(db.String(5), nullable=False)
    jurusan = db.Column(db.String(50))
    id_wali = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="SET NULL"),
        nullable=True,
    )
    tahun_ajaran = db.Column(db.String(10), nullable=False)

    wali_kelas = db.relationship(
        "User",
        back_populates="kelas_wali",
        foreign_keys=[id_wali],
    )
    siswa = db.relationship("Siswa", back_populates="kelas")

    __table_args__ = (
        db.CheckConstraint(
            f"tingkat IN {TINGKAT_VALUES}",
            name="ck_kelas_tingkat_valid",
        ),
        db.UniqueConstraint(
            "nama_kelas",
            "tahun_ajaran",
            name="uq_kelas_nama_tahun_ajaran",
        ),
    )

    def __repr__(self) -> str:
        return f"<Kelas {self.nama_kelas}>"
