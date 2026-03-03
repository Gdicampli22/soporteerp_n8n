-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.auditoria (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  fecha timestamp with time zone DEFAULT now(),
  usuario_responsable text,
  accion text,
  detalle text,
  entidad text,
  CONSTRAINT auditoria_pkey PRIMARY KEY (id)
);
CREATE TABLE public.clientes (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  nombre text UNIQUE,
  nombre_completo text,
  email text UNIQUE,
  empresa text,
  telefono text,
  fecha_registro timestamp with time zone DEFAULT now(),
  CONSTRAINT clientes_pkey PRIMARY KEY (id)
);
CREATE TABLE public.reportantes (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  cliente text,
  nombre text,
  email text UNIQUE,
  telefono text,
  fecha_registro timestamp with time zone DEFAULT now(),
  password text,
  activo boolean DEFAULT false,
  CONSTRAINT reportantes_pkey PRIMARY KEY (id)
);
CREATE TABLE public.tickets (
  id_ticket text NOT NULL,
  empresa text,
  usuario_reportante text,
  agente_soporte text,
  modulo_erp text,
  prioridad text,
  categoria text,
  estado text,
  sla text,
  fecha_creacion text,
  tiempo_resolucion_hs real,
  comentarios text,
  satisfaccion real,
  titulo text,
  historial character varying,
  resumen text,
  es_ticket_valido boolean,
  descripcion text,
  adjuntos text,
  respuesta_ia text,
  intencion text,
  razonamiento_ia text,
  datos_faltantes text,
  feedback_cliente text,
  email_reportante text,
  asunto text,
  cliente text,
  sla_cumplido boolean,
  CONSTRAINT tickets_pkey PRIMARY KEY (id_ticket)
);
CREATE TABLE public.usuarios (
  usuario text NOT NULL,
  contrasena text,
  rol text,
  nombre_agente text,
  email text,
  CONSTRAINT usuarios_pkey PRIMARY KEY (usuario)
);