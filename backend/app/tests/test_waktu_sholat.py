from datetime import time

from app.extensions import db
from app.models import User, WaktuSholat


def seed_users_and_waktu():
    admin = User(
        username="admin_waktu",
        full_name="Admin Waktu",
        email="admin.waktu@sikap.local",
        role="admin",
    )
    admin.set_password("admin123")

    guru = User(
        username="guru_waktu",
        full_name="Guru Waktu",
        email="guru.waktu@sikap.local",
        role="guru_piket",
    )
    guru.set_password("guru12345")

    waktu = WaktuSholat(
        nama_sholat="Dzuhur",
        waktu_adzan=time(12, 0, 0),
        waktu_iqamah=time(12, 10, 0),
        waktu_selesai=time(12, 30, 0),
    )

    db.session.add_all([admin, guru, waktu])
    db.session.commit()
    return waktu


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_authenticated_user_can_list_waktu_sholat(client, app):
    with app.app_context():
        seed_users_and_waktu()

    token = login(client, "guru_waktu", "guru12345")
    response = client.get(
        "/api/v1/waktu-sholat",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert len(body) == 1
    assert body[0]["nama_sholat"] == "Dzuhur"


def test_admin_can_update_waktu_sholat(client, app):
    with app.app_context():
        waktu = seed_users_and_waktu()
        waktu_id = waktu.id_waktu

    token = login(client, "admin_waktu", "admin123")
    response = client.put(
        f"/api/v1/waktu-sholat/{waktu_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "waktu_adzan": "12:05",
            "waktu_iqamah": "12:15",
            "waktu_selesai": "12:35",
        },
    )

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["waktu_adzan"] == "12:05:00"
    assert body["waktu_iqamah"] == "12:15:00"
    assert body["waktu_selesai"] == "12:35:00"


def test_non_admin_cannot_update_waktu_sholat(client, app):
    with app.app_context():
        waktu = seed_users_and_waktu()
        waktu_id = waktu.id_waktu

    token = login(client, "guru_waktu", "guru12345")
    response = client.put(
        f"/api/v1/waktu-sholat/{waktu_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "waktu_adzan": "12:05",
            "waktu_iqamah": "12:15",
            "waktu_selesai": "12:35",
        },
    )

    assert response.status_code == 403
