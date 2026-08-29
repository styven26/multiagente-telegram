--
-- PostgreSQL database dump
--

\restrict aXZh4lQYjC9fjixS1kNbTPzsf7LAW5UDGacG97bmDxQ8t1MXxgUd19Cu2B3vw1d

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_interactions (
    id integer NOT NULL,
    student_id integer,
    session_id integer,
    model_run_id integer,
    agente character varying(32) NOT NULL,
    accion character varying(64) NOT NULL,
    entrada json,
    salida json,
    exitosa boolean DEFAULT true NOT NULL,
    duracion_ms double precision,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_agent_interactions_agent CHECK (((agente)::text = ANY ((ARRAY['orchestrator'::character varying, 'evaluation'::character varying, 'student_model'::character varying, 'pedagogical'::character varying, 'spaced_repetition'::character varying])::text[])))
);


ALTER TABLE public.agent_interactions OWNER TO postgres;

--
-- Name: agent_interactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_interactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_interactions_id_seq OWNER TO postgres;

--
-- Name: agent_interactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_interactions_id_seq OWNED BY public.agent_interactions.id;


--
-- Name: capsules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.capsules (
    id character varying(64) NOT NULL,
    topic_id character varying(64) NOT NULL,
    titulo character varying(200) NOT NULL,
    objetivo text NOT NULL,
    contenido text NOT NULL,
    orden integer DEFAULT 0 NOT NULL,
    duracion_min integer DEFAULT 5 NOT NULL,
    dificultad integer DEFAULT 1 NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    imagen_url character varying(500),
    CONSTRAINT ck_capsules_dificultad CHECK (((dificultad >= 1) AND (dificultad <= 3))),
    CONSTRAINT ck_capsules_duracion CHECK (((duracion_min >= 1) AND (duracion_min <= 60))),
    CONSTRAINT ck_capsules_orden CHECK ((orden >= 0))
);


ALTER TABLE public.capsules OWNER TO postgres;

--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id integer NOT NULL,
    student_id integer,
    session_id integer,
    ciclo integer DEFAULT 1 NOT NULL,
    tipo character varying(64) NOT NULL,
    payload json,
    ocurrido_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_events_ciclo CHECK (((ciclo >= 1) AND (ciclo <= 3)))
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.events_id_seq OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: mastery; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mastery (
    id integer NOT NULL,
    student_id integer NOT NULL,
    topic_id character varying(64) NOT NULL,
    nivel double precision DEFAULT '0'::double precision NOT NULL,
    fuente character varying(24) DEFAULT 'baseline'::character varying NOT NULL,
    probabilidad_siguiente_correcta double precision,
    numero_evidencias integer DEFAULT 0 NOT NULL,
    modelo_version character varying(64),
    ultima_respuesta_en timestamp with time zone,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_mastery_evidencias CHECK ((numero_evidencias >= 0)),
    CONSTRAINT ck_mastery_fuente CHECK (((fuente)::text = ANY ((ARRAY['baseline'::character varying, 'sakt'::character varying, 'manual'::character varying])::text[]))),
    CONSTRAINT ck_mastery_nivel CHECK (((nivel >= (0.0)::double precision) AND (nivel <= (1.0)::double precision)))
);


ALTER TABLE public.mastery OWNER TO postgres;

--
-- Name: mastery_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mastery_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mastery_id_seq OWNER TO postgres;

--
-- Name: mastery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mastery_id_seq OWNED BY public.mastery.id;


--
-- Name: model_predictions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_predictions (
    id integer NOT NULL,
    student_id integer NOT NULL,
    model_run_id integer NOT NULL,
    question_id integer,
    topic_id character varying(64),
    secuencia integer,
    probabilidad double precision NOT NULL,
    resultado_real boolean,
    error_absoluto double precision,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_predictions_probability CHECK (((probabilidad >= (0.0)::double precision) AND (probabilidad <= (1.0)::double precision)))
);


ALTER TABLE public.model_predictions OWNER TO postgres;

--
-- Name: model_predictions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.model_predictions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.model_predictions_id_seq OWNER TO postgres;

--
-- Name: model_predictions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.model_predictions_id_seq OWNED BY public.model_predictions.id;


--
-- Name: model_runs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_runs (
    id integer NOT NULL,
    ciclo integer NOT NULL,
    tipo character varying(32) NOT NULL,
    nombre_modelo character varying(128) NOT NULL,
    version character varying(64) NOT NULL,
    dataset character varying(128) NOT NULL,
    descripcion text,
    hiperparametros json,
    metricas json,
    auc double precision,
    f1 double precision,
    accuracy double precision,
    "precision" double precision,
    recall double precision,
    reward_medio double precision,
    fecha_entrenamiento timestamp with time zone,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    CONSTRAINT ck_model_runs_ciclo CHECK (((ciclo >= 1) AND (ciclo <= 3))),
    CONSTRAINT ck_model_runs_tipo CHECK (((tipo)::text = ANY ((ARRAY['sakt'::character varying, 'dqn'::character varying, 'spaced_nn'::character varying, 'baseline'::character varying, 'otro'::character varying])::text[])))
);


ALTER TABLE public.model_runs OWNER TO postgres;

--
-- Name: model_runs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.model_runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.model_runs_id_seq OWNER TO postgres;

--
-- Name: model_runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.model_runs_id_seq OWNED BY public.model_runs.id;


--
-- Name: pedagogical_decisions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedagogical_decisions (
    id integer NOT NULL,
    student_id integer NOT NULL,
    session_id integer,
    model_run_id integer,
    ciclo integer DEFAULT 3 NOT NULL,
    estrategia character varying(24) DEFAULT 'dqn'::character varying NOT NULL,
    tipo_accion character varying(48) NOT NULL,
    objetivo_id character varying(64),
    estado json NOT NULL,
    accion json NOT NULL,
    recompensa double precision,
    siguiente_estado json,
    terminada boolean DEFAULT false NOT NULL,
    parametros json,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_pedagogical_ciclo CHECK (((ciclo >= 1) AND (ciclo <= 3))),
    CONSTRAINT ck_pedagogical_strategy CHECK (((estrategia)::text = ANY ((ARRAY['reglas'::character varying, 'mago_oz'::character varying, 'dqn'::character varying])::text[])))
);


ALTER TABLE public.pedagogical_decisions OWNER TO postgres;

--
-- Name: pedagogical_decisions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pedagogical_decisions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pedagogical_decisions_id_seq OWNER TO postgres;

--
-- Name: pedagogical_decisions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pedagogical_decisions_id_seq OWNED BY public.pedagogical_decisions.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questions (
    id integer NOT NULL,
    capsule_id character varying(64) NOT NULL,
    topic_id character varying(64) NOT NULL,
    tipo character varying(24) DEFAULT 'opcion_multiple'::character varying NOT NULL,
    enunciado text NOT NULL,
    opciones json NOT NULL,
    correcta integer NOT NULL,
    retroalimentacion text,
    dificultad integer DEFAULT 1 NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    imagen_url character varying(500),
    CONSTRAINT ck_questions_correcta CHECK ((correcta >= 0)),
    CONSTRAINT ck_questions_dificultad CHECK (((dificultad >= 1) AND (dificultad <= 3))),
    CONSTRAINT ck_questions_tipo CHECK (((tipo)::text = ANY ((ARRAY['opcion_multiple'::character varying, 'verdadero_falso'::character varying, 'respuesta_corta'::character varying])::text[])))
);


ALTER TABLE public.questions OWNER TO postgres;

--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questions_id_seq OWNER TO postgres;

--
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questions_id_seq OWNED BY public.questions.id;


--
-- Name: reminders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reminders (
    id integer NOT NULL,
    student_id integer NOT NULL,
    spaced_repetition_id integer,
    titulo character varying(200) NOT NULL,
    mensaje text NOT NULL,
    canal character varying(24) DEFAULT 'telegram'::character varying NOT NULL,
    programado_en timestamp with time zone NOT NULL,
    enviado_en timestamp with time zone,
    estado character varying(16) DEFAULT 'pendiente'::character varying NOT NULL,
    intentos_envio integer DEFAULT 0 NOT NULL,
    error_detalle text,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_reminders_attempts CHECK ((intentos_envio >= 0)),
    CONSTRAINT ck_reminders_estado CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'enviado'::character varying, 'fallido'::character varying, 'cancelado'::character varying])::text[])))
);


ALTER TABLE public.reminders OWNER TO postgres;

--
-- Name: reminders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reminders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reminders_id_seq OWNER TO postgres;

--
-- Name: reminders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reminders_id_seq OWNED BY public.reminders.id;


--
-- Name: responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.responses (
    id integer NOT NULL,
    student_id integer NOT NULL,
    session_id integer,
    question_id integer NOT NULL,
    topic_id character varying(64) NOT NULL,
    orden_interaccion integer NOT NULL,
    intento integer DEFAULT 1 NOT NULL,
    seleccion integer NOT NULL,
    es_correcta boolean NOT NULL,
    tiempo_seg double precision,
    respondido_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_responses_seleccion CHECK ((seleccion >= 0)),
    CONSTRAINT ck_responses_sequence CHECK ((orden_interaccion >= 1)),
    CONSTRAINT ck_responses_tiempo CHECK (((tiempo_seg IS NULL) OR (tiempo_seg >= (0)::double precision)))
);


ALTER TABLE public.responses OWNER TO postgres;

--
-- Name: responses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.responses_id_seq OWNER TO postgres;

--
-- Name: responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.responses_id_seq OWNED BY public.responses.id;


--
-- Name: spaced_repetition; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.spaced_repetition (
    id integer NOT NULL,
    student_id integer NOT NULL,
    topic_id character varying(64) NOT NULL,
    capsule_id character varying(64) NOT NULL,
    calidad integer DEFAULT 0 NOT NULL,
    ease_factor double precision DEFAULT '2.5'::double precision NOT NULL,
    intervalo_dias integer DEFAULT 0 NOT NULL,
    repeticiones integer DEFAULT 0 NOT NULL,
    errores integer DEFAULT 0 NOT NULL,
    dificultad double precision DEFAULT '0.5'::double precision NOT NULL,
    estabilidad double precision DEFAULT '0'::double precision NOT NULL,
    ajuste_red_neuronal double precision DEFAULT '1'::double precision NOT NULL,
    ultima_revision_en timestamp with time zone,
    proxima_revision_en timestamp with time zone,
    modelo_version character varying(64),
    activo boolean DEFAULT true NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_spaced_difficulty CHECK (((dificultad >= (0.0)::double precision) AND (dificultad <= (1.0)::double precision))),
    CONSTRAINT ck_spaced_ease CHECK ((ease_factor >= (1.3)::double precision)),
    CONSTRAINT ck_spaced_errors CHECK ((errores >= 0)),
    CONSTRAINT ck_spaced_interval CHECK ((intervalo_dias >= 0)),
    CONSTRAINT ck_spaced_quality CHECK (((calidad >= 0) AND (calidad <= 5))),
    CONSTRAINT ck_spaced_repetitions CHECK ((repeticiones >= 0)),
    CONSTRAINT ck_spaced_stability CHECK ((estabilidad >= (0.0)::double precision))
);


ALTER TABLE public.spaced_repetition OWNER TO postgres;

--
-- Name: spaced_repetition_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.spaced_repetition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.spaced_repetition_id_seq OWNER TO postgres;

--
-- Name: spaced_repetition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.spaced_repetition_id_seq OWNED BY public.spaced_repetition.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    codigo_anonimo character varying(16) NOT NULL,
    nombre_telegram character varying(128),
    consentimiento boolean DEFAULT false NOT NULL,
    fecha_consentimiento timestamp with time zone,
    version_consentimiento character varying(32),
    grupo character varying(16),
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_students_consentimiento_fecha CHECK ((((consentimiento = false) AND (fecha_consentimiento IS NULL)) OR ((consentimiento = true) AND (fecha_consentimiento IS NOT NULL)))),
    CONSTRAINT ck_students_grupo CHECK (((grupo IS NULL) OR ((grupo)::text = ANY ((ARRAY['experimental'::character varying, 'control'::character varying])::text[]))))
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO postgres;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: study_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_sessions (
    id integer NOT NULL,
    student_id integer NOT NULL,
    capsule_id character varying(64),
    ciclo integer DEFAULT 1 NOT NULL,
    estrategia character varying(24) DEFAULT 'manual_mago_oz'::character varying NOT NULL,
    iniciada_en timestamp with time zone DEFAULT now() NOT NULL,
    finalizada_en timestamp with time zone,
    duracion_seg double precision,
    completada boolean DEFAULT false NOT NULL,
    CONSTRAINT ck_sessions_ciclo CHECK (((ciclo >= 1) AND (ciclo <= 3))),
    CONSTRAINT ck_sessions_duracion CHECK (((duracion_seg IS NULL) OR (duracion_seg >= (0)::double precision))),
    CONSTRAINT ck_sessions_estrategia CHECK (((estrategia)::text = ANY ((ARRAY['fija'::character varying, 'adaptativa'::character varying, 'manual_mago_oz'::character varying])::text[]))),
    CONSTRAINT ck_sessions_fechas CHECK (((finalizada_en IS NULL) OR (finalizada_en >= iniciada_en)))
);


ALTER TABLE public.study_sessions OWNER TO postgres;

--
-- Name: study_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.study_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_sessions_id_seq OWNER TO postgres;

--
-- Name: study_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.study_sessions_id_seq OWNED BY public.study_sessions.id;


--
-- Name: sus_responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sus_responses (
    id integer NOT NULL,
    student_id integer NOT NULL,
    fase character varying(32) DEFAULT 'ciclo_3'::character varying NOT NULL,
    q1 integer NOT NULL,
    q2 integer NOT NULL,
    q3 integer NOT NULL,
    q4 integer NOT NULL,
    q5 integer NOT NULL,
    q6 integer NOT NULL,
    q7 integer NOT NULL,
    q8 integer NOT NULL,
    q9 integer NOT NULL,
    q10 integer NOT NULL,
    score double precision NOT NULL,
    comentario text,
    enviado_en timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_sus_q1 CHECK (((q1 >= 1) AND (q1 <= 5))),
    CONSTRAINT ck_sus_q10 CHECK (((q10 >= 1) AND (q10 <= 5))),
    CONSTRAINT ck_sus_q2 CHECK (((q2 >= 1) AND (q2 <= 5))),
    CONSTRAINT ck_sus_q3 CHECK (((q3 >= 1) AND (q3 <= 5))),
    CONSTRAINT ck_sus_q4 CHECK (((q4 >= 1) AND (q4 <= 5))),
    CONSTRAINT ck_sus_q5 CHECK (((q5 >= 1) AND (q5 <= 5))),
    CONSTRAINT ck_sus_q6 CHECK (((q6 >= 1) AND (q6 <= 5))),
    CONSTRAINT ck_sus_q7 CHECK (((q7 >= 1) AND (q7 <= 5))),
    CONSTRAINT ck_sus_q8 CHECK (((q8 >= 1) AND (q8 <= 5))),
    CONSTRAINT ck_sus_q9 CHECK (((q9 >= 1) AND (q9 <= 5))),
    CONSTRAINT ck_sus_score CHECK (((score >= (0)::double precision) AND (score <= (100)::double precision)))
);


ALTER TABLE public.sus_responses OWNER TO postgres;

--
-- Name: sus_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sus_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sus_responses_id_seq OWNER TO postgres;

--
-- Name: sus_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sus_responses_id_seq OWNED BY public.sus_responses.id;


