# 📘 Nexus ERP - Documentación Técnica y Funcional
**Versión:** 1.0.0 | **Tecnologías:** Streamlit, Supabase, Make, Gmail

---

## 📑 Índice
1. [Visión General de Arquitectura](#1-visión-general-de-arquitectura)
2. [Configuración de Base de Datos (Supabase)](#2-configuración-de-base-de-datos-supabase)
3. [Automatización (Make.com)](#3-automatización-makecom)
4. [Manual del Agente (Staff)](#4-manual-del-agente-staff)
5. [Manual del Usuario (Cliente)](#5-manual-del-usuario-cliente)
6. [Estados y Flujos de Trabajo](#6-estados-y-flujos-de-trabajo)

---

## 1. Visión General de Arquitectura

El sistema **Nexus ERP Support** centraliza la gestión de tickets provenientes de múltiples canales (Web y Email).

* **Frontend:** Desarrollado en Python con **Streamlit**. Existen dos interfaces:
    * `dashboard.py`: Panel de control para agentes (Kanban, métricas, gestión).
    * `portal_cliente.py`: Interfaz para que los clientes carguen incidentes.
* **Backend:** **Supabase (PostgreSQL)**. Maneja la persistencia de datos, autenticación y almacenamiento de archivos adjuntos.
* **Automatización:** **Make (ex-Integromat)**. Orquesta la comunicación bidireccional por correo electrónico.

---

## 2. Configuración de Base de Datos (Supabase)

### Tabla: `tickets`
Almacena el núcleo de las incidencias.

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | int8 (PK) | Identificador único interno. |
| `id_ticket` | text | Identificador público (Ej: `TK-1745...`). |
| `usuario_reportante` | text | Nombre del cliente. |
| `email_reportante` | text | Correo para notificaciones. |
| `categoria` | text | Asunto o tipificación del problema. |
| `comentarios` | text | Historial completo del chat (concatenado). |
| `estado` | text | `Abierto`, `Cerrado`, `En Progreso`. |
| `prioridad` | text | `Alta`, `Media`, `Baja`. |
| `created_at` | timestamp | Fecha de creación. |

### Tabla: `reportantes` (Lista Blanca)
Controla qué usuarios tienen permiso para crear tickets vía email.

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `email` | text (PK) | Correo electrónico autorizado. |
| `nombre` | text | Nombre de la empresa o persona. |
| `activo` | boolean | `TRUE` si puede operar. |

---

## 3. Automatización (Make.com)

El sistema utiliza dos escenarios principales ("Robots") conectados a la API de Gmail y Supabase.

### 🤖 Robot 1: Actualización de Ticket (Respuestas)
Maneja las respuestas de los clientes a tickets existentes.

* **Trigger (Disparador):** Gmail - Watch Emails.
    * *Filtro:* Asunto contiene `TK-` (Case insensitive).
* **Paso 1: Text Parser:** Extrae el ID numérico usando Regex: `TK-(\d+)`.
* **Paso 2: Validación (Filtro de Seguridad):** Verifica que el Parser haya encontrado un número. Si no, se detiene.
* **Paso 3: Búsqueda (Supabase Get Items):**
    * Busca en tabla `tickets`.
    * Condición: `id_ticket` = `TK-{{ParserValue}}`.
    * Límite: 1.
* **Paso 4: Actualización (Supabase Update Row):**
    * **Row ID:** Usa el `id` obtenido en el Paso 3.
    * **Comentarios:** Concatena `[NUEVO EMAIL] + Cuerpo del Correo + Separador + Historial Viejo`.
    * **Estado:** Fuerza el estado a `Abierto`.

### 🤖 Robot 2: Creación de Ticket (Nuevos)
Maneja correos nuevos que no son respuestas.

* **Trigger:** Gmail - Watch Emails.
    * *Filtro:* Asunto **NO** contiene `TK-`.
* **Paso 1: Verificación de Cliente (Supabase Search):** Busca el remitente en la tabla `reportantes`.
* **Paso 2: Router (Semáforo):**
    * **Camino A (Cliente Existe):** Si `Count > 0`.
        * Crea fila en `tickets`.
        * Genera ID `TK-{timestamp}`.
        * Envía auto-respuesta con el número de ticket.
    * **Camino B (Desconocido):** Si `Count = 0`.
        * Envía correo de rechazo ("No registrado").

---

## 4. Manual del Agente (Staff)

### Acceso al Dashboard
1.  Ingrese a la URL del sistema (`nexus-erp.streamlit.app`).
2.  Loguearse con credenciales de administrador.

### Gestión de Tickets
* **Vista Kanban:** Mueva las tarjetas entre columnas (`Abierto` -> `En Progreso` -> `Cerrado`) para cambiar el estado rápidamente.
* **Responder:** Haga clic en un ticket para ver el detalle. Escriba en el campo de respuesta y presione "Enviar". Esto:
    * Guardará el mensaje en el historial.
    * Enviará un correo automático al cliente.

### Reglas de Oro
* ❌ **Nunca** modifique manualmente el campo `id_ticket` en la base de datos.
* ✅ Siempre verifique el historial antes de responder.

---

## 5. Manual del Usuario (Cliente)

### Opción A: Portal Web
1.  Ingrese al Portal de Ayuda.
2.  Complete el formulario con Categoría, Prioridad y Descripción.
3.  Recibirá un correo de confirmación con su número de ticket.

### Opción B: Correo Electrónico
1.  Envíe un correo a `soporte@tunegocio.com`.
2.  **Importante:** Si recibe una respuesta automática solicitando más datos, **responda siempre sobre ese mismo correo** sin borrar el código `[TK-XXXX]` del asunto.
    * ✅ Correcto: `RE: Problema de acceso [TK-1769530959]`
    * ❌ Incorrecto: `RE: Problema de acceso` (Borrar el código creará un ticket duplicado).

---

## 6. Estados y Flujos de Trabajo

| Estado | Significado | Acción Automática |
| :--- | :--- | :--- |
| **Abierto** | Ticket nuevo o cliente ha respondido. Requiere atención. | Se activa al recibir email del cliente. |
| **En Progreso** | Agente está trabajando en la solución. | Agente lo marca manualmente. |
| **Esperando Cliente** | Agente respondió y espera datos del usuario. | Se puede configurar automático al responder. |
| **Cerrado** | Incidente resuelto. | Final del ciclo. Si el cliente responde, vuelve a **Abierto**. |

---
*Documentación generada automáticamente para Nexus ERP - 2026*