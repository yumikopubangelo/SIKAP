import json
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Absensi, AuditLog, Perangkat, SesiSholat, Siswa, WaktuSholat


class AbsensiServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    try:
        return value.isoformat()
    except AttributeError:
        return str(value)


def _serialize_audit_log(audit_log: AuditLog) -> dict:
    return {
        "id_log": audit_log.id_log,
        "aksi": audit_log.aksi,
        "tabel": audit_log.tabel,
        "record_pk": audit_log.record_pk,
        "timestamp": audit_log.timestamp.isoformat() if audit_log.timestamp else None,
        "old_value": audit_log.parse_json_field("old_value"),
        "new_value": audit_log.parse_json_field("new_value"),
    }


def serialize_absensi(absensi: Absensi, include_audit: bool = False) -> dict:
    waktu_sholat = absensi.sesi.waktu_sholat if absensi.sesi else None
    data = {
        "id_absensi": absensi.id_absensi,
        "tanggal": absensi.sesi.tanggal.isoformat() if absensi.sesi and absensi.sesi.tanggal else None,
        "timestamp": absensi.timestamp.isoformat() if absensi.timestamp else None,
        "waktu_sholat": waktu_sholat.nama_sholat if waktu_sholat else None,
        "status": absensi.status,
        "keterangan": absensi.keterangan,
        "device_id": absensi.device_id,
        "verified_at": absensi.verified_at.isoformat() if absensi.verified_at else None,
        "verified_by_guru_piket": bool(
            absensi.id_verifikator and absensi.verifikator and absensi.verifikator.role == "guru_piket"
        ),
        "verifikator": {
            "id_user": absensi.verifikator.id_user,
            "full_name": absensi.verifikator.full_name,
            "role": absensi.verifikator.role,
        } if absensi.verifikator else None,
        "siswa": {
            "id_siswa": absensi.siswa.id_siswa,
            "nisn": absensi.siswa.nisn,
            "nama": absensi.siswa.nama,
            "kelas": absensi.siswa.kelas.nama_kelas if absensi.siswa.kelas else None,
        } if absensi.siswa else None,
    }
    if include_audit:
        audit_logs = (
            AuditLog.query.filter_by(tabel="absensi", record_pk=str(absensi.id_absensi))
            .order_by(AuditLog.timestamp.desc(), AuditLog.id_log.desc())
            .all()
        )
        data["audit_log"] = [_serialize_audit_log(item) for item in audit_logs]
    return data


def _serialize_absensi_list_item(absensi: Absensi) -> dict:
    kelas = absensi.siswa.kelas if absensi.siswa else None
    waktu_sholat = absensi.sesi.waktu_sholat if absensi.sesi else None
    return {
        "id_absensi": absensi.id_absensi,
        "tanggal": absensi.sesi.tanggal.isoformat() if absensi.sesi and absensi.sesi.tanggal else None,
        "waktu_sholat": waktu_sholat.nama_sholat if waktu_sholat else None,
        "timestamp": absensi.timestamp.isoformat() if absensi.timestamp else None,
        "status": absensi.status,
        "device_id": absensi.device_id,
        "keterangan": absensi.keterangan,
        "siswa": {
            "id_siswa": absensi.siswa.id_siswa,
            "nisn": absensi.siswa.nisn,
            "nama": absensi.siswa.nama,
            "kelas": kelas.nama_kelas if kelas else None,
        }
        if absensi.siswa
        else None,
    }


def _get_siswa_or_raise(siswa_id: int) -> Siswa:
    siswa = (
        Siswa.query.options(
            joinedload(Siswa.kelas),
            joinedload(Siswa.user),
        )
        .filter_by(id_siswa=siswa_id)
        .first()
    )
    if siswa is None:
        raise AbsensiServiceError("Data siswa tidak ditemukan.", 404)
    return siswa


def _get_waktu_sholat_or_raise(nama_sholat: str) -> WaktuSholat:
    waktu_sholat = (
        WaktuSholat.query.filter(
            func.lower(WaktuSholat.nama_sholat) == nama_sholat.lower()
        ).first()
    )
    if waktu_sholat is None:
        raise AbsensiServiceError("Waktu sholat tidak ditemukan.", 404)
    return waktu_sholat