--
-- Name: teacher_student_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teacher_student_assignments (
    id integer NOT NULL,
    teacher_id integer NOT NULL,
    student_id integer NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.teacher_student_assignments OWNER TO postgres;

--
-- Name: teacher_student_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teacher_student_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teacher_student_assignments_id_seq OWNER TO postgres;

--
-- Name: teacher_student_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teacher_student_assignments_id_seq OWNED BY public.teacher_student_assignments.id;


--
-- Name: teachers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.teachers (
    id integer NOT NULL,
    nombre character varying(128) NOT NULL,
    email character varying(255) NOT NULL,
    rol character varying(24) DEFAULT 'docente'::character varying NOT NULL,
    activo boolean DEFAULT true NOT NULL,
    creado_en timestamp with time zone DEFAULT now() NOT NULL,
    actualizado_en timestamp with time zone DEFAULT now() NOT NULL,
    password_hash character varying(128),
    CONSTRAINT ck_teachers_rol CHECK (((rol)::text = ANY ((ARRAY['docente'::character varying, 'investigador'::character varying, 'administrador'::character varying])::text[])))
);


ALTER TABLE public.teachers OWNER TO postgres;

--
-- Name: teachers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.teachers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.teachers_id_seq OWNER TO postgres;

--
-- Name: teachers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.teachers_id_seq OWNED BY public.teachers.id;


--
-- Name: topics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.topics (
    id character varying(64) NOT NULL,
    nombre character varying(128) NOT NULL,
    descripcion text,
    orden integer DEFAULT 0 NOT NULL,
    prerrequisitos json,
    emoji character varying(8),
    activo boolean DEFAULT true NOT NULL,
    unidad integer,
    CONSTRAINT ck_topics_orden CHECK ((orden >= 0)),
    CONSTRAINT ck_topics_unidad CHECK (((unidad IS NULL) OR ((unidad >= 1) AND (unidad <= 4))))
);


ALTER TABLE public.topics OWNER TO postgres;

--
-- Name: agent_interactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_interactions ALTER COLUMN id SET DEFAULT nextval('public.agent_interactions_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: mastery id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mastery ALTER COLUMN id SET DEFAULT nextval('public.mastery_id_seq'::regclass);


--
-- Name: model_predictions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_predictions ALTER COLUMN id SET DEFAULT nextval('public.model_predictions_id_seq'::regclass);


--
-- Name: model_runs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_runs ALTER COLUMN id SET DEFAULT nextval('public.model_runs_id_seq'::regclass);


--
-- Name: pedagogical_decisions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedagogical_decisions ALTER COLUMN id SET DEFAULT nextval('public.pedagogical_decisions_id_seq'::regclass);


--
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions ALTER COLUMN id SET DEFAULT nextval('public.questions_id_seq'::regclass);


--
-- Name: reminders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminders ALTER COLUMN id SET DEFAULT nextval('public.reminders_id_seq'::regclass);


--
-- Name: responses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses ALTER COLUMN id SET DEFAULT nextval('public.responses_id_seq'::regclass);


--
-- Name: spaced_repetition id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spaced_repetition ALTER COLUMN id SET DEFAULT nextval('public.spaced_repetition_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: study_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_sessions ALTER COLUMN id SET DEFAULT nextval('public.study_sessions_id_seq'::regclass);


--
-- Name: sus_responses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sus_responses ALTER COLUMN id SET DEFAULT nextval('public.sus_responses_id_seq'::regclass);


--
-- Name: teacher_student_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_student_assignments ALTER COLUMN id SET DEFAULT nextval('public.teacher_student_assignments_id_seq'::regclass);


--
-- Name: teachers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers ALTER COLUMN id SET DEFAULT nextval('public.teachers_id_seq'::regclass);


--
-- Data for Name: agent_interactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_interactions (id, student_id, session_id, model_run_id, agente, accion, entrada, salida, exitosa, duracion_ms, error, created_at) FROM stdin;
\.


--
-- Data for Name: capsules; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.capsules (id, topic_id, titulo, objetivo, contenido, orden, duracion_min, dificultad, activo, creado_en, imagen_url) FROM stdin;
T1_variables_C1	T1_variables	¿Qué es una variable?	Reconocer una variable como un espacio de memoria con nombre	Una variable es un nombre que apunta a un valor guardado en memoria. Al asignar un nuevo valor, el nombre pasa a apuntar al nuevo dato.	1	4	1	t	2026-08-15 01:07:53.977853-05	\N
T2_tipos_datos_C1	T2_tipos_datos	Entero (int)	Identificar el tipo de dato entero (int).	Un número entero es un tipo de dato que permite almacenar números sin decimales.	1	5	1	t	2026-08-16 19:31:25.016303-05	\N
T7_generalidades_de_la_informatica_C1	T7_generalidades_de_la_informatica	Introducción a la Informática	Comprender qué es la informática, para qué sirve y cuáles son sus principales componentes.	¿Qué es la informática?	1	5	1	t	2026-08-16 19:44:22.09664-05	\N
T3_estructuras_control_C1	T3_estructuras_control	Estructuras de control	Comprender cómo las estructuras de control organizan la ejecución de un programa.	Las <b>estructuras de control</b> permiten controlar el flujo de un programa.	1	3	1	t	2026-08-16 19:57:21.89891-05	\N
T3_estructuras_control_C2	T3_estructuras_control	Estructuras condicionales	Comprender cómo un programa toma decisiones.	Las estructuras condicionales ejecutan acciones según si una condición es verdadera o falsa.	2	3	1	t	2026-08-16 19:58:16.359819-05	\N
T3_estructuras_control_C3	T3_estructuras_control	Estructuras repetitivas	Identificar cómo se repiten instrucciones.	Las estructuras repetitivas permiten ejecutar un bloque de instrucciones varias veces.	3	3	1	t	2026-08-16 19:59:32.303817-05	\N
T5_estructuras_datos_C1	T5_estructuras_datos	Listas	Comprender qué son las listas y su utilidad.	Las <b>listas</b> almacenan varios elementos en un mismo lugar y permiten modificarlos.	1	4	1	t	2026-08-16 22:03:26.791012-05	\N
T5_estructuras_datos_C2	T5_estructuras_datos	Tuplas	Comprender el uso de las tuplas.	Las <b>tuplas</b> almacenan varios elementos que no pueden modificarse después de crearse.	2	4	1	t	2026-08-16 22:04:25.375274-05	\N
T4_funciones_C1	T4_funciones	¿Qué es una función?	Comprender qué es una función y reconocer su utilidad para organizar y reutilizar instrucciones.	Una función es un conjunto de instrucciones agrupadas bajo un nombre que permite realizar una tarea específica.	1	5	2	t	2026-08-17 19:57:09.920348-05	\N
T6_archivos_excepciones_C1	T6_archivos_excepciones	¿Qué son los archivos?	Comprender qué son los archivos y por qué se utilizan para almacenar información.	Un archivo es un espacio donde se puede almacenar información de manera permanente. Los programas pueden utilizar archivos para guardar datos que necesitamos conservar después de cerrar el programa.\nAlgunos archivos comunes son:\n.txt → archivos de texto.\n.csv → datos organizados en filas y columnas.\n.json → información estructurada.	1	5	2	t	2026-08-17 20:04:44.081081-05	\N
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (id, student_id, session_id, ciclo, tipo, payload, ocurrido_en) FROM stdin;
1	1	\N	1	inicio	{"comando": "/start"}	2026-08-14 09:57:58.080513-05
2	1	\N	1	consentimiento	{"acepta": true, "version": "v1.0"}	2026-08-14 10:07:08.526403-05
3	1	\N	1	menu_abierto	\N	2026-08-14 10:32:14.191996-05
4	\N	\N	1	admin_tema_editado	{"topic_id": "T2_tipos_datos", "cambios": {"emoji": ["\\ud83d\\udd22", "\\ud83d\\udd22"], "descripcion": ["...", "..."]}, "actor": 1}	2026-08-14 23:10:48.692065-05
5	\N	\N	1	admin_tema_creado	{"topic_id": "T7_generalidades_de_la_informatica", "actor": 1}	2026-08-14 23:12:31.113322-05
6	\N	\N	1	admin_tema_visibilidad	{"topic_id": "T7_generalidades_de_la_informatica", "activo": false, "actor": 1}	2026-08-14 23:13:02.837093-05
7	\N	\N	1	admin_tema_visibilidad	{"topic_id": "T7_generalidades_de_la_informatica", "activo": true, "actor": 1}	2026-08-14 23:13:14.431216-05
8	\N	\N	1	admin_capsula_creada	{"capsule_id": "T1_variables_C1", "topic_id": "T1_variables", "actor": 1}	2026-08-15 01:07:53.977853-05
9	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T1_variables_C1", "actor": 1}	2026-08-15 09:03:55.093379-05
10	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T1_variables_C1", "actor": 1}	2026-08-15 09:18:37.222203-05
11	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"opciones": [["Verdadero", "Falso"], ["Verdadero", "Falso"]], "correcta": [0, 1]}, "actor": 1}	2026-08-15 09:22:01.208337-05
12	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"opciones": [["Verdadero", "Falso"], ["Verdadero", "Falso"]], "correcta": [1, 0]}, "actor": 1}	2026-08-15 09:22:28.138929-05
13	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 12:06:27.264323-05
14	1	\N	1	retiro_estudio	\N	2026-08-15 12:07:30.924607-05
15	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 12:07:39.419412-05
16	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 12:14:50.343243-05
17	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 12:15:08.358019-05
18	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 12:48:45.100649-05
19	1	1	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-15 12:50:00.084484-05
20	1	1	1	pregunta_respondida	{"question_id": 1, "correcta": true}	2026-08-15 12:50:23.14495-05
21	1	1	1	pregunta_respondida	{"question_id": 2, "correcta": false}	2026-08-15 12:50:51.2644-05
22	1	1	1	capsula_completada	{"aciertos": 1, "total": 2, "nivel_tema": 0.5}	2026-08-15 12:50:51.307973-05
23	1	\N	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-15 12:52:18.315333-05
24	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 17:12:38.897139-05
25	1	3	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-15 17:12:56.375826-05
26	1	3	1	pregunta_respondida	{"question_id": 1, "correcta": true}	2026-08-15 17:13:07.558191-05
27	1	3	1	pregunta_respondida	{"question_id": 2, "correcta": true}	2026-08-15 17:13:24.23137-05
28	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 17:38:56.491074-05
29	1	3	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-15 17:39:09.856211-05
30	1	3	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 3}	2026-08-15 17:39:23.550383-05
31	1	3	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 3}	2026-08-15 17:39:31.567928-05
32	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 17:44:11.960943-05
33	1	3	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-15 17:44:30.560859-05
34	1	3	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 4}	2026-08-15 17:44:37.243191-05
35	1	3	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 4}	2026-08-15 17:44:42.022299-05
38	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-15 17:57:22.438719-05
39	1	4	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-15 17:57:30.18321-05
40	1	4	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 5}	2026-08-15 17:57:34.013313-05
41	1	4	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 5}	2026-08-15 17:57:37.583469-05
42	1	4	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-15 17:57:37.601134-05
43	1	4	1	capsula_completada	{"aciertos": 2, "total": 2, "nivel_tema": 0.9}	2026-08-15 17:57:37.601134-05
44	1	\N	1	recordatorio_enviado	{"capsule_id": "T1_variables_C1", "reminder_id": 1}	2026-08-15 18:26:33.318443-05
45	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-16 09:49:44.421746-05
46	1	5	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-16 09:49:58.003609-05
47	1	5	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 6}	2026-08-16 09:50:02.570222-05
48	1	5	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 6}	2026-08-16 09:50:21.776703-05
49	1	5	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 5, "intervalo_dias": 6, "ease_factor": 2.7}	2026-08-16 09:50:21.793685-05
50	1	5	1	capsula_completada	{"aciertos": 2, "total": 2, "nivel_tema": 0.917}	2026-08-16 09:50:21.793685-05
51	\N	\N	1	admin_tema_editado	{"topic_id": "T2_tipos_datos", "cambios": {"emoji": ["\\ud83d\\udd22", "\\ud83d\\udd22"], "descripcion": ["...", "..."], "prerrequisitos": [["T1_variables"], ["T1_variables"]]}, "actor": 1}	2026-08-16 16:40:51.150022-05
52	\N	\N	1	admin_tema_editado	{"topic_id": "T1_variables", "cambios": {"emoji": ["\\ud83d\\udce6", "\\ud83d\\udce6"], "descripcion": ["...", "..."], "prerrequisitos": [[], []]}, "actor": 1}	2026-08-16 16:41:53.090247-05
53	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T1_variables_C1", "actor": 1}	2026-08-16 19:23:40.627485-05
54	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T1_variables_C1", "actor": 1}	2026-08-16 19:24:24.529461-05
55	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T1_variables_C1", "actor": 1}	2026-08-16 19:25:31.270415-05
56	\N	\N	1	admin_capsula_creada	{"capsule_id": "T2_tipos_datos_C1", "topic_id": "T2_tipos_datos", "actor": 1}	2026-08-16 19:31:25.016303-05
57	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T2_tipos_datos_C1", "actor": 1}	2026-08-16 19:35:39.616683-05
60	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T2_tipos_datos_C1", "actor": 1}	2026-08-16 19:40:14.12694-05
63	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "actor": 1}	2026-08-16 19:48:14.021561-05
69	\N	\N	1	admin_capsula_creada	{"capsule_id": "T3_estructuras_control_C3", "topic_id": "T3_estructuras_control", "actor": 1}	2026-08-16 19:59:32.303817-05
71	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C1", "actor": 1}	2026-08-16 20:57:52.861781-05
75	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C2", "actor": 1}	2026-08-16 21:01:51.046362-05
76	\N	\N	1	admin_capsula_visibilidad	{"capsule_id": "T3_estructuras_control_C3", "activo": false, "actor": 1}	2026-08-16 21:01:58.159355-05
79	\N	\N	1	admin_capsula_visibilidad	{"capsule_id": "T3_estructuras_control_C3", "activo": true, "actor": 1}	2026-08-16 21:59:37.614761-05
83	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T5_estructuras_datos_C1", "actor": 1}	2026-08-16 22:08:19.028377-05
86	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T5_estructuras_datos_C2", "actor": 1}	2026-08-16 22:11:09.724489-05
95	\N	\N	1	admin_pregunta_editada	{"question_id": 14, "cambios": {"opciones": [["Para decorar el programa", "Para controlar el flujo de ejecuci\\u00f3n del programa", "Para eliminar variables", "Para crear archivos"], ["Para decorar el programa", "Para controlar el flujo de ejecuci\\u00f3n del programa", "Para eliminar variables", "Para crear archivos"]]}, "actor": 1}	2026-08-16 22:16:33.103882-05
58	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T2_tipos_datos_C1", "actor": 1}	2026-08-16 19:36:36.363099-05
61	\N	\N	1	admin_capsula_creada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "topic_id": "T7_generalidades_de_la_informatica", "actor": 1}	2026-08-16 19:44:22.09664-05
62	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "actor": 1}	2026-08-16 19:47:31.594167-05
65	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "actor": 1}	2026-08-16 19:51:03.573655-05
66	\N	\N	1	admin_tema_editado	{"topic_id": "T3_estructuras_control", "cambios": {"emoji": ["\\ud83d\\udd00", "\\ud83d\\udd00"], "descripcion": ["...", "..."], "prerrequisitos": [["T2_tipos_datos"], ["T2_tipos_datos"]]}, "actor": 1}	2026-08-16 19:53:58.896474-05
67	\N	\N	1	admin_capsula_creada	{"capsule_id": "T3_estructuras_control_C1", "topic_id": "T3_estructuras_control", "actor": 1}	2026-08-16 19:57:21.89891-05
70	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C1", "actor": 1}	2026-08-16 20:56:26.710336-05
74	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C2", "actor": 1}	2026-08-16 21:00:44.570536-05
78	\N	\N	1	admin_capsula_visibilidad	{"capsule_id": "T3_estructuras_control_C3", "activo": false, "actor": 1}	2026-08-16 21:02:19.118822-05
81	\N	\N	1	admin_capsula_creada	{"capsule_id": "T5_estructuras_datos_C2", "topic_id": "T5_estructuras_datos", "actor": 1}	2026-08-16 22:04:25.375274-05
84	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T5_estructuras_datos_C1", "actor": 1}	2026-08-16 22:09:20.616437-05
88	\N	\N	1	admin_pregunta_editada	{"question_id": 20, "cambios": {"opciones": [["Para organizar varios elementos", "Para apagar un dispositivo", "Para crear una contrase\\u00f1a", "Para borrar informaci\\u00f3n"], ["Para organizar varios elementos", "Para apagar un dispositivo", "Para crear una contrase\\u00f1a", "Para borrar informaci\\u00f3n"]]}, "actor": 1}	2026-08-16 22:12:25.24162-05
90	\N	\N	1	admin_pregunta_editada	{"question_id": 1, "cambios": {"opciones": [["5", "8", "13", "Error"], ["5", "8", "13", "Error"]]}, "actor": 1}	2026-08-16 22:13:48.657593-05
92	\N	\N	1	admin_pregunta_editada	{"question_id": 1, "cambios": {"opciones": [["5", "8", "13", "Error"], ["5", "8", "13", "Error"]]}, "actor": 1}	2026-08-16 22:15:39.046904-05
94	\N	\N	1	admin_pregunta_editada	{"question_id": 5, "cambios": {"opciones": [["20", "45", "25", "0"], ["20", "45", "25", "0"]]}, "actor": 1}	2026-08-16 22:16:02.562416-05
96	\N	\N	1	admin_pregunta_editada	{"question_id": 16, "cambios": {"opciones": [["Verdadero", "Falso"], ["Verdadero", "Falso"]]}, "actor": 1}	2026-08-16 22:18:17.349176-05
97	\N	\N	1	admin_tema_editado	{"topic_id": "T1_variables", "cambios": {"emoji": ["\\ud83d\\udce6", "\\ud83d\\udce6"], "prerrequisitos": [[], []]}, "actor": 1}	2026-08-16 22:29:59.902068-05
59	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T2_tipos_datos_C1", "actor": 1}	2026-08-16 19:37:41.674221-05
64	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "actor": 1}	2026-08-16 19:49:43.116639-05
68	\N	\N	1	admin_capsula_creada	{"capsule_id": "T3_estructuras_control_C2", "topic_id": "T3_estructuras_control", "actor": 1}	2026-08-16 19:58:16.359819-05
72	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C1", "actor": 1}	2026-08-16 20:58:32.057352-05
73	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C2", "actor": 1}	2026-08-16 21:00:08.988144-05
77	\N	\N	1	admin_capsula_visibilidad	{"capsule_id": "T3_estructuras_control_C3", "activo": true, "actor": 1}	2026-08-16 21:02:10.440484-05
80	\N	\N	1	admin_capsula_creada	{"capsule_id": "T5_estructuras_datos_C1", "topic_id": "T5_estructuras_datos", "actor": 1}	2026-08-16 22:03:26.791012-05
82	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T5_estructuras_datos_C1", "actor": 1}	2026-08-16 22:07:35.673636-05
85	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T5_estructuras_datos_C2", "actor": 1}	2026-08-16 22:10:16.637222-05
87	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T5_estructuras_datos_C2", "actor": 1}	2026-08-16 22:12:01.815013-05
89	\N	\N	1	admin_pregunta_editada	{"question_id": 22, "cambios": {"opciones": [["Frutas: manzana, pera y uva", "Solo una fruta", "Una contrase\\u00f1a", "Una imagen"], ["Frutas: manzana, pera y uva", "Solo una fruta", "Una contrase\\u00f1a", "Una imagen"]]}, "actor": 1}	2026-08-16 22:12:37.65137-05
91	\N	\N	1	admin_pregunta_editada	{"question_id": 1, "cambios": {"opciones": [["5", "8", "13", "Error"], ["5", "8", "13", "Error"]]}, "actor": 1}	2026-08-16 22:14:21.294245-05
93	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"opciones": [["Verdadero", "Falso"], ["Verdadero", "Falso"]]}, "actor": 1}	2026-08-16 22:15:50.974681-05
98	\N	\N	1	admin_tema_editado	{"topic_id": "T1_variables", "cambios": {"prerrequisitos": [[], []]}, "actor": 1}	2026-08-16 23:20:47.010433-05
99	\N	\N	1	admin_tema_editado	{"topic_id": "T1_variables", "cambios": {"prerrequisitos": [[], []]}, "actor": 1}	2026-08-16 23:22:03.155846-05
100	\N	\N	1	admin_tema_editado	{"topic_id": "T1_variables", "cambios": {"prerrequisitos": [[], []]}, "actor": 1}	2026-08-16 23:22:24.167615-05
101	\N	\N	1	admin_pregunta_editada	{"question_id": 1, "cambios": {"opciones": [["5", "8", "13", "Error"], ["5", "8", "13", "Error"]], "retroalimentacion": [true, false]}, "actor": 1}	2026-08-16 23:26:18.727896-05
102	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"opciones": [["Verdadero", "Falso"], ["Verdadero", "Falso"]], "retroalimentacion": [true, false]}, "actor": 1}	2026-08-16 23:27:05.486902-05
103	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"enunciado": ["...", "..."], "opciones": [["Verdadero", "Falso"], ["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos."]]}, "actor": 1}	2026-08-16 23:28:28.572525-05
104	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"opciones": [["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos."], ["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos."]]}, "actor": 1}	2026-08-16 23:31:19.273643-05
105	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"tipo": ["verdadero_falso", "opcion_multiple"], "opciones": [["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos."], ["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos."]]}, "actor": 1}	2026-08-17 00:04:14.8543-05
106	\N	\N	1	admin_pregunta_editada	{"question_id": 17, "cambios": {"opciones": [["Para tomar decisiones seg\\u00fan una condici\\u00f3n", "Para guardar archivos", "Para apagar el computador", "Para crear carpetas"], ["Para tomar decisiones seg\\u00fan una condici\\u00f3n", "Para guardar archivos", "Para apagar el computador", "Para crear carpetas"]], "retroalimentacion": [true, false]}, "actor": 1}	2026-08-17 10:03:49.317431-05
107	\N	\N	1	admin_tema_editado	{"topic_id": "T3_estructuras_control", "cambios": {"nombre": ["Estructuras de control", "Estructuras"], "prerrequisitos": [["T2_tipos_datos"], ["T2_tipos_datos"]]}, "actor": 1}	2026-08-17 10:59:44.374408-05
108	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C3", "actor": 1}	2026-08-17 11:00:59.413544-05
109	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C3", "actor": 1}	2026-08-17 11:02:17.471002-05
110	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T3_estructuras_control_C3", "actor": 1}	2026-08-17 11:02:58.183197-05
111	\N	\N	1	admin_tema_visibilidad	{"topic_id": "T4_funciones", "activo": false, "actor": 1}	2026-08-17 11:11:28.412841-05
112	\N	\N	1	admin_tema_visibilidad	{"topic_id": "T6_archivos_excepciones", "activo": false, "actor": 1}	2026-08-17 11:11:29.997062-05
113	\N	\N	1	admin_tema_visibilidad	{"topic_id": "T4_funciones", "activo": true, "actor": 1}	2026-08-17 19:45:46.468226-05
114	\N	\N	1	admin_tema_visibilidad	{"topic_id": "T6_archivos_excepciones", "activo": true, "actor": 1}	2026-08-17 19:45:47.87961-05
115	\N	\N	1	admin_capsula_creada	{"capsule_id": "T4_funciones_C1", "topic_id": "T4_funciones", "actor": 1}	2026-08-17 19:57:09.920348-05
116	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T4_funciones_C1", "actor": 1}	2026-08-17 20:00:17.508314-05
117	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T4_funciones_C1", "actor": 1}	2026-08-17 20:01:19.884849-05
118	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T4_funciones_C1", "actor": 1}	2026-08-17 20:02:18.285509-05
119	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T4_funciones_C1", "actor": 1}	2026-08-17 20:02:53.477451-05
120	\N	\N	1	admin_capsula_creada	{"capsule_id": "T6_archivos_excepciones_C1", "topic_id": "T6_archivos_excepciones", "actor": 1}	2026-08-17 20:04:44.081081-05
121	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T6_archivos_excepciones_C1", "actor": 1}	2026-08-17 20:06:09.01756-05
122	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T6_archivos_excepciones_C1", "actor": 1}	2026-08-17 20:07:12.673981-05
123	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T6_archivos_excepciones_C1", "actor": 1}	2026-08-17 20:07:46.521642-05
124	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T6_archivos_excepciones_C1", "actor": 1}	2026-08-17 20:08:13.721754-05
125	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-18 11:20:19.260325-05
126	1	6	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-18 11:21:11.522787-05
127	1	6	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 7}	2026-08-18 11:21:28.933653-05
128	1	6	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 7}	2026-08-18 11:22:09.083885-05
129	1	6	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 1}	2026-08-18 11:22:26.373299-05
130	1	6	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 1}	2026-08-18 11:22:44.809569-05
131	1	6	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 1}	2026-08-18 11:22:58.01694-05
132	1	6	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 5, "intervalo_dias": 17, "ease_factor": 2.8}	2026-08-18 11:22:58.068942-05
133	1	6	1	capsula_completada	{"aciertos": 5, "total": 5, "nivel_tema": 0.941}	2026-08-18 11:22:58.068942-05
134	1	7	1	capsula_abierta	{"capsule_id": "T2_tipos_datos_C1"}	2026-08-18 11:24:02.319704-05
135	1	7	1	pregunta_respondida	{"question_id": 6, "correcta": true, "intento": 1}	2026-08-18 11:24:13.183027-05
136	1	7	1	pregunta_respondida	{"question_id": 7, "correcta": true, "intento": 1}	2026-08-18 11:24:22.806586-05
137	1	7	1	pregunta_respondida	{"question_id": 8, "correcta": false, "intento": 1}	2026-08-18 11:24:30.571679-05
138	1	7	1	pregunta_respondida	{"question_id": 9, "correcta": true, "intento": 1}	2026-08-18 11:24:48.298461-05
139	1	7	1	repaso_programado	{"capsule_id": "T2_tipos_datos_C1", "calidad": 3, "intervalo_dias": 1, "ease_factor": 2.36}	2026-08-18 11:24:48.334303-05
140	1	7	1	capsula_completada	{"aciertos": 3, "total": 4, "nivel_tema": 0.75}	2026-08-18 11:24:48.334303-05
141	1	8	1	capsula_abierta	{"capsule_id": "T7_generalidades_de_la_informatica_C1"}	2026-08-18 11:25:11.447435-05
142	1	8	1	pregunta_respondida	{"question_id": 10, "correcta": true, "intento": 1}	2026-08-18 11:25:30.102955-05
143	1	8	1	pregunta_respondida	{"question_id": 11, "correcta": true, "intento": 1}	2026-08-18 11:25:44.41773-05
144	1	8	1	pregunta_respondida	{"question_id": 12, "correcta": true, "intento": 1}	2026-08-18 11:28:04.280671-05
145	1	8	1	pregunta_respondida	{"question_id": 13, "correcta": true, "intento": 1}	2026-08-18 11:28:13.158089-05
146	1	8	1	repaso_programado	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 11:28:13.17424-05
147	1	8	1	capsula_completada	{"aciertos": 4, "total": 4, "nivel_tema": 1.0}	2026-08-18 11:28:13.17424-05
148	1	9	1	capsula_abierta	{"capsule_id": "T3_estructuras_control_C1"}	2026-08-18 11:32:00.637748-05
149	1	9	1	pregunta_respondida	{"question_id": 14, "correcta": true, "intento": 1}	2026-08-18 11:32:19.070658-05
150	1	9	1	pregunta_respondida	{"question_id": 15, "correcta": true, "intento": 1}	2026-08-18 11:32:43.43847-05
151	1	9	1	pregunta_respondida	{"question_id": 16, "correcta": false, "intento": 1}	2026-08-18 11:32:49.580025-05
152	1	9	1	repaso_programado	{"capsule_id": "T3_estructuras_control_C1", "calidad": 3, "intervalo_dias": 1, "ease_factor": 2.36}	2026-08-18 11:32:49.616279-05
153	1	9	1	capsula_completada	{"aciertos": 2, "total": 3, "nivel_tema": 0.667}	2026-08-18 11:32:49.616279-05
154	1	10	1	capsula_abierta	{"capsule_id": "T3_estructuras_control_C2"}	2026-08-18 11:33:31.15499-05
155	1	10	1	pregunta_respondida	{"question_id": 17, "correcta": true, "intento": 1}	2026-08-18 11:33:41.428249-05
156	1	10	1	pregunta_respondida	{"question_id": 18, "correcta": true, "intento": 1}	2026-08-18 11:33:48.972415-05
157	1	10	1	pregunta_respondida	{"question_id": 19, "correcta": true, "intento": 1}	2026-08-18 11:33:58.027413-05
158	1	10	1	repaso_programado	{"capsule_id": "T3_estructuras_control_C2", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 11:33:58.040948-05
159	1	10	1	capsula_completada	{"aciertos": 3, "total": 3, "nivel_tema": 0.833}	2026-08-18 11:33:58.040948-05
160	1	11	1	capsula_abierta	{"capsule_id": "T3_estructuras_control_C3"}	2026-08-18 11:34:08.631833-05
161	1	11	1	pregunta_respondida	{"question_id": 26, "correcta": true, "intento": 1}	2026-08-18 11:34:15.800427-05
162	1	11	1	pregunta_respondida	{"question_id": 27, "correcta": true, "intento": 1}	2026-08-18 11:34:22.152611-05
163	1	11	1	pregunta_respondida	{"question_id": 28, "correcta": true, "intento": 1}	2026-08-18 11:34:32.766202-05
164	1	11	1	repaso_programado	{"capsule_id": "T3_estructuras_control_C3", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 11:34:32.800023-05
165	1	11	1	capsula_completada	{"aciertos": 3, "total": 3, "nivel_tema": 0.889}	2026-08-18 11:34:32.800023-05
166	1	12	1	capsula_abierta	{"capsule_id": "T5_estructuras_datos_C1"}	2026-08-18 11:34:52.876572-05
167	1	12	1	pregunta_respondida	{"question_id": 20, "correcta": true, "intento": 1}	2026-08-18 11:35:51.599889-05
168	1	12	1	pregunta_respondida	{"question_id": 21, "correcta": true, "intento": 1}	2026-08-18 11:35:56.462424-05
169	1	12	1	pregunta_respondida	{"question_id": 22, "correcta": true, "intento": 1}	2026-08-18 11:36:02.604499-05
170	1	12	1	repaso_programado	{"capsule_id": "T5_estructuras_datos_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 11:36:02.637834-05
171	1	12	1	capsula_completada	{"aciertos": 3, "total": 3, "nivel_tema": 1.0}	2026-08-18 11:36:02.637834-05
172	1	13	1	capsula_abierta	{"capsule_id": "T5_estructuras_datos_C2"}	2026-08-18 11:36:15.40566-05
173	1	13	1	pregunta_respondida	{"question_id": 23, "correcta": true, "intento": 1}	2026-08-18 11:36:20.624674-05
174	1	13	1	pregunta_respondida	{"question_id": 24, "correcta": false, "intento": 1}	2026-08-18 11:36:36.626207-05
175	1	13	1	pregunta_respondida	{"question_id": 25, "correcta": true, "intento": 1}	2026-08-18 11:36:43.875013-05
176	1	13	1	repaso_programado	{"capsule_id": "T5_estructuras_datos_C2", "calidad": 3, "intervalo_dias": 1, "ease_factor": 2.36}	2026-08-18 11:36:43.886919-05
177	1	13	1	capsula_completada	{"aciertos": 2, "total": 3, "nivel_tema": 0.833}	2026-08-18 11:36:43.886919-05
178	1	14	1	capsula_abierta	{"capsule_id": "T4_funciones_C1"}	2026-08-18 11:36:54.485264-05
179	1	14	1	pregunta_respondida	{"question_id": 29, "correcta": true, "intento": 1}	2026-08-18 11:37:03.743841-05
180	1	14	1	pregunta_respondida	{"question_id": 30, "correcta": true, "intento": 1}	2026-08-18 11:37:11.008398-05
181	1	14	1	pregunta_respondida	{"question_id": 31, "correcta": true, "intento": 1}	2026-08-18 11:37:17.051961-05
182	1	14	1	pregunta_respondida	{"question_id": 32, "correcta": true, "intento": 1}	2026-08-18 11:37:21.318331-05
183	1	14	1	repaso_programado	{"capsule_id": "T4_funciones_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 11:37:21.354787-05
184	1	14	1	capsula_completada	{"aciertos": 4, "total": 4, "nivel_tema": 1.0}	2026-08-18 11:37:21.354787-05
185	1	15	1	capsula_abierta	{"capsule_id": "T6_archivos_excepciones_C1"}	2026-08-18 11:37:53.719928-05
186	1	15	1	pregunta_respondida	{"question_id": 33, "correcta": true, "intento": 1}	2026-08-18 11:38:08.047341-05
187	1	15	1	pregunta_respondida	{"question_id": 34, "correcta": true, "intento": 1}	2026-08-18 11:38:13.780391-05
188	1	15	1	pregunta_respondida	{"question_id": 35, "correcta": true, "intento": 1}	2026-08-18 11:38:20.949996-05
189	1	15	1	pregunta_respondida	{"question_id": 36, "correcta": true, "intento": 1}	2026-08-18 11:38:25.954088-05
190	1	15	1	repaso_programado	{"capsule_id": "T6_archivos_excepciones_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 11:38:25.981976-05
191	1	15	1	capsula_completada	{"aciertos": 4, "total": 4, "nivel_tema": 1.0}	2026-08-18 11:38:25.981976-05
192	1	16	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-18 11:41:55.683307-05
193	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-18 13:42:07.290184-05
194	1	16	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-18 13:42:18.108672-05
195	1	16	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 8}	2026-08-18 13:42:22.818628-05
196	1	16	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 8}	2026-08-18 13:42:31.626944-05
197	1	16	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 2}	2026-08-18 13:42:37.148735-05
198	1	16	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 2}	2026-08-18 13:42:46.776838-05
199	1	16	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 2}	2026-08-18 13:42:51.711859-05
200	1	16	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 5, "intervalo_dias": 49, "ease_factor": 2.9}	2026-08-18 13:42:51.729664-05
201	1	16	1	capsula_completada	{"aciertos": 5, "total": 5, "nivel_tema": 0.955}	2026-08-18 13:42:51.729664-05
202	2	\N	1	inicio	{"comando": "/start", "nuevo": true}	2026-08-18 14:07:23.796099-05
203	2	\N	1	consentimiento	{"acepta": true, "version": "v1.0"}	2026-08-18 14:11:59.460815-05
204	2	17	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-18 14:12:21.581834-05
205	2	17	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 1}	2026-08-18 14:12:28.647836-05
206	2	17	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 1}	2026-08-18 14:12:38.170209-05
207	2	17	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 1}	2026-08-18 14:15:05.916636-05
208	2	17	1	pregunta_respondida	{"question_id": 4, "correcta": false, "intento": 1}	2026-08-18 14:15:14.229616-05
209	2	17	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 1}	2026-08-18 14:15:21.805143-05
210	2	17	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 4, "intervalo_dias": 1, "ease_factor": 2.5}	2026-08-18 14:15:21.842878-05
211	2	17	1	capsula_completada	{"aciertos": 4, "total": 5, "nivel_tema": 0.8}	2026-08-18 14:15:21.842878-05
212	2	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-18 15:40:17.365705-05
213	2	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-18 18:19:49.832575-05
214	2	18	1	capsula_abierta	{"capsule_id": "T3_estructuras_control_C1"}	2026-08-18 18:20:14.756985-05
215	2	18	1	pregunta_respondida	{"question_id": 14, "correcta": true, "intento": 1}	2026-08-18 18:20:25.916604-05
216	2	18	1	pregunta_respondida	{"question_id": 15, "correcta": true, "intento": 1}	2026-08-18 18:20:36.763978-05
217	2	18	1	pregunta_respondida	{"question_id": 16, "correcta": true, "intento": 1}	2026-08-18 18:20:40.952794-05
218	2	18	1	repaso_programado	{"capsule_id": "T3_estructuras_control_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 18:20:40.965865-05
219	2	18	1	capsula_completada	{"aciertos": 3, "total": 3, "nivel_tema": 1.0}	2026-08-18 18:20:40.965865-05
220	2	19	1	capsula_abierta	{"capsule_id": "T4_funciones_C1"}	2026-08-18 18:21:04.435907-05
221	2	19	1	pregunta_respondida	{"question_id": 29, "correcta": true, "intento": 1}	2026-08-18 18:21:14.581228-05
222	2	19	1	pregunta_respondida	{"question_id": 30, "correcta": false, "intento": 1}	2026-08-18 18:21:18.866144-05
223	2	19	1	pregunta_respondida	{"question_id": 31, "correcta": false, "intento": 1}	2026-08-18 18:21:22.234736-05
224	2	19	1	pregunta_respondida	{"question_id": 32, "correcta": true, "intento": 1}	2026-08-18 18:21:26.731995-05
225	2	19	1	repaso_programado	{"capsule_id": "T4_funciones_C1", "calidad": 2, "intervalo_dias": 1, "ease_factor": 2.18}	2026-08-18 18:21:26.743212-05
226	2	19	1	capsula_completada	{"aciertos": 2, "total": 4, "nivel_tema": 0.5}	2026-08-18 18:21:26.743212-05
227	3	\N	1	inicio	{"comando": "/start", "nuevo": true}	2026-08-18 20:40:08.541984-05
228	3	\N	1	consentimiento	{"acepta": true, "version": "v1.0"}	2026-08-18 20:40:30.056641-05
229	3	20	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-18 20:41:03.308945-05
230	3	20	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 1}	2026-08-18 20:41:40.242667-05
231	3	20	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 1}	2026-08-18 20:42:26.701207-05
232	3	20	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 1}	2026-08-18 20:42:40.189377-05
233	3	20	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 1}	2026-08-18 20:43:05.201614-05
234	3	20	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 1}	2026-08-18 20:43:17.5805-05
235	3	20	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-18 20:43:17.618419-05
236	3	20	1	capsula_completada	{"aciertos": 5, "total": 5, "nivel_tema": 1.0}	2026-08-18 20:43:17.618419-05
237	3	21	1	capsula_abierta	{"capsule_id": "T2_tipos_datos_C1"}	2026-08-18 20:43:37.963955-05
238	3	22	1	capsula_abierta	{"capsule_id": "T7_generalidades_de_la_informatica_C1"}	2026-08-18 20:43:59.371132-05
239	3	23	1	capsula_abierta	{"capsule_id": "T4_funciones_C1"}	2026-08-18 20:44:41.052382-05
240	2	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-19 09:48:22.597823-05
241	2	24	1	capsula_abierta	{"capsule_id": "T7_generalidades_de_la_informatica_C1"}	2026-08-19 09:48:34.509048-05
242	2	24	1	pregunta_respondida	{"question_id": 10, "correcta": true, "intento": 1}	2026-08-19 09:49:02.751632-05
243	2	24	1	pregunta_respondida	{"question_id": 11, "correcta": true, "intento": 1}	2026-08-19 09:49:13.867933-05
244	2	24	1	pregunta_respondida	{"question_id": 12, "correcta": true, "intento": 1}	2026-08-19 09:49:32.242451-05
245	2	24	1	pregunta_respondida	{"question_id": 13, "correcta": true, "intento": 1}	2026-08-19 09:49:38.975568-05
246	2	24	1	repaso_programado	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-19 09:49:39.015502-05
247	2	24	1	capsula_completada	{"aciertos": 4, "total": 4, "nivel_tema": 1.0}	2026-08-19 09:49:39.015502-05
248	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-19 09:50:11.153745-05
249	1	25	1	capsula_abierta	{"capsule_id": "T7_generalidades_de_la_informatica_C1"}	2026-08-19 09:50:19.452006-05
250	2	26	1	capsula_abierta	{"capsule_id": "T7_generalidades_de_la_informatica_C1"}	2026-08-19 09:50:33.290979-05
251	1	25	1	pregunta_respondida	{"question_id": 10, "correcta": true, "intento": 2}	2026-08-19 09:50:39.941022-05
252	1	25	1	pregunta_respondida	{"question_id": 11, "correcta": true, "intento": 2}	2026-08-19 09:50:46.601489-05
253	2	26	1	pregunta_respondida	{"question_id": 10, "correcta": true, "intento": 2}	2026-08-19 09:51:07.428679-05
254	2	26	1	pregunta_respondida	{"question_id": 11, "correcta": true, "intento": 2}	2026-08-19 09:51:11.161459-05
255	2	26	1	pregunta_respondida	{"question_id": 12, "correcta": true, "intento": 2}	2026-08-19 09:51:15.258155-05
256	1	25	1	pregunta_respondida	{"question_id": 12, "correcta": true, "intento": 2}	2026-08-19 09:51:18.000348-05
257	1	25	1	pregunta_respondida	{"question_id": 13, "correcta": true, "intento": 2}	2026-08-19 09:51:20.995985-05
258	1	25	1	repaso_programado	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "calidad": 5, "intervalo_dias": 1, "ease_factor": 2.6}	2026-08-19 09:51:21.021123-05
259	1	25	1	capsula_completada	{"aciertos": 4, "total": 4, "nivel_tema": 1.0}	2026-08-19 09:51:21.021123-05
260	2	26	1	pregunta_respondida	{"question_id": 13, "correcta": true, "intento": 2}	2026-08-19 09:51:28.159655-05
261	2	26	1	practica_extra	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "calidad": 5, "programado_para": "2026-08-20T14:49:39.040162+00:00"}	2026-08-19 09:51:28.215848-05
262	2	26	1	capsula_completada	{"aciertos": 4, "total": 4, "nivel_tema": 1.0}	2026-08-19 09:51:28.215848-05
263	3	21	1	sesion_abandonada	{"capsule_id": "T2_tipos_datos_C1", "duracion_seg": 0.0, "con_respuestas": false}	2026-08-19 10:00:48.132103-05
264	3	22	1	sesion_abandonada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "duracion_seg": 0.0, "con_respuestas": false}	2026-08-19 10:00:48.132103-05
265	3	23	1	sesion_abandonada	{"capsule_id": "T4_funciones_C1", "duracion_seg": 0.0, "con_respuestas": false}	2026-08-19 10:00:48.132103-05
266	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-19 10:52:51.972561-05
267	1	27	1	capsula_abierta	{"capsule_id": "T4_funciones_C1"}	2026-08-19 11:28:53.047239-05
268	1	27	1	pregunta_respondida	{"question_id": 29, "correcta": false, "intento": 2}	2026-08-19 11:28:56.423635-05
269	1	27	1	pregunta_respondida	{"question_id": 30, "correcta": false, "intento": 2}	2026-08-19 11:28:58.72012-05
270	1	27	1	pregunta_respondida	{"question_id": 31, "correcta": false, "intento": 2}	2026-08-19 11:29:01.10772-05
271	1	27	1	pregunta_respondida	{"question_id": 32, "correcta": true, "intento": 2}	2026-08-19 11:29:03.456651-05
272	1	27	1	repaso_programado	{"capsule_id": "T4_funciones_C1", "calidad": 1, "intervalo_dias": 1, "ease_factor": 1.96}	2026-08-19 11:29:03.481387-05
273	1	27	1	capsula_completada	{"aciertos": 1, "total": 4, "nivel_tema": 0.625}	2026-08-19 11:29:03.481387-05
274	1	28	1	capsula_abierta	{"capsule_id": "T6_archivos_excepciones_C1"}	2026-08-19 11:31:53.616031-05
275	1	28	1	pregunta_respondida	{"question_id": 33, "correcta": false, "intento": 2}	2026-08-19 11:31:56.722537-05
276	1	28	1	pregunta_respondida	{"question_id": 34, "correcta": false, "intento": 2}	2026-08-19 11:31:59.693834-05
277	1	28	1	pregunta_respondida	{"question_id": 35, "correcta": true, "intento": 2}	2026-08-19 11:32:02.353751-05
278	1	28	1	pregunta_respondida	{"question_id": 36, "correcta": false, "intento": 2}	2026-08-19 11:32:06.039591-05
279	1	28	1	repaso_programado	{"capsule_id": "T6_archivos_excepciones_C1", "calidad": 1, "intervalo_dias": 1, "ease_factor": 1.96}	2026-08-19 11:32:06.059283-05
280	1	28	1	capsula_completada	{"aciertos": 1, "total": 4, "nivel_tema": 0.625}	2026-08-19 11:32:06.059283-05
281	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-22 16:23:13.112247-05
282	1	29	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-22 16:24:18.847401-05
283	1	29	1	pregunta_respondida	{"question_id": 1, "correcta": false, "intento": 9}	2026-08-22 16:24:23.542615-05
284	1	29	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 9}	2026-08-22 16:24:27.327835-05
285	1	29	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 3}	2026-08-22 16:24:31.419119-05
286	1	29	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 3}	2026-08-22 16:24:35.416652-05
287	1	29	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 3}	2026-08-22 16:24:41.147087-05
288	1	29	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 4, "intervalo_dias": 1, "ease_factor": 2.5}	2026-08-22 16:24:41.184332-05
289	1	29	1	capsula_completada	{"aciertos": 4, "total": 5, "nivel_tema": 0.926}	2026-08-22 16:24:41.184332-05
290	1	\N	1	retiro_estudio	\N	2026-08-22 16:28:48.362404-05
291	1	\N	1	reingreso_estudio	\N	2026-08-22 16:44:08.355806-05
292	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-22 16:44:08.355806-05
293	1	\N	1	retiro_estudio	\N	2026-08-22 16:44:17.92437-05
294	1	\N	1	reingreso_estudio	\N	2026-08-22 16:45:02.779003-05
295	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-22 16:45:02.779003-05
296	1	30	1	capsula_abierta	{"capsule_id": "T2_tipos_datos_C1"}	2026-08-22 16:45:10.691165-05
297	1	30	1	pregunta_respondida	{"question_id": 6, "correcta": true, "intento": 2}	2026-08-22 16:45:16.045976-05
298	1	30	1	pregunta_respondida	{"question_id": 7, "correcta": true, "intento": 2}	2026-08-22 16:45:22.792505-05
299	1	30	1	pregunta_respondida	{"question_id": 8, "correcta": false, "intento": 2}	2026-08-22 16:45:27.803978-05
300	1	30	1	pregunta_respondida	{"question_id": 9, "correcta": true, "intento": 2}	2026-08-22 16:45:37.228146-05
301	1	30	1	repaso_programado	{"capsule_id": "T2_tipos_datos_C1", "calidad": 3, "intervalo_dias": 1, "ease_factor": 2.36}	2026-08-22 16:45:37.243456-05
302	1	30	1	capsula_completada	{"aciertos": 3, "total": 4, "nivel_tema": 0.75}	2026-08-22 16:45:37.243456-05
303	1	\N	1	retiro_estudio	\N	2026-08-22 16:45:47.902662-05
304	1	\N	1	reingreso_estudio	\N	2026-08-22 16:47:31.923415-05
305	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-22 16:47:31.923415-05
306	1	31	1	capsula_abierta	{"capsule_id": "T5_estructuras_datos_C2"}	2026-08-22 16:47:39.644217-05
307	1	31	1	pregunta_respondida	{"question_id": 23, "correcta": false, "intento": 2}	2026-08-22 16:47:42.780942-05
308	1	31	1	pregunta_respondida	{"question_id": 24, "correcta": true, "intento": 2}	2026-08-22 16:47:45.873658-05
309	1	31	1	pregunta_respondida	{"question_id": 25, "correcta": false, "intento": 2}	2026-08-22 16:47:49.509878-05
310	1	31	1	repaso_programado	{"capsule_id": "T5_estructuras_datos_C2", "calidad": 1, "intervalo_dias": 1, "ease_factor": 1.96}	2026-08-22 16:47:49.525208-05
311	1	31	1	capsula_completada	{"aciertos": 1, "total": 3, "nivel_tema": 0.667}	2026-08-22 16:47:49.525208-05
312	1	32	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-22 16:48:06.601265-05
313	1	32	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 10}	2026-08-22 16:48:11.673195-05
314	1	32	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 10}	2026-08-22 16:48:14.843034-05
315	1	32	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 4}	2026-08-22 16:48:18.312126-05
316	1	32	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 4}	2026-08-22 16:48:21.367327-05
317	1	32	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 4}	2026-08-22 16:48:26.364845-05
318	1	32	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-22 16:48:26.372624-05
319	1	32	1	capsula_completada	{"aciertos": 5, "total": 5, "nivel_tema": 0.938}	2026-08-22 16:48:26.372624-05
320	1	\N	1	retiro_estudio	\N	2026-08-22 16:49:08.422872-05
321	\N	\N	1	admin_pregunta_creada	{"capsule_id": "T1_variables_C1", "actor": 1}	2026-08-22 23:54:09.567447-05
322	\N	\N	1	admin_pregunta_editada	{"question_id": 37, "cambios": {"tipo": ["verdadero_falso", "opcion_multiple"], "enunciado": ["...", "..."], "opciones": [["Verdadero", "Falso"], ["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"]], "retroalimentacion": [false, true], "imagen_url": [true, true]}, "actor": 1}	2026-08-23 08:52:02.442969-05
323	1	\N	1	reingreso_estudio	\N	2026-08-23 08:55:16.324998-05
324	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 08:55:16.324998-05
325	1	33	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 08:55:26.564081-05
326	1	33	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 11}	2026-08-23 08:55:32.450625-05
327	1	33	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 11}	2026-08-23 08:55:37.024624-05
328	1	33	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 5}	2026-08-23 08:55:40.90042-05
329	1	33	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 5}	2026-08-23 08:55:45.867777-05
330	1	33	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 5}	2026-08-23 08:55:50.430955-05
331	1	33	1	sesion_abandonada	{"capsule_id": "T1_variables_C1", "duracion_seg": 23.9, "con_respuestas": true}	2026-08-23 11:10:07.902368-05
332	1	33	1	pregunta_respondida	{"question_id": 37, "correcta": false, "intento": 1}	2026-08-23 12:45:56.372986-05
333	1	33	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 4, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 12:45:56.424077-05
334	1	33	1	capsula_completada	{"aciertos": 5, "total": 6, "nivel_tema": 0.921}	2026-08-23 12:45:56.424077-05
335	1	\N	1	retiro_estudio	\N	2026-08-23 12:46:24.405986-05
336	1	\N	1	reingreso_estudio	\N	2026-08-23 12:46:40.328959-05
337	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 12:46:40.328959-05
338	1	34	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 12:46:47.79336-05
339	1	34	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 12}	2026-08-23 12:46:52.817682-05
340	1	34	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 12}	2026-08-23 12:46:56.116919-05
341	1	34	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 6}	2026-08-23 12:46:59.496671-05
342	1	34	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 6}	2026-08-23 12:47:02.915905-05
343	1	34	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 6}	2026-08-23 12:47:09.327871-05
344	1	34	1	pregunta_respondida	{"question_id": 37, "correcta": false, "intento": 2}	2026-08-23 12:47:15.676215-05
345	1	34	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 4, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 12:47:15.69904-05
346	1	34	1	capsula_completada	{"aciertos": 5, "total": 6, "nivel_tema": 0.909}	2026-08-23 12:47:15.69904-05
347	1	\N	1	retiro_estudio	\N	2026-08-23 12:47:24.399274-05
348	1	\N	1	reingreso_estudio	\N	2026-08-23 12:48:27.047572-05
349	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 12:48:27.047572-05
350	1	35	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 12:48:38.612256-05
351	1	35	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 13}	2026-08-23 12:48:42.21739-05
352	1	35	1	pregunta_respondida	{"question_id": 2, "correcta": false, "intento": 13}	2026-08-23 12:48:45.379248-05
353	1	35	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 7}	2026-08-23 12:48:48.755713-05
354	1	35	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 7}	2026-08-23 12:48:51.925085-05
355	1	35	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 7}	2026-08-23 12:48:56.089173-05
356	1	35	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 3}	2026-08-23 12:49:19.846193-05
357	1	35	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 4, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 12:49:19.900116-05
358	1	35	1	capsula_completada	{"aciertos": 5, "total": 6, "nivel_tema": 0.9}	2026-08-23 12:49:19.900116-05
359	1	\N	1	retiro_estudio	\N	2026-08-23 12:58:28.625318-05
360	1	\N	1	reingreso_estudio	\N	2026-08-23 13:15:01.413082-05
361	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 13:15:01.413082-05
362	1	36	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 13:15:08.520859-05
363	1	36	1	pregunta_respondida	{"question_id": 1, "correcta": false, "intento": 14}	2026-08-23 13:15:11.398753-05
364	1	36	1	pregunta_respondida	{"question_id": 2, "correcta": false, "intento": 14}	2026-08-23 13:15:14.747753-05
365	1	36	1	pregunta_respondida	{"question_id": 3, "correcta": false, "intento": 8}	2026-08-23 13:15:17.610235-05
366	1	36	1	pregunta_respondida	{"question_id": 4, "correcta": false, "intento": 8}	2026-08-23 13:15:20.122183-05
367	1	36	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 8}	2026-08-23 13:15:23.264539-05
368	1	36	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 4}	2026-08-23 13:15:47.105953-05
369	1	36	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 1, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 13:15:47.141302-05
370	1	36	1	capsula_completada	{"aciertos": 2, "total": 6, "nivel_tema": 0.839}	2026-08-23 13:15:47.141302-05
371	1	37	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 13:21:39.946726-05
372	1	37	1	pregunta_respondida	{"question_id": 1, "correcta": false, "intento": 15}	2026-08-23 13:21:43.244843-05
373	1	37	1	pregunta_respondida	{"question_id": 2, "correcta": false, "intento": 15}	2026-08-23 13:21:45.883193-05
374	1	37	1	pregunta_respondida	{"question_id": 3, "correcta": false, "intento": 9}	2026-08-23 13:21:48.611792-05
375	1	37	1	pregunta_respondida	{"question_id": 4, "correcta": false, "intento": 9}	2026-08-23 13:21:51.108413-05
376	1	37	1	pregunta_respondida	{"question_id": 5, "correcta": false, "intento": 9}	2026-08-23 13:21:53.960218-05
377	1	37	1	pregunta_respondida	{"question_id": 37, "correcta": false, "intento": 5}	2026-08-23 13:26:43.05037-05
378	1	37	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 0, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 13:26:43.067635-05
379	1	37	1	capsula_completada	{"aciertos": 0, "total": 6, "nivel_tema": 0.758}	2026-08-23 13:26:43.067635-05
380	1	38	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 13:28:25.076207-05
381	1	38	1	pregunta_respondida	{"question_id": 1, "correcta": false, "intento": 16}	2026-08-23 13:28:27.821719-05
382	1	38	1	pregunta_respondida	{"question_id": 2, "correcta": false, "intento": 16}	2026-08-23 13:28:30.43983-05
383	1	38	1	pregunta_respondida	{"question_id": 3, "correcta": false, "intento": 10}	2026-08-23 13:28:32.763724-05
384	1	38	1	pregunta_respondida	{"question_id": 4, "correcta": false, "intento": 10}	2026-08-23 13:28:35.86856-05
385	1	38	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 10}	2026-08-23 13:28:38.73127-05
386	1	38	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 6}	2026-08-23 13:28:50.579325-05
387	1	38	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 1, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 13:28:50.591207-05
388	1	38	1	capsula_completada	{"aciertos": 2, "total": 6, "nivel_tema": 0.721}	2026-08-23 13:28:50.591207-05
389	1	\N	1	retiro_estudio	\N	2026-08-23 13:35:42.691584-05
390	\N	\N	1	admin_pregunta_editada	{"question_id": 37, "cambios": {"enunciado": ["...", "..."], "opciones": [["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"], ["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"]], "imagen_url": [true, false]}, "actor": 1}	2026-08-23 13:36:48.382302-05
392	1	\N	1	reingreso_estudio	\N	2026-08-23 13:37:22.910918-05
393	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 13:37:22.910918-05
391	\N	\N	1	admin_pregunta_editada	{"question_id": 37, "cambios": {"opciones": [["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"], ["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"]]}, "actor": 1}	2026-08-23 13:37:17.749706-05
394	1	39	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 13:37:29.597249-05
395	1	39	1	pregunta_respondida	{"question_id": 1, "correcta": false, "intento": 17}	2026-08-23 13:37:32.497111-05
396	1	39	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 17}	2026-08-23 13:37:35.349663-05
397	1	39	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 11}	2026-08-23 13:37:39.18821-05
398	1	39	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 11}	2026-08-23 13:37:42.584064-05
399	1	39	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 11}	2026-08-23 13:37:46.578993-05
400	1	39	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 7}	2026-08-23 13:37:52.237172-05
401	1	39	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 4, "programado_para": "2026-08-23T21:24:41.261421+00:00"}	2026-08-23 13:37:52.251762-05
402	1	39	1	capsula_completada	{"aciertos": 5, "total": 6, "nivel_tema": 0.73}	2026-08-23 13:37:52.251762-05
403	1	\N	1	retiro_estudio	\N	2026-08-23 16:51:15.297119-05
404	1	\N	1	reingreso_estudio	\N	2026-08-23 16:51:18.817563-05
405	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 16:51:18.817563-05
406	1	40	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 16:51:26.093577-05
407	1	40	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 18}	2026-08-23 16:51:29.685284-05
408	1	40	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 18}	2026-08-23 16:51:33.063102-05
409	1	40	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 12}	2026-08-23 16:51:36.640334-05
410	1	40	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 12}	2026-08-23 16:51:40.168452-05
411	1	40	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 12}	2026-08-23 16:51:43.728503-05
412	1	40	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 8}	2026-08-23 16:51:48.697305-05
413	1	40	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 5, "intervalo_dias": 6, "ease_factor": 2.6}	2026-08-23 16:51:48.730976-05
414	1	40	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.75}	2026-08-23 16:51:48.730976-05
415	1	\N	1	retiro_estudio	\N	2026-08-23 16:57:11.172213-05
416	1	\N	1	reingreso_estudio	\N	2026-08-23 16:57:12.842262-05
417	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 16:57:12.842262-05
418	1	\N	1	retiro_estudio	\N	2026-08-23 16:57:19.42997-05
419	\N	\N	1	admin_pregunta_editada	{"question_id": 37, "cambios": {"enunciado": ["...", "..."], "opciones": [["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"], ["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"]], "imagen_url": [false, true]}, "actor": 1}	2026-08-23 16:58:25.18042-05
420	1	\N	1	reingreso_estudio	\N	2026-08-23 16:58:43.0056-05
421	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-23 16:58:43.0056-05
422	1	41	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-23 16:58:49.634225-05
423	1	41	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 19}	2026-08-23 16:58:53.031872-05
424	1	41	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 19}	2026-08-23 16:58:56.772203-05
425	1	41	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 13}	2026-08-23 16:59:00.17881-05
426	1	41	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 13}	2026-08-23 16:59:03.55076-05
427	1	41	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 13}	2026-08-23 16:59:07.389246-05
428	1	41	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 9}	2026-08-23 16:59:14.815014-05
429	1	41	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-23 16:59:14.867165-05
430	1	41	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.767}	2026-08-23 16:59:14.867165-05
431	2	\N	1	recordatorio_enviado	{"capsule_id": "T1_variables_C1", "reminder_id": 5}	2026-08-26 07:27:42.847339-05
432	2	\N	1	recordatorio_enviado	{"capsule_id": "T3_estructuras_control_C1", "reminder_id": 4}	2026-08-26 07:27:42.847339-05
433	2	\N	1	recordatorio_enviado	{"capsule_id": "T4_funciones_C1", "reminder_id": 3}	2026-08-26 07:27:42.847339-05
434	3	\N	1	recordatorio_enviado	{"capsule_id": "T1_variables_C1", "reminder_id": 6}	2026-08-26 07:27:42.847339-05
435	2	\N	1	recordatorio_enviado	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "reminder_id": 2}	2026-08-26 07:27:42.847339-05
436	1	\N	1	recordatorio_enviado	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "reminder_id": 11}	2026-08-26 07:27:42.847339-05
437	1	\N	1	recordatorio_enviado	{"capsule_id": "T4_funciones_C1", "reminder_id": 10}	2026-08-26 07:27:42.847339-05
438	1	\N	1	recordatorio_enviado	{"capsule_id": "T6_archivos_excepciones_C1", "reminder_id": 9}	2026-08-26 07:27:42.847339-05
439	1	\N	1	recordatorio_enviado	{"capsule_id": "T2_tipos_datos_C1", "reminder_id": 8}	2026-08-26 07:27:42.847339-05
440	1	\N	1	recordatorio_enviado	{"capsule_id": "T5_estructuras_datos_C2", "reminder_id": 7}	2026-08-26 07:27:42.847339-05
441	2	42	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 07:35:35.947707-05
442	2	43	1	capsula_abierta	{"capsule_id": "T3_estructuras_control_C1"}	2026-08-26 07:35:40.120064-05
443	2	44	1	capsula_abierta	{"capsule_id": "T4_funciones_C1"}	2026-08-26 07:35:45.570213-05
444	2	45	1	capsula_abierta	{"capsule_id": "T7_generalidades_de_la_informatica_C1"}	2026-08-26 07:35:52.10336-05
445	2	\N	1	retiro_estudio	\N	2026-08-26 07:36:00.702981-05
446	2	\N	1	reingreso_estudio	\N	2026-08-26 07:36:03.073193-05
447	2	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-26 07:36:03.073193-05
448	2	42	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 07:36:12.004112-05
449	2	42	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 2}	2026-08-26 07:36:16.781391-05
450	2	42	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 2}	2026-08-26 07:36:21.065669-05
451	2	42	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 2}	2026-08-26 07:36:34.059006-05
452	2	42	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 2}	2026-08-26 07:36:39.869912-05
453	2	42	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 2}	2026-08-26 07:36:46.463889-05
454	2	42	1	pregunta_respondida	{"question_id": 37, "correcta": false, "intento": 1}	2026-08-26 07:37:01.025688-05
455	2	42	1	repaso_programado	{"capsule_id": "T1_variables_C1", "calidad": 4, "intervalo_dias": 6, "ease_factor": 2.5}	2026-08-26 07:37:01.047843-05
456	2	42	1	capsula_completada	{"aciertos": 5, "total": 6, "nivel_tema": 0.818}	2026-08-26 07:37:01.047843-05
457	1	\N	1	retiro_estudio	\N	2026-08-26 07:37:31.13982-05
458	1	\N	1	reingreso_estudio	\N	2026-08-26 07:37:52.622922-05
459	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-26 07:37:52.622922-05
460	2	46	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 07:38:07.056824-05
461	1	47	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 07:38:09.857976-05
462	1	47	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 20}	2026-08-26 07:38:20.945557-05
463	2	46	1	pregunta_respondida	{"question_id": 1, "correcta": false, "intento": 3}	2026-08-26 07:38:22.846921-05
464	2	46	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 3}	2026-08-26 07:39:31.875636-05
465	1	47	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 20}	2026-08-26 07:39:34.212535-05
466	2	46	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 3}	2026-08-26 07:39:43.833074-05
467	1	47	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 14}	2026-08-26 07:39:45.372445-05
468	2	46	1	pregunta_respondida	{"question_id": 4, "correcta": false, "intento": 3}	2026-08-26 07:39:52.113069-05
469	1	47	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 14}	2026-08-26 07:39:55.064001-05
470	2	46	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 3}	2026-08-26 07:39:59.812061-05
471	1	47	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 14}	2026-08-26 07:40:02.923522-05
472	2	46	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 2}	2026-08-26 07:40:19.107697-05
476	1	47	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-26 07:40:31.893992-05
477	1	47	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.783}	2026-08-26 07:40:31.893992-05
479	1	\N	1	retiro_estudio	\N	2026-08-26 07:41:34.667942-05
488	1	48	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 15}	2026-08-26 07:52:45.474655-05
473	2	46	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 3, "programado_para": "2026-09-01T12:37:01.134704+00:00"}	2026-08-26 07:40:19.130343-05
474	2	46	1	capsula_completada	{"aciertos": 4, "total": 6, "nivel_tema": 0.765}	2026-08-26 07:40:19.130343-05
475	1	47	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 10}	2026-08-26 07:40:31.866658-05
478	2	\N	1	retiro_estudio	\N	2026-08-26 07:41:27.717141-05
480	\N	\N	1	admin_pregunta_editada	{"question_id": 2, "cambios": {"opciones": [["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos."], ["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos.", "Un tipo de lenguaje de programaci\\u00f3n.", "Un proceso que ejecuta instrucciones autom\\u00e1ticamente."]], "retroalimentacion": [false, true]}, "actor": 1}	2026-08-26 07:51:00.092768-05
481	1	\N	1	reingreso_estudio	\N	2026-08-26 07:52:04.93358-05
482	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-26 07:52:04.93358-05
483	1	48	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 07:52:11.926097-05
484	1	48	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 21}	2026-08-26 07:52:18.392291-05
485	1	48	1	pregunta_respondida	{"question_id": 2, "correcta": false, "intento": 21}	2026-08-26 07:52:33.818507-05
486	1	48	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 15}	2026-08-26 07:52:37.529926-05
487	1	48	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 15}	2026-08-26 07:52:40.591353-05
489	1	48	1	pregunta_respondida	{"question_id": 37, "correcta": false, "intento": 11}	2026-08-26 07:52:51.539032-05
490	1	48	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 3, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-26 07:52:51.590188-05
491	1	48	1	capsula_completada	{"aciertos": 4, "total": 6, "nivel_tema": 0.776}	2026-08-26 07:52:51.590188-05
492	1	\N	1	retiro_estudio	\N	2026-08-26 07:53:05.737089-05
493	1	\N	1	reingreso_estudio	\N	2026-08-26 08:10:53.033235-05
494	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-26 08:10:53.033235-05
495	1	49	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 08:11:01.033213-05
496	1	49	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 22}	2026-08-26 08:11:31.82731-05
497	1	49	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 22}	2026-08-26 08:11:45.447225-05
498	1	49	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 16}	2026-08-26 08:11:49.089831-05
499	1	49	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 16}	2026-08-26 08:11:53.472462-05
500	1	49	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 16}	2026-08-26 08:11:58.142271-05
501	1	49	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 12}	2026-08-26 08:12:05.633186-05
502	1	49	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-26 08:12:05.664609-05
503	1	49	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.788}	2026-08-26 08:12:05.664609-05
504	1	\N	1	retiro_estudio	\N	2026-08-26 08:12:14.760279-05
505	2	44	1	sesion_abandonada	{"capsule_id": "T4_funciones_C1", "duracion_seg": 0.0, "con_respuestas": false}	2026-08-26 09:40:19.742074-05
506	2	45	1	sesion_abandonada	{"capsule_id": "T7_generalidades_de_la_informatica_C1", "duracion_seg": 0.0, "con_respuestas": false}	2026-08-26 09:40:19.742074-05
507	2	43	1	sesion_abandonada	{"capsule_id": "T3_estructuras_control_C1", "duracion_seg": 0.0, "con_respuestas": false}	2026-08-26 09:40:19.742074-05
508	1	\N	1	reingreso_estudio	\N	2026-08-26 10:18:28.471944-05
509	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-26 10:18:28.471944-05
510	1	50	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-26 10:18:35.975813-05
511	1	50	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 23}	2026-08-26 10:22:47.18249-05
512	1	50	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 23}	2026-08-26 10:23:06.554917-05
513	1	50	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 17}	2026-08-26 10:23:25.527517-05
514	1	50	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 17}	2026-08-26 10:23:28.89957-05
515	1	50	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 17}	2026-08-26 10:23:33.670162-05
516	1	50	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 13}	2026-08-26 10:23:40.130578-05
517	1	50	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-26 10:23:40.179617-05
518	1	50	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.8}	2026-08-26 10:23:40.179617-05
519	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-26 10:23:48.064472-05
520	1	\N	1	retiro_estudio	\N	2026-08-26 10:23:53.351101-05
521	1	\N	1	reingreso_estudio	\N	2026-08-28 11:36:02.183005-05
522	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-28 11:36:02.183005-05
523	1	51	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-28 11:36:16.828936-05
524	1	51	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 24}	2026-08-28 11:36:22.326892-05
525	1	51	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 24}	2026-08-28 11:36:26.191282-05
526	1	51	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 18}	2026-08-28 11:36:29.677516-05
527	1	51	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 18}	2026-08-28 11:36:32.920703-05
528	1	51	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 18}	2026-08-28 11:36:36.996524-05
529	1	51	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 14}	2026-08-28 11:36:43.909337-05
530	1	51	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-28 11:36:43.931945-05
531	1	51	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.81}	2026-08-28 11:36:43.931945-05
532	1	\N	1	retiro_estudio	\N	2026-08-28 11:37:16.418405-05
533	1	\N	1	reingreso_estudio	\N	2026-08-28 11:43:57.827772-05
534	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-28 11:43:57.827772-05
535	1	52	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-28 11:44:06.101663-05
536	1	52	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 25}	2026-08-28 11:44:09.906391-05
537	1	52	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 25}	2026-08-28 11:44:19.49663-05
538	1	52	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 19}	2026-08-28 11:44:23.824083-05
539	1	52	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 19}	2026-08-28 11:44:26.630896-05
540	1	52	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 19}	2026-08-28 11:44:31.218161-05
541	1	52	1	pregunta_respondida	{"question_id": 37, "correcta": false, "intento": 15}	2026-08-28 11:44:36.166156-05
542	1	52	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 4, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-28 11:44:36.188453-05
543	1	52	1	capsula_completada	{"aciertos": 5, "total": 6, "nivel_tema": 0.811}	2026-08-28 11:44:36.188453-05
544	1	\N	1	retiro_estudio	\N	2026-08-28 11:45:33.21201-05
545	1	\N	1	reingreso_estudio	\N	2026-08-28 18:15:02.068543-05
546	1	\N	1	inicio	{"comando": "/start", "nuevo": false}	2026-08-28 18:15:02.068543-05
547	1	53	1	capsula_abierta	{"capsule_id": "T1_variables_C1"}	2026-08-28 18:15:26.590076-05
548	1	53	1	pregunta_respondida	{"question_id": 1, "correcta": true, "intento": 26}	2026-08-28 18:15:32.021569-05
549	1	53	1	pregunta_respondida	{"question_id": 2, "correcta": true, "intento": 26}	2026-08-28 18:15:35.634379-05
550	1	53	1	pregunta_respondida	{"question_id": 3, "correcta": true, "intento": 20}	2026-08-28 18:15:38.908938-05
551	1	53	1	pregunta_respondida	{"question_id": 4, "correcta": true, "intento": 20}	2026-08-28 18:15:41.962303-05
552	1	53	1	pregunta_respondida	{"question_id": 5, "correcta": true, "intento": 20}	2026-08-28 18:15:46.865479-05
553	1	53	1	pregunta_respondida	{"question_id": 37, "correcta": true, "intento": 16}	2026-08-28 18:15:51.892647-05
554	1	53	1	practica_extra	{"capsule_id": "T1_variables_C1", "calidad": 5, "programado_para": "2026-08-29T21:51:48.780987+00:00"}	2026-08-28 18:15:51.941088-05
555	1	53	1	capsula_completada	{"aciertos": 6, "total": 6, "nivel_tema": 0.82}	2026-08-28 18:15:51.941088-05
556	1	\N	1	retiro_estudio	\N	2026-08-28 18:16:17.075562-05
\.


