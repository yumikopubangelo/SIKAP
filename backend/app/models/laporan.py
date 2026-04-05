from . import db


LAPORAN_FORMAT_VALUES = ("pdf", "excel")
LAPORAN_JENIS_VALUES = ("kelas", "siswa", "sekolah")


class Laporan(db.Model):
    __tablename__ = "laporan"
    __table_args__ = (
        db.CheckConstraint(
            f"format IN {LAPORAN_FORMAT_VALUES}",
            name="ck_laporan_format_valid",
        ),
        db.CheckConstraint(
            f"jenis IN {LAPORAN_JENIS_VALUES}",
            name="ck_laporan_jenis_valid",
        ),
    )

    id_laporan = db.Column(db.Integer, primary_key=True)
    jenis = db.Column(db.String(20), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    filter_data = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False, unique=True)
    generated_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    user = db.relationship("User", backref="laporan")

    def __repr__(self) -> str:
        return f"<Laporan {self.id_laporan}>"
