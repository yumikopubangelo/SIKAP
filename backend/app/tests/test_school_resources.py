import io
from datetime import date

from app.extensions import db
from app.models import JadwalPiket, Kelas, OrangTua, SuratPeringatan, Siswa, User


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def seed_admin_bundle():
    admin = User(
        username="admin_school",
        full_name="Admin School",
        email="admin.school@sikap.local",
        role="admin",
    )
    admin.set_password("admin123")

    wali = User(
        username="wali_school",
        full_name="Wali School",
        email="wali.school@sikap.local",
        role="wali_kelas",
    )
    wali.set_password("wali12345")

    guru_1 = User(
        username="guru_one",
        full_name="Guru Satu",
        email="guru.one@sikap.local",
        role="guru_piket",
    )
    guru_1.set_password("guru12345")

    guru_2 = User(
        username="guru_two",
        full_name="Guru Dua",
        email="guru.two@sikap.local",
        role="guru_piket",
    )
    guru_2.set_password("guru12345")

    parent = User(
        username="ortu_school",
        full_name="Orang Tua School",
        email="ortu.school@sikap.local",
        role="orangtua",
        no_telp="081234500001",
    )
    parent.set_password("orangtua123")

    student_user = User(
        username="siswa_school",
        full_name="Siswa School",
        email="siswa.school@sikap.local",
        role="siswa",
    )
    student_user.set_password("siswa12345")

    db.session.add_all([admin, wali, guru_1, guru_2, parent, student_user])
    db.session.commit()
    return {
        "admin": admin,
        "wali": wali,
        "guru_1": guru_1,
        "guru_2": guru_2,
        "parent": parent,
        "student_user": student_user,
    }


