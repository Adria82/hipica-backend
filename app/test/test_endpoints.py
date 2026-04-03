"""
Tests de integración para los endpoints de la API.

Cobertura:
- Health checks (/ y /health/db)
- CRUD de stables, clients, horses, users, lessons
- Auth: login y refresh

Estos tests usan SQLite en memoria y sobreescriben la dependencia de sesión
para no requerir PostgreSQL.

Cada test que accede a endpoints protegidos obtiene un JWT mediante login
y lo envía como cabecera Authorization: Bearer <token>.
"""

import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

# Forzamos uso de SQLite en memoria durante los tests.
os.environ["DATABASE_URL"] = "sqlite://"

from app.main import app
from app.db.session import get_session
from app.models.box import Box
from app.models.horse import Horse
from app.models.stable import Stable
from app.models.user import User
from app.security import hash_password


@pytest.fixture()
def client():
    """
    Crea un TestClient con una base de datos SQLite en memoria.

    Devuelve:
        tuple[TestClient, Engine]: cliente de pruebas y engine SQLModel.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        """Sobrescribe get_session para usar el engine de test."""
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client, engine

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Helpers de creación de entidades
# ---------------------------------------------------------------------------

def create_stable(session, name="Stable 1"):
    """Crea una hípica de prueba y la persiste en la base de datos."""
    stable = Stable(name=name, location="Location", is_active=True)
    session.add(stable)
    session.commit()
    session.refresh(stable)
    return stable


def create_user(
    session,
    stable_id,
    email="user@example.com",
    password="secret",
    role="monitor",
):
    """Crea un usuario de prueba con contraseña hasheada."""
    user = User(
        name="User",
        email=email,
        hashed_password=hash_password(password),
        role=role,
        stable_id=stable_id,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_client_user(session, stable_id, name="Client 1", email="client@example.com"):
    """Crea un usuario con role=client y lo asocia a una hípica."""
    u = User(
        name=name,
        email=email,
        phone="123",
        role="client",
        stable_id=stable_id,
        is_active=True,
        hashed_password=hash_password("changeme"),
    )
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def create_horse_entity(session, stable_id, name="Horse 1"):
    """Crea un caballo de prueba asociado a una hípica."""
    horse = Horse(
        name=name,
        stable_id=stable_id,
        is_active=True,
    )
    session.add(horse)
    session.commit()
    session.refresh(horse)
    return horse


def login(test_client, email, password="secret"):
    """Realiza login y devuelve el access_token."""
    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


def auth_headers(token):
    """Devuelve el dict de cabeceras con el token Bearer."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_root_and_health(client):
    """Verifica los endpoints raíz y health check de base de datos."""
    test_client, _ = client

    response = test_client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"

    response = test_client.get("/health/db")
    assert response.status_code == 200
    payload = response.json()
    assert payload["db"] == "ok"


