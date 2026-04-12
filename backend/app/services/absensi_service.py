import json
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Absensi, AuditLog, SesiSholat, Siswa, WaktuSholat


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
