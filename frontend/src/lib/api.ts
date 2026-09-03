const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Docente {
  id: number;
  nombre: string;
  email: string;
  rol: string;
  activo: boolean;
}

export interface Tema {
  id: string;
  nombre: string;
  descripcion: string | null;
  orden: number;
  unidad: number | null;
  emoji: string;
  activo: boolean;
  prerrequisitos: string[];
}

const CLAVE_TOKEN = "sti_token";

export function guardarToken(token: string) {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function leerToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(CLAVE_TOKEN);
}

export function borrarToken() {
  localStorage.removeItem(CLAVE_TOKEN);
}

/** Envuelve fetch: añade el token y traduce los errores del backend. */
async function pedir<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const token = leerToken();

  const res = await fetch(`${API}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...opciones.headers,
    },
  });

  if (res.status === 401) {
    borrarToken();
    throw new Error("Sesión expirada. Inicia sesión de nuevo.");
  }

  if (!res.ok) {
    const cuerpo = await res.json().catch(() => null);
    throw new Error(cuerpo?.detail ?? `Error ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export async function login(email: string, password: string) {
  return pedir<{ access_token: string; docente: Docente }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function yo() {
  return pedir<Docente>("/api/auth/me");
}

export async function listarTemas() {
  return pedir<Tema[]>("/api/teacher/topics");
}

export interface DominioTema {
  topic_id: string;
  nombre: string;
  dominio: number;      // 0..1
  respuestas: number;
}

export interface ProgresoEstudiante {
  codigo_anonimo: string;
  temas_completados: number;
  total_temas: number;
  aciertos: number;
  respuestas: number;
  ultima_actividad: string | null;
}

export interface RetornoDia {
  dia: string;          // "2026-08-19"
  activos: number;
  volvieron: number;
  parcial: boolean;     // el día en curso: su "día siguiente" aún no existe
}

export interface Embudo {
  registrados: number;
  iniciaron: number;
  completaron: number;
  retorno: RetornoDia[];
}

export interface ResumenDocente {
  estudiantes_activos: number;
  total_estudiantes: number;
  capsulas_entregadas: number;
  tasa_acierto: number;
  dominio_por_tema: DominioTema[];
  estudiantes: ProgresoEstudiante[];
  embudo: Embudo; 
}

export async function resumenDocente() {
  return pedir<ResumenDocente>("/api/teacher/metrics/overview");
}

export async function crearTema(datos: {
  nombre: string;
  emoji: string;
  descripcion?: string | null;
  unidad?: number | null;
  prerrequisitos?: string[];
}) {
  return pedir<Tema>("/api/teacher/topics", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function editarTema(
  id: string,
  datos: {
    nombre?: string;
    emoji?: string;
    descripcion?: string | null;
    unidad?: number | null;
    prerrequisitos?: string[];
  },
) {
  return pedir<Tema>(`/api/teacher/topics/${id}`, {
    method: "PATCH",
    body: JSON.stringify(datos),
  });
}

export async function alternarTema(id: string) {
  return pedir<Tema>(`/api/teacher/topics/${id}/toggle`, { method: "POST" });
}

export interface Capsula {
  id: string;
  topic_id: string;
  titulo: string;
  objetivo: string;
  contenido: string;
  imagen_url: string | null;
  orden: number;
  duracion_min: number;
  dificultad: number;
  activo: boolean;
}

export async function listarCapsulas(topicId: string) {
  return pedir<Capsula[]>(`/api/teacher/topics/${topicId}/capsules`);
}

export async function crearCapsula(topicId: string, datos: {
  titulo: string;
  objetivo: string;
  contenido: string;
  imagen_url?: string | null;
  duracion_min?: number;
  dificultad?: number;
}) {
  return pedir<Capsula>(`/api/teacher/topics/${topicId}/capsules`, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function editarCapsula(id: string, datos: {
  titulo?: string;
  objetivo?: string;
  contenido?: string;
  imagen_url?: string | null;
  duracion_min?: number;
  dificultad?: number;
}) {
  return pedir<Capsula>(`/api/teacher/capsules/${id}`, {
    method: "PATCH",
    body: JSON.stringify(datos),
  });
}

export async function alternarCapsula(id: string) {
  return pedir<Capsula>(`/api/teacher/capsules/${id}/toggle`, { method: "POST" });
}

export interface Pregunta {
  id: number;
  capsule_id: string;
  topic_id: string;
  tipo: string;
  enunciado: string;
  imagen_url: string | null;
  opciones: string[];
  correcta: number;
  retroalimentacion: string | null;
  dificultad: number;
  activo: boolean;
}

export async function listarPreguntas(capsuleId: string) {
  return pedir<Pregunta[]>(`/api/teacher/capsules/${capsuleId}/questions`);
}

export async function crearPregunta(capsuleId: string, datos: {
  tipo: string;
  enunciado: string;
  imagen_url?: string | null;
  opciones: string[];
  correcta: number;
  retroalimentacion?: string | null;
  dificultad?: number;
}) {
  return pedir<Pregunta>(`/api/teacher/capsules/${capsuleId}/questions`, {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export async function editarPregunta(id: number, datos: {
  tipo?: string;
  enunciado?: string;
  imagen_url?: string | null;
  opciones?: string[];
  correcta?: number;
  retroalimentacion?: string | null;
  dificultad?: number;
}) {
  return pedir<Pregunta>(`/api/teacher/questions/${id}`, {
    method: "PATCH",
    body: JSON.stringify(datos),
  });
}

export async function alternarPregunta(id: number) {
  return pedir<Pregunta>(`/api/teacher/questions/${id}/toggle`, { method: "POST" });
}

/** Sube una imagen y devuelve su ruta pública. No usa `pedir`: un archivo
 *  viaja como multipart, no como JSON. */
export async function subirImagen(archivo: File): Promise<string> {
  const token = leerToken();
  const cuerpo = new FormData();
  cuerpo.append("archivo", archivo);

  const res = await fetch(`${API}/api/teacher/uploads`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: cuerpo,
  });

  if (!res.ok) {
    const detalle = await res.json().catch(() => null);
    throw new Error(detalle?.detail ?? `Error ${res.status}`);
  }

  const datos = (await res.json()) as { url: string };
  return datos.url;
}

/** Convierte la ruta relativa que guarda la BD en una URL que el navegador
 *  pueda cargar. */
export function urlImagen(ruta: string | null): string | null {
  return ruta ? `${API}${ruta}` : null;
}