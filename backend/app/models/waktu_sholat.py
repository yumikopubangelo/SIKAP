from . import db


SESI_STATUS_VALUES = ("aktif", "selesai")


class WaktuSholat(db.Model):
    __tablename__ = "waktu_sholat"

    id_waktu = db.Column(db.Integer, primary_key=True)
    nama_sholat = db.Column(db.String(20), nullable=False, unique=True)
    waktu_adzan = db.Column(db.Time, nullable=False)
    waktu_iqamah = db.Column(db.Time, nullable=False)
    waktu_selesai = db.Column(db.Time, nullable=False)

    sesi = db.relationship("SesiSholat", back_populates="waktu_sholat")

    def __repr__(self) -> str:
        return f"<WaktuSholat {self.nama_sholat}>"

    def to_dict(self) -> dict:
        return {
            "id_waktu": self.id_waktu,
            "nama_sholat": self.nama_sholat,
            "waktu_adzan": self.waktu_adzan.isoformat() if self.waktu_adzan else None,
            "waktu_iqamah": self.waktu_iqamah.isoformat() if self.waktu_iqamah else None,
            "waktu_selesai": self.waktu_selesai.isoformat() if self.waktu_selesai else None,
        }


class SesiSholat(db.Model):
    __tablename__ = "sesi_sholat"
    __table_args__ = (
        db.CheckConstraint(
            f"status IN {SESI_STATUS_VALUES}",
            name="ck_sesi_sholat_status_valid",
        ),
        db.UniqueConstraint(
            "id_waktu",
            "tanggal",
            name="uq_sesi_sholat_id_waktu_tanggal",
        ),
    )

    id_sesi = db.Column(db.Integer, primary_key=True)
    id_waktu = db.Column(
        db.Integer,
        db.ForeignKey("waktu_sholat.id_waktu", ondelete="CASCADE"),
        nullable=False,
    )
    tanggal = db.Column(db.Date, nullable=False)
    status = db.Column(
        db.String(20),
        nullable=False,
        server_default="aktif",
    )

    waktu_sholat = db.relationship("WaktuSholat", back_populates="sesi")
    absensi = db.relationship("Absensi", back_populates="sesi")

    def __repr__(self) -> str:
        return f"<SesiSholat {self.id_sesi}>"

    def to_dict(self) -> dict:
        return {
            "id_sesi": self.id_sesi,
            "id_waktu": self.id_waktu,
            "tanggal": self.tanggal.isoformat() if self.tanggal else None,
            "status": self.status,
            "waktu_sholat": self.waktu_sholat.to_dict() if self.waktu_sholat else None,
        }
