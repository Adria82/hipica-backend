"""
Script para insertar datos de prueba en la base de datos de la hípica.

- Crea una hípica (Stable)
- Crea usuarios (admin, monitor, ayudante y clientes) con contraseñas hasheadas
- Rellena perfiles extendidos de clientes y monitores
- Crea caballos con niveles asignados
- Crea clases en enero con relaciones N:N

Autor: Adrià Bofill
Fecha: 31/01/2026
Proyecto: Gestión de Hípica
"""

import json
from datetime import datetime, timezone

from sqlmodel import Session, SQLModel

from app.db.session import engine
from app.models.level import Level
from app.security import hash_password

from app.models.stable import Stable
from app.models.user import User
from app.models.horse import Horse
from app.models.lesson import Lesson
from app.models.links import HorseLevelLink, LessonHorseLink, LessonUserLink
from app.models.stable_feature import StableFeature
from app.models.feature import FeatureCode
from app.models.box import Box
from app.models.client_profile import ClientProfile
from app.models.monitor_profile import MonitorProfile


def seed_db() -> None:
    """
    Borra y recrea todas las tablas y carga datos de prueba.
    SOLO USAR EN ENTORNOS DE DESARROLLO.
    """

    # ------------------------------------------------------------------
    # 0. Reset de base de datos
    # ------------------------------------------------------------------
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("Tablas recreadas correctamente.")

    now = datetime.now(timezone.utc)

    with Session(engine) as session:
        # --------------------------------------------------------------
        # 1. Crear hípica
        # --------------------------------------------------------------
        stable = Stable(
            name="Hípica Can Valls",
            location="Caldes de Montbui",
            is_active=True,
        )
        session.add(stable)
        session.commit()
        session.refresh(stable)
        print(f"Stable creado: {stable}")

        # --------------------------------------------------------------
        # 1.1 Activar funcionalidades
        # --------------------------------------------------------------
        features = [
            FeatureCode.HORSES,
            FeatureCode.CLIENTS,
            FeatureCode.LESSONS,
        ]
        session.add_all(
            [StableFeature(stable_id=stable.id, feature=feature) for feature in features]
        )
        session.commit()
        print(f"Features activadas: {features}")

        # --------------------------------------------------------------
        # 2. Crear usuarios staff
        # --------------------------------------------------------------
        superAdmin = User(
            name="ABE",
            email="abe@hipica.com",
            role="app_admin",
            hashed_password=hash_password("qwerty"),
            is_active=True,
            created_at=now,
        )

        admin = User(
            name="Toni",
            email="toni@canvalls.es",
            role="stable_admin",
            stable_id=stable.id,
            hashed_password=hash_password("admin123"),
            is_active=True,
            created_at=now,
        )

        monitor = User(
            name="Juan García",
            email="juan@hipica.com",
            role="monitor",
            stable_id=stable.id,
            phone="600100200",
            hashed_password=hash_password("monitor123"),
            is_active=True,
            created_at=now,
        )

        assistant = User(
            name="Marta López",
            email="marta@hipica.com",
            role="assistant",
            stable_id=stable.id,
            phone="600100300",
            hashed_password=hash_password("assistant123"),
            is_active=True,
            created_at=now,
        )

        session.add_all([superAdmin, admin, monitor, assistant])
        session.commit()
        session.refresh(monitor)
        session.refresh(assistant)
        print(f"Staff creado: {superAdmin}, {admin}, {monitor}, {assistant}")

        # Monitor profile
        monitor_schedule = [
            {"day": "monday",    "slots": [{"from": "10:00", "to": "13:00"}, {"from": "17:00", "to": "20:00"}]},
            {"day": "wednesday", "slots": [{"from": "16:00", "to": "20:00"}]},
            {"day": "sunday",    "slots": [{"from": "09:00", "to": "14:00"}]},
        ]
        session.add(MonitorProfile(
            user_id=monitor.id,
            especialidad="Doma clásica",
            disponibilidad=json.dumps(monitor_schedule),
            certificados="RFHE Nivel 2",
            experiencia="8 años como monitor federado",
            telefono="600100200",
            iban="ES7621000418401234567891",
            notas="Monitor principal de la hípica",
            tarifa_hora=25.0,
        ))

        # Assistant profile
        assistant_schedule = [
            {"day": "tuesday",  "slots": [{"from": "16:00", "to": "20:00"}]},
            {"day": "saturday", "slots": [{"from": "09:00", "to": "13:00"}]},
        ]
        session.add(MonitorProfile(
            user_id=assistant.id,
            especialidad="Salto",
            disponibilidad=json.dumps(assistant_schedule),
            certificados="RFHE Nivel 1",
            experiencia="3 años",
            telefono="600100300",
            iban="ES7621000418401234567892",
            notas="Ayudante de fin de semana",
            tarifa_hora=18.0,
        ))
        session.commit()

        # --------------------------------------------------------------
        # 2.1 Crear niveles de equitación
        # --------------------------------------------------------------
        nivel_data = [
            {"es": "Principiante", "en": "Beginner",     "ca": "Principiant"},
            {"es": "Iniciado",     "en": "Novice",        "ca": "Iniciat"},
            {"es": "Intermedio",   "en": "Intermediate",  "ca": "Intermedi"},
            {"es": "Avanzado",     "en": "Advanced",      "ca": "Avançat"},
            {"es": "Experto",      "en": "Expert",        "ca": "Expert"},
        ]
        levels = []
        for names in nivel_data:
            level = Level(names=names)
            session.add(level)
            levels.append(level)
        session.commit()
        for l in levels:
            session.refresh(l)
        print(f"Niveles creados: {[l.names.get('es') for l in levels]}")

        # --------------------------------------------------------------
        # 2.2 Crear clientes (≥4)
        # --------------------------------------------------------------
        clients_data = [
            dict(name="Carlos Ruiz",    email="carlos@gmail.com",  phone="600111222", level_idx=0),
            dict(name="Ana Martínez",   email="ana@gmail.com",     phone="600333444", level_idx=1),
            dict(name="Lucía Fernández",email="lucia@gmail.com",   phone="600555666", level_idx=2),
            dict(name="Pedro Sánchez",  email="pedro@gmail.com",   phone="600777888", level_idx=1),
        ]
        clients = []
        for cd in clients_data:
            u = User(
                name=cd["name"],
                email=cd["email"],
                phone=cd["phone"],
                role="client",
                stable_id=stable.id,
                hashed_password=hash_password("changeme"),
                is_active=True,
                created_at=now,
            )
            session.add(u)
            clients.append((u, cd["level_idx"]))

        session.commit()
        for u, _ in clients:
            session.refresh(u)

        # Perfiles de cliente
        client_extra = [
            dict(apellidos="Ruiz Mora",       direccion="Calle Mayor 1, Barcelona",    iban="ES7621000418401234567801", notes="Alérgico al polvo"),
            dict(apellidos="Martínez Gil",    direccion="Av. Diagonal 200, Barcelona", iban="ES7621000418401234567802", notes="Paga por domiciliación"),
            dict(apellidos="Fernández Puig",  direccion="Carrer Nou 5, Sabadell",      iban="ES7621000418401234567803", notes="Prefiere horario tarde"),
            dict(apellidos="Sánchez Torres",  direccion="Passeig de Gràcia 10",        iban="ES7621000418401234567804", notes="Nuevo alumno"),
        ]
        for (u, level_idx), extra in zip(clients, client_extra):
            session.add(ClientProfile(
                user_id=u.id,
                apellidos=extra["apellidos"],
                direccion=extra["direccion"],
                iban=extra["iban"],
                notes=extra["notes"],
                level_id=levels[level_idx].id,
            ))
        session.commit()
        print(f"Clientes creados: {[u.name for u, _ in clients]}")

        # --------------------------------------------------------------
        # 2.3 Crear boxes
        # --------------------------------------------------------------
        box1 = Box(name="Box 1", capacity=1, stable_id=stable.id)
        box2 = Box(name="Box 2", capacity=1, stable_id=stable.id)
        box3 = Box(name="Box 3", capacity=2, stable_id=stable.id)
        session.add_all([box1, box2, box3])
        session.commit()
        session.refresh(box1)
        session.refresh(box2)
        session.refresh(box3)

        # --------------------------------------------------------------
        # 3. Crear caballos
        # --------------------------------------------------------------
        horse1 = Horse(name="Trueno",   stable_id=stable.id, box_id=box1.id)
        horse2 = Horse(name="Rayo",     stable_id=stable.id, box_id=box2.id)
        horse3 = Horse(name="Estrella", stable_id=stable.id, box_id=box3.id)
        horse4 = Horse(name="Viento",   stable_id=stable.id, box_id=box3.id)
        session.add_all([horse1, horse2, horse3, horse4])
        session.commit()
        session.refresh(horse1)
        session.refresh(horse2)
        session.refresh(horse3)
        session.refresh(horse4)

        # Asignar niveles a caballos
        session.add_all([
            HorseLevelLink(horse_id=horse1.id, level_id=levels[0].id),
            HorseLevelLink(horse_id=horse1.id, level_id=levels[1].id),
            HorseLevelLink(horse_id=horse2.id, level_id=levels[1].id),
            HorseLevelLink(horse_id=horse2.id, level_id=levels[2].id),
            HorseLevelLink(horse_id=horse3.id, level_id=levels[3].id),
            HorseLevelLink(horse_id=horse3.id, level_id=levels[4].id),
            HorseLevelLink(horse_id=horse4.id, level_id=levels[0].id),
        ])
        session.commit()
        print("Caballos y niveles creados.")

        # --------------------------------------------------------------
        # 4. Crear clases de enero 2026
        #    Mínimo 4 clases, cada una con ≥1 cliente diferente
        # --------------------------------------------------------------
        client_users = [u for u, _ in clients]

        lessons_data = [
            dict(date=datetime(2026, 1, 6,  10, 0, tzinfo=timezone.utc),
                 end=datetime(2026, 1, 6,  11, 0, tzinfo=timezone.utc),
                 horses=[horse1, horse2], students=[client_users[0], client_users[1]]),
            dict(date=datetime(2026, 1, 10, 9, 0, tzinfo=timezone.utc),
                 end=datetime(2026, 1, 10, 10, 30, tzinfo=timezone.utc),
                 horses=[horse3], students=[client_users[2]]),
            dict(date=datetime(2026, 1, 14, 17, 0, tzinfo=timezone.utc),
                 end=datetime(2026, 1, 14, 18, 30, tzinfo=timezone.utc),
                 horses=[horse1, horse4], students=[client_users[0], client_users[3]]),
            dict(date=datetime(2026, 1, 18, 10, 0, tzinfo=timezone.utc),
                 end=datetime(2026, 1, 18, 11, 0, tzinfo=timezone.utc),
                 horses=[horse2, horse3], students=[client_users[1], client_users[2]]),
            dict(date=datetime(2026, 1, 21, 16, 0, tzinfo=timezone.utc),
                 end=datetime(2026, 1, 21, 17, 30, tzinfo=timezone.utc),
                 horses=[horse4], students=[client_users[3]]),
            dict(date=datetime(2026, 1, 25, 9, 0, tzinfo=timezone.utc),
                 end=datetime(2026, 1, 25, 10, 30, tzinfo=timezone.utc),
                 horses=[horse1, horse2, horse3], students=[client_users[0], client_users[1], client_users[2], client_users[3]]),
        ]

        for ld in lessons_data:
            lesson = Lesson(
                date_time=ld["date"],
                end_time=ld["end"],
                instructor_id=monitor.id,
                stable_id=stable.id,
            )
            session.add(lesson)
            session.commit()
            session.refresh(lesson)
            for h in ld["horses"]:
                session.add(LessonHorseLink(lesson_id=lesson.id, horse_id=h.id))
            for s in ld["students"]:
                session.add(LessonUserLink(lesson_id=lesson.id, user_id=s.id))
            session.commit()

        print(f"Clases de enero creadas: {len(lessons_data)}")
        print("Seed completado correctamente.")


# -------------------------------------------------------------------------
# Ejecutar script
# -------------------------------------------------------------------------
if __name__ == "__main__":
    seed_db()
