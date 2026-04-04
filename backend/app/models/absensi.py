from . import db


ABSENSI_STATUS_VALUES = (
    "tepat_waktu",
    "terlambat",
    "alpha",
    "haid",
    "izin",
    "sakit",
)


class StatusAbsensi(db.Model):
    __tablename__ = "status_absensi"

    kode = db.Column(db.String(20), primary_key=True)
    deskripsi = db.Column(db.String(50), nullable=False)

    absensi = db.relationship("Absensi", back_populates="status_ref")

    def __repr__(self) -> str:
        return f"<StatusAbsensi {self.kode}>"


class Absensi(db.Model):
    __tablename__ = "absensi"
    __table_args__ = (
        db.CheckConstraint(
            f"status IN {ABSENSI_STATUS_VALUES}",
            name="ck_absensi_status_valid",
        ),
        db.UniqueConstraint(
            "id_siswa",
            "id_sesi",
            name="uq_absensi_id_siswa_id_sesi",
        ),
    )

    id_absensi = db.Column(db.Integer, primary_key=True)
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
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )
    status = db.Column(
        db.String(20),
        db.ForeignKey("status_absensi.kode", ondelete="RESTRICT"),
        nullable=False,
    )
    device_id = db.Column(
        db.String(50),
        db.ForeignKey("perangkat.device_id", ondelete="SET NULL"),
    )
    id_verifikator = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="SET NULL"),
    )
    verified_at = db.Column(db.DateTime)
    keterangan = db.Column(db.String(255))

    siswa = db.relationship("Siswa", back_populates="absensi")
    sesi = db.relationship("SesiSholat", back_populates="absensi")
    status_ref = db.relationship("StatusAbsensi", back_populates="absensi")
    perangkat = db.relationship("Perangkat", back_populates="absensi")
    verifikator = db.relationship(
        "User",
        back_populates="absensi_terverifikasi",
        foreign_keys=[id_verifikator],
    )

    def __repr__(self) -> str:
        return f"<Absensi {self.id_absensi}>"
