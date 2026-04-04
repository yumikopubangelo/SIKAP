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

    def to_dict(self) -> dict:
        kelas = self.siswa.kelas if self.siswa else None
        waktu_sholat = self.sesi.waktu_sholat if self.sesi else None
        return {
            "id_absensi": self.id_absensi,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "status": self.status,
            "keterangan": self.keterangan,
            "device_id": self.device_id,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "siswa": {
                "id_siswa": self.siswa.id_siswa,
                "nisn": self.siswa.nisn,
                "nama": self.siswa.nama,
                "id_card": self.siswa.id_card,
                "kelas": kelas.nama_kelas if kelas else None,
            } if self.siswa else None,
            "sesi": {
                "id_sesi": self.sesi.id_sesi,
                "tanggal": self.sesi.tanggal.isoformat() if self.sesi and self.sesi.tanggal else None,
                "status": self.sesi.status if self.sesi else None,
                "waktu_sholat": waktu_sholat.nama_sholat if waktu_sholat else None,
            } if self.sesi else None,
            "perangkat": self.perangkat.to_dict() if self.perangkat else None,
        }
