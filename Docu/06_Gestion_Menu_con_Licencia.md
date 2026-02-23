# 06 - Gestión de los Menús con Licencia

## 1. Objetivo

Definir el mecanismo mediante el cual la aplicación habilita o
deshabilita funcionalidades según la licencia contratada por cada hípica
(**Stable**).

Este sistema permite: - Ofrecer un modelo SaaS modular. - Activar o
desactivar funcionalidades sin desplegar nuevas versiones. -
Personalizar la aplicación según el plan contratado. - Escalar el
producto a futuro (BASIC / PRO / PREMIUM). - Evitar bifurcaciones de
código por cliente.

> ⚠️ No es un sistema de permisos ni de roles. Es un sistema de
> licenciamiento funcional por hípica.

------------------------------------------------------------------------

## 2. Concepto Funcional

Cada hípica tiene asociadas una serie de features activas que determinan
qué módulos de la aplicación están disponibles.

Relación lógica: User → pertenece a → Stable → tiene → Features activas

------------------------------------------------------------------------

## 3. Modelo de Datos

Tabla: stablefeature

  Campo       Descripción
  ----------- -------------------------
  stable_id   Hípica propietaria
  feature     Código de funcionalidad

Clave primaria compuesta: (stable_id, feature)

------------------------------------------------------------------------

## 4. Catálogo de Funcionalidades

Definidas mediante Enum en código (`app/models/feature.py`):

-   HORSES → Gestión de caballos
-   CLIENTS → Gestión de clientes
-   LESSONS → Gestión de clases
-   BOOKINGS → Reservas (futuro)
-   BILLING → Facturación (futuro)
-   REPORTING → Informes (futuro)

------------------------------------------------------------------------

## 5. Endpoint de Consulta

GET /api/v1/me/features

Respuesta: { "features": \["HORSES", "CLIENTS", "LESSONS"\] }

------------------------------------------------------------------------

## 6. Responsabilidades

### Backend

-   Decide funcionalidades activas.
-   Garantiza consistencia de licencias.
-   Expone las features vía API.

### Frontend

-   Consume /me/features al iniciar sesión.
-   Construye navegación dinámica.
-   Oculta módulos no licenciados.

------------------------------------------------------------------------

## 7. Seed de Datos

El seed activa automáticamente funcionalidades iniciales para la hípica
de desarrollo.

------------------------------------------------------------------------

## 8. Diferencia entre Roles y Licencias

  Concepto   Controla
  ---------- ----------------------------
  Rol        Qué puede hacer el usuario
  Licencia   Qué módulos existen

------------------------------------------------------------------------

## 9. Ventajas

-   Arquitectura SaaS real.
-   Sin sobreingeniería.
-   Escalable.
-   Fácil de mantener.
-   Añadir una feature = añadir un Enum.

------------------------------------------------------------------------

## 10. Estado Actual

✔ Backend preparado para licenciamiento por hípica\
✔ Endpoint /me/features operativo\
✔ Seed alineado con el modelo SaaS