--
-- Data for Name: mastery; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mastery (id, student_id, topic_id, nivel, fuente, probabilidad_siguiente_correcta, numero_evidencias, modelo_version, ultima_respuesta_en, actualizado_en) FROM stdin;
4	1	T3_estructuras_control	0.8888888888888888	baseline	\N	9	\N	2026-08-18 11:34:32.801949-05	2026-08-18 11:34:32.800023-05
9	2	T3_estructuras_control	1	baseline	\N	3	\N	2026-08-18 18:20:40.967623-05	2026-08-18 18:20:40.965865-05
10	2	T4_funciones	0.5	baseline	\N	4	\N	2026-08-18 18:21:26.743669-05	2026-08-18 18:21:26.743212-05
11	3	T1_variables	1	baseline	\N	5	\N	2026-08-18 20:43:17.615895-05	2026-08-18 20:43:17.618419-05
3	1	T7_generalidades_de_la_informatica	1	baseline	\N	8	\N	2026-08-19 09:51:21.025583-05	2026-08-19 09:51:21.021123-05
12	2	T7_generalidades_de_la_informatica	1	baseline	\N	8	\N	2026-08-19 09:51:28.220816-05	2026-08-19 09:51:28.215848-05
6	1	T4_funciones	0.625	baseline	\N	8	\N	2026-08-19 11:29:03.486275-05	2026-08-19 11:29:03.481387-05
7	1	T6_archivos_excepciones	0.625	baseline	\N	8	\N	2026-08-19 11:32:06.062532-05	2026-08-19 11:32:06.059283-05
2	1	T2_tipos_datos	0.75	baseline	\N	8	\N	2026-08-22 16:45:37.24945-05	2026-08-22 16:45:37.243456-05
5	1	T5_estructuras_datos	0.6666666666666666	baseline	\N	9	\N	2026-08-22 16:47:49.527516-05	2026-08-22 16:47:49.525208-05
8	2	T1_variables	0.7647058823529411	baseline	\N	17	\N	2026-08-26 07:40:19.134673-05	2026-08-26 07:40:19.130343-05
1	1	T1_variables	0.8203125	baseline	\N	128	\N	2026-08-28 18:15:51.946077-05	2026-08-28 18:15:51.941088-05
\.