def test_admin_can_crud_kelas(client, app):
    with app.app_context():
        seeded = seed_admin_bundle()
        wali_id = seeded["wali"].id_user

    token = login(client, "admin_school", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/kelas",
        headers=headers,
        json={
            "nama_kelas": "XI RPL API",
            "tingkat": "XI",
            "jurusan": "RPL",
            "tahun_ajaran": "2025/2026",
            "id_wali": wali_id,
        },
    )
    assert create_response.status_code == 201
    kelas_id = create_response.get_json()["data"]["id_kelas"]

    list_response = client.get("/api/v1/kelas?search=API", headers=headers)
    assert list_response.status_code == 200
    assert list_response.get_json()["pagination"]["total_items"] >= 1

    detail_response = client.get(f"/api/v1/kelas/{kelas_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["wali_kelas"]["id_user"] == wali_id

    update_response = client.put(
        f"/api/v1/kelas/{kelas_id}",
        headers=headers,
        json={"jurusan": "RPLX"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["jurusan"] == "RPLX"

    delete_response = client.delete(f"/api/v1/kelas/{kelas_id}", headers=headers)
    assert delete_response.status_code == 200


def test_admin_can_crud_siswa_and_link_parent_relation(client, app):
    with app.app_context():
        seeded = seed_admin_bundle()
        kelas = Kelas(
            nama_kelas="X TKJ CRUD",
            tingkat="X",
            jurusan="TKJ",
            tahun_ajaran="2025/2026",
            id_wali=seeded["wali"].id_user,
        )
        db.session.add(kelas)
        db.session.commit()
        kelas_id = kelas.id_kelas
        parent_user_id = seeded["parent"].id_user
        student_user_id = seeded["student_user"].id_user

    token = login(client, "admin_school", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/siswa",
        headers=headers,
        json={
            "nisn": "5000011111",
            "nama": "Siswa CRUD",
            "jenis_kelamin": "L",
            "alamat": "Jl. Integrasi",
            "no_telp_ortu": "081234500001",
            "id_card": "CARD-SISWA-CRUD",
            "id_kelas": kelas_id,
            "parent_user_id": parent_user_id,
        },
    )
    assert create_response.status_code == 201
    siswa_id = create_response.get_json()["data"]["id_siswa"]
    assert create_response.get_json()["data"]["orangtua"]["id_user"] == parent_user_id

    update_response = client.put(
        f"/api/v1/siswa/{siswa_id}",
        headers=headers,
        json={
            "id_user": student_user_id,
            "nama": "Siswa CRUD Update",
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["user"]["id_user"] == student_user_id

    detail_response = client.get(f"/api/v1/siswa/{siswa_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["nama"] == "Siswa CRUD Update"

    delete_response = client.delete(f"/api/v1/siswa/{siswa_id}", headers=headers)
    assert delete_response.status_code == 200


def test_admin_can_import_school_csv_and_create_parent_relations(client, app):
    with app.app_context():
        seed_admin_bundle()

    token = login(client, "admin_school", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    csv_text = """nama_kelas,tingkat,jurusan,tahun_ajaran,nisn,nama,jenis_kelamin,alamat,id_card,parent_full_name,parent_email,parent_phone
XI RPL CSV,XI,RPL,2025/2026,5000020001,Budi CSV,L,Jl. CSV 1,CARD-CSV-001,Ortu Budi,ortu.budi@sikap.local,081100000001
XI RPL CSV,XI,RPL,2025/2026,5000020002,Siti CSV,P,Jl. CSV 2,CARD-CSV-002,Ortu Siti,ortu.siti@sikap.local,081100000002
"""

    response = client.post(
        "/api/v1/siswa/import-csv",
        headers=headers,
        data={"file": (io.BytesIO(csv_text.encode("utf-8")), "school.csv")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["processed_rows"] == 2
    assert body["created_classes"] == 1
    assert body["created_students"] == 2
    assert body["created_parent_users"] == 2
    assert body["linked_parent_relations"] == 2
    assert body["errors"] == []

    with app.app_context():
        assert Kelas.query.count() == 1
        assert Siswa.query.count() == 2
        assert OrangTua.query.count() == 2


def test_admin_can_manage_jadwal_piket_and_guru_only_sees_own_schedule(client, app):
    with app.app_context():
        seeded = seed_admin_bundle()
        guru_1_id = seeded["guru_1"].id_user
        guru_2_id = seeded["guru_2"].id_user

    admin_token = login(client, "admin_school", "admin123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    first_response = client.post(
        "/api/v1/jadwal-piket",
        headers=admin_headers,
        json={
            "user_id": guru_1_id,
            "hari": "senin",
            "jam_mulai": "06:30",
            "jam_selesai": "09:00",
        },
    )
    assert first_response.status_code == 201
    jadwal_id = first_response.get_json()["data"]["id_jadwal"]

    second_response = client.post(
        "/api/v1/jadwal-piket",
        headers=admin_headers,
        json={
            "user_id": guru_2_id,
            "hari": "selasa",
            "jam_mulai": "09:00",
            "jam_selesai": "11:00",
        },
    )
    assert second_response.status_code == 201

    admin_list_response = client.get("/api/v1/jadwal-piket", headers=admin_headers)
    assert admin_list_response.status_code == 200
    assert admin_list_response.get_json()["pagination"]["total_items"] == 2

    guru_token = login(client, "guru_one", "guru12345")
    guru_headers = {"Authorization": f"Bearer {guru_token}"}
    guru_list_response = client.get("/api/v1/jadwal-piket", headers=guru_headers)
    assert guru_list_response.status_code == 200
    assert guru_list_response.get_json()["pagination"]["total_items"] == 1
    assert guru_list_response.get_json()["data"][0]["user"]["id_user"] == guru_1_id

    update_response = client.put(
        f"/api/v1/jadwal-piket/{jadwal_id}",
        headers=admin_headers,
        json={"jam_selesai": "09:30"},
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["jam_selesai"] == "09:30:00"

    delete_response = client.delete(f"/api/v1/jadwal-piket/{jadwal_id}", headers=admin_headers)
    assert delete_response.status_code == 200


def test_surat_peringatan_routes_are_scoped_and_orangtua_dashboard_uses_relation(client, app):
    with app.app_context():
        seeded = seed_admin_bundle()
        kelas = Kelas(
            nama_kelas="XI RPL SPROUTE",
            tingkat="XI",
            jurusan="RPL",
            tahun_ajaran="2025/2026",
            id_wali=seeded["wali"].id_user,
        )
        db.session.add(kelas)
        db.session.flush()

        siswa = Siswa(
            id_user=seeded["student_user"].id_user,
            nisn="5000030001",
            nama="Siswa Surat",
            id_card="CARD-SP-ROUTE",
            id_kelas=kelas.id_kelas,
            no_telp_ortu="089999999999",
        )
        db.session.add(siswa)
        db.session.flush()

        db.session.add(
            OrangTua(
                id_user=seeded["parent"].id_user,
                id_siswa=siswa.id_siswa,
            )
        )
        sp = SuratPeringatan(
            id_siswa=siswa.id_siswa,
            sp_ke=1,
            tanggal=date.today(),
            jenis="SP1",
            status_kirim="terkirim",
            id_pengirim=seeded["admin"].id_user,
            alasan="Pengujian route SP",
        )
        db.session.add(sp)
        db.session.commit()
        sp_id = sp.id_sp
        siswa_id = siswa.id_siswa

    admin_token = login(client, "admin_school", "admin123")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    admin_list_response = client.get(
        f"/api/v1/surat-peringatan?siswa_id={siswa_id}",
        headers=admin_headers,
    )
    assert admin_list_response.status_code == 200
    assert admin_list_response.get_json()["pagination"]["total_items"] == 1

    parent_token = login(client, "ortu_school", "orangtua123")
    parent_headers = {"Authorization": f"Bearer {parent_token}"}
    parent_list_response = client.get("/api/v1/surat-peringatan", headers=parent_headers)
    assert parent_list_response.status_code == 200
    assert parent_list_response.get_json()["pagination"]["total_items"] == 1

    detail_response = client.get(f"/api/v1/surat-peringatan/{sp_id}", headers=parent_headers)
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["jenis"] == "SP1"

    dashboard_response = client.get("/api/v1/dashboard", headers=parent_headers)
    assert dashboard_response.status_code == 200
    assert dashboard_response.get_json()["data"]["student"]["nisn"] == "5000030001"

    with app.app_context():
        assert JadwalPiket.query.count() >= 0
