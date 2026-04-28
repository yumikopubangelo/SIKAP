from ..extensions import db
from ..models import Notifikasi


def create_notifikasi(
    *,
    user_id: int,
    judul: str,
    pesan: str,
    tipe: str = "umum",
    auto_commit: bool = False,
) -> Notifikasi:
    notifikasi = Notifikasi(
        id_user=user_id,
        judul=judul,
        pesan=pesan,
        tipe=tipe,
        is_read=False,
    )
    db.session.add(notifikasi)
    db.session.flush()

    if auto_commit:
        db.session.commit()

    return notifikasi
