import json

from . import db


AUDIT_ACTION_VALUES = ("INSERT", "UPDATE", "DELETE")


class AuditLog(db.Model):
    __tablename__ = "audit_log"
    __table_args__ = (
        db.CheckConstraint(
            f"aksi IN {AUDIT_ACTION_VALUES}",
            name="ck_audit_log_aksi_valid",
        ),
    )

    id_log = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="SET NULL"),
        nullable=True,
    )
    aksi = db.Column(db.String(10), nullable=False)
    tabel = db.Column(db.String(50), nullable=False)
    record_pk = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)

    user = db.relationship("User", back_populates="audit_logs")

    def parse_json_field(self, field_name: str):
        raw_value = getattr(self, field_name)
        if not raw_value:
            return None
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            return None

    def __repr__(self) -> str:
        return f"<AuditLog {self.aksi} {self.tabel}:{self.record_pk}>"
