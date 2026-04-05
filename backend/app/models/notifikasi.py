from datetime import datetime
from ..extensions import db


class Notifikasi(db.Model):
    __tablename__ = 'notifikasi'

    id_notifikasi = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user', ondelete='CASCADE'), nullable=False)
    judul = db.Column(db.String(100), nullable=False)
    pesan = db.Column(db.Text, nullable=False)
    tipe = db.Column(db.String(50), nullable=False, default='umum')
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notifikasi', lazy=True, cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id_notifikasi': self.id_notifikasi,
            'id_user': self.id_user,
            'judul': self.judul,
            'pesan': self.pesan,
            'tipe': self.tipe,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat()
        }

    @staticmethod
    def get_unread_count(user_id):
        return Notifikasi.query.filter_by(id_user=user_id, is_read=False).count()

    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()
