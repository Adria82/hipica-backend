"""
Script para insertar datos de prueba en la base de datos de la hípica.

- Crea una hípica (Stable)
- Crea usuarios (admin y monitor) con contraseñas hasheadas
- Crea caballos
- Crea clientes
- Crea lecciones con relaciones N:N entre caballos y clientes

Autor: Adrià Bofill
Fecha: 31/01/2026
Proyecto: Gestión de Hípica
"""

from datetime import datetime, timezone

from sqlmodel import Session, SQLModel

from app.db.session import engine
from app.models.level import Level, NivelEquitacion
from app.security import hash_password

# Importar modelos (sin provocar imports circulares)
from app.models.stable import Stable
from app.models.user import User
from app.models.horse import Horse
from app.models.client import Client
from app.models.lesson import Lesson
from app.models.links import HorseLevelLink, LessonHorseLink, LessonClientLink
from app.models.stable_feature import StableFeature
from app.models.feature import FeatureCode
from app.models.box import Box


def seed_db() -> None:
    """
    Borra y recrea todas las tablas y carga datos de prueba.
    SOLO USAR EN ENTORNOS DE DESARROLLO.
    """

    # ---------------------------------------------------------------------
    # 0. Reset de base de datos
    # ---------------------------------------------------------------------
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    print("Tablas recreadas correctamente.")

    now = datetime.now(timezone.utc)

    with Session(engine) as session:
        # -----------------------------------------------------------------
        # 1. Crear hípica
        # -----------------------------------------------------------------
        stable = Stable(
            name="Hípica Can Valls",
            location="Caldes de Montbui",
            is_active=True,
        )
        session.add(stable)
        session.commit()
        session.refresh(stable)
        print(f"Stable creado: {stable}")

        # -----------------------------------------------------------------
        # 1.1 Activar funcionalidades para la hípica (licenciamiento)
        # -----------------------------------------------------------------
        features = [
            FeatureCode.HORSES,
            FeatureCode.CLIENTS,
            FeatureCode.LESSONS,
        ]

        session.add_all(
            [StableFeature(stable_id=stable.id, feature=feature) for feature in features]
        )
        session.commit()

        print(f"Features activadas para la stable {stable.id}: {features}")

        # -----------------------------------------------------------------
        # 2. Crear usuarios
        # -----------------------------------------------------------------
        superAdmin = User(
            name="ABE",
            email="abe@hipica.com",
            role="app_admin",
            #stable_id=stable.id,
            hashed_password=hash_password("qwerty"),
            is_active=True,
            created_at=now,
        )

        admin = User(
            name="Admin Hípica",
            email="admin@hipica.com",
            role="stable_admin",
            stable_id=stable.id,
            hashed_password=hash_password("admin123"),
            is_active=True,
            created_at=now,
        )

        monitor = User(
            name="Monitor Juan",
            email="juan@hipica.com",
            role="monitor",
            stable_id=stable.id,
            hashed_password=hash_password("monitor123"),
            is_active=True,
            created_at=now,
        )

        client = User(
            name="Cliente Ana",
            email="ana@hipica.com",
            role="client",
            stable_id=stable.id,
            hashed_password=hash_password("client123"),
            is_active=True,
            created_at=now,
        )

        session.add_all([superAdmin, admin, monitor, client])
        session.commit()
        print(f"Usuarios creados: {superAdmin}, {admin}, {monitor}, {client}")

        # -----------------------------------------------------------------
        # 2.5 Crear niveles de equitación (catálogo)
        # -----------------------------------------------------------------
        levels = []
        for nivel in NivelEquitacion:
            level = Level(name=nivel)
            session.add(level)
            levels.append(level)

        session.commit()
        print(f"Niveles de equitación creados: {[l.name for l in levels]}")
        
        # -----------------------------------------------------------------
        # 2.8 Crear boxes
        # -----------------------------------------------------------------
        box1 = Box(name="Box 1", capacity=1, stable_id=stable.id)
        box2 = Box(name="Box 2", capacity=1, stable_id=stable.id)
        box3 = Box(name="Box 3", capacity=2, stable_id=stable.id)

        session.add_all([box1, box2, box3])
        session.commit()
        session.refresh(box1)
        session.refresh(box2)
        session.refresh(box3)
        print(f"Boxes creados: {box1}, {box2}, {box3}")

        # -----------------------------------------------------------------
        # 3. Crear caballos
        # -----------------------------------------------------------------
        horse1 = Horse(name="Trueno", stable_id=stable.id, box_id=box1.id)
        horse2 = Horse(name="Rayo", stable_id=stable.id, box_id=box2.id)
        horse3 = Horse(name="Estrella", stable_id=stable.id, box_id=box3.id)
        horse4 = Horse(name="Viento", stable_id=stable.id, box_id=box3.id)

        session.add_all([horse1, horse2, horse3, horse4])
        session.commit()
        print(f"Caballos creados: {horse1}, {horse2}, {horse3}, {horse4}")

        # -----------------------------------------------------------------
        # 3.1 Asignar niveles a caballos
        # -----------------------------------------------------------------
        # Trueno: principiante + iniciado
        session.add_all([
            HorseLevelLink(horse_id=horse1.id, level_id=levels[0].id),
            HorseLevelLink(horse_id=horse1.id, level_id=levels[1].id),
        ])

        # Rayo: iniciado + experto
        session.add_all([
            HorseLevelLink(horse_id=horse2.id, level_id=levels[1].id),
            HorseLevelLink(horse_id=horse2.id, level_id=levels[2].id),
        ])

        # Estrella: solo experto
        session.add(
            HorseLevelLink(horse_id=horse3.id, level_id=levels[2].id)
        )

        # Viento: principiante
        session.add(
            HorseLevelLink(horse_id=horse4.id, level_id=levels[0].id)
        )

        session.commit()
        print("Niveles asignados a los caballos.")

        # -----------------------------------------------------------------
        # 4. Crear clientes
        # -----------------------------------------------------------------
        client1 = Client(
            name="Carlos",
            email="carlos@gmail.com",
            phone="600111222",
            stable_id=stable.id,
        )
        client2 = Client(
            name="Ana",
            email="ana@gmail.com",
            phone="600333444",
            stable_id=stable.id,
        )
        client3 = Client(
            name="Lucía",
            email="lucia@gmail.com",
            phone="600555666",
            stable_id=stable.id,
        )

        session.add_all([client1, client2, client3])
        session.commit()
        print(f"Clientes creados: {client1}, {client2}, {client3}")

        # -----------------------------------------------------------------
        # 5. Crear lecciones
        # -----------------------------------------------------------------
        lesson1 = Lesson(
            date_time=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
            instructor_id=monitor.id,
            stable_id=stable.id,
        )
        lesson2 = Lesson(
            date_time=datetime(2026, 2, 1, 12, 0, tzinfo=timezone.utc),
            instructor_id=monitor.id,
            stable_id=stable.id,
        )

        session.add_all([lesson1, lesson2])
        session.commit()
        session.refresh(lesson1)
        session.refresh(lesson2)

        # -----------------------------------------------------------------
        # 6. Relaciones N:N (lecciones ↔ caballos / clientes)
        # -----------------------------------------------------------------
        session.add_all([
            # Lesson 1
            LessonHorseLink(lesson_id=lesson1.id, horse_id=horse1.id),
            LessonHorseLink(lesson_id=lesson1.id, horse_id=horse2.id),
            LessonClientLink(lesson_id=lesson1.id, client_id=client1.id),
            LessonClientLink(lesson_id=lesson1.id, client_id=client2.id),

            # Lesson 2
            LessonHorseLink(lesson_id=lesson2.id, horse_id=horse2.id),
            LessonHorseLink(lesson_id=lesson2.id, horse_id=horse3.id),
            LessonClientLink(lesson_id=lesson2.id, client_id=client2.id),
            LessonClientLink(lesson_id=lesson2.id, client_id=client3.id),
        ])

        session.commit()
        print(f"Lecciones creadas con relaciones N:N: {lesson1}, {lesson2}")


# -------------------------------------------------------------------------
# Ejecutar script
# -------------------------------------------------------------------------
if __name__ == "__main__":
    seed_db()