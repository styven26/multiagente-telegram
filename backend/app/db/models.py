"""
Modelos ORM completos del Sistema Tutor Inteligente (STI).

CICLO 1 - MVP CONVERSACIONAL
    - Telegram
    - Agente Orquestador
    - Agente de Evaluación
    - Micro-cápsulas
    - Quizzes
    - Reglas simples / Mago de Oz
    - Sesiones
    - Finalización
    - Retorno D1
    - Grupos control/experimental

CICLO 2 - KNOWLEDGE TRACING
    - Respuestas secuenciales
    - Mastery
    - SAKT / Transformer
    - Predicciones
    - Versionado de modelos
    - Métricas AUC, F1, accuracy, etc.
    - Comparación ruta fija vs adaptativa

CICLO 3 - PERSONALIZACIÓN
    - Agente Pedagógico
    - DQN
    - Estado / acción / recompensa
    - SM-2
    - Red neuronal para repetición espaciada
    - Programación de repasos
    - Recordatorios
    - Dashboard docente
    - SUS
    - Trazabilidad de agentes
    - Registro de experimentos y modelos

IDENTIDAD / PRIVACIDAD
    - telegram_id permanece únicamente en students.
    - El resto del sistema trabaja mediante student_id.
    - codigo_anonimo se utiliza para análisis e investigación.
    - Se recomienda desactivar estudiantes mediante activo=False.
    - Los registros históricos no se deben eliminarse durante el experimento.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ============================================================
# 1. STUDENTS
# ============================================================

class Student(Base):
    """
    Estudiante del STI.

    telegram_id:
        Identificador técnico de Telegram.
        Debe permanecer exclusivamente en esta tabla.

    codigo_anonimo:
        Identificador utilizado para investigación y analítica.
    """

    __tablename__ = "students"

    __table_args__ = (
        CheckConstraint(
            """
            (
                consentimiento = FALSE
                AND fecha_consentimiento IS NULL
            )
            OR
            (
                consentimiento = TRUE
                AND fecha_consentimiento IS NOT NULL
            )
            """,
            name="ck_students_consentimiento_fecha",
        ),
        CheckConstraint(
            """
            grupo IS NULL
            OR grupo IN ('experimental', 'control')
            """,
            name="ck_students_grupo",
        ),
        Index(
            "ix_students_activo",
            "activo",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    codigo_anonimo: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        nullable=False,
        index=True,
    )

    nombre_telegram: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    consentimiento: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    fecha_consentimiento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    version_consentimiento: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    grupo: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    cohorte: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        index=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # --------------------------------------------------------
    # Relaciones
    # --------------------------------------------------------

    respuestas: Mapped[list["Response"]] = relationship(
        "Response",
        back_populates="student",
        passive_deletes=True,
    )

    sesiones: Mapped[list["StudySession"]] = relationship(
        "StudySession",
        back_populates="student",
        passive_deletes=True,
    )

    mastery_records: Mapped[list["Mastery"]] = relationship(
        "Mastery",
        back_populates="student",
        passive_deletes=True,
    )

    eventos: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="student",
        passive_deletes=True,
    )

    decisiones_pedagogicas: Mapped[list["PedagogicalDecision"]] = relationship(
        "PedagogicalDecision",
        back_populates="student",
        passive_deletes=True,
    )

    repeticiones: Mapped[list["SpacedRepetition"]] = relationship(
        "SpacedRepetition",
        back_populates="student",
        passive_deletes=True,
    )

    recordatorios: Mapped[list["Reminder"]] = relationship(
        "Reminder",
        back_populates="student",
        passive_deletes=True,
    )

    interacciones_agentes: Mapped[list["AgentInteraction"]] = relationship(
        "AgentInteraction",
        back_populates="student",
        passive_deletes=True,
    )

    predicciones_modelo: Mapped[list["ModelPrediction"]] = relationship(
        "ModelPrediction",
        back_populates="student",
        passive_deletes=True,
    )


# ============================================================
# 2. TEACHERS
# ============================================================

class Teacher(Base):
    """
    Docente / investigador que accede al dashboard.
    """

    __tablename__ = "teachers"

    __table_args__ = (
        CheckConstraint(
            "rol IN ('docente', 'investigador', 'administrador')",
            name="ck_teachers_rol",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    rol: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="docente",
        server_default="docente",
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# 3. TOPICS
# ============================================================

class Topic(Base):
    """
    Tema / nodo del grafo de conocimiento.

    Ejemplo:
        T1_variables
        T2_ecuaciones
        T3_funciones
    """

    __tablename__ = "topics"

    __table_args__ = (
        CheckConstraint(
            "orden >= 0",
            name="ck_topics_orden",
        ),
        CheckConstraint(
            "unidad IS NULL OR unidad BETWEEN 1 AND 4",
            name="ck_topics_unidad",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    unidad: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    prerrequisitos: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        default=list,
    )

    emoji: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # --------------------------------------------------------
    # Relaciones
    # --------------------------------------------------------

    capsulas: Mapped[list["Capsule"]] = relationship(
        "Capsule",
        back_populates="topic",
        passive_deletes=True,
    )

    preguntas: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="topic",
        viewonly=True,
    )

    mastery_records: Mapped[list["Mastery"]] = relationship(
        "Mastery",
        back_populates="topic",
        passive_deletes=True,
    )

    respuestas: Mapped[list["Response"]] = relationship(
        "Response",
        back_populates="topic",
        passive_deletes=True,
    )

    repeticiones: Mapped[list["SpacedRepetition"]] = relationship(
        "SpacedRepetition",
        back_populates="topic",
        passive_deletes=True,
    )


# ============================================================
# 4. CAPSULES
# ============================================================

class Capsule(Base):
    """
    Micro-cápsula educativa.

    Diseñada para:
        - 3 a 10 minutos
        - un objetivo principal
        - dificultad 1-3
        - adaptación pedagógica
    """

    __tablename__ = "capsules"

    __table_args__ = (
        UniqueConstraint(
            "id",
            "topic_id",
            name="uq_capsules_id_topic",
        ),
        UniqueConstraint(
            "topic_id",
            "orden",
            name="uq_capsules_topic_orden",
        ),
        CheckConstraint(
            "orden >= 0",
            name="ck_capsules_orden",
        ),
        CheckConstraint(
            "duracion_min BETWEEN 1 AND 60",
            name="ck_capsules_duracion",
        ),
        CheckConstraint(
            "dificultad BETWEEN 1 AND 3",
            name="ck_capsules_dificultad",
        ),
        Index(
            "ix_capsules_topic_orden",
            "topic_id",
            "orden",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    topic_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "topics.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    objetivo: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    contenido: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    imagen_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    orden: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    duracion_min: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        server_default="5",
    )

    dificultad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="capsulas",
    )

    preguntas: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="capsula",
        passive_deletes=True,
    )

    sesiones: Mapped[list["StudySession"]] = relationship(
        "StudySession",
        back_populates="capsula",
        passive_deletes=True,
    )

    repeticiones: Mapped[list["SpacedRepetition"]] = relationship(
        "SpacedRepetition",
        back_populates="capsula",
        passive_deletes=True,
    )


# ============================================================
# 5. QUESTIONS
# ============================================================

class Question(Base):
    """
    Pregunta del banco de evaluación.

    La ForeignKeyConstraint compuesta garantiza que:
        Question.topic_id == Capsule.topic_id
    """

    __tablename__ = "questions"

    __table_args__ = (
        ForeignKeyConstraint(
            ["capsule_id", "topic_id"],
            ["capsules.id", "capsules.topic_id"],
            name="fk_questions_capsule_topic",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "correcta >= 0",
            name="ck_questions_correcta",
        ),
        CheckConstraint(
            "dificultad BETWEEN 1 AND 3",
            name="ck_questions_dificultad",
        ),
        CheckConstraint(
            """
            tipo IN (
                'opcion_multiple',
                'verdadero_falso',
                'respuesta_corta'
            )
            """,
            name="ck_questions_tipo",
        ),
        Index(
            "ix_questions_topic_difficulty",
            "topic_id",
            "dificultad",
        ),
        Index(
            "ix_questions_capsule",
            "capsule_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    capsule_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "topics.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    tipo: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="opcion_multiple",
        server_default="opcion_multiple",
    )

    enunciado: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    imagen_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    opciones: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    correcta: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    retroalimentacion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    dificultad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    capsula: Mapped["Capsule"] = relationship(
        "Capsule",
        back_populates="preguntas",
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="preguntas",
        viewonly=True,
    )

    respuestas: Mapped[list["Response"]] = relationship(
        "Response",
        back_populates="question",
        passive_deletes=True,
    )

    predicciones: Mapped[list["ModelPrediction"]] = relationship(
        "ModelPrediction",
        back_populates="question",
        passive_deletes=True,
    )


# ============================================================
# 6. STUDY SESSIONS
# ============================================================

class StudySession(Base):
    """
    Sesión de estudio.

    Permite medir:
        - inicio
        - finalización
        - duración
        - retorno
        - estrategia fija/adaptativa
        - ciclo experimental
    """

    __tablename__ = "study_sessions"

    __table_args__ = (
        CheckConstraint(
            """
            finalizada_en IS NULL
            OR finalizada_en >= iniciada_en
            """,
            name="ck_sessions_fechas",
        ),
        CheckConstraint(
            "duracion_seg IS NULL OR duracion_seg >= 0",
            name="ck_sessions_duracion",
        ),
        CheckConstraint(
            "ciclo BETWEEN 1 AND 3",
            name="ck_sessions_ciclo",
        ),
        CheckConstraint(
            """
            estrategia IN (
                'fija',
                'adaptativa',
                'manual_mago_oz'
            )
            """,
            name="ck_sessions_estrategia",
        ),
        Index(
            "ix_sessions_student_start",
            "student_id",
            "iniciada_en",
        ),
        Index(
            "ix_sessions_student_strategy",
            "student_id",
            "estrategia",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    capsule_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey(
            "capsules.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    ciclo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    estrategia: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="manual_mago_oz",
        server_default="manual_mago_oz",
    )

    iniciada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    finalizada_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duracion_seg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    completada: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="sesiones",
    )

    capsula: Mapped["Capsule | None"] = relationship(
        "Capsule",
        back_populates="sesiones",
    )

    respuestas: Mapped[list["Response"]] = relationship(
        "Response",
        back_populates="session",
        passive_deletes=True,
    )

    decisiones_pedagogicas: Mapped[list["PedagogicalDecision"]] = relationship(
        "PedagogicalDecision",
        back_populates="session",
        passive_deletes=True,
    )

    eventos: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="session",
        passive_deletes=True,
    )

    interacciones_agentes: Mapped[list["AgentInteraction"]] = relationship(
        "AgentInteraction",
        back_populates="session",
        passive_deletes=True,
    )


# ============================================================
# 7. RESPONSES
# ============================================================

class Response(Base):
    """
    Respuesta histórica de un estudiante.

    Es la principal fuente para:
        - Knowledge Tracing
        - SAKT
        - accuracy
        - F1
        - AUC
        - mastery
        - secuencias de interacción
    """

    __tablename__ = "responses"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "orden_interaccion",
            name="uq_response_student_sequence",
        ),
        CheckConstraint(
            "seleccion >= 0",
            name="ck_responses_seleccion",
        ),
        CheckConstraint(
            "tiempo_seg IS NULL OR tiempo_seg >= 0",
            name="ck_responses_tiempo",
        ),
        CheckConstraint(
            """
            orden_interaccion >= 1
            """,
            name="ck_responses_sequence",
        ),
        Index(
            "ix_responses_student_topic_time",
            "student_id",
            "topic_id",
            "respondido_en",
        ),
        Index(
            "ix_responses_student_time",
            "student_id",
            "respondido_en",
        ),
        Index(
            "ix_responses_question_time",
            "question_id",
            "respondido_en",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    session_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "study_sessions.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "questions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "topics.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    orden_interaccion: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    intento: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    seleccion: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    es_correcta: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    tiempo_seg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    respondido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="respuestas",
    )

    session: Mapped["StudySession | None"] = relationship(
        "StudySession",
        back_populates="respuestas",
    )

    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="respuestas",
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="respuestas",
    )


# ============================================================
# 8. MASTERY
# ============================================================

class Mastery(Base):
    """
    Dominio estimado por estudiante y tema.

    CICLO 1:
        baseline mediante reglas simples.

    CICLO 2:
        SAKT / Knowledge Tracing.

    CICLO 3:
        utilizado como parte del estado del agente pedagógico.
    """

    __tablename__ = "mastery"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "topic_id",
            name="uq_mastery_student_topic",
        ),
        CheckConstraint(
            "nivel >= 0.0 AND nivel <= 1.0",
            name="ck_mastery_nivel",
        ),
        CheckConstraint(
            """
            fuente IN (
                'baseline',
                'sakt',
                'manual'
            )
            """,
            name="ck_mastery_fuente",
        ),
        CheckConstraint(
            "numero_evidencias >= 0",
            name="ck_mastery_evidencias",
        ),
        Index(
            "ix_mastery_student_topic",
            "student_id",
            "topic_id",
        ),
        Index(
            "ix_mastery_topic_level",
            "topic_id",
            "nivel",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "topics.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    nivel: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
    )

    fuente: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="baseline",
        server_default="baseline",
    )

    probabilidad_siguiente_correcta: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    numero_evidencias: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    modelo_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    ultima_respuesta_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="mastery_records",
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="mastery_records",
    )


# ============================================================
# 9. EVENTS
# ============================================================

class Event(Base):
    """
    Bitácora cruda de interacciones del sistema.

    Ejemplos:
        session_started
        session_completed
        capsule_opened
        capsule_completed
        question_presented
        question_answered
        hint_requested
        recommendation_generated
        mastery_updated
        sakt_prediction
        dqn_decision
        spaced_review_scheduled
        reminder_sent
        telegram_message
        telegram_callback

    payload:
        Datos adicionales en JSON.
    """

    __tablename__ = "events"

    __table_args__ = (
        CheckConstraint(
            "ciclo BETWEEN 1 AND 3",
            name="ck_events_ciclo",
        ),
        Index(
            "ix_events_student_time",
            "student_id",
            "ocurrido_en",
        ),
        Index(
            "ix_events_type_time",
            "tipo",
            "ocurrido_en",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    session_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "study_sessions.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    ciclo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    tipo: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    ocurrido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    student: Mapped["Student | None"] = relationship(
        "Student",
        back_populates="eventos",
    )

    session: Mapped["StudySession | None"] = relationship(
        "StudySession",
        back_populates="eventos",
    )


# ============================================================
# 10. PEDAGOGICAL DECISIONS
# ============================================================

class PedagogicalDecision(Base):
    """
    Decisión tomada por el Agente Pedagógico.

    Diseñada para DQN:

        STATE
          ↓
        ACTION
          ↓
        REWARD
          ↓
      NEXT STATE

    También permite registrar decisiones por reglas durante
    el Ciclo 1.
    """

    __tablename__ = "pedagogical_decisions"

    __table_args__ = (
        CheckConstraint(
            "ciclo BETWEEN 1 AND 3",
            name="ck_pedagogical_ciclo",
        ),
        CheckConstraint(
            """
            estrategia IN (
                'reglas',
                'mago_oz',
                'dqn'
            )
            """,
            name="ck_pedagogical_strategy",
        ),
        Index(
            "ix_pedagogical_student_time",
            "student_id",
            "created_at",
        ),
        Index(
            "ix_pedagogical_strategy",
            "estrategia",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    session_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "study_sessions.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    model_run_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "model_runs.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    ciclo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3",
    )

    estrategia: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="dqn",
        server_default="dqn",
    )

    tipo_accion: Mapped[str] = mapped_column(
        String(48),
        nullable=False,
    )

    objetivo_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    estado: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    accion: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    recompensa: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    siguiente_estado: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    terminada: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    parametros: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="decisiones_pedagogicas",
    )

    session: Mapped["StudySession | None"] = relationship(
        "StudySession",
        back_populates="decisiones_pedagogicas",
    )

    model_run: Mapped["ModelRun | None"] = relationship(
        "ModelRun",
        back_populates="decisiones_pedagogicas",
    )


# ============================================================
# 11. SPACED REPETITION
# ============================================================

class SpacedRepetition(Base):
    """
    Programación de repetición espaciada.

    CICLO 3:
        - SM-2
        - parámetros individualizados
        - ajuste de red neuronal
        - siguiente repaso
        - curva de olvido

    Una fila representa la agenda de repaso de una cápsula
    para un estudiante.
    """

    __tablename__ = "spaced_repetition"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "capsule_id",
            name="uq_spaced_student_capsule",
        ),
        CheckConstraint(
            "calidad BETWEEN 0 AND 5",
            name="ck_spaced_quality",
        ),
        CheckConstraint(
            "ease_factor >= 1.3",
            name="ck_spaced_ease",
        ),
        CheckConstraint(
            "intervalo_dias >= 0",
            name="ck_spaced_interval",
        ),
        CheckConstraint(
            "repeticiones >= 0",
            name="ck_spaced_repetitions",
        ),
        CheckConstraint(
            "errores >= 0",
            name="ck_spaced_errors",
        ),
        CheckConstraint(
            "dificultad >= 0.0 AND dificultad <= 1.0",
            name="ck_spaced_difficulty",
        ),
        CheckConstraint(
            "estabilidad >= 0.0",
            name="ck_spaced_stability",
        ),
        Index(
            "ix_spaced_student_next_review",
            "student_id",
            "proxima_revision_en",
        ),
        Index(
            "ix_spaced_due",
            "proxima_revision_en",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    topic_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "topics.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    capsule_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey(
            "capsules.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    calidad: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    ease_factor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=2.5,
        server_default="2.5",
    )

    intervalo_dias: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    repeticiones: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    errores: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    dificultad: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        server_default="0.5",
    )

    estabilidad: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
    )

    ajuste_red_neuronal: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        server_default="1.0",
    )

    ultima_revision_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    proxima_revision_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    modelo_version: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="repeticiones",
    )

    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="repeticiones",
    )

    capsula: Mapped["Capsule"] = relationship(
        "Capsule",
        back_populates="repeticiones",
    )

    recordatorios: Mapped[list["Reminder"]] = relationship(
        "Reminder",
        back_populates="spaced_repetition",
        passive_deletes=True,
    )


# ============================================================
# 12. REMINDERS
# ============================================================

class Reminder(Base):
    """
    Recordatorios automáticos del Agente de Repetición Espaciada.
    """

    __tablename__ = "reminders"

    __table_args__ = (
        CheckConstraint(
            """
            estado IN (
                'pendiente',
                'enviado',
                'fallido',
                'cancelado'
            )
            """,
            name="ck_reminders_estado",
        ),
        CheckConstraint(
            "intentos_envio >= 0",
            name="ck_reminders_attempts",
        ),
        Index(
            "ix_reminders_student_due",
            "student_id",
            "programado_en",
        ),
        Index(
            "ix_reminders_status_due",
            "estado",
            "programado_en",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    spaced_repetition_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "spaced_repetition.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    titulo: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    mensaje: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    canal: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="telegram",
        server_default="telegram",
    )

    programado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    enviado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pendiente",
        server_default="pendiente",
    )

    intentos_envio: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    error_detalle: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="recordatorios",
    )

    spaced_repetition: Mapped["SpacedRepetition | None"] = relationship(
        "SpacedRepetition",
        back_populates="recordatorios",
    )


# ============================================================
# 13. MODEL RUNS
# ============================================================

class ModelRun(Base):
    """
    Registro de ejecuciones/versiones de modelos.

    Permite documentar:
        - SAKT
        - DQN
        - red neuronal de repetición espaciada
        - datasets públicos
        - datasets del Ciclo 1
        - métricas
        - hiperparámetros
    """

    __tablename__ = "model_runs"

    __table_args__ = (
        CheckConstraint(
            "ciclo BETWEEN 1 AND 3",
            name="ck_model_runs_ciclo",
        ),
        CheckConstraint(
            """
            tipo IN (
                'sakt',
                'dqn',
                'spaced_nn',
                'baseline',
                'otro'
            )
            """,
            name="ck_model_runs_tipo",
        ),
        Index(
            "ix_model_runs_type_created",
            "tipo",
            "creado_en",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    ciclo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    nombre_modelo: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    dataset: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    hiperparametros: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    metricas: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    auc: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    f1: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    accuracy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    precision: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    recall: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    reward_medio: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    fecha_entrenamiento: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    decisiones_pedagogicas: Mapped[list["PedagogicalDecision"]] = relationship(
        "PedagogicalDecision",
        back_populates="model_run",
        passive_deletes=True,
    )

    predicciones: Mapped[list["ModelPrediction"]] = relationship(
        "ModelPrediction",
        back_populates="model_run",
        passive_deletes=True,
    )

    interacciones_agentes: Mapped[list["AgentInteraction"]] = relationship(
        "AgentInteraction",
        back_populates="model_run",
        passive_deletes=True,
    )


# ============================================================
# 14. MODEL PREDICTIONS
# ============================================================

class ModelPrediction(Base):
    """
    Predicción generada por un modelo.

    Principalmente para:
        - SAKT
        - Knowledge Tracing
        - comparación predicción / resultado real
    """

    __tablename__ = "model_predictions"

    __table_args__ = (
        CheckConstraint(
            "probabilidad >= 0.0 AND probabilidad <= 1.0",
            name="ck_predictions_probability",
        ),
        Index(
            "ix_predictions_student_time",
            "student_id",
            "creado_en",
        ),
        Index(
            "ix_predictions_model",
            "model_run_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    model_run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "model_runs.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    question_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "questions.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    topic_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey(
            "topics.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    secuencia: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    probabilidad: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    resultado_real: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    error_absoluto: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="predicciones_modelo",
    )

    model_run: Mapped["ModelRun"] = relationship(
        "ModelRun",
        back_populates="predicciones",
    )

    question: Mapped["Question | None"] = relationship(
        "Question",
        back_populates="predicciones",
    )


# ============================================================
# 15. AGENT INTERACTIONS
# ============================================================

class AgentInteraction(Base):
    """
    Trazabilidad de los agentes del sistema.

    Agentes:
        - orchestrator
        - evaluation
        - student_model
        - pedagogical
        - spaced_repetition

    Sirve para saber:
        - qué agente actuó
        - qué recibió
        - qué produjo
        - cuánto tardó
        - si tuvo error
    """

    __tablename__ = "agent_interactions"

    __table_args__ = (
        CheckConstraint(
            """
            agente IN (
                'orchestrator',
                'evaluation',
                'student_model',
                'pedagogical',
                'spaced_repetition'
            )
            """,
            name="ck_agent_interactions_agent",
        ),
        Index(
            "ix_agent_interactions_student_time",
            "student_id",
            "created_at",
        ),
        Index(
            "ix_agent_interactions_agent_time",
            "agente",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    student_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "students.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    session_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "study_sessions.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    model_run_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "model_runs.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    agente: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    accion: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    entrada: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    salida: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    exitosa: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    duracion_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    student: Mapped["Student | None"] = relationship(
        "Student",
        back_populates="interacciones_agentes",
    )

    session: Mapped["StudySession | None"] = relationship(
        "StudySession",
        back_populates="interacciones_agentes",
    )

    model_run: Mapped["ModelRun | None"] = relationship(
        "ModelRun",
        back_populates="interacciones_agentes",
    )


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "Student",
    "Teacher",
    "Topic",
    "Capsule",
    "Question",
    "StudySession",
    "Response",
    "Mastery",
    "Event",
    "PedagogicalDecision",
    "SpacedRepetition",
    "Reminder",
    "ModelRun",
    "ModelPrediction",
    "AgentInteraction",
]