def test_i18n_headers(client):
    """Verifica traducciones básicas por Accept-Language."""
    test_client, engine = client

    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "API Hípica en marxa"

    response = test_client.get("/", headers={"Accept-Language": "en"})
    assert response.status_code == 200
    assert response.json()["message"] == "Hipica API is running"

    # Verificar 404 en stable inexistente (requiere app_admin)
    with Session(engine) as session:
        stable = create_stable(session, name="I18nStable")
        admin = create_user(
            session,
            stable.id,
            email="admin_i18n@example.com",
            password="secret",
            role="app_admin",
        )

    token = login(test_client, admin.email)
    response = test_client.get(
        "/api/v1/stables/999",
        headers={**auth_headers(token), "Accept-Language": "ca"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Hípica no trobada"


def test_stable_crud(client):
    """Valida el CRUD completo de stables (solo app_admin)."""
    test_client, engine = client

    # Necesitamos un app_admin — creamos la stable directamente en DB
    # para que el admin pueda existir primero.
    with Session(engine) as session:
        stable = create_stable(session, name="Bootstrap")
        admin = create_user(
            session,
            stable.id,
            email="admin_stable@example.com",
            password="secret",
            role="app_admin",
        )

    token = login(test_client, admin.email)
    hdrs = auth_headers(token)

    payload = {"name": "Hipica Norte", "location": "Barcelona", "is_active": True}
    response = test_client.post("/api/v1/stables/", json=payload, headers=hdrs)
    assert response.status_code == 201
    stable_data = response.json()
    assert stable_data["name"] == payload["name"]

    response = test_client.get("/api/v1/stables/", headers=hdrs)
    assert response.status_code == 200
    assert len(response.json()) >= 1

    response = test_client.get(f"/api/v1/stables/{stable_data['id']}", headers=hdrs)
    assert response.status_code == 200

    response = test_client.patch(
        f"/api/v1/stables/{stable_data['id']}",
        json={"location": "Girona"},
        headers=hdrs,
    )
    assert response.status_code == 200
    assert response.json()["location"] == "Girona"

    response = test_client.delete(f"/api/v1/stables/{stable_data['id']}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_list_users_by_role(client):
    """Valida el filtro ?role= en GET /api/v1/users/."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_role@example.com",
            password="secret",
            role="stable_admin",
        )
        admin_email = admin.email
        create_client_user(session, stable.id, name="Alumno 1", email="alumno1@example.com")
        create_client_user(session, stable.id, name="Alumno 2", email="alumno2@example.com")
        create_user(session, stable.id, email="mon@example.com", role="monitor")

    token = login(test_client, admin_email)
    hdrs = auth_headers(token)

    # Sin filtro: devuelve todos los usuarios de la cuadra
    response = test_client.get("/api/v1/users/", headers=hdrs)
    assert response.status_code == 200
    all_users = response.json()
    assert len(all_users) >= 4

    # Con ?role=client: solo los alumnos
    response = test_client.get("/api/v1/users/?role=client", headers=hdrs)
    assert response.status_code == 200
    clients_only = response.json()
    assert len(clients_only) == 2
    assert all(u["role"] == "client" for u in clients_only)

    # Con ?role=monitor
    response = test_client.get("/api/v1/users/?role=monitor", headers=hdrs)
    assert response.status_code == 200
    monitors = response.json()
    assert len(monitors) == 1
    assert monitors[0]["role"] == "monitor"


def test_horse_crud(client):
    """Valida el CRUD completo de horses (stable_admin)."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_horse@example.com",
            password="secret",
            role="stable_admin",
        )
        stable_id = stable.id

    token = login(test_client, admin.email)
    hdrs = auth_headers(token)

    payload = {"name": "Rayo", "stable_id": stable_id, "is_active": True}
    response = test_client.post("/api/v1/horses/", json=payload, headers=hdrs)
    assert response.status_code == 201
    horse_data = response.json()
    assert horse_data["name"] == payload["name"]

    response = test_client.get("/api/v1/horses/", headers=hdrs)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = test_client.get(f"/api/v1/horses/{horse_data['id']}", headers=hdrs)
    assert response.status_code == 200

    response = test_client.put(
        f"/api/v1/horses/{horse_data['id']}",
        json={"name": "Rayo II", "stable_id": stable_id, "is_active": True},
        headers=hdrs,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Rayo II"

    response = test_client.delete(f"/api/v1/horses/{horse_data['id']}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_user_crud(client):
    """Valida el CRUD completo de users."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        # app_admin para poder crear y borrar usuarios
        admin = create_user(
            session,
            stable.id,
            email="admin_user@example.com",
            password="secret",
            role="app_admin",
        )
        stable_id = stable.id

    token = login(test_client, admin.email)
    hdrs = auth_headers(token)

    payload = {
        "name": "Laura",
        "email": "laura@example.com",
        "role": "monitor",
        "stable_id": stable_id,
        "is_active": True,
        "password": "secret",
    }
    response = test_client.post("/api/v1/users/", json=payload, headers=hdrs)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == payload["email"]

    response = test_client.get("/api/v1/users/", headers=hdrs)
    assert response.status_code == 200
    # Al menos el admin y el usuario recién creado
    assert len(response.json()) >= 1

    response = test_client.get(f"/api/v1/users/{user_data['id']}", headers=hdrs)
    assert response.status_code == 200

    response = test_client.put(
        f"/api/v1/users/{user_data['id']}",
        json={"name": "Laura Updated"},
        headers=hdrs,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Laura Updated"

    response = test_client.delete(f"/api/v1/users/{user_data['id']}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_auth_login_and_refresh(client):
    """Comprueba login y refresh token con credenciales válidas."""
    test_client, engine = client

    with Session(engine) as session:
        stable_id = create_stable(session).id
        user = create_user(session, stable_id, email="auth@example.com", password="secret")

    response = test_client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "secret"},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    refreshed = response.json()
    assert "access_token" in refreshed
    assert refreshed["refresh_token"] == tokens["refresh_token"]


def test_lesson_crud(client):
    """Valida el CRUD completo de lessons, incluyendo relaciones N:N."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        stable_id = stable.id
        instructor = create_user(
            session,
            stable_id,
            email="inst@example.com",
            role="monitor",
        )
        instructor_id = instructor.id
        student_a_id = create_client_user(
            session, stable_id, name="Student A", email="a@example.com"
        ).id
        horse_a_id = create_horse_entity(session, stable_id, name="Horse A").id
        student_b_id = create_client_user(
            session, stable_id, name="Student B", email="b@example.com"
        ).id
        horse_b_id = create_horse_entity(session, stable_id, name="Horse B").id

        admin = create_user(
            session,
            stable_id,
            email="admin_lesson@example.com",
            role="stable_admin",
        )

    token = login(test_client, admin.email)
    hdrs = auth_headers(token)

    payload = {
        "date_time": datetime(2026, 2, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
        "stable_id": stable_id,
        "instructor_id": instructor_id,
        "student_ids": [student_a_id],
        "horse_ids": [horse_a_id],
    }
    response = test_client.post("/api/v1/lessons/", json=payload, headers=hdrs)
    assert response.status_code == 201
    lesson_data = response.json()
    assert lesson_data["stable_id"] == stable_id
    assert len(lesson_data["student_names"]) == 1
    assert len(lesson_data["horse_names"]) == 1

    response = test_client.get(f"/api/v1/lessons/{lesson_data['id']}", headers=hdrs)
    assert response.status_code == 200

    response = test_client.get("/api/v1/lessons/", headers=hdrs)
    assert response.status_code == 200
    assert len(response.json()) == 1

    update_payload = {
        "student_ids": [student_b_id],
        "horse_ids": [horse_b_id],
    }
    response = test_client.put(
        f"/api/v1/lessons/{lesson_data['id']}",
        json=update_payload,
        headers=hdrs,
    )
    assert response.status_code == 200
    updated = response.json()
    assert "Student B" in updated["student_names"]
    assert "Horse B" in updated["horse_names"]

    response = test_client.delete(f"/api/v1/lessons/{lesson_data['id']}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_access_control_forbidden(client):
    """Verifica que un rol insuficiente recibe 403."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        # Un client no debe poder crear caballos
        regular = create_user(
            session,
            stable.id,
            email="client_role@example.com",
            role="client",
        )
        stable_id = stable.id

    token = login(test_client, regular.email)
    hdrs = auth_headers(token)

    response = test_client.post(
        "/api/v1/horses/",
        json={"name": "Forbidden", "stable_id": stable_id, "is_active": True},
        headers=hdrs,
    )
    assert response.status_code == 403


def test_unauthenticated_returns_401(client):
    """Verifica que un endpoint protegido sin token devuelve 401."""
    test_client, _ = client

    response = test_client.get("/api/v1/horses/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Helpers adicionales
# ---------------------------------------------------------------------------

def create_box_entity(session, stable_id, name="Box 1", capacity=2):
    """Crea un box de prueba y lo asocia a una hípica."""
    box = Box(name=name, capacity=capacity, stable_id=stable_id, is_active=True)
    session.add(box)
    session.commit()
    session.refresh(box)
    return box


# ---------------------------------------------------------------------------
# Tests de Box
# ---------------------------------------------------------------------------

def test_box_crud(client):
    """Valida el CRUD completo de boxes (stable_admin)."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_box@example.com",
            password="secret",
            role="stable_admin",
        )
        stable_id = stable.id
        admin_email = admin.email

    token = login(test_client, admin_email)
    hdrs = auth_headers(token)

    # Crear sin stable_id (el endpoint lo inyecta del usuario)
    response = test_client.post(
        "/api/v1/boxes/",
        json={"name": "Box 1", "capacity": 3, "is_active": True},
        headers=hdrs,
    )
    assert response.status_code == 201
    box_data = response.json()
    assert box_data["name"] == "Box 1"
    assert box_data["capacity"] == 3
    assert box_data["stable_id"] == stable_id
    assert box_data["horses_count"] == 0

    # Listar
    response = test_client.get("/api/v1/boxes/", headers=hdrs)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Obtener por id
    response = test_client.get(f"/api/v1/boxes/{box_data['id']}", headers=hdrs)
    assert response.status_code == 200

    # Actualizar
    response = test_client.put(
        f"/api/v1/boxes/{box_data['id']}",
        json={"name": "Box Actualizado", "capacity": 5, "is_active": True},
        headers=hdrs,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Box Actualizado"
    assert response.json()["capacity"] == 5

    # Eliminar (sin caballos → debe funcionar)
    response = test_client.delete(f"/api/v1/boxes/{box_data['id']}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_box_delete_with_horses_returns_409(client):
    """Verifica que eliminar un box con caballos asignados devuelve 409 con los nombres."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_box_del@example.com",
            password="secret",
            role="stable_admin",
        )
        box = create_box_entity(session, stable.id, name="Box Ocupado", capacity=3)
        horse_a = Horse(name="Trueno", stable_id=stable.id, box_id=box.id, is_active=True)
        horse_b = Horse(name="Ventisca", stable_id=stable.id, box_id=box.id, is_active=True)
        session.add_all([horse_a, horse_b])
        session.commit()
        box_id = box.id
        admin_email = admin.email

    token = login(test_client, admin_email)
    hdrs = auth_headers(token)

    response = test_client.delete(f"/api/v1/boxes/{box_id}", headers=hdrs)
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert "Trueno" in detail
    assert "Ventisca" in detail


def test_box_create_monitor_forbidden(client):
    """Verifica que un monitor no puede crear boxes (403)."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        monitor = create_user(
            session,
            stable.id,
            email="monitor_box@example.com",
            role="monitor",
        )
        monitor_email = monitor.email

    token = login(test_client, monitor_email)
    hdrs = auth_headers(token)

    response = test_client.post(
        "/api/v1/boxes/",
        json={"name": "Box Prohibido", "capacity": 1, "is_active": True},
        headers=hdrs,
    )
    assert response.status_code == 403


def test_box_delete_not_found(client):
    """Verifica que eliminar un box inexistente devuelve 404."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_box_404@example.com",
            role="stable_admin",
        )
        admin_email = admin.email

    token = login(test_client, admin_email)
    response = test_client.delete("/api/v1/boxes/9999", headers=auth_headers(token))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests de Horse — creación sin stable_id y eliminación
# ---------------------------------------------------------------------------

def test_horse_create_without_stable_id(client):
    """Verifica que stable_admin puede crear un caballo sin enviar stable_id."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_horse_create@example.com",
            role="stable_admin",
        )
        stable_id = stable.id
        admin_email = admin.email

    token = login(test_client, admin_email)
    hdrs = auth_headers(token)

    response = test_client.post(
        "/api/v1/horses/",
        json={"name": "Relámpago", "is_active": True},
        headers=hdrs,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Relámpago"
    assert data["stable_id"] == stable_id


def test_horse_delete(client):
    """Verifica que stable_admin puede eliminar un caballo."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_horse_del@example.com",
            role="stable_admin",
        )
        horse = create_horse_entity(session, stable.id, name="Borrable")
        horse_id = horse.id
        admin_email = admin.email

    token = login(test_client, admin_email)
    hdrs = auth_headers(token)

    response = test_client.delete(f"/api/v1/horses/{horse_id}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True

    response = test_client.get(f"/api/v1/horses/{horse_id}", headers=hdrs)
    assert response.status_code == 404


def test_horse_delete_not_found(client):
    """Verifica que eliminar un caballo inexistente devuelve 404."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_horse_404@example.com",
            role="stable_admin",
        )
        admin_email = admin.email

    token = login(test_client, admin_email)
    response = test_client.delete("/api/v1/horses/9999", headers=auth_headers(token))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests de /me/profile
# ---------------------------------------------------------------------------

def test_me_profile(client):
    """Verifica que /me/profile devuelve el perfil del usuario autenticado."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_profile@example.com",
            role="stable_admin",
        )
        stable_id = stable.id
        admin_email = admin.email

    token = login(test_client, admin_email)
    response = test_client.get("/api/v1/me/profile", headers=auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == admin_email
    assert data["role"] == "stable_admin"
    assert data["stable_id"] == stable_id


def test_me_profile_unauthenticated(client):
    """Verifica que /me/profile sin token devuelve 401."""
    test_client, _ = client

    response = test_client.get("/api/v1/me/profile")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tests de capacidad de box
# ---------------------------------------------------------------------------

def test_box_capacity_exceeded(client):
    """Verifica que asignar un caballo a un box lleno devuelve 409."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_capacity@example.com",
            role="stable_admin",
        )
        # Box con capacidad 1
        box = create_box_entity(session, stable.id, name="Box Pequeño", capacity=1)
        # Caballo que ya ocupa el box
        occupant = Horse(name="Ocupante", stable_id=stable.id, box_id=box.id, is_active=True)
        session.add(occupant)
        session.commit()
        box_id = box.id
        admin_email = admin.email

    token = login(test_client, admin_email)
    hdrs = auth_headers(token)

    response = test_client.post(
        "/api/v1/horses/",
        json={"name": "Intruso", "is_active": True, "box_id": box_id},
        headers=hdrs,
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert "Box Pequeño" in detail
    assert "1" in detail          # capacidad
    assert "Ocupante" in detail   # caballo que ya está dentro