def _get_siswa_by_card_or_raise(uid_card: str) -> Siswa:
    siswa = (
        Siswa.query.options(
            joinedload(Siswa.kelas),
            joinedload(Siswa.user),
        )
        .filter_by(id_card=uid_card)
        .first()
    )
    if siswa is None:
        raise AbsensiServiceError("Kartu tidak terdaftar.", 404)
    return siswa


def _get_perangkat_or_raise(device_id: str, api_key: str | None) -> Perangkat:
    if not api_key:
        raise AbsensiServiceError("API key perangkat wajib disertakan.", 401)

    perangkat = Perangkat.query.filter_by(device_id=device_id, api_key=api_key).first()
    if perangkat is None:
        raise AbsensiServiceError("Perangkat tidak valid atau API key salah.", 401)
    return perangkat


def _get_or_create_sesi(tanggal, waktu_sholat: WaktuSholat) -> SesiSholat:
    sesi = SesiSholat.query.filter_by(
        id_waktu=waktu_sholat.id_waktu,
        tanggal=tanggal,
    ).first()
    if sesi is not None:
        return sesi

    sesi = SesiSholat(
        id_waktu=waktu_sholat.id_waktu,
        tanggal=tanggal,
        status="aktif",
    )
    db.session.add(sesi)
    db.session.flush()
    return sesi


def _get_or_create_active_sesi(tanggal, waktu_sholat: WaktuSholat) -> SesiSholat:
    sesi = SesiSholat.query.filter_by(
        id_waktu=waktu_sholat.id_waktu,
        tanggal=tanggal,
    ).first()
    if sesi is None:
        sesi = SesiSholat(
            id_waktu=waktu_sholat.id_waktu,
            tanggal=tanggal,
            status="aktif",
        )
        db.session.add(sesi)
        db.session.flush()
        return sesi

    if sesi.status != "aktif":
        raise AbsensiServiceError("Sesi sholat untuk waktu ini sudah ditutup.", 409)

    return sesi


def _build_manual_timestamp(payload: dict, waktu_sholat: WaktuSholat) -> datetime:
    if payload.get("timestamp") is not None:
        return payload["timestamp"].replace(tzinfo=None)

    status = payload["status"]
    if status == "tepat_waktu":
        event_time = waktu_sholat.waktu_adzan
    elif status == "terlambat":
        event_time = waktu_sholat.waktu_iqamah
    else:
        event_time = waktu_sholat.waktu_selesai
    return datetime.combine(payload["tanggal"], event_time)