--
-- Data for Name: model_predictions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.model_predictions (id, student_id, model_run_id, question_id, topic_id, secuencia, probabilidad, resultado_real, error_absoluto, creado_en) FROM stdin;
1	1	5	1	T1_variables	131	0.7439024390243902	t	0.25609756097560976	2026-08-23 16:58:53.031872-05
2	1	5	2	T1_variables	132	0.7469879518072289	t	0.2530120481927711	2026-08-23 16:58:56.772203-05
3	1	5	3	T1_variables	133	0.75	t	0.25	2026-08-23 16:59:00.17881-05
4	1	5	4	T1_variables	134	0.7529411764705882	t	0.24705882352941178	2026-08-23 16:59:03.55076-05
5	1	5	5	T1_variables	135	0.7558139534883721	t	0.2441860465116279	2026-08-23 16:59:07.389246-05
6	1	5	37	T1_variables	136	0.7586206896551724	t	0.24137931034482762	2026-08-23 16:59:14.815014-05
7	2	5	1	T1_variables	21	0.7142857142857143	t	0.2857142857142857	2026-08-26 07:36:16.781391-05
8	2	5	2	T1_variables	22	0.75	t	0.25	2026-08-26 07:36:21.065669-05
9	2	5	3	T1_variables	23	0.7777777777777778	t	0.2222222222222222	2026-08-26 07:36:34.059006-05
10	2	5	4	T1_variables	24	0.8	t	0.19999999999999996	2026-08-26 07:36:39.869912-05
11	2	5	5	T1_variables	25	0.8181818181818182	t	0.18181818181818177	2026-08-26 07:36:46.463889-05
12	2	5	37	T1_variables	26	0.8333333333333334	f	0.8333333333333334	2026-08-26 07:37:01.025688-05
13	1	5	1	T1_variables	137	0.7613636363636364	t	0.23863636363636365	2026-08-26 07:38:20.945557-05
14	2	5	1	T1_variables	27	0.7692307692307693	f	0.7692307692307693	2026-08-26 07:38:22.846921-05
15	2	5	2	T1_variables	28	0.7142857142857143	t	0.2857142857142857	2026-08-26 07:39:31.875636-05
16	1	5	2	T1_variables	138	0.7640449438202247	t	0.2359550561797753	2026-08-26 07:39:34.212535-05
17	2	5	3	T1_variables	29	0.7333333333333333	t	0.2666666666666667	2026-08-26 07:39:43.833074-05
18	1	5	3	T1_variables	139	0.7666666666666667	t	0.23333333333333328	2026-08-26 07:39:45.372445-05
19	2	5	4	T1_variables	30	0.75	f	0.75	2026-08-26 07:39:52.113069-05
20	1	5	4	T1_variables	140	0.7692307692307693	t	0.23076923076923073	2026-08-26 07:39:55.064001-05
21	2	5	5	T1_variables	31	0.7058823529411765	t	0.2941176470588235	2026-08-26 07:39:59.812061-05
22	1	5	5	T1_variables	141	0.7717391304347826	t	0.2282608695652174	2026-08-26 07:40:02.923522-05
23	2	5	37	T1_variables	32	0.7222222222222222	t	0.2777777777777778	2026-08-26 07:40:19.107697-05
24	1	5	37	T1_variables	142	0.7741935483870968	t	0.22580645161290325	2026-08-26 07:40:31.866658-05
25	1	5	1	T1_variables	143	0.776595744680851	t	0.22340425531914898	2026-08-26 07:52:18.392291-05
26	1	5	2	T1_variables	144	0.7789473684210526	f	0.7789473684210526	2026-08-26 07:52:33.818507-05
27	1	5	3	T1_variables	145	0.7708333333333334	t	0.22916666666666663	2026-08-26 07:52:37.529926-05
28	1	5	4	T1_variables	146	0.7731958762886598	t	0.22680412371134018	2026-08-26 07:52:40.591353-05
29	1	5	5	T1_variables	147	0.7755102040816326	t	0.22448979591836737	2026-08-26 07:52:45.474655-05
30	1	5	37	T1_variables	148	0.7777777777777778	f	0.7777777777777778	2026-08-26 07:52:51.539032-05
31	1	5	1	T1_variables	149	0.77	t	0.22999999999999998	2026-08-26 08:11:31.82731-05
32	1	5	2	T1_variables	150	0.7722772277227723	t	0.2277227722772277	2026-08-26 08:11:45.447225-05
33	1	5	3	T1_variables	151	0.7745098039215687	t	0.22549019607843135	2026-08-26 08:11:49.089831-05
34	1	5	4	T1_variables	152	0.7766990291262136	t	0.22330097087378642	2026-08-26 08:11:53.472462-05
35	1	5	5	T1_variables	153	0.7788461538461539	t	0.22115384615384615	2026-08-26 08:11:58.142271-05
36	1	5	37	T1_variables	154	0.780952380952381	t	0.21904761904761905	2026-08-26 08:12:05.633186-05
37	1	5	1	T1_variables	155	0.7830188679245284	t	0.21698113207547165	2026-08-26 10:22:47.18249-05
38	1	5	2	T1_variables	156	0.7850467289719626	t	0.2149532710280374	2026-08-26 10:23:06.554917-05
39	1	5	3	T1_variables	157	0.7870370370370371	t	0.2129629629629629	2026-08-26 10:23:25.527517-05
40	1	5	4	T1_variables	158	0.7889908256880734	t	0.21100917431192656	2026-08-26 10:23:28.89957-05
41	1	5	5	T1_variables	159	0.7909090909090909	t	0.2090909090909091	2026-08-26 10:23:33.670162-05
42	1	5	37	T1_variables	160	0.7927927927927928	t	0.2072072072072072	2026-08-26 10:23:40.130578-05
43	1	5	1	T1_variables	161	0.7946428571428571	t	0.2053571428571429	2026-08-28 11:36:22.326892-05
44	1	5	2	T1_variables	162	0.7964601769911505	t	0.20353982300884954	2026-08-28 11:36:26.191282-05
45	1	5	3	T1_variables	163	0.7982456140350878	t	0.20175438596491224	2026-08-28 11:36:29.677516-05
46	1	5	4	T1_variables	164	0.8	t	0.19999999999999996	2026-08-28 11:36:32.920703-05
47	1	5	5	T1_variables	165	0.8017241379310345	t	0.19827586206896552	2026-08-28 11:36:36.996524-05
48	1	5	37	T1_variables	166	0.8034188034188035	t	0.19658119658119655	2026-08-28 11:36:43.909337-05
49	1	5	1	T1_variables	167	0.8050847457627118	t	0.19491525423728817	2026-08-28 11:44:09.906391-05
50	1	5	2	T1_variables	168	0.8067226890756303	t	0.19327731092436973	2026-08-28 11:44:19.49663-05
51	1	5	3	T1_variables	169	0.8083333333333333	t	0.19166666666666665	2026-08-28 11:44:23.824083-05
52	1	5	4	T1_variables	170	0.8099173553719008	t	0.1900826446280992	2026-08-28 11:44:26.630896-05
53	1	5	5	T1_variables	171	0.8114754098360656	t	0.1885245901639344	2026-08-28 11:44:31.218161-05
54	1	5	37	T1_variables	172	0.8130081300813008	f	0.8130081300813008	2026-08-28 11:44:36.166156-05
55	1	5	1	T1_variables	173	0.8064516129032258	t	0.19354838709677424	2026-08-28 18:15:32.021569-05
56	1	5	2	T1_variables	174	0.808	t	0.19199999999999995	2026-08-28 18:15:35.634379-05
57	1	5	3	T1_variables	175	0.8095238095238095	t	0.19047619047619047	2026-08-28 18:15:38.908938-05
58	1	5	4	T1_variables	176	0.8110236220472441	t	0.1889763779527559	2026-08-28 18:15:41.962303-05
59	1	5	5	T1_variables	177	0.8125	t	0.1875	2026-08-28 18:15:46.865479-05
60	1	5	37	T1_variables	178	0.813953488372093	t	0.18604651162790697	2026-08-28 18:15:51.892647-05
\.


