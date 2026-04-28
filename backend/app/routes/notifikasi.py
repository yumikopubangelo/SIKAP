from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.notifikasi import Notifikasi
from ..utils.response import success_response, error_response


notifikasi_bp = Blueprint("notifikasi", __name__, url_prefix="/api/v1/notifikasi")


@notifikasi_bp.post('/send')
@jwt_required()
def send_notifikasi():
    try:
        data = request.get_json()

        if not data:
            return error_response("Data tidak boleh kosong", 400)

        required_fields = ['id_user', 'judul', 'pesan']
        for field in required_fields:
            if field not in data:
                return error_response(f"Field {field} harus diisi", 400)

        notifikasi = Notifikasi(
            id_user=data['id_user'],
            judul=data['judul'],
            pesan=data['pesan'],
            tipe=data.get('tipe', 'umum')
        )

        db.session.add(notifikasi)
        db.session.commit()

        return success_response(
            data=notifikasi.to_dict(),
            message="Notifikasi berhasil dikirim",
            status_code=201,
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f"Gagal mengirim notifikasi: {str(e)}", 500)


@notifikasi_bp.get('')
@jwt_required()
def get_notifikasi():
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        only_unread = request.args.get('only_unread', 'false').lower() == 'true'

        query = Notifikasi.query.filter_by(id_user=current_user_id)

        if only_unread:
            query = query.filter_by(is_read=False)

        paginated = query.order_by(Notifikasi.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        unread_count = Notifikasi.get_unread_count(current_user_id)

        return success_response(
            data={
                'notifikasi': [n.to_dict() for n in paginated.items],
                'unread_count': unread_count,
                'total': paginated.total,
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total_pages': paginated.pages
            },
            message="Berhasil mendapatkan notifikasi",
        )

    except Exception as e:
        return error_response(f"Gagal mendapatkan notifikasi: {str(e)}", 500)


@notifikasi_bp.put('/<int:id_notifikasi>/read')
@jwt_required()
def mark_as_read(id_notifikasi):
    try:
        current_user_id = get_jwt_identity()
        notifikasi = Notifikasi.query.filter_by(
            id_notifikasi=id_notifikasi, id_user=current_user_id
        ).first()

        if not notifikasi:
            return error_response("Notifikasi tidak ditemukan", 404)

        notifikasi.mark_as_read()
        db.session.commit()

        return success_response(
            data=notifikasi.to_dict(),
            message="Notifikasi berhasil ditandai sebagai dibaca",
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f"Gagal menandai notifikasi: {str(e)}", 500)


@notifikasi_bp.put('/read-all')
@jwt_required()
def mark_all_as_read():
    try:
        current_user_id = get_jwt_identity()

        Notifikasi.query.filter_by(
            id_user=current_user_id, is_read=False
        ).update({
            'is_read': True,
            'read_at': db.func.now()
        })

        db.session.commit()

        return success_response(
            data={
                'marked_count': Notifikasi.get_unread_count(current_user_id)
            },
            message="Semua notifikasi berhasil ditandai sebagai dibaca",
        )

    except Exception as e:
        db.session.rollback()
        return error_response(f"Gagal menandai semua notifikasi: {str(e)}", 500)
