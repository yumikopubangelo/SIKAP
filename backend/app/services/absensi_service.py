from datetime import datetime

from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Absensi, Perangkat, SesiSholat, Siswa, WaktuSholat


def _normalize_timestamp(timestamp: datetime | None) -> datetime:
    if timestamp is None:
        return datetime.now()
    if timestamp.tzinfo is not None:
        return timestamp.astimezone().replace(tzinfo=None)
    return timestamp


def get_device_by_credentials(device_id: str, api_key: str | None):
    if not api_key:
        return None
    return Perangkat.query.filter_by(device_id=device_id, api_key=api_key).first()


def get_student_by_card(uid_card: str):
    return Siswa.query.filter_by(id_card=uid_card).first()


def find_matching_waktu_sholat(tap_timestamp: datetime):
    tap_time = tap_timestamp.time()
    return (
        WaktuSholat.query.filter(WaktuSholat.waktu_adzan <= tap_time)
        .filter(WaktuSholat.waktu_selesai >= tap_time)
        .order_by(WaktuSholat.waktu_adzan.asc())
        .first()
    )


def get_or_create_active_session(waktu_sholat: WaktuSholat, tap_timestamp: datetime):
    session = SesiSholat.query.filter_by(
        id_waktu=waktu_sholat.id_waktu,
        tanggal=tap_timestamp.date(),
    ).first()
    if session is None:
        session = SesiSholat(
            id_waktu=waktu_sholat.id_waktu,
            tanggal=tap_timestamp.date(),
            status="aktif",
        )
        db.session.add(session)
        db.session.flush()
    return session


def determine_absensi_status(tap_timestamp: datetime, waktu_sholat: WaktuSholat):
    tap_time = tap_timestamp.time()
    if tap_time < waktu_sholat.waktu_adzan:
        raise ValueError("Tap terjadi sebelum waktu adzan dimulai.")
    if tap_time < waktu_sholat.waktu_iqamah:
        return "tepat_waktu"
    if tap_time <= waktu_sholat.waktu_selesai:
        return "terlambat"
    raise ValueError("Tap terjadi di luar rentang sesi sholat aktif.")


def create_rfid_absensi(uid_card: str, device_id: str, api_key: str, timestamp: datetime | None):
    tap_timestamp = _normalize_timestamp(timestamp)
    device = get_device_by_credentials(device_id, api_key)
    if device is None:
        raise PermissionError("Perangkat atau API key tidak valid.")

    student = get_student_by_card(uid_card)
    if student is None:
        raise LookupError("Kartu tidak terdaftar.")

    waktu_sholat = find_matching_waktu_sholat(tap_timestamp)
    if waktu_sholat is None:
        raise LookupError("Tidak ada sesi sholat aktif untuk waktu tap tersebut.")

    session = get_or_create_active_session(waktu_sholat, tap_timestamp)
    if session.status != "aktif":
        raise ValueError("Sesi sholat sudah ditutup.")

    existing_absensi = Absensi.query.filter_by(
        id_siswa=student.id_siswa,
        id_sesi=session.id_sesi,
    ).first()
    if existing_absensi:
        raise ValueError("Siswa sudah tercatat hadir untuk sesi ini.")

    status = determine_absensi_status(tap_timestamp, waktu_sholat)
    device.status = "online"
    device.last_ping = tap_timestamp

    absensi = Absensi(
        id_siswa=student.id_siswa,
        id_sesi=session.id_sesi,
        timestamp=tap_timestamp,
        status=status,
        device_id=device.device_id,
    )
    db.session.add(absensi)
    db.session.commit()

    return absensi


def build_absensi_query(filters: dict):
    query = (
        Absensi.query.options(
            joinedload(Absensi.siswa).joinedload(Siswa.kelas),
            joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
            joinedload(Absensi.perangkat),
        )
    )

    if filters.get("siswa_id"):
        query = query.filter(Absensi.id_siswa == filters["siswa_id"])
    if filters.get("kelas_id"):
        query = query.join(Absensi.siswa).filter(Siswa.id_kelas == filters["kelas_id"])
    if filters.get("status"):
        query = query.filter(Absensi.status == filters["status"])
    if filters.get("waktu_sholat"):
        query = (
            query.join(Absensi.sesi)
            .join(SesiSholat.waktu_sholat)
            .filter(WaktuSholat.nama_sholat == filters["waktu_sholat"])
        )
    if filters.get("start_date"):
        query = query.join(Absensi.sesi).filter(SesiSholat.tanggal >= filters["start_date"])
    if filters.get("end_date"):
        query = query.join(Absensi.sesi).filter(SesiSholat.tanggal <= filters["end_date"])

    order_column = Absensi.timestamp.asc() if filters["sort"] == "asc" else Absensi.timestamp.desc()
    return query.order_by(order_column)


def list_absensi(filters: dict):
    query = build_absensi_query(filters)
    page = filters["page"]
    limit = filters["limit"]
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return {
        "items": [item.to_dict() for item in pagination.items],
        "pagination": {
            "page": pagination.page,
            "limit": limit,
            "total_items": pagination.total,
            "total_pages": pagination.pages,
        },
    }


def get_absensi_detail(absensi_id: int):
    return (
        Absensi.query.options(
            joinedload(Absensi.siswa).joinedload(Siswa.kelas),
            joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
            joinedload(Absensi.perangkat),
        )
        .filter_by(id_absensi=absensi_id)
        .first()
    )