--
-- Data for Name: model_runs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.model_runs (id, ciclo, tipo, nombre_modelo, version, dataset, descripcion, hiperparametros, metricas, auc, f1, accuracy, "precision", recall, reward_medio, fecha_entrenamiento, creado_en, activo) FROM stdin;
1	2	sakt	SAKT	20260816_071216	ASSISTments 2009	Self-Attentive Knowledge Tracing, 1 capa	{"d_modelo": 128, "cabezas": 8, "largo": 100, "dropout": 0.2, "lr": 0.001, "lote": 64, "weight_decay": 1e-05, "epocas_max": 20, "semilla": 42, "n_destrezas": 111}	{"perdida": 0.5610549449920654, "auc": 0.7373583756676665, "accuracy": 0.7177343109859865, "f1": 0.8020392827147215, "precision": 0.733723344027175, "recall": 0.8843829206472996, "n": 47597}	0.7373583756676665	0.8020392827147215	0.7177343109859865	0.733723344027175	0.8843829206472996	\N	2026-08-16 07:12:18.101509-05	2026-08-16 07:12:18.834172-05	t
2	2	sakt	SAKT	20260816_073615	ASSISTments 2009	Self-Attentive Knowledge Tracing, 1 capa	{"d_modelo": 128, "cabezas": 8, "largo": 50, "dropout": 0.2, "lr": 0.001, "lote": 64, "weight_decay": 1e-05, "epocas_max": 20, "semilla": 42, "n_destrezas": 111}	{"perdida": 0.5564643984491174, "auc": 0.7427978315018078, "accuracy": 0.7211447542602593, "f1": 0.8094533863626574, "precision": 0.7250559456748206, "recall": 0.9160870978225545, "n": 47591}	0.7427978315018078	0.8094533863626574	0.7211447542602593	0.7250559456748206	0.9160870978225545	\N	2026-08-16 07:36:17.193619-05	2026-08-16 07:36:17.591408-05	t
3	2	sakt	SAKT	20260816_080853	ASSISTments 2009	Self-Attentive Knowledge Tracing, 1 capa	{"d_modelo": 128, "cabezas": 8, "largo": 200, "dropout": 0.2, "lr": 0.001, "lote": 64, "weight_decay": 1e-05, "epocas_max": 20, "semilla": 42, "n_destrezas": 111}	{"perdida": 0.5622496902942657, "auc": 0.737145181447414, "accuracy": 0.7181184083364848, "f1": 0.8044254624433334, "precision": 0.7294332240668288, "recall": 0.896604386677498, "n": 47598}	0.737145181447414	0.8044254624433334	0.7181184083364848	0.7294332240668288	0.896604386677498	\N	2026-08-16 08:08:56.085617-05	2026-08-16 08:08:56.486543-05	t
4	2	sakt	SAKT	20260816_082530	ASSISTments 2009	Self-Attentive Knowledge Tracing, 1 capa	{"d_modelo": 256, "cabezas": 8, "largo": 50, "dropout": 0.2, "lr": 0.001, "lote": 64, "weight_decay": 1e-05, "epocas_max": 25, "semilla": 42, "n_destrezas": 111}	{"perdida": 0.5551067319783297, "auc": 0.7429771122138926, "accuracy": 0.721964236935555, "f1": 0.8052628480602814, "precision": 0.7358652966808328, "recall": 0.8891127721806955, "n": 47591}	0.7429771122138926	0.8052628480602814	0.721964236935555	0.7358652966808328	0.8891127721806955	\N	2026-08-16 08:25:30.503068-05	2026-08-16 08:25:30.880981-05	t
5	1	baseline	proporcion_aciertos_por_tema	baseline-v1	produccion_local	Linea base del Ciclo 1: proporcion de aciertos del estudiante en el tema, con prior de Laplace (peso 2, prior 0.5). Contraste para el SAKT local del Ciclo 2 sobre las mismas secuencias.	\N	\N	\N	\N	\N	\N	\N	\N	\N	2026-08-23 16:55:05.645343-05	t
\.


