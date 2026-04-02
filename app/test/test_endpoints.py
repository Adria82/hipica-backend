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
from app.models.client import Client
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


def create_client_entity(session, stable_id, name="Client 1", email="client@example.com"):
    """Crea un cliente de prueba y lo asocia a una hípica."""
    c = Client(
        name=name,
        email=email,
        phone="123",
        stable_id=stable_id,
        is_active=True,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


def create_horse_entity(session, stable_id, name="Horse 1"):
    """Crea un caballo de prueba asociado a una hípica."""
    horse = Horse(
        name=name,
        stable_id=stable_id,
        box="A1",
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


def test_client_crud(client):
    """Valida el CRUD completo de clients (stable_admin)."""
    test_client, engine = client

    with Session(engine) as session:
        stable = create_stable(session)
        admin = create_user(
            session,
            stable.id,
            email="admin_client@example.com",
            password="secret",
            role="stable_admin",
        )
        stable_id = stable.id

    token = login(test_client, admin.email)
    hdrs = auth_headers(token)

    payload = {
        "name": "Ana",
        "email": "ana@example.com",
        "phone": "600123456",
        "stable_id": stable_id,
        "is_active": True,
    }
    response = test_client.post("/api/v1/clients/", json=payload, headers=hdrs)
    assert response.status_code == 201
    client_data = response.json()
    assert client_data["email"] == payload["email"]

    response = test_client.get("/api/v1/clients/", headers=hdrs)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = test_client.get(f"/api/v1/clients/{client_data['id']}", headers=hdrs)
    assert response.status_code == 200

    response = test_client.put(
        f"/api/v1/clients/{client_data['id']}",
        json={
            "name": "Ana Updated",
            "email": "ana2@example.com",
            "phone": "600000000",
            "stable_id": stable_id,
            "is_active": True,
        },
        headers=hdrs,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Ana Updated"

    response = test_client.delete(f"/api/v1/clients/{client_data['id']}", headers=hdrs)
    assert response.status_code == 200
    assert response.json()["ok"] is True


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
        client_a_id = create_client_entity(
            session, stable_id, name="Client A", email="a@example.com"
        ).id
        horse_a_id = create_horse_entity(session, stable_id, name="Horse A").id
        client_b_id = create_client_entity(
            session, stable_id, name="Client B", email="b@example.com"
        ).id
        horse_b_id = create_horse_entity(session, stable_id, name="Horse B").id

        # Monitor puede crear/gestionar clases
        monitor = create_user(
            session,
            stable_id,
            email="monitor_lesson@example.com",
            role="monitor",
        )

    token = login(test_client, monitor.email)
    hdrs = auth_headers(token)

    payload = {
        "date_time": datetime(2026, 2, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
        "stable_id": stable_id,
        "instructor_id": instructor_id,
        "client_ids": [client_a_id],
        "horse_ids": [horse_a_id],
    }
    response = test_client.post("/api/v1/lessons/", json=payload, headers=hdrs)
    assert response.status_code == 201
    lesson_data = response.json()
    assert lesson_data["stable_id"] == stable_id
    assert len(lesson_data["clients"]) == 1
    assert len(lesson_data["horses"]) == 1

    response = test_client.get(f"/api/v1/lessons/{lesson_data['id']}", headers=hdrs)
    assert response.status_code == 200

    response = test_client.get("/api/v1/lessons/", headers=hdrs)
    assert response.status_code == 200
    assert len(response.json()) == 1

    update_payload = {
        "client_ids": [client_b_id],
        "horse_ids": [horse_b_id],
    }
    response = test_client.put(
        f"/api/v1/lessons/{lesson_data['id']}",
        json=update_payload,
        headers=hdrs,
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["clients"][0]["id"] == client_b_id
    assert updated["horses"][0]["id"] == horse_b_id

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
