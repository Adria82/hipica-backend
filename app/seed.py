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
from app.security import hash_password

# Importar modelos (sin provocar imports circulares)
from app.models.stable import Stable
from app.models.user import User
from app.models.horse import Horse
from app.models.client import Client
from app.models.lesson import Lesson
from app.models.links import LessonHorseLink, LessonClientLink


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
        # 2. Crear usuarios
        # -----------------------------------------------------------------
        admin = User(
            name="Admin Hípica",
            email="admin@hipica.com",
            role="admin",
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

        session.add_all([admin, monitor])
        session.commit()
        print(f"Usuarios creados: {admin}, {monitor}")

        # -----------------------------------------------------------------
        # 3. Crear caballos
        # -----------------------------------------------------------------
        horse1 = Horse(name="Trueno", box="A1", stable_id=stable.id)
        horse2 = Horse(name="Rayo", box="B2", stable_id=stable.id)
        horse3 = Horse(name="Estrella", box="C3", stable_id=stable.id)

        session.add_all([horse1, horse2, horse3])
        session.commit()
        print(f"Caballos creados: {horse1}, {horse2}, {horse3}")

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