--
-- Data for Name: pedagogical_decisions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedagogical_decisions (id, student_id, session_id, model_run_id, ciclo, estrategia, tipo_accion, objetivo_id, estado, accion, recompensa, siguiente_estado, terminada, parametros, created_at) FROM stdin;
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.questions (id, capsule_id, topic_id, tipo, enunciado, opciones, correcta, retroalimentacion, dificultad, activo, imagen_url) FROM stdin;
21	T5_estructuras_datos_C1	T5_estructuras_datos	verdadero_falso	Una lista puede contener varios elementos.	["Verdadero", "Falso"]	0	Las listas permiten almacenar varios elementos juntos.	1	t	\N
17	T3_estructuras_control_C2	T3_estructuras_control	opcion_multiple	¿Para qué sirve una estructura condicional?	["Para tomar decisiones seg\\u00fan una condici\\u00f3n", "Para guardar archivos", "Para apagar el computador", "Para crear carpetas"]	0	\N	1	t	\N
3	T1_variables_C1	T1_variables	opcion_multiple	¿Qué operador se utiliza normalmente para asignar un valor a una variable?	["==", "=", "+", "!="]	1	El operador = asigna un valor a una variable.	1	t	\N
4	T1_variables_C1	T1_variables	verdadero_falso	Una variable puede cambiar su valor durante la ejecución de un programa.	["Verdadero", "Falso"]	0	Una variable puede recibir nuevos valores mediante la reasignación.	1	t	\N
5	T1_variables_C1	T1_variables	opcion_multiple	Si edad = 20 y después edad = 25, ¿Cuál es el valor actual de edad?	["20", "45", "25", "0"]	2	La nueva asignación reemplaza el valor anterior.	1	t	\N
6	T2_tipos_datos_C1	T2_tipos_datos	opcion_multiple	¿Qué tipo de datos almacena int?	["N\\u00fameros enteros", "Textos", "N\\u00fameros decimales", "Verdadero o falso"]	0	int se utiliza para representar números enteros, como 5, 10, -3 y 100.	1	t	\N
7	T2_tipos_datos_C1	T2_tipos_datos	verdadero_falso	El número 25 puede almacenarse en una variable de tipo int.	["Verdadero", "Falso"]	0	25 es un número entero, por lo que puede almacenarse utilizando el tipo int.	1	t	\N
8	T2_tipos_datos_C1	T2_tipos_datos	opcion_multiple	¿Cuál de los siguientes valores es un número entero?	["4.5", "\\"10\\"", "10", "True"]	0	10 es un número entero. 4.5 es decimal, "10" es texto y True es booleano.	1	t	\N
9	T2_tipos_datos_C1	T2_tipos_datos	verdadero_falso	El tipo int se utiliza para almacenar números con decimales, como 3.14.	["Verdadero", "Falso"]	1	int representa números enteros. Los números con decimales normalmente se representan con float	1	t	\N
10	T7_generalidades_de_la_informatica_C1	T7_generalidades_de_la_informatica	opcion_multiple	¿Qué es la informática?	["La ciencia que estudia el procesamiento inform\\u00e1tico", "El estudio exclusivo de los tel\\u00e9fonos celulares.", "Una herramienta para reparar computadores.", "Un programa para navegar por Internet."]	0	La informática estudia cómo se procesa, almacena, transmite y utiliza la información mediante sistemas computacionales.	1	t	\N
11	T7_generalidades_de_la_informatica_C1	T7_generalidades_de_la_informatica	verdadero_falso	La informática permite procesar y almacenar información mediante computadoras.	["Verdadero", "Falso"]	0	Las computadoras utilizan sistemas informáticos para procesar, almacenar y gestionar información.	1	t	\N
12	T7_generalidades_de_la_informatica_C1	T7_generalidades_de_la_informatica	opcion_multiple	¿Cuál es uno de los principales objetivos de la informática?	["Procesar y gestionar informaci\\u00f3n de manera autom\\u00e1tica", "Fabricar \\u00fanicamente componentes electr\\u00f3nicos", "Crear solamente videojuegos", "Reemplazar todos los dispositivos tecnol\\u00f3gicos"]	0	La informática busca facilitar el procesamiento y gestión de información mediante tecnologías computacionales.	1	t	\N
13	T7_generalidades_de_la_informatica_C1	T7_generalidades_de_la_informatica	opcion_multiple	¿Cuál de los siguientes es un ejemplo de aplicación de la informática?	["Un sistema que almacena y consulta informaci\\u00f3n", "Una silla sin componentes tecnol\\u00f3gicos.", "Un cuaderno de papel.", "Un l\\u00e1piz tradicional."]	0	Un sistema informático puede almacenar, procesar y consultar datos para facilitar diferentes actividades.	1	t	\N
14	T3_estructuras_control_C1	T3_estructuras_control	opcion_multiple	¿Para qué sirven las estructuras de control?	["Para decorar el programa", "Para controlar el flujo de ejecuci\\u00f3n del programa", "Para eliminar variables", "Para crear archivos"]	1	Permiten controlar el orden, las decisiones y las repeticiones de un programa.	1	t	\N
15	T3_estructuras_control_C1	T3_estructuras_control	opcion_multiple	¿Qué permiten las estructuras de control?	["Controlar el flujo de un programa", "Crear im\\u00e1genes", "Aumentar la memoria", "Instalar programas"]	0	Controlan cómo y cuándo se ejecutan las instrucciones.	1	t	\N
16	T3_estructuras_control_C1	T3_estructuras_control	verdadero_falso	Las estructuras de control permiten modificar el orden de ejecución de las instrucciones.	["Verdadero", "Falso"]	0	Permiten controlar la secuencia de ejecución.	1	t	\N
18	T3_estructuras_control_C2	T3_estructuras_control	verdadero_falso	La instrucción if se utiliza para evaluar una condición.	["Verdadero", "Falso"]	0	if permite ejecutar código cuando una condición es verdadera.	1	t	\N
19	T3_estructuras_control_C2	T3_estructuras_control	opcion_multiple	¿Qué ocurre si una condición de un if es verdadera?	["Se ejecuta el bloque de instrucciones", "Se elimina el programa", "Se apaga el computador", "No ocurre nada"]	0	El bloque asociado al if se ejecuta cuando la condición es verdadera.	1	t	\N
20	T5_estructuras_datos_C1	T5_estructuras_datos	opcion_multiple	¿Para qué sirve una lista?	["Para organizar varios elementos", "Para apagar un dispositivo", "Para crear una contrase\\u00f1a", "Para borrar informaci\\u00f3n"]	0	Una lista permite organizar varios elementos.	1	t	\N
22	T5_estructuras_datos_C1	T5_estructuras_datos	opcion_multiple	¿Cuál es un ejemplo de una lista?	["Frutas: manzana, pera y uva", "Solo una fruta", "Una contrase\\u00f1a", "Una imagen"]	0	Varias frutas organizadas forman una lista.	1	t	\N
23	T5_estructuras_datos_C2	T5_estructuras_datos	opcion_multiple	¿Qué es una tupla?	["Un programa inform\\u00e1tico", "Un dispositivo electr\\u00f3nico", "Una imagen", "Un conjunto ordenado de elementos"]	3	\N	1	t	\N
24	T5_estructuras_datos_C2	T5_estructuras_datos	verdadero_falso	Una tupla mantiene sus elementos sin cambios después de crearse.	["Verdadero", "Falso"]	0	\N	1	t	\N
25	T5_estructuras_datos_C2	T5_estructuras_datos	opcion_multiple	¿Cuál podría ser un ejemplo de tupla?	["Una carpeta", "Una canci\\u00f3n", "Una fotograf\\u00eda", "Coordenadas de un lugar: (10, 20)"]	3	\N	1	t	\N
1	T1_variables_C1	T1_variables	opcion_multiple	Si x = 5 y luego escribes x = 8, ¿qué contiene x?	["5", "8", "13", "Error"]	1	\N	1	t	\N
26	T3_estructuras_control_C3	T3_estructuras_control	opcion_multiple	¿Para qué sirven las estructuras repetitivas?	["Para repetir instrucciones", "Para borrar variables", "Para crear usuarios", "Para cerrar el programa"]	0	\N	1	t	\N
27	T3_estructuras_control_C3	T3_estructuras_control	verdadero_falso	Un ciclo for puede utilizarse para repetir instrucciones varias veces.	["Verdadero", "Falso"]	0	\N	1	t	\N
28	T3_estructuras_control_C3	T3_estructuras_control	opcion_multiple	¿Cuál de las siguientes es una estructura repetitiva en Python?	["if", "for", "else", "print"]	1	\N	1	t	\N
29	T4_funciones_C1	T4_funciones	opcion_multiple	¿Qué es una función?	["Un dato almacenado en una variable.", "Un conjunto de instrucciones que realiza una tarea", "Un error producido durante la ejecuci\\u00f3n.", "Un tipo de archivo."]	1	\N	1	t	\N
30	T4_funciones_C1	T4_funciones	opcion_multiple	¿Para qué sirven principalmente los parámetros de una función?	["Para eliminar una funci\\u00f3n.", "Para proporcionar datos que la funci\\u00f3n necesita", "Para cerrar el programa.", "Para crear archivos."]	1	\N	1	t	\N
31	T4_funciones_C1	T4_funciones	verdadero_falso	Una función siempre debe devolver un resultado.	["Verdadero", "Falso"]	1	Algunas funciones simplemente realizan una acción, como mostrar un mensaje.	1	t	\N
32	T4_funciones_C1	T4_funciones	verdadero_falso	Las funciones ayudan a evitar la repetición de instrucciones en un programa.	["Verdadero", "Falso"]	0	\N	1	t	\N
33	T6_archivos_excepciones_C1	T6_archivos_excepciones	opcion_multiple	¿Cuál es la principal finalidad de utilizar archivos en un programa?	["Cambiar el lenguaje de programaci\\u00f3n.", "Almacenar informaci\\u00f3n para poder utilizarla despu\\u00e9s", "Eliminar autom\\u00e1ticamente los datos.", "Crear excepciones."]	1	Los archivos permiten almacenar información de forma persistente para utilizarla posteriormente.	1	t	\N
34	T6_archivos_excepciones_C1	T6_archivos_excepciones	opcion_multiple	¿Qué significa leer un archivo?	["Eliminar el archivo.", "Cambiar su nombre.", "Obtener informaci\\u00f3n que est\\u00e1 almacenada en \\u00e9l.", "Crear una excepci\\u00f3n."]	2	Leer un archivo significa acceder a la información que contiene para que el programa pueda utilizarla.	1	t	\N
35	T6_archivos_excepciones_C1	T6_archivos_excepciones	verdadero_falso	Una excepción puede ocurrir cuando un programa intenta abrir un archivo que no existe.	["Verdadero", "Falso"]	0	\N	1	t	\N
36	T6_archivos_excepciones_C1	T6_archivos_excepciones	verdadero_falso	El manejo de excepciones permite controlar situaciones inesperadas durante la ejecución de un programa.	["Verdadero", "Falso"]	0	\N	1	t	\N
37	T1_variables_C1	T1_variables	opcion_multiple	¿ Qué imprime el siguiente código en pantalla ?	["x es mayor que y", "x es menor o igual que y", "5 es mayor que 3", "No imprime nada"]	0	Como x tiene el valor 5 y y tiene el valor 3, la condición x > y es verdadera. Por lo tanto, el programa muestra “x es mayor que y” en pantalla.	1	t	/media/uploads/7c8e5be8ee51a7d84828b1a262df4cbb.png
2	T1_variables_C1	T1_variables	opcion_multiple	¿Qué es una variable en programación?	["Un espacio de memoria que almacena un valor.", "Un dispositivo f\\u00edsico para ingresar datos.", "Un tipo de lenguaje de programaci\\u00f3n.", "Un proceso que ejecuta instrucciones autom\\u00e1ticamente."]	0	Una variable almacena un valor que puede cambiar durante la ejecución del programa.	1	t	\N
\.


--
-- Data for Name: reminders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.reminders (id, student_id, spaced_repetition_id, titulo, mensaje, canal, programado_en, enviado_en, estado, intentos_envio, error_detalle, creado_en) FROM stdin;
2	2	16	Repaso: Introducción a la Informática	🔁 <b>Toca repasar</b>\n\nIntroducción a la Informática\n<i>5 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-20 09:49:39.040162-05	2026-08-26 07:27:45.71586-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
3	2	14	Repaso: ¿Qué es una función?	🔁 <b>Toca repasar</b>\n\n¿Qué es una función?\n<i>5 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-19 18:21:26.745678-05	2026-08-26 07:27:45.014665-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
4	2	13	Repaso: Estructuras de control	🔁 <b>Toca repasar</b>\n\nEstructuras de control\n<i>3 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-19 18:20:40.982501-05	2026-08-26 07:27:44.604685-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
5	2	12	Repaso: ¿Qué es una variable?	🔁 <b>Toca repasar</b>\n\n¿Qué es una variable?\n<i>4 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-19 14:15:21.848694-05	2026-08-26 07:27:44.132947-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
6	3	15	Repaso: ¿Qué es una variable?	🔁 <b>Toca repasar</b>\n\n¿Qué es una variable?\n<i>4 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-19 20:43:17.621792-05	2026-08-26 07:27:45.421211-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
7	1	22	Repaso: Tuplas	🔁 <b>Toca repasar</b>\n\nTuplas\n<i>4 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-23 16:47:49.533472-05	2026-08-26 07:27:47.590072-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
8	1	21	Repaso: Entero (int)	🔁 <b>Toca repasar</b>\n\nEntero (int)\n<i>5 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-23 16:45:37.278311-05	2026-08-26 07:27:47.069765-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
9	1	19	Repaso: ¿Qué son los archivos?	🔁 <b>Toca repasar</b>\n\n¿Qué son los archivos?\n<i>5 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-20 11:32:06.070949-05	2026-08-26 07:27:46.711026-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
10	1	18	Repaso: ¿Qué es una función?	🔁 <b>Toca repasar</b>\n\n¿Qué es una función?\n<i>5 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-20 11:29:03.498842-05	2026-08-26 07:27:46.416383-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
11	1	17	Repaso: Introducción a la Informática	🔁 <b>Toca repasar</b>\n\nIntroducción a la Informática\n<i>5 min</i>\n\nRepasar ahora consolida lo que ya estudiaste.	telegram	2026-08-20 09:51:21.036051-05	2026-08-26 07:27:46.125319-05	enviado	1	\N	2026-08-26 07:27:42.779713-05
\.


