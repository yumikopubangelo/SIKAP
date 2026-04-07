from . import db

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_token"

    id_token = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(
        db.Integer,
        db.ForeignKey("users.id_user", ondelete="CASCADE"),
        nullable=False,
    )
    token = db.Column(db.String(255), nullable=False, unique=True)
    expired_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, server_default=db.text("FALSE"))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )

    user = db.relationship("User", backref=db.backref("reset_tokens", lazy="dynamic"))

    def __repr__(self) -> str:
        return f"<PasswordResetToken id_token={self.id_token}>"
