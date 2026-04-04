import bcrypt

from . import db


ROLE_VALUES = (
    "admin",
    "kepsek",
    "wali_kelas",
    "guru_piket",
    "siswa",
    "orangtua",
)


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            f"role IN {ROLE_VALUES}",
            name="ck_users_role_valid",
        ),
    )

    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    no_telp = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    siswa_profile = db.relationship(
        "Siswa",
        back_populates="user",
        uselist=False,
    )
    kelas_wali = db.relationship(
        "Kelas",
        back_populates="wali_kelas",
        foreign_keys="Kelas.id_wali",
    )
    absensi_terverifikasi = db.relationship(
        "Absensi",
        back_populates="verifikator",
        foreign_keys="Absensi.id_verifikator",
    )

    def set_password(self, raw_password: str) -> None:
        self.password = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        if not self.password:
            return False
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            self.password.encode("utf-8"),
        )

    def to_dict(self) -> dict:
        return {
            "id_user": self.id_user,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "no_telp": self.no_telp,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"