--
-- Data for Name: responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.responses (id, student_id, session_id, question_id, topic_id, orden_interaccion, intento, seleccion, es_correcta, tiempo_seg, respondido_en) FROM stdin;
1	1	1	1	T1_variables	1	1	1	t	7.41	2026-08-15 12:50:23.14495-05
3	1	3	1	T1_variables	3	2	1	t	7.47	2026-08-15 17:13:07.558191-05
2	1	1	2	T1_variables	2	1	1	f	6.35	2026-08-15 12:50:51.2644-05
4	1	3	2	T1_variables	4	2	0	t	14.43	2026-08-15 17:13:24.23137-05
5	1	3	1	T1_variables	5	3	1	t	4.08	2026-08-15 17:39:23.550383-05
6	1	3	2	T1_variables	6	3	0	t	3.01	2026-08-15 17:39:31.567928-05
7	1	3	1	T1_variables	7	4	1	t	3.37	2026-08-15 17:44:37.243191-05
8	1	3	2	T1_variables	8	4	0	t	2.38	2026-08-15 17:44:42.022299-05
9	1	4	1	T1_variables	9	5	1	t	2.09	2026-08-15 17:57:34.013313-05
10	1	4	2	T1_variables	10	5	0	t	1.84	2026-08-15 17:57:37.583469-05
11	1	5	1	T1_variables	11	6	1	t	2.57	2026-08-16 09:50:02.570222-05
12	1	5	2	T1_variables	12	6	0	t	11.3	2026-08-16 09:50:21.776703-05
13	1	6	1	T1_variables	13	7	1	t	4.91	2026-08-18 11:21:28.933653-05
14	1	6	2	T1_variables	14	7	0	t	37.27	2026-08-18 11:22:09.083885-05
15	1	6	3	T1_variables	15	1	1	t	12.92	2026-08-18 11:22:26.373299-05
16	1	6	4	T1_variables	16	1	0	t	13.82	2026-08-18 11:22:44.809569-05
17	1	6	5	T1_variables	17	1	2	t	8.38	2026-08-18 11:22:58.01694-05
18	1	7	6	T2_tipos_datos	18	1	0	t	5.25	2026-08-18 11:24:13.183027-05
19	1	7	7	T2_tipos_datos	19	1	0	t	4.4	2026-08-18 11:24:22.806586-05
20	1	7	8	T2_tipos_datos	20	1	2	f	5.74	2026-08-18 11:24:30.571679-05
21	1	7	9	T2_tipos_datos	21	1	1	t	6.34	2026-08-18 11:24:48.298461-05
22	1	8	10	T7_generalidades_de_la_informatica	22	1	0	t	11.97	2026-08-18 11:25:30.102955-05
23	1	8	11	T7_generalidades_de_la_informatica	23	1	0	t	9.22	2026-08-18 11:25:44.41773-05
24	1	8	12	T7_generalidades_de_la_informatica	24	1	0	t	137.9	2026-08-18 11:28:04.280671-05
25	1	8	13	T7_generalidades_de_la_informatica	25	1	0	t	7.13	2026-08-18 11:28:13.158089-05
26	1	9	14	T3_estructuras_control	26	1	1	t	10.02	2026-08-18 11:32:19.070658-05
27	1	9	15	T3_estructuras_control	27	1	0	t	20.07	2026-08-18 11:32:43.43847-05
28	1	9	16	T3_estructuras_control	28	1	1	f	4.29	2026-08-18 11:32:49.580025-05
29	1	10	17	T3_estructuras_control	29	1	0	t	7.39	2026-08-18 11:33:41.428249-05
30	1	10	18	T3_estructuras_control	30	1	0	t	4.81	2026-08-18 11:33:48.972415-05
31	1	10	19	T3_estructuras_control	31	1	0	t	6.79	2026-08-18 11:33:58.027413-05
32	1	11	26	T3_estructuras_control	32	1	0	t	4.8	2026-08-18 11:34:15.800427-05
33	1	11	27	T3_estructuras_control	33	1	0	t	4.5	2026-08-18 11:34:22.152611-05
34	1	11	28	T3_estructuras_control	34	1	1	t	8.97	2026-08-18 11:34:32.766202-05
35	1	12	20	T5_estructuras_datos	35	1	0	t	3.83	2026-08-18 11:35:51.599889-05
36	1	12	21	T5_estructuras_datos	36	1	0	t	2.96	2026-08-18 11:35:56.462424-05
37	1	12	22	T5_estructuras_datos	37	1	0	t	4.74	2026-08-18 11:36:02.604499-05
38	1	13	23	T5_estructuras_datos	38	1	3	t	3.36	2026-08-18 11:36:20.624674-05
39	1	13	24	T5_estructuras_datos	39	1	1	f	14.36	2026-08-18 11:36:36.626207-05
40	1	13	25	T5_estructuras_datos	40	1	3	t	5.16	2026-08-18 11:36:43.875013-05
41	1	14	29	T4_funciones	41	1	1	t	7.67	2026-08-18 11:37:03.743841-05
42	1	14	30	T4_funciones	42	1	1	t	5.21	2026-08-18 11:37:11.008398-05
43	1	14	31	T4_funciones	43	1	1	t	4.3	2026-08-18 11:37:17.051961-05
44	1	14	32	T4_funciones	44	1	0	t	1.69	2026-08-18 11:37:21.318331-05
45	1	15	33	T6_archivos_excepciones	45	1	1	t	8.8	2026-08-18 11:38:08.047341-05
46	1	15	34	T6_archivos_excepciones	46	1	2	t	3.89	2026-08-18 11:38:13.780391-05
47	1	15	35	T6_archivos_excepciones	47	1	0	t	5.52	2026-08-18 11:38:20.949996-05
48	1	15	36	T6_archivos_excepciones	48	1	0	t	3.16	2026-08-18 11:38:25.954088-05
49	1	16	1	T1_variables	49	8	1	t	2.71	2026-08-18 13:42:22.818628-05
50	1	16	2	T1_variables	50	8	0	t	4.58	2026-08-18 13:42:31.626944-05
51	1	16	3	T1_variables	51	2	1	t	3.45	2026-08-18 13:42:37.148735-05
52	1	16	4	T1_variables	52	2	0	t	7.67	2026-08-18 13:42:46.776838-05
53	1	16	5	T1_variables	53	2	2	t	2.97	2026-08-18 13:42:51.711859-05
54	2	17	1	T1_variables	1	1	1	t	4.08	2026-08-18 14:12:28.647836-05
55	2	17	2	T1_variables	2	1	0	t	7.37	2026-08-18 14:12:38.170209-05
56	2	17	3	T1_variables	3	1	1	t	145.68	2026-08-18 14:15:05.916636-05
57	2	17	4	T1_variables	4	1	1	f	5.93	2026-08-18 14:15:14.229616-05
58	2	17	5	T1_variables	5	1	2	t	3.02	2026-08-18 14:15:21.805143-05
59	2	18	14	T3_estructuras_control	6	1	1	t	4.33	2026-08-18 18:20:25.916604-05
60	2	18	15	T3_estructuras_control	7	1	0	t	8.9	2026-08-18 18:20:36.763978-05
61	2	18	16	T3_estructuras_control	8	1	0	t	1.84	2026-08-18 18:20:40.952794-05
62	2	19	29	T4_funciones	9	1	1	t	4.99	2026-08-18 18:21:14.581228-05
63	2	19	30	T4_funciones	10	1	3	f	2.48	2026-08-18 18:21:18.866144-05
64	2	19	31	T4_funciones	11	1	0	f	1.73	2026-08-18 18:21:22.234736-05
65	2	19	32	T4_funciones	12	1	0	t	2.98	2026-08-18 18:21:26.731995-05
66	3	20	1	T1_variables	1	1	1	t	14.52	2026-08-18 20:41:40.242667-05
67	3	20	2	T1_variables	2	1	0	t	43.33	2026-08-18 20:42:26.701207-05
68	3	20	3	T1_variables	3	1	1	t	7.34	2026-08-18 20:42:40.189377-05
69	3	20	4	T1_variables	4	1	0	t	6.37	2026-08-18 20:43:05.201614-05
70	3	20	5	T1_variables	5	1	2	t	7.93	2026-08-18 20:43:17.5805-05
71	2	24	10	T7_generalidades_de_la_informatica	13	1	0	t	25.77	2026-08-19 09:49:02.751632-05
72	2	24	11	T7_generalidades_de_la_informatica	14	1	0	t	8.72	2026-08-19 09:49:13.867933-05
73	2	24	12	T7_generalidades_de_la_informatica	15	1	0	t	16.37	2026-08-19 09:49:32.242451-05
74	2	24	13	T7_generalidades_de_la_informatica	16	1	0	t	4.68	2026-08-19 09:49:38.975568-05
75	1	25	10	T7_generalidades_de_la_informatica	54	2	0	t	18.52	2026-08-19 09:50:39.941022-05
76	1	25	11	T7_generalidades_de_la_informatica	55	2	0	t	4.34	2026-08-19 09:50:46.601489-05
77	2	26	10	T7_generalidades_de_la_informatica	17	2	0	t	32.5	2026-08-19 09:51:07.428679-05
78	2	26	11	T7_generalidades_de_la_informatica	18	2	0	t	1.92	2026-08-19 09:51:11.161459-05
79	2	26	12	T7_generalidades_de_la_informatica	19	2	0	t	2.3	2026-08-19 09:51:15.258155-05
80	1	25	12	T7_generalidades_de_la_informatica	56	2	0	t	29.74	2026-08-19 09:51:18.000348-05
81	1	25	13	T7_generalidades_de_la_informatica	57	2	0	t	1.48	2026-08-19 09:51:20.995985-05
82	2	26	13	T7_generalidades_de_la_informatica	20	2	0	t	1.63	2026-08-19 09:51:28.159655-05
83	1	27	29	T4_funciones	58	2	0	f	1.69	2026-08-19 11:28:56.423635-05
84	1	27	30	T4_funciones	59	2	0	f	1.06	2026-08-19 11:28:58.72012-05
85	1	27	31	T4_funciones	60	2	0	f	1.12	2026-08-19 11:29:01.10772-05
86	1	27	32	T4_funciones	61	2	0	t	1.03	2026-08-19 11:29:03.456651-05
87	1	28	33	T6_archivos_excepciones	62	2	0	f	1.64	2026-08-19 11:31:56.722537-05
88	1	28	34	T6_archivos_excepciones	63	2	1	f	1.63	2026-08-19 11:31:59.693834-05
89	1	28	35	T6_archivos_excepciones	64	2	0	t	1.2	2026-08-19 11:32:02.353751-05
90	1	28	36	T6_archivos_excepciones	65	2	1	f	2.14	2026-08-19 11:32:06.039591-05
91	1	29	1	T1_variables	66	9	0	f	2.77	2026-08-22 16:24:23.542615-05
92	1	29	2	T1_variables	67	9	0	t	1.76	2026-08-22 16:24:27.327835-05
93	1	29	3	T1_variables	68	3	1	t	2.84	2026-08-22 16:24:31.419119-05
94	1	29	4	T1_variables	69	3	0	t	2.54	2026-08-22 16:24:35.416652-05
95	1	29	5	T1_variables	70	3	2	t	3.89	2026-08-22 16:24:41.147087-05
96	1	30	6	T2_tipos_datos	71	2	0	t	3.95	2026-08-22 16:45:16.045976-05
97	1	30	7	T2_tipos_datos	72	2	0	t	4.92	2026-08-22 16:45:22.792505-05
98	1	30	8	T2_tipos_datos	73	2	2	f	3.6	2026-08-22 16:45:27.803978-05
99	1	30	9	T2_tipos_datos	74	2	1	t	7.04	2026-08-22 16:45:37.228146-05
100	1	31	23	T5_estructuras_datos	75	2	0	f	1.9	2026-08-22 16:47:42.780942-05
101	1	31	24	T5_estructuras_datos	76	2	0	t	1.41	2026-08-22 16:47:45.873658-05
102	1	31	25	T5_estructuras_datos	77	2	1	f	1.9	2026-08-22 16:47:49.509878-05
103	1	32	1	T1_variables	78	10	1	t	3.7	2026-08-22 16:48:11.673195-05
104	1	32	2	T1_variables	79	10	0	t	1.78	2026-08-22 16:48:14.843034-05
105	1	32	3	T1_variables	80	4	1	t	2.11	2026-08-22 16:48:18.312126-05
106	1	32	4	T1_variables	81	4	0	t	1.8	2026-08-22 16:48:21.367327-05
107	1	32	5	T1_variables	82	4	2	t	3.1	2026-08-22 16:48:26.364845-05
108	1	33	1	T1_variables	83	11	1	t	3.82	2026-08-23 08:55:32.450625-05
109	1	33	2	T1_variables	84	11	0	t	2.82	2026-08-23 08:55:37.024624-05
110	1	33	3	T1_variables	85	5	1	t	2.37	2026-08-23 08:55:40.90042-05
111	1	33	4	T1_variables	86	5	0	t	3.08	2026-08-23 08:55:45.867777-05
112	1	33	5	T1_variables	87	5	2	t	3.1	2026-08-23 08:55:50.430955-05
113	1	33	37	T1_variables	88	1	3	f	13804.34	2026-08-23 12:45:56.372986-05
114	1	34	1	T1_variables	89	12	1	t	3.83	2026-08-23 12:46:52.817682-05
115	1	34	2	T1_variables	90	12	0	t	1.92	2026-08-23 12:46:56.116919-05
116	1	34	3	T1_variables	91	6	1	t	2.05	2026-08-23 12:46:59.496671-05
117	1	34	4	T1_variables	92	6	0	t	1.74	2026-08-23 12:47:02.915905-05
118	1	34	5	T1_variables	93	6	2	t	5.12	2026-08-23 12:47:09.327871-05
119	1	34	37	T1_variables	94	2	2	f	4.79	2026-08-23 12:47:15.676215-05
120	1	35	1	T1_variables	95	13	1	t	2.02	2026-08-23 12:48:42.21739-05
121	1	35	2	T1_variables	96	13	1	f	1.6	2026-08-23 12:48:45.379248-05
122	1	35	3	T1_variables	97	7	1	t	1.93	2026-08-23 12:48:48.755713-05
123	1	35	4	T1_variables	98	7	0	t	1.73	2026-08-23 12:48:51.925085-05
124	1	35	5	T1_variables	99	7	2	t	2.39	2026-08-23 12:48:56.089173-05
125	1	35	37	T1_variables	100	3	0	t	21.93	2026-08-23 12:49:19.846193-05
126	1	36	1	T1_variables	101	14	2	f	1.3	2026-08-23 13:15:11.398753-05
127	1	36	2	T1_variables	102	14	1	f	1.6	2026-08-23 13:15:14.747753-05
128	1	36	3	T1_variables	103	8	3	f	1.66	2026-08-23 13:15:17.610235-05
129	1	36	4	T1_variables	104	8	1	f	1.22	2026-08-23 13:15:20.122183-05
130	1	36	5	T1_variables	105	8	2	t	1.99	2026-08-23 13:15:23.264539-05
131	1	36	37	T1_variables	106	4	0	t	11.32	2026-08-23 13:15:47.105953-05
132	1	37	1	T1_variables	107	15	2	f	1.18	2026-08-23 13:21:43.244843-05
133	1	37	2	T1_variables	108	15	1	f	1.15	2026-08-23 13:21:45.883193-05
134	1	37	3	T1_variables	109	9	3	f	1.64	2026-08-23 13:21:48.611792-05
135	1	37	4	T1_variables	110	9	1	f	1.43	2026-08-23 13:21:51.108413-05
136	1	37	5	T1_variables	111	9	3	f	1.51	2026-08-23 13:21:53.960218-05
137	1	37	37	T1_variables	112	5	2	f	287.39	2026-08-23 13:26:43.05037-05
138	1	38	1	T1_variables	113	16	2	f	1.14	2026-08-23 13:28:27.821719-05
139	1	38	2	T1_variables	114	16	1	f	1.07	2026-08-23 13:28:30.43983-05
140	1	38	3	T1_variables	115	10	3	f	1.21	2026-08-23 13:28:32.763724-05
141	1	38	4	T1_variables	116	10	1	f	1.64	2026-08-23 13:28:35.86856-05
142	1	38	5	T1_variables	117	10	2	t	1.7	2026-08-23 13:28:38.73127-05
143	1	38	37	T1_variables	118	6	0	t	9.4	2026-08-23 13:28:50.579325-05
144	1	39	1	T1_variables	119	17	2	f	1.49	2026-08-23 13:37:32.497111-05
145	1	39	2	T1_variables	120	17	0	t	1.27	2026-08-23 13:37:35.349663-05
146	1	39	3	T1_variables	121	11	1	t	2.29	2026-08-23 13:37:39.18821-05
147	1	39	4	T1_variables	122	11	0	t	1.76	2026-08-23 13:37:42.584064-05
148	1	39	5	T1_variables	123	11	2	t	2.21	2026-08-23 13:37:46.578993-05
149	1	39	37	T1_variables	124	7	0	t	3.74	2026-08-23 13:37:52.237172-05
150	1	40	1	T1_variables	125	18	1	t	1.85	2026-08-23 16:51:29.685284-05
151	1	40	2	T1_variables	126	18	0	t	1.7	2026-08-23 16:51:33.063102-05
152	1	40	3	T1_variables	127	12	1	t	1.8	2026-08-23 16:51:36.640334-05
153	1	40	4	T1_variables	128	12	0	t	1.72	2026-08-23 16:51:40.168452-05
154	1	40	5	T1_variables	129	12	2	t	1.74	2026-08-23 16:51:43.728503-05
155	1	40	37	T1_variables	130	8	0	t	3.38	2026-08-23 16:51:48.697305-05
156	1	41	1	T1_variables	131	19	1	t	1.78	2026-08-23 16:58:53.031872-05
157	1	41	2	T1_variables	132	19	0	t	1.78	2026-08-23 16:58:56.772203-05
158	1	41	3	T1_variables	133	13	1	t	1.8	2026-08-23 16:59:00.17881-05
159	1	41	4	T1_variables	134	13	0	t	1.62	2026-08-23 16:59:03.55076-05
160	1	41	5	T1_variables	135	13	2	t	1.99	2026-08-23 16:59:07.389246-05
161	1	41	37	T1_variables	136	9	0	t	5.61	2026-08-23 16:59:14.815014-05
162	2	42	1	T1_variables	21	2	1	t	2.3	2026-08-26 07:36:16.781391-05
163	2	42	2	T1_variables	22	2	0	t	2.3	2026-08-26 07:36:21.065669-05
164	2	42	3	T1_variables	23	2	1	t	4.08	2026-08-26 07:36:34.059006-05
165	2	42	4	T1_variables	24	2	0	t	3.83	2026-08-26 07:36:39.869912-05
166	2	42	5	T1_variables	25	2	2	t	3	2026-08-26 07:36:46.463889-05
167	2	42	37	T1_variables	26	1	2	f	12.73	2026-08-26 07:37:01.025688-05
168	1	47	1	T1_variables	137	20	1	t	6.09	2026-08-26 07:38:20.945557-05
169	2	46	1	T1_variables	27	3	2	f	10.21	2026-08-26 07:38:22.846921-05
170	2	46	2	T1_variables	28	3	0	t	64.74	2026-08-26 07:39:31.875636-05
171	1	47	2	T1_variables	138	20	0	t	67.88	2026-08-26 07:39:34.212535-05
172	2	46	3	T1_variables	29	3	1	t	4.42	2026-08-26 07:39:43.833074-05
173	1	47	3	T1_variables	139	14	1	t	8.98	2026-08-26 07:39:45.372445-05
174	2	46	4	T1_variables	30	3	1	f	4.97	2026-08-26 07:39:52.113069-05
175	1	47	4	T1_variables	140	14	0	t	5.94	2026-08-26 07:39:55.064001-05
176	2	46	5	T1_variables	31	3	2	t	5.78	2026-08-26 07:39:59.812061-05
177	1	47	5	T1_variables	141	14	2	t	4.59	2026-08-26 07:40:02.923522-05
178	2	46	37	T1_variables	32	2	0	t	11.09	2026-08-26 07:40:19.107697-05
179	1	47	37	T1_variables	142	10	0	t	26.66	2026-08-26 07:40:31.866658-05
180	1	48	1	T1_variables	143	21	1	t	4.69	2026-08-26 07:52:18.392291-05
181	1	48	2	T1_variables	144	21	3	f	13.85	2026-08-26 07:52:33.818507-05
182	1	48	3	T1_variables	145	15	1	t	1.97	2026-08-26 07:52:37.529926-05
183	1	48	4	T1_variables	146	15	0	t	1.82	2026-08-26 07:52:40.591353-05
184	1	48	5	T1_variables	147	15	2	t	2.88	2026-08-26 07:52:45.474655-05
185	1	48	37	T1_variables	148	11	2	f	3.14	2026-08-26 07:52:51.539032-05
186	1	49	1	T1_variables	149	22	1	t	28.85	2026-08-26 08:11:31.82731-05
187	1	49	2	T1_variables	150	22	0	t	11.95	2026-08-26 08:11:45.447225-05
188	1	49	3	T1_variables	151	16	1	t	2.28	2026-08-26 08:11:49.089831-05
189	1	49	4	T1_variables	152	16	0	t	1.98	2026-08-26 08:11:53.472462-05
190	1	49	5	T1_variables	153	16	2	t	3.14	2026-08-26 08:11:58.142271-05
191	1	49	37	T1_variables	154	12	0	t	5.85	2026-08-26 08:12:05.633186-05
192	1	50	1	T1_variables	155	23	1	t	249.39	2026-08-26 10:22:47.18249-05
193	1	50	2	T1_variables	156	23	0	t	17.01	2026-08-26 10:23:06.554917-05
194	1	50	3	T1_variables	157	17	1	t	17.53	2026-08-26 10:23:25.527517-05
195	1	50	4	T1_variables	158	17	0	t	1.88	2026-08-26 10:23:28.89957-05
196	1	50	5	T1_variables	159	17	2	t	3.13	2026-08-26 10:23:33.670162-05
197	1	50	37	T1_variables	160	13	0	t	5.03	2026-08-26 10:23:40.130578-05
198	1	51	1	T1_variables	161	24	1	t	3.9	2026-08-28 11:36:22.326892-05
199	1	51	2	T1_variables	162	24	0	t	1.9	2026-08-28 11:36:26.191282-05
200	1	51	3	T1_variables	163	18	1	t	1.89	2026-08-28 11:36:29.677516-05
201	1	51	4	T1_variables	164	18	0	t	1.68	2026-08-28 11:36:32.920703-05
202	1	51	5	T1_variables	165	18	2	t	2.74	2026-08-28 11:36:36.996524-05
203	1	51	37	T1_variables	166	14	0	t	5.33	2026-08-28 11:36:43.909337-05
204	1	52	1	T1_variables	167	25	1	t	2.29	2026-08-28 11:44:09.906391-05
205	1	52	2	T1_variables	168	25	0	t	8.2	2026-08-28 11:44:19.49663-05
206	1	52	3	T1_variables	169	19	1	t	2.67	2026-08-28 11:44:23.824083-05
207	1	52	4	T1_variables	170	19	0	t	1.39	2026-08-28 11:44:26.630896-05
208	1	52	5	T1_variables	171	19	2	t	3.14	2026-08-28 11:44:31.218161-05
209	1	52	37	T1_variables	172	15	2	f	3.55	2026-08-28 11:44:36.166156-05
210	1	53	1	T1_variables	173	26	1	t	3.54	2026-08-28 18:15:32.021569-05
211	1	53	2	T1_variables	174	26	0	t	1.85	2026-08-28 18:15:35.634379-05
212	1	53	3	T1_variables	175	20	1	t	1.72	2026-08-28 18:15:38.908938-05
213	1	53	4	T1_variables	176	20	0	t	1.64	2026-08-28 18:15:41.962303-05
214	1	53	5	T1_variables	177	20	2	t	3.56	2026-08-28 18:15:46.865479-05
215	1	53	37	T1_variables	178	16	0	t	3.17	2026-08-28 18:15:51.892647-05
\.


--
-- Data for Name: spaced_repetition; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spaced_repetition (id, student_id, topic_id, capsule_id, calidad, ease_factor, intervalo_dias, repeticiones, errores, dificultad, estabilidad, ajuste_red_neuronal, ultima_revision_en, proxima_revision_en, modelo_version, activo, actualizado_en) FROM stdin;
13	2	T3_estructuras_control	T3_estructuras_control_C1	5	2.6	1	1	0	0.4583	1	1	2026-08-18 18:20:40.982501-05	2026-08-19 18:20:40.982501-05	\N	t	2026-08-18 18:20:40.965865-05
14	2	T4_funciones	T4_funciones_C1	2	2.1799999999999997	1	0	1	0.6333	1	1	2026-08-18 18:21:26.745678-05	2026-08-19 18:21:26.745678-05	\N	t	2026-08-18 18:21:26.743212-05
15	3	T1_variables	T1_variables_C1	5	2.6	1	1	0	0.4583	1	1	2026-08-18 20:43:17.621792-05	2026-08-19 20:43:17.621792-05	\N	t	2026-08-18 20:43:17.618419-05
16	2	T7_generalidades_de_la_informatica	T7_generalidades_de_la_informatica_C1	5	2.6	1	1	0	0.4583	1	1	2026-08-19 09:49:39.040162-05	2026-08-20 09:49:39.040162-05	\N	t	2026-08-19 09:49:39.015502-05
17	1	T7_generalidades_de_la_informatica	T7_generalidades_de_la_informatica_C1	5	2.6	1	1	0	0.4583	1	1	2026-08-19 09:51:21.036051-05	2026-08-20 09:51:21.036051-05	\N	t	2026-08-19 09:51:21.021123-05
18	1	T4_funciones	T4_funciones_C1	1	1.96	1	0	1	0.725	1	1	2026-08-19 11:29:03.498842-05	2026-08-20 11:29:03.498842-05	\N	t	2026-08-19 11:29:03.481387-05
19	1	T6_archivos_excepciones	T6_archivos_excepciones_C1	1	1.96	1	0	1	0.725	1	1	2026-08-19 11:32:06.070949-05	2026-08-20 11:32:06.070949-05	\N	t	2026-08-19 11:32:06.059283-05
21	1	T2_tipos_datos	T2_tipos_datos_C1	3	2.36	1	1	0	0.5583	1	1	2026-08-22 16:45:37.278311-05	2026-08-23 16:45:37.278311-05	\N	t	2026-08-22 16:45:37.243456-05
22	1	T5_estructuras_datos	T5_estructuras_datos_C2	1	1.96	1	0	1	0.725	1	1	2026-08-22 16:47:49.533472-05	2026-08-23 16:47:49.533472-05	\N	t	2026-08-22 16:47:49.525208-05
20	1	T1_variables	T1_variables_C1	5	2.6	6	2	0	0.4583	6	1	2026-08-23 16:51:48.780987-05	2026-08-29 16:51:48.780987-05	\N	t	2026-08-23 16:51:48.730976-05
12	2	T1_variables	T1_variables_C1	4	2.5	6	2	0	0.5	6	1	2026-08-26 07:37:01.134704-05	2026-09-01 07:37:01.134704-05	\N	t	2026-08-26 07:37:01.047843-05
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.students (id, telegram_id, codigo_anonimo, nombre_telegram, consentimiento, fecha_consentimiento, version_consentimiento, grupo, activo, creado_en, actualizado_en) FROM stdin;
3	8816713758	98C47F23DB4D	Margarita	t	2026-08-18 20:40:30.050674-05	v1.0	\N	t	2026-08-18 20:40:08.541984-05	2026-08-18 20:40:30.056641-05
2	6258623781	AFAD98847E5A	styven	t	2026-08-18 14:11:59.463261-05	v1.0	\N	f	2026-08-18 14:07:23.796099-05	2026-08-26 07:41:27.717141-05
1	8923571045	46AC0B36C5DF	Gustavo Padilla	t	2026-08-14 10:07:08.527541-05	v1.0	\N	f	2026-08-14 09:57:58.080513-05	2026-08-28 18:16:17.075562-05
\.


--
-- Data for Name: study_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.study_sessions (id, student_id, capsule_id, ciclo, estrategia, iniciada_en, finalizada_en, duracion_seg, completada) FROM stdin;
1	1	T1_variables_C1	1	fija	2026-08-15 12:50:00.084484-05	2026-08-15 12:50:51.319716-05	51.235232	t
36	1	T1_variables_C1	1	fija	2026-08-23 13:15:08.520859-05	2026-08-23 13:15:47.146857-05	38.625998	t
3	1	T1_variables_C1	1	fija	2026-08-15 17:12:56.375826-05	2026-08-15 17:14:56.375826-05	120	f
4	1	T1_variables_C1	1	fija	2026-08-15 17:57:30.18321-05	2026-08-15 17:57:37.60674-05	7.42353	t
5	1	T1_variables_C1	1	fija	2026-08-16 09:49:58.003609-05	2026-08-16 09:50:21.800288-05	23.796679	t
6	1	T1_variables_C1	1	fija	2026-08-18 11:21:11.522787-05	2026-08-18 11:22:58.073744-05	106.550957	t
7	1	T2_tipos_datos_C1	1	fija	2026-08-18 11:24:02.319704-05	2026-08-18 11:24:48.334731-05	46.015027	t
8	1	T7_generalidades_de_la_informatica_C1	1	fija	2026-08-18 11:25:11.447435-05	2026-08-18 11:28:13.173173-05	181.725738	t
9	1	T3_estructuras_control_C1	1	fija	2026-08-18 11:32:00.637748-05	2026-08-18 11:32:49.618276-05	48.980528	t
10	1	T3_estructuras_control_C2	1	fija	2026-08-18 11:33:31.15499-05	2026-08-18 11:33:58.0385-05	26.88351	t
11	1	T3_estructuras_control_C3	1	fija	2026-08-18 11:34:08.631833-05	2026-08-18 11:34:32.801949-05	24.170116	t
12	1	T5_estructuras_datos_C1	1	fija	2026-08-18 11:34:52.876572-05	2026-08-18 11:36:02.638845-05	69.762273	t
13	1	T5_estructuras_datos_C2	1	fija	2026-08-18 11:36:15.40566-05	2026-08-18 11:36:43.888868-05	28.483208	t
14	1	T4_funciones_C1	1	fija	2026-08-18 11:36:54.485264-05	2026-08-18 11:37:21.355849-05	26.870585	t
15	1	T6_archivos_excepciones_C1	1	fija	2026-08-18 11:37:53.719928-05	2026-08-18 11:38:25.980359-05	32.260431	t
16	1	T1_variables_C1	1	fija	2026-08-18 11:41:55.683307-05	2026-08-18 13:42:51.734817-05	7256.05151	t
17	2	T1_variables_C1	1	fija	2026-08-18 14:12:21.581834-05	2026-08-18 14:15:21.841411-05	180.259577	t
18	2	T3_estructuras_control_C1	1	fija	2026-08-18 18:20:14.756985-05	2026-08-18 18:20:40.967623-05	26.210638	t
19	2	T4_funciones_C1	1	fija	2026-08-18 18:21:04.435907-05	2026-08-18 18:21:26.743669-05	22.307762	t
20	3	T1_variables_C1	1	fija	2026-08-18 20:41:03.308945-05	2026-08-18 20:43:17.615895-05	134.30695	t
24	2	T7_generalidades_de_la_informatica_C1	1	fija	2026-08-19 09:48:34.509048-05	2026-08-19 09:49:39.018928-05	64.50988	t
25	1	T7_generalidades_de_la_informatica_C1	1	fija	2026-08-19 09:50:19.452006-05	2026-08-19 09:51:21.025583-05	61.573577	t
26	2	T7_generalidades_de_la_informatica_C1	1	fija	2026-08-19 09:50:33.290979-05	2026-08-19 09:51:28.220816-05	54.929837	t
21	3	T2_tipos_datos_C1	1	fija	2026-08-18 20:43:37.963955-05	2026-08-18 20:43:37.963955-05	0	f
22	3	T7_generalidades_de_la_informatica_C1	1	fija	2026-08-18 20:43:59.371132-05	2026-08-18 20:43:59.371132-05	0	f
23	3	T4_funciones_C1	1	fija	2026-08-18 20:44:41.052382-05	2026-08-18 20:44:41.052382-05	0	f
27	1	T4_funciones_C1	1	fija	2026-08-19 11:28:53.047239-05	2026-08-19 11:29:03.486275-05	10.439036	t
28	1	T6_archivos_excepciones_C1	1	fija	2026-08-19 11:31:53.616031-05	2026-08-19 11:32:06.062532-05	12.446501	t
29	1	T1_variables_C1	1	fija	2026-08-22 16:24:18.847401-05	2026-08-22 16:24:41.187947-05	22.340546	t
30	1	T2_tipos_datos_C1	1	fija	2026-08-22 16:45:10.691165-05	2026-08-22 16:45:37.24945-05	26.558285	t
31	1	T5_estructuras_datos_C2	1	fija	2026-08-22 16:47:39.644217-05	2026-08-22 16:47:49.527516-05	9.883299	t
32	1	T1_variables_C1	1	fija	2026-08-22 16:48:06.601265-05	2026-08-22 16:48:26.374804-05	19.773539	t
37	1	T1_variables_C1	1	fija	2026-08-23 13:21:39.946726-05	2026-08-23 13:26:43.069952-05	303.123226	t
33	1	T1_variables_C1	1	fija	2026-08-23 08:55:26.564081-05	2026-08-23 12:45:56.442475-05	13829.878394	t
34	1	T1_variables_C1	1	fija	2026-08-23 12:46:47.79336-05	2026-08-23 12:47:15.703106-05	27.909746	t
35	1	T1_variables_C1	1	fija	2026-08-23 12:48:38.612256-05	2026-08-23 12:49:19.909547-05	41.297291	t
38	1	T1_variables_C1	1	fija	2026-08-23 13:28:25.076207-05	2026-08-23 13:28:50.59235-05	25.516143	t
39	1	T1_variables_C1	1	fija	2026-08-23 13:37:29.597249-05	2026-08-23 13:37:52.253025-05	22.655776	t
40	1	T1_variables_C1	1	fija	2026-08-23 16:51:26.093577-05	2026-08-23 16:51:48.744164-05	22.650587	t
41	1	T1_variables_C1	1	fija	2026-08-23 16:58:49.634225-05	2026-08-23 16:59:14.877883-05	25.243658	t
42	2	T1_variables_C1	1	fija	2026-08-26 07:35:35.947707-05	2026-08-26 07:37:01.050788-05	85.103081	t
46	2	T1_variables_C1	1	fija	2026-08-26 07:38:07.056824-05	2026-08-26 07:40:19.134673-05	132.077849	t
47	1	T1_variables_C1	1	fija	2026-08-26 07:38:09.857976-05	2026-08-26 07:40:31.897767-05	142.039791	t
48	1	T1_variables_C1	1	fija	2026-08-26 07:52:11.926097-05	2026-08-26 07:52:51.593461-05	39.667364	t
49	1	T1_variables_C1	1	fija	2026-08-26 08:11:01.033213-05	2026-08-26 08:12:05.67311-05	64.639897	t
43	2	T3_estructuras_control_C1	1	fija	2026-08-26 07:35:40.120064-05	2026-08-26 07:35:40.120064-05	0	f
44	2	T4_funciones_C1	1	fija	2026-08-26 07:35:45.570213-05	2026-08-26 07:35:45.570213-05	0	f
45	2	T7_generalidades_de_la_informatica_C1	1	fija	2026-08-26 07:35:52.10336-05	2026-08-26 07:35:52.10336-05	0	f
50	1	T1_variables_C1	1	fija	2026-08-26 10:18:35.975813-05	2026-08-26 10:23:40.187145-05	304.211332	t
51	1	T1_variables_C1	1	fija	2026-08-28 11:36:16.828936-05	2026-08-28 11:36:43.937481-05	27.108545	t
52	1	T1_variables_C1	1	fija	2026-08-28 11:44:06.101663-05	2026-08-28 11:44:36.194385-05	30.092722	t
53	1	T1_variables_C1	1	fija	2026-08-28 18:15:26.590076-05	2026-08-28 18:15:51.946077-05	25.356001	t
\.