def _normalize_event_timestamp(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now()
    return value.replace(tzinfo=None) if value.tzinfo is not None else value


def _resolve_active_waktu_sholat_or_raise(event_timestamp: datetime) -> WaktuSholat:
    event_time = event_timestamp.time()
    waktu_sholat = (
        WaktuSholat.query.filter(
            WaktuSholat.waktu_adzan <= event_time,
            WaktuSholat.waktu_selesai >= event_time,
        )
        .order_by(WaktuSholat.waktu_adzan.asc())
        .first()
    )
    if waktu_sholat is None:
        raise AbsensiServiceError("Tidak ada sesi sholat aktif untuk timestamp ini.", 409)
    return waktu_sholat


def _resolve_rfid_status(event_timestamp: datetime, waktu_sholat: WaktuSholat) -> str:
    if event_timestamp.time() <= waktu_sholat.waktu_iqamah:
        return "tepat_waktu"
    return "terlambat"


def _snapshot_absensi(absensi: Absensi) -> dict:
    return {
        "id_absensi": absensi.id_absensi,
        "id_siswa": absensi.id_siswa,
        "id_sesi": absensi.id_sesi,
        "timestamp": absensi.timestamp.isoformat() if absensi.timestamp else None,
        "status": absensi.status,
        "device_id": absensi.device_id,
        "id_verifikator": absensi.id_verifikator,
        "verified_at": absensi.verified_at.isoformat() if absensi.verified_at else None,
        "keterangan": absensi.keterangan,
    }


def _create_audit_log(
    *,
    actor_id: int | None,
    action: str,
    record_pk: str,
    old_value: dict | None,
    new_value: dict | None,
) -> AuditLog:
    audit_log = AuditLog(
        id_user=actor_id,
        aksi=action,
        tabel="absensi",
        record_pk=record_pk,
        old_value=json.dumps(old_value, ensure_ascii=False, default=_json_default) if old_value is not None else None,
        new_value=json.dumps(new_value, ensure_ascii=False, default=_json_default) if new_value is not None else None,
    )
    db.session.add(audit_log)
    db.session.flush()
    return audit_log


def _base_absensi_query():
    return Absensi.query.options(
        joinedload(Absensi.siswa).joinedload(Siswa.kelas),
        joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
        joinedload(Absensi.perangkat),
        joinedload(Absensi.verifikator),
    )


def create_rfid_absensi(payload: dict, api_key: str | None) -> tuple[dict, int]:
    perangkat = _get_perangkat_or_raise(payload["device_id"], api_key)
    siswa = _get_siswa_by_card_or_raise(payload["uid_card"])
    event_timestamp = _normalize_event_timestamp(payload.get("timestamp"))
    waktu_sholat = _resolve_active_waktu_sholat_or_raise(event_timestamp)
    sesi = _get_or_create_active_sesi(event_timestamp.date(), waktu_sholat)

    existing = Absensi.query.filter_by(
        id_siswa=siswa.id_siswa,
        id_sesi=sesi.id_sesi,
    ).first()
    if existing is not None:
        raise AbsensiServiceError("Siswa sudah tercatat hadir untuk sesi ini.", 409)

    absensi = Absensi(
        id_siswa=siswa.id_siswa,
        id_sesi=sesi.id_sesi,
        timestamp=event_timestamp,
        status=_resolve_rfid_status(event_timestamp, waktu_sholat),
        device_id=perangkat.device_id,
        id_verifikator=None,
        verified_at=None,
        keterangan=None,
    )
    db.session.add(absensi)
    db.session.flush()

    perangkat.status = "online"
    perangkat.last_ping = datetime.utcnow()

    audit_log = _create_audit_log(
        actor_id=None,
        action="INSERT",
        record_pk=str(absensi.id_absensi),
        old_value=None,
        new_value=_snapshot_absensi(absensi),
    )
    db.session.commit()

    persisted = (
        _base_absensi_query()
        .filter_by(id_absensi=absensi.id_absensi)
        .first()
    )
    data = serialize_absensi(persisted)
    data["color"] = "green" if persisted.status == "tepat_waktu" else "yellow"
    return data, audit_log.id_log


def create_manual_absensi(payload: dict, current_user) -> tuple[dict, int]:
    siswa = _get_siswa_or_raise(payload["siswa_id"])
    waktu_sholat = _get_waktu_sholat_or_raise(payload["waktu_sholat"])
    sesi = _get_or_create_sesi(payload["tanggal"], waktu_sholat)

    existing = Absensi.query.filter_by(
        id_siswa=siswa.id_siswa,
        id_sesi=sesi.id_sesi,
    ).first()
    if existing is not None:
        raise AbsensiServiceError("Siswa sudah memiliki absensi pada sesi ini.", 409)

    absensi = Absensi(
        id_siswa=siswa.id_siswa,
        id_sesi=sesi.id_sesi,
        timestamp=_build_manual_timestamp(payload, waktu_sholat),
        status=payload["status"],
        device_id=None,
        id_verifikator=current_user.id_user,
        verified_at=datetime.utcnow(),
        keterangan=payload.get("keterangan"),
    )
    db.session.add(absensi)
    db.session.flush()

    audit_log = _create_audit_log(
        actor_id=current_user.id_user,
        action="INSERT",
        record_pk=str(absensi.id_absensi),
        old_value=None,
        new_value=_snapshot_absensi(absensi),
    )
    db.session.commit()

    persisted = (
        Absensi.query.options(
            joinedload(Absensi.siswa).joinedload(Siswa.kelas),
            joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
            joinedload(Absensi.verifikator),
        )
        .filter_by(id_absensi=absensi.id_absensi)
        .first()
    )
    return serialize_absensi(persisted, include_audit=True), audit_log.id_log


def update_absensi(absensi_id: int, payload: dict, current_user) -> tuple[dict, int]:
    absensi = (
        Absensi.query.options(
            joinedload(Absensi.siswa).joinedload(Siswa.kelas),
            joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
            joinedload(Absensi.verifikator),
        )
        .filter_by(id_absensi=absensi_id)
        .first()
    )
    if absensi is None:
        raise AbsensiServiceError("Data absensi tidak ditemukan.", 404)

    old_snapshot = _snapshot_absensi(absensi)
    absensi.status = payload["status"]
    absensi.keterangan = payload["keterangan"]
    absensi.id_verifikator = current_user.id_user
    absensi.verified_at = datetime.utcnow()
    db.session.flush()

    audit_log = _create_audit_log(
        actor_id=current_user.id_user,
        action="UPDATE",
        record_pk=str(absensi.id_absensi),
        old_value=old_snapshot,
        new_value=_snapshot_absensi(absensi),
    )
    db.session.commit()

    refreshed = (
        Absensi.query.options(
            joinedload(Absensi.siswa).joinedload(Siswa.kelas),
            joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
            joinedload(Absensi.verifikator),
        )
        .filter_by(id_absensi=absensi.id_absensi)
        .first()
    )
    return serialize_absensi(refreshed, include_audit=True), audit_log.id_log


def _empty_scoped_absensi_query():
    return _base_absensi_query().join(Absensi.siswa).join(Absensi.sesi).filter(Absensi.id_absensi == -1)


def _scoped_absensi_query(current_user):
    query = _base_absensi_query().join(Absensi.siswa).join(Absensi.sesi)
    role = current_user.role

    if role in ("admin", "kepsek", "guru_piket"):
        return query

    if role == "wali_kelas":
        kelas_ids = [kelas.id_kelas for kelas in current_user.kelas_wali]
        if not kelas_ids:
            return _empty_scoped_absensi_query()
        return query.filter(Siswa.id_kelas.in_(kelas_ids))

    if role == "siswa":
        if current_user.siswa_profile is None:
            return _empty_scoped_absensi_query()
        return query.filter(Absensi.id_siswa == current_user.siswa_profile.id_siswa)

    if role == "orangtua":
        student_id = None
        orangtua_profile = getattr(current_user, "orangtua_profile", None)
        if orangtua_profile is not None:
            student_id = orangtua_profile.id_siswa
        elif current_user.no_telp:
            student_id = (
                Siswa.query.with_entities(Siswa.id_siswa)
                .filter_by(no_telp_ortu=current_user.no_telp)
                .scalar()
            )

        if student_id is None:
            return _empty_scoped_absensi_query()
        return query.filter(Absensi.id_siswa == student_id)

    return _empty_scoped_absensi_query()


def list_absensi(params: dict, current_user) -> tuple[list[dict], dict]:
    query = _scoped_absensi_query(current_user)

    if params.get("siswa_id") is not None:
        query = query.filter(Absensi.id_siswa == params["siswa_id"])

    if params.get("kelas_id") is not None:
        query = query.filter(Siswa.id_kelas == params["kelas_id"])

    if params.get("start_date") is not None:
        query = query.filter(SesiSholat.tanggal >= params["start_date"])

    if params.get("end_date") is not None:
        query = query.filter(SesiSholat.tanggal <= params["end_date"])

    if params.get("status") is not None:
        query = query.filter(Absensi.status == params["status"])

    if params.get("waktu_sholat") is not None:
        query = query.join(SesiSholat.waktu_sholat).filter(
            func.lower(WaktuSholat.nama_sholat) == params["waktu_sholat"]
        )

    total_items = query.count()
    page = params["page"]
    limit = params["limit"]
    total_pages = max(1, (total_items + limit - 1) // limit)

    order_by = Absensi.timestamp.asc() if params["sort"] == "asc" else Absensi.timestamp.desc()
    rows = (
        query.order_by(order_by, Absensi.id_absensi.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return (
        [_serialize_absensi_list_item(item) for item in rows],
        {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    )
