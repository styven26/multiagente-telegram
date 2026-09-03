export const LIM = {
  temaNombre: 128, temaNombreAviso: 60, temaEmoji: 8, temaDesc: 300,
  capTitulo: 200, capTituloAviso: 55, capObjetivo: 300, capContenido: 3500,
  preEnunciado: 1000, preEnunciadoAviso: 300, preOpcion: 55, preRetro: 500,
} as const;

// Telegram cuenta en UTF-16, igual que String.length
export const largo = (s: string) => s.length;
// Postgres cuenta caracteres, no unidades UTF-16
export const puntos = (s: string) => [...s].length;

const TAGS_OK = ["b", "strong", "i", "em", "u", "s", "code", "pre", "a", "br"];

/** Devuelve un mensaje si Telegram rechazaría el HTML, o null si está bien. */
export function validarHTML(texto: string): string | null {
  const pila: string[] = [];
  const re = /<\/?([a-zA-Z]+)[^>]*>/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(texto))) {
    const tag = m[1].toLowerCase();
    if (!TAGS_OK.includes(tag)) return `Telegram no admite la etiqueta <${tag}>`;
    if (tag === "br") continue;
    if (m[0].startsWith("</")) {
      if (pila.pop() !== tag) return `La etiqueta </${tag}> no cierra correctamente`;
    } else pila.push(tag);
  }
  if (pila.length) return `Falta cerrar <${pila[pila.length - 1]}>`;

  // Un < o & suelto rompe el parseo y el mensaje NO llega
  const suelto = texto.replace(re, "").match(/<|&(?!(amp|lt|gt);)/);
  if (suelto) {
    return `Escribe &lt; &gt; &amp; en vez de < > & sueltos (aparecerán correctos en Telegram)`;
  }
  return null;
}

export function validarTema(v: { nombre: string; emoji: string; descripcion: string }) {
  const e: string[] = [];
  if (v.nombre.trim().length < 3) e.push("El nombre necesita al menos 3 caracteres");
  if (largo(v.nombre) > LIM.temaNombre) e.push(`Nombre: máximo ${LIM.temaNombre}`);
  if (puntos(v.emoji) > LIM.temaEmoji) e.push("El emoji es demasiado largo");
  if (largo(v.descripcion) > LIM.temaDesc) e.push(`Descripción: máximo ${LIM.temaDesc}`);
  return { ok: e.length === 0, errores: e };
}

export function validarCapsula(v: {
  titulo: string; objetivo: string; contenido: string; duracion_min: number;
}) {
  const e: string[] = [];
  if (v.titulo.trim().length < 3) e.push("El título necesita al menos 3 caracteres");
  if (largo(v.titulo) > LIM.capTitulo) e.push(`Título: máximo ${LIM.capTitulo}`);
  if (v.objetivo.trim().length < 5) e.push("Escribe el objetivo de aprendizaje");
  if (largo(v.objetivo) > LIM.capObjetivo) e.push(`Objetivo: máximo ${LIM.capObjetivo}`);
  if (v.contenido.trim().length < 10) e.push("El contenido está vacío");
  if (largo(v.contenido) > LIM.capContenido)
    e.push(`Contenido: máximo ${LIM.capContenido}. Telegram no envía mensajes más largos`);
  const html = validarHTML(v.contenido);
  if (html) e.push(html);
  if (v.duracion_min < 1 || v.duracion_min > 60) e.push("La duración va de 1 a 60 minutos");
  return { ok: e.length === 0, errores: e };
}

export function validarPregunta(v: {
  enunciado: string; opciones: string[]; correcta: number; retroalimentacion: string;
}) {
  const e: string[] = [];
  if (v.enunciado.trim().length < 5) e.push("El enunciado necesita al menos 5 caracteres");
  if (largo(v.enunciado) > LIM.preEnunciado) e.push(`Enunciado: máximo ${LIM.preEnunciado}`);
  const html = validarHTML(v.enunciado);
  if (html) e.push(html);

  const limpias = v.opciones.map((o) => o.trim());
  if (limpias.some((o) => !o)) e.push("Hay opciones vacías");
  if (limpias.length < 2) e.push("Se necesitan al menos 2 opciones");
  const larga = limpias.find((o) => largo(o) > LIM.preOpcion);
  if (larga) e.push(`Cada opción admite ${LIM.preOpcion} caracteres: el botón se corta`);
  if (new Set(limpias.map((o) => o.toLowerCase())).size !== limpias.length)
    e.push("Hay opciones repetidas");
  if (v.correcta < 0 || v.correcta >= limpias.length) e.push("Marca cuál es la correcta");
  if (largo(v.retroalimentacion) > LIM.preRetro)
    e.push(`Retroalimentación: máximo ${LIM.preRetro}`);
  return { ok: e.length === 0, errores: e };
}

const PATRON_EMAIL = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

export const MIN_CLAVE = 8;
export const MAX_EMAIL = 255;

export function validarEmail(v: string): string | null {
  const t = v.trim();
  if (!t) return "Escribe tu correo";
  if (t.length > MAX_EMAIL) return `El correo admite máximo ${MAX_EMAIL} caracteres`;
  if (/\s/.test(t)) return "El correo no puede llevar espacios";
  if (!PATRON_EMAIL.test(t)) return "Formato inválido. Ejemplo: docente@universidad.edu.ec";
  return null;
}

export function validarClave(v: string): string | null {
  if (!v) return "Escribe tu contraseña";
  if (v.length < MIN_CLAVE) return `Mínimo ${MIN_CLAVE} caracteres`;
  // bcrypt cuenta bytes: una vocal acentuada ocupa 2 y el hash se trunca en 72.
  if (new TextEncoder().encode(v).length > 72) return "Contraseña demasiado larga";
  if (v !== v.trim()) return "Sobra un espacio al inicio o al final";
  return null;
}