--
-- Data for Name: sus_responses; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sus_responses (id, student_id, fase, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, score, comentario, enviado_en) FROM stdin;
\.


--
-- Data for Name: teacher_student_assignments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teacher_student_assignments (id, teacher_id, student_id, creado_en) FROM stdin;
\.


--
-- Data for Name: teachers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.teachers (id, nombre, email, rol, activo, creado_en, actualizado_en, password_hash) FROM stdin;
1	Styven	styvenpadilla@gmail.com	docente	t	2026-08-14 13:10:33.272665-05	2026-08-14 13:10:33.272665-05	$2b$12$rmg8ocXmaci6YeDG2/ci2uNTcETq96vv1ABFfJSFa21cFcPvYghkC
\.


--
-- Data for Name: topics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.topics (id, nombre, descripcion, orden, prerrequisitos, emoji, activo, unidad) FROM stdin;
T5_estructuras_datos	Estructuras de datos	\N	5	["T4_funciones"]	📚	t	3
T7_generalidades_de_la_informatica	Generalidades de la Informática	La informática procesa, almacena y transmite información mediante tecnologías digitales.	7	[]	📘	t	1
T2_tipos_datos	Tipos de datos	Clasificación que define qué valores puede almacenar una variable.	2	["T1_variables"]	🔢	t	1
T1_variables	Variables y asignación	Espacios que almacenan datos y reciben valores durante la ejecución.	1	[]	📦	t	1
T3_estructuras_control	Estructuras	Las estructuras de control permiten decidir y repetir acciones según condiciones específicas.	3	["T2_tipos_datos"]	🔀	t	2
T4_funciones	Funciones	\N	4	["T3_estructuras_control"]	⚙️	t	4
T6_archivos_excepciones	Archivos y excepciones	\N	6	["T4_funciones"]	📄	t	4
\.


--
-- Name: agent_interactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_interactions_id_seq', 1, false);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 556, true);


--
-- Name: mastery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mastery_id_seq', 12, true);


--
-- Name: model_predictions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.model_predictions_id_seq', 60, true);


--
-- Name: model_runs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.model_runs_id_seq', 5, true);


--
-- Name: pedagogical_decisions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pedagogical_decisions_id_seq', 1, false);


--
-- Name: questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.questions_id_seq', 37, true);


--
-- Name: reminders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.reminders_id_seq', 11, true);


--
-- Name: responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.responses_id_seq', 215, true);


--
-- Name: spaced_repetition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.spaced_repetition_id_seq', 22, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.students_id_seq', 3, true);


--
-- Name: study_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.study_sessions_id_seq', 53, true);


--
-- Name: sus_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sus_responses_id_seq', 1, false);


--
-- Name: teacher_student_assignments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teacher_student_assignments_id_seq', 1, false);


--
-- Name: teachers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.teachers_id_seq', 1, true);


--
-- Name: agent_interactions agent_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_pkey PRIMARY KEY (id);


--
-- Name: capsules capsules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capsules
    ADD CONSTRAINT capsules_pkey PRIMARY KEY (id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: mastery mastery_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mastery
    ADD CONSTRAINT mastery_pkey PRIMARY KEY (id);


--
-- Name: model_predictions model_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_predictions
    ADD CONSTRAINT model_predictions_pkey PRIMARY KEY (id);


--
-- Name: model_runs model_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_runs
    ADD CONSTRAINT model_runs_pkey PRIMARY KEY (id);


--
-- Name: pedagogical_decisions pedagogical_decisions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedagogical_decisions
    ADD CONSTRAINT pedagogical_decisions_pkey PRIMARY KEY (id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- Name: reminders reminders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminders
    ADD CONSTRAINT reminders_pkey PRIMARY KEY (id);


--
-- Name: responses responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_pkey PRIMARY KEY (id);


--
-- Name: spaced_repetition spaced_repetition_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spaced_repetition
    ADD CONSTRAINT spaced_repetition_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: study_sessions study_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_pkey PRIMARY KEY (id);


--
-- Name: sus_responses sus_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sus_responses
    ADD CONSTRAINT sus_responses_pkey PRIMARY KEY (id);


--
-- Name: teacher_student_assignments teacher_student_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_student_assignments
    ADD CONSTRAINT teacher_student_assignments_pkey PRIMARY KEY (id);


--
-- Name: teachers teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (id);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (id);


--
-- Name: capsules uq_capsules_id_topic; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capsules
    ADD CONSTRAINT uq_capsules_id_topic UNIQUE (id, topic_id);


--
-- Name: capsules uq_capsules_topic_orden; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capsules
    ADD CONSTRAINT uq_capsules_topic_orden UNIQUE (topic_id, orden);


--
-- Name: mastery uq_mastery_student_topic; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mastery
    ADD CONSTRAINT uq_mastery_student_topic UNIQUE (student_id, topic_id);


--
-- Name: responses uq_response_student_sequence; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT uq_response_student_sequence UNIQUE (student_id, orden_interaccion);


--
-- Name: spaced_repetition uq_spaced_student_capsule; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spaced_repetition
    ADD CONSTRAINT uq_spaced_student_capsule UNIQUE (student_id, capsule_id);


--
-- Name: teacher_student_assignments uq_teacher_student_assignment; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_student_assignments
    ADD CONSTRAINT uq_teacher_student_assignment UNIQUE (teacher_id, student_id);


--
-- Name: ix_agent_interactions_agent_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_agent_time ON public.agent_interactions USING btree (agente, created_at);


--
-- Name: ix_agent_interactions_agente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_agente ON public.agent_interactions USING btree (agente);


--
-- Name: ix_agent_interactions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_created_at ON public.agent_interactions USING btree (created_at);


--
-- Name: ix_agent_interactions_model_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_model_run_id ON public.agent_interactions USING btree (model_run_id);


--
-- Name: ix_agent_interactions_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_session_id ON public.agent_interactions USING btree (session_id);


--
-- Name: ix_agent_interactions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_student_id ON public.agent_interactions USING btree (student_id);


--
-- Name: ix_agent_interactions_student_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_agent_interactions_student_time ON public.agent_interactions USING btree (student_id, created_at);


--
-- Name: ix_capsules_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_capsules_topic_id ON public.capsules USING btree (topic_id);


--
-- Name: ix_capsules_topic_orden; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_capsules_topic_orden ON public.capsules USING btree (topic_id, orden);


--
-- Name: ix_events_ocurrido_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_ocurrido_en ON public.events USING btree (ocurrido_en);


--
-- Name: ix_events_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_session_id ON public.events USING btree (session_id);


--
-- Name: ix_events_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_student_id ON public.events USING btree (student_id);


--
-- Name: ix_events_student_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_student_time ON public.events USING btree (student_id, ocurrido_en);


--
-- Name: ix_events_tipo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_tipo ON public.events USING btree (tipo);


--
-- Name: ix_events_type_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_events_type_time ON public.events USING btree (tipo, ocurrido_en);


--
-- Name: ix_mastery_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mastery_student_id ON public.mastery USING btree (student_id);


--
-- Name: ix_mastery_student_topic; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mastery_student_topic ON public.mastery USING btree (student_id, topic_id);


--
-- Name: ix_mastery_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mastery_topic_id ON public.mastery USING btree (topic_id);


--
-- Name: ix_mastery_topic_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_mastery_topic_level ON public.mastery USING btree (topic_id, nivel);


--
-- Name: ix_model_predictions_creado_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_model_predictions_creado_en ON public.model_predictions USING btree (creado_en);


--
-- Name: ix_model_predictions_model_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_model_predictions_model_run_id ON public.model_predictions USING btree (model_run_id);


--
-- Name: ix_model_predictions_question_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_model_predictions_question_id ON public.model_predictions USING btree (question_id);


--
-- Name: ix_model_predictions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_model_predictions_student_id ON public.model_predictions USING btree (student_id);


--
-- Name: ix_model_predictions_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_model_predictions_topic_id ON public.model_predictions USING btree (topic_id);


--
-- Name: ix_model_runs_type_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_model_runs_type_created ON public.model_runs USING btree (tipo, creado_en);


--
-- Name: ix_pedagogical_decisions_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedagogical_decisions_created_at ON public.pedagogical_decisions USING btree (created_at);


--
-- Name: ix_pedagogical_decisions_model_run_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedagogical_decisions_model_run_id ON public.pedagogical_decisions USING btree (model_run_id);


--
-- Name: ix_pedagogical_decisions_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedagogical_decisions_session_id ON public.pedagogical_decisions USING btree (session_id);


--
-- Name: ix_pedagogical_decisions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedagogical_decisions_student_id ON public.pedagogical_decisions USING btree (student_id);


--
-- Name: ix_pedagogical_strategy; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedagogical_strategy ON public.pedagogical_decisions USING btree (estrategia);


--
-- Name: ix_pedagogical_student_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_pedagogical_student_time ON public.pedagogical_decisions USING btree (student_id, created_at);


--
-- Name: ix_predictions_model; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_predictions_model ON public.model_predictions USING btree (model_run_id);


--
-- Name: ix_predictions_student_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_predictions_student_time ON public.model_predictions USING btree (student_id, creado_en);


--
-- Name: ix_questions_capsule; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_questions_capsule ON public.questions USING btree (capsule_id);


--
-- Name: ix_questions_capsule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_questions_capsule_id ON public.questions USING btree (capsule_id);


--
-- Name: ix_questions_topic_difficulty; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_questions_topic_difficulty ON public.questions USING btree (topic_id, dificultad);


--
-- Name: ix_questions_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_questions_topic_id ON public.questions USING btree (topic_id);


--
-- Name: ix_reminders_programado_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reminders_programado_en ON public.reminders USING btree (programado_en);


--
-- Name: ix_reminders_spaced_repetition_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reminders_spaced_repetition_id ON public.reminders USING btree (spaced_repetition_id);


--
-- Name: ix_reminders_status_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reminders_status_due ON public.reminders USING btree (estado, programado_en);


--
-- Name: ix_reminders_student_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reminders_student_due ON public.reminders USING btree (student_id, programado_en);


--
-- Name: ix_reminders_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reminders_student_id ON public.reminders USING btree (student_id);


--
-- Name: ix_responses_question_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_question_id ON public.responses USING btree (question_id);


--
-- Name: ix_responses_question_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_question_time ON public.responses USING btree (question_id, respondido_en);


--
-- Name: ix_responses_respondido_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_respondido_en ON public.responses USING btree (respondido_en);


--
-- Name: ix_responses_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_session_id ON public.responses USING btree (session_id);


--
-- Name: ix_responses_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_student_id ON public.responses USING btree (student_id);


--
-- Name: ix_responses_student_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_student_time ON public.responses USING btree (student_id, respondido_en);


--
-- Name: ix_responses_student_topic_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_student_topic_time ON public.responses USING btree (student_id, topic_id, respondido_en);


--
-- Name: ix_responses_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_responses_topic_id ON public.responses USING btree (topic_id);


--
-- Name: ix_sessions_student_start; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_student_start ON public.study_sessions USING btree (student_id, iniciada_en);


--
-- Name: ix_sessions_student_strategy; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sessions_student_strategy ON public.study_sessions USING btree (student_id, estrategia);


--
-- Name: ix_spaced_due; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spaced_due ON public.spaced_repetition USING btree (proxima_revision_en);


--
-- Name: ix_spaced_repetition_capsule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spaced_repetition_capsule_id ON public.spaced_repetition USING btree (capsule_id);


--
-- Name: ix_spaced_repetition_proxima_revision_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spaced_repetition_proxima_revision_en ON public.spaced_repetition USING btree (proxima_revision_en);


--
-- Name: ix_spaced_repetition_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spaced_repetition_student_id ON public.spaced_repetition USING btree (student_id);


--
-- Name: ix_spaced_repetition_topic_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spaced_repetition_topic_id ON public.spaced_repetition USING btree (topic_id);


--
-- Name: ix_spaced_student_next_review; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_spaced_student_next_review ON public.spaced_repetition USING btree (student_id, proxima_revision_en);


--
-- Name: ix_students_activo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_students_activo ON public.students USING btree (activo);


--
-- Name: ix_students_codigo_anonimo; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_students_codigo_anonimo ON public.students USING btree (codigo_anonimo);


--
-- Name: ix_students_telegram_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_students_telegram_id ON public.students USING btree (telegram_id);


--
-- Name: ix_study_sessions_capsule_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_sessions_capsule_id ON public.study_sessions USING btree (capsule_id);


--
-- Name: ix_study_sessions_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_study_sessions_student_id ON public.study_sessions USING btree (student_id);


--
-- Name: ix_sus_responses_enviado_en; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sus_responses_enviado_en ON public.sus_responses USING btree (enviado_en);


--
-- Name: ix_sus_responses_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sus_responses_student_id ON public.sus_responses USING btree (student_id);


--
-- Name: ix_sus_student_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sus_student_date ON public.sus_responses USING btree (student_id, enviado_en);


--
-- Name: ix_teacher_student_assignments_student_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_student_assignments_student_id ON public.teacher_student_assignments USING btree (student_id);


--
-- Name: ix_teacher_student_assignments_teacher_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_teacher_student_assignments_teacher_id ON public.teacher_student_assignments USING btree (teacher_id);


--
-- Name: ix_teachers_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_teachers_email ON public.teachers USING btree (email);


--
-- Name: ix_topics_unidad; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_topics_unidad ON public.topics USING btree (unidad);


--
-- Name: agent_interactions agent_interactions_model_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_model_run_id_fkey FOREIGN KEY (model_run_id) REFERENCES public.model_runs(id) ON DELETE RESTRICT;


--
-- Name: agent_interactions agent_interactions_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.study_sessions(id) ON DELETE RESTRICT;


--
-- Name: agent_interactions agent_interactions_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_interactions
    ADD CONSTRAINT agent_interactions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: capsules capsules_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.capsules
    ADD CONSTRAINT capsules_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id) ON DELETE RESTRICT;


--
-- Name: events events_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.study_sessions(id) ON DELETE RESTRICT;


--
-- Name: events events_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: questions fk_questions_capsule_topic; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT fk_questions_capsule_topic FOREIGN KEY (capsule_id, topic_id) REFERENCES public.capsules(id, topic_id) ON DELETE RESTRICT;


--
-- Name: mastery mastery_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mastery
    ADD CONSTRAINT mastery_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: mastery mastery_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mastery
    ADD CONSTRAINT mastery_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id) ON DELETE RESTRICT;


--
-- Name: model_predictions model_predictions_model_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_predictions
    ADD CONSTRAINT model_predictions_model_run_id_fkey FOREIGN KEY (model_run_id) REFERENCES public.model_runs(id) ON DELETE RESTRICT;


--
-- Name: model_predictions model_predictions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_predictions
    ADD CONSTRAINT model_predictions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE RESTRICT;


--
-- Name: model_predictions model_predictions_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_predictions
    ADD CONSTRAINT model_predictions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: model_predictions model_predictions_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_predictions
    ADD CONSTRAINT model_predictions_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id) ON DELETE RESTRICT;


--
-- Name: pedagogical_decisions pedagogical_decisions_model_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedagogical_decisions
    ADD CONSTRAINT pedagogical_decisions_model_run_id_fkey FOREIGN KEY (model_run_id) REFERENCES public.model_runs(id) ON DELETE RESTRICT;


--
-- Name: pedagogical_decisions pedagogical_decisions_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedagogical_decisions
    ADD CONSTRAINT pedagogical_decisions_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.study_sessions(id) ON DELETE RESTRICT;


--
-- Name: pedagogical_decisions pedagogical_decisions_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pedagogical_decisions
    ADD CONSTRAINT pedagogical_decisions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: questions questions_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id) ON DELETE RESTRICT;


--
-- Name: reminders reminders_spaced_repetition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminders
    ADD CONSTRAINT reminders_spaced_repetition_id_fkey FOREIGN KEY (spaced_repetition_id) REFERENCES public.spaced_repetition(id) ON DELETE RESTRICT;


--
-- Name: reminders reminders_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reminders
    ADD CONSTRAINT reminders_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: responses responses_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE RESTRICT;


--
-- Name: responses responses_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.study_sessions(id) ON DELETE RESTRICT;


--
-- Name: responses responses_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: responses responses_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id) ON DELETE RESTRICT;


--
-- Name: spaced_repetition spaced_repetition_capsule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spaced_repetition
    ADD CONSTRAINT spaced_repetition_capsule_id_fkey FOREIGN KEY (capsule_id) REFERENCES public.capsules(id) ON DELETE RESTRICT;


--
-- Name: spaced_repetition spaced_repetition_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spaced_repetition
    ADD CONSTRAINT spaced_repetition_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: spaced_repetition spaced_repetition_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.spaced_repetition
    ADD CONSTRAINT spaced_repetition_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id) ON DELETE RESTRICT;


--
-- Name: study_sessions study_sessions_capsule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_capsule_id_fkey FOREIGN KEY (capsule_id) REFERENCES public.capsules(id) ON DELETE RESTRICT;


--
-- Name: study_sessions study_sessions_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: sus_responses sus_responses_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sus_responses
    ADD CONSTRAINT sus_responses_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: teacher_student_assignments teacher_student_assignments_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_student_assignments
    ADD CONSTRAINT teacher_student_assignments_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE RESTRICT;


--
-- Name: teacher_student_assignments teacher_student_assignments_teacher_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.teacher_student_assignments
    ADD CONSTRAINT teacher_student_assignments_teacher_id_fkey FOREIGN KEY (teacher_id) REFERENCES public.teachers(id) ON DELETE RESTRICT;


--
-- PostgreSQL database dump complete
--

\unrestrict aXZh4lQYjC9fjixS1kNbTPzsf7LAW5UDGacG97bmDxQ8t1MXxgUd19Cu2B3vw1d

