from . import db


PERANGKAT_STATUS_VALUES = ("online", "offline")


class Perangkat(db.Model):
    __tablename__ = "perangkat"
    __table_args__ = (
        db.CheckConstraint(
            f"status IN {PERANGKAT_STATUS_VALUES}",
            name="ck_perangkat_status_valid",
        ),
    )

    device_id = db.Column(db.String(50), primary_key=True)
    nama_device = db.Column(db.String(100), nullable=False)
    lokasi = db.Column(db.String(100))
    api_key = db.Column(db.String(100), nullable=False, unique=True)
    public_key = db.Column(db.Text, nullable=True)  # PEM encoded public key for signature verification
    last_nonce = db.Column(db.BigInteger, nullable=True)  # stores last used timestamp to prevent replay
    status = db.Column(
        db.String(20),
        nullable=False,
        server_default="offline",
    )
    last_ping = db.Column(db.DateTime)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    absensi = db.relationship("Absensi", back_populates="perangkat")

    def __repr__(self) -> str:
        return f"<Perangkat {self.device_id}>"

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "nama_device": self.nama_device,
            "lokasi": self.lokasi,
            "status": self.status,
            "last_ping": self.last_ping.isoformat() if self.last_ping else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "public_key": self.public_key,
            "last_nonce": self.last_nonce,
        }
