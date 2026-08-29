"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import {
  alternarCapsula, crearCapsula, editarCapsula, listarCapsulas, listarTemas,
  type Capsula, type Tema,
} from "@/lib/api";
import { colorDeUnidad, UNIDADES } from "@/lib/unidades";
import { LIM, largo, validarCapsula } from "@/lib/limites";

const campo =
  "w-full rounded-md border border-[#1a1830]/15 bg-white px-3 py-2 text-[14.5px] " +
  "text-[#1a1830] placeholder:text-[#a5a2b8] outline-none transition " +
  "focus:border-[#1a1830] focus:ring-4 focus:ring-[#1a1830]/10";

const etiqueta =
  "mb-1.5 block font-mono text-[10.5px] uppercase tracking-[0.14em] text-[#6b6788]";

const DIFICULTAD = ["", "Básica", "Media", "Alta"];

type Borrador = {
  titulo: string; objetivo: string; contenido: string;
  duracion_min: number; dificultad: number;
};

const VACIO: Borrador = {
  titulo: "", objetivo: "", contenido: "", duracion_min: 5, dificultad: 1,
};

function Formulario({
  valor, cambiar, color, onGuardar, onCancelar, guardando, textoBoton,
}: {
  valor: Borrador; cambiar: (v: Borrador) => void; color: string;
  onGuardar: () => void; onCancelar: () => void;
  guardando: boolean; textoBoton: string;
}) {
  const { ok: listo, errores } = validarCapsula(valor);
  return (
    <div className="space-y-4">
      <div>
        <label className={etiqueta}>Título</label>
        <input
          value={valor.titulo}
          onChange={(e) => cambiar({ ...valor, titulo: e.target.value })}
          placeholder="¿Qué es una variable?"
          maxLength={LIM.capTitulo}
          className={campo}
        />
      </div>

      <div>
        <label className={etiqueta}>Objetivo de aprendizaje</label>
        <input
          value={valor.objetivo}
          onChange={(e) => cambiar({ ...valor, objetivo: e.target.value })}
          placeholder="Reconocer una variable como un espacio de memoria con nombre"
          maxLength={LIM.capObjetivo}
          className={campo}
        />
        <p className="mt-1 text-[12px] text-[#a5a2b8]">
          Uno solo por cápsula. Si necesitas dos, son dos cápsulas.
        </p>
      </div>

      <div>
        <label className={etiqueta}>Descripción</label>
        <textarea
          value={valor.contenido}
          onChange={(e) => cambiar({ ...valor, contenido: e.target.value })}
          rows={7}
          maxLength={LIM.capContenido}
          placeholder="Texto"
          className={campo + " resize-y font-mono text-[13.5px] leading-relaxed"}
        />
        <p className="mt-1 text-[12px] text-[#a5a2b8]">
          {largo(valor.contenido)} / {LIM.capContenido} caracteres · Telegram admite
          {" "}<code className="font-mono">&lt;b&gt;</code>{" "}
          <code className="font-mono">&lt;i&gt;</code>{" "}
          <code className="font-mono">&lt;code&gt;</code>{" "}
          <code className="font-mono">&lt;pre&gt;</code>. Máximo 4096.
        </p>
      </div>

      <div className="flex gap-4">
        <div className="w-40">
          <label className={etiqueta}>Duración (min)</label>
          <input
            type="number" min={1} max={60}
            value={valor.duracion_min}
            onChange={(e) => cambiar({ ...valor, duracion_min: Math.min(60, Math.max(1, Number(e.target.value) || 1)) })}
            className={campo}
          />
        </div>
        <div className="w-48">
          <label className={etiqueta}>Dificultad</label>
          <select
            value={valor.dificultad}
            onChange={(e) => cambiar({ ...valor, dificultad: Number(e.target.value) })}
            className={campo}
          >
            <option value={1}>1 · Básica</option>
            <option value={2}>2 · Media</option>
            <option value={3}>3 · Alta</option>
          </select>
        </div>
      </div>

      {errores.length > 0 && (
        <ul className="border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-4 pr-3">
          {errores.map((e) => (
            <li key={e} className="text-[13.5px] text-[#8c2b20]">{e}</li>
          ))}
        </ul>
      )}

      <div className="flex gap-2 pt-1">
        <button
          disabled={!listo || guardando}
          onClick={onGuardar}
          className="rounded-md px-4 py-2 text-[14px] font-medium text-white transition disabled:opacity-30"
          style={{ backgroundColor: color }}
        >
          {guardando ? "Guardando…" : textoBoton}
        </button>
        <button
          onClick={onCancelar}
          className="rounded-md px-3 py-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] hover:text-[#1a1830]"
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}

export default function PaginaCapsulas() {
  const { topicId } = useParams<{ topicId: string }>();

  const [tema, setTema] = useState<Tema | null>(null);
  const [capsulas, setCapsulas] = useState<Capsula[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  const [ocupado, setOcupado] = useState<string | null>(null);

  const [creando, setCreando] = useState(false);
  const [nueva, setNueva] = useState<Borrador>(VACIO);
  const [editando, setEditando] = useState<string | null>(null);
  const [borrador, setBorrador] = useState<Borrador>(VACIO);

  useEffect(() => {
    Promise.all([listarTemas(), listarCapsulas(topicId)])
      .then(([ts, cs]) => {
        setTema(ts.find((t) => t.id === topicId) ?? null);
        setCapsulas(cs);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Error inesperado"))
      .finally(() => setCargando(false));
  }, [topicId]);

  const color = colorDeUnidad(tema?.unidad ?? null);
  const unidad = UNIDADES.find((u) => u.numero === tema?.unidad);

  async function accion<T>(id: string, fn: () => Promise<T>, despues: (r: T) => void) {
    setError(null);
    setOcupado(id);
    try {
      despues(await fn());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error inesperado");
    } finally {
      setOcupado(null);
    }
  }

  function abrirEdicion(c: Capsula) {
    setEditando(c.id);
    setCreando(false);
    setBorrador({
      titulo: c.titulo, objetivo: c.objetivo, contenido: c.contenido,
      duracion_min: c.duracion_min, dificultad: c.dificultad,
    });
  }

  if (cargando) {
    return (
      <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6788]">
        Cargando…
      </p>
    );
  }

  return (
    <>
      <Link
        href="/temas"
        className="inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:text-[#1a1830]"
      >
        <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Contenido
      </Link>

      <div className="mt-5 flex items-start justify-between gap-6">
        <div className="min-w-0">
          {unidad && (
            <p className="font-mono text-[10.5px] uppercase tracking-[0.16em]" style={{ color }}>
              Unidad {unidad.numero} · {unidad.nombre}
            </p>
          )}
          <h1 className="mt-1.5 font-display text-[2rem] font-medium tracking-tight text-[#1a1830]">
            {tema ? `${tema.emoji ?? ""} ${tema.nombre}`.trim() : topicId}
          </h1>
          <p className="mt-2 text-[15px] text-[#6b6788]">
            {capsulas.length === 0
              ? "Este tema todavía no tiene cápsulas."
              : `${capsulas.length} ${capsulas.length === 1 ? "cápsula" : "cápsulas"} · ${capsulas.filter((c) => c.activo).length} visibles para el estudiante.`}
          </p>
        </div>

        <button
          onClick={() => { setCreando((v) => !v); setEditando(null); setNueva(VACIO); }}
          className="shrink-0 rounded-md px-4 py-2.5 text-[14px] font-medium text-white transition"
          style={{ backgroundColor: creando ? "#8e8ba5" : "#1a1830" }}
        >
          {creando ? "Cancelar" : "Nueva micro-cápsula"}
        </button>
      </div>

      {error && (
        <div role="alert" className="mt-6 border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-4 pr-3">
          <p className="text-[13.5px] text-[#8c2b20]">{error}</p>
        </div>
      )}

      {creando && (
        <div className="mt-7 rounded-xl border bg-white p-6" style={{ borderColor: `${color}33` }}>
          <h2 className="mb-5 font-display text-[1.2rem] font-medium text-[#1a1830]">
            Nueva micro-cápsula
          </h2>
          <Formulario
            valor={nueva} cambiar={setNueva} color={color}
            guardando={ocupado === "nueva"} textoBoton="Crear cápsula"
            onCancelar={() => { setCreando(false); setNueva(VACIO); }}
            onGuardar={() =>
              accion("nueva",
                () => crearCapsula(topicId, {
                  titulo: nueva.titulo.trim(),
                  objetivo: nueva.objetivo.trim(),
                  contenido: nueva.contenido.trim(),
                  duracion_min: nueva.duracion_min,
                  dificultad: nueva.dificultad,
                }),
                (c) => { setCapsulas((p) => [...p, c]); setNueva(VACIO); setCreando(false); })
            }
          />
        </div>
      )}

      <ol className="mt-8 space-y-3">
        {capsulas.map((c) => (
          <li key={c.id} className="overflow-hidden rounded-xl border border-[#1a1830]/10 bg-white">
            {editando === c.id ? (
              <div className="p-6">
                <h2 className="mb-5 font-display text-[1.2rem] font-medium text-[#1a1830]">
                  Editar micro-cápsula
                </h2>
                <Formulario
                  valor={borrador} cambiar={setBorrador} color={color}
                  guardando={ocupado === c.id} textoBoton="Guardar cambios"
                  onCancelar={() => setEditando(null)}
                  onGuardar={() =>
                    accion(c.id,
                      () => editarCapsula(c.id, {
                        titulo: borrador.titulo.trim(),
                        objetivo: borrador.objetivo.trim(),
                        contenido: borrador.contenido.trim(),
                        duracion_min: borrador.duracion_min,
                        dificultad: borrador.dificultad,
                      }),
                      (r) => {
                        setCapsulas((p) => p.map((x) => (x.id === r.id ? r : x)));
                        setEditando(null);
                      })
                  }
                />
              </div>
            ) : (
              <div className="flex flex-col gap-4 p-4 sm:flex-row sm:gap-5 sm:p-5">
                <div className="flex min-w-0 flex-1 gap-4">
                  <span
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md font-mono text-[13px]"
                    style={{ backgroundColor: `${color}1a`, color }}
                  >
                    {c.orden}
                  </span>

                  <div className="min-w-0 flex-1">
                    <h2 className="text-[15.5px] font-medium text-[#1a1830]">{c.titulo}</h2>
                    <p className="mt-1 text-[13.5px] text-[#6b6788]">{c.objetivo}</p>
                    <p className="mt-2 line-clamp-2 text-[13px] leading-relaxed text-[#8e8ba5]">
                      {c.contenido}
                    </p>
                    <p className="mt-2.5 break-all font-mono text-[10.5px] uppercase tracking-[0.12em] text-[#a5a2b8]">
                      {c.duracion_min} min · {DIFICULTAD[c.dificultad]} · {c.id}
                    </p>
                  </div>
                </div>

                <div className="flex shrink-0 flex-wrap items-center justify-end gap-1 pl-[3.25rem] sm:flex-col sm:items-end sm:justify-between sm:gap-0 sm:pl-0">
                  <button
                    disabled={ocupado === c.id}
                    onClick={() => accion(c.id, () => alternarCapsula(c.id),
                      (r) => setCapsulas((p) => p.map((x) => (x.id === r.id ? r : x))))}
                    aria-pressed={c.activo}
                    className="order-3 flex items-center gap-2.5 disabled:opacity-40 sm:order-1"
                  >
                    <span className="font-mono text-[10.5px] uppercase tracking-[0.14em]"
                          style={{ color: c.activo ? color : "#a5a2b8" }}>
                      {c.activo ? "Visible" : "Oculta"}
                    </span>
                    <span className="relative h-5 w-9 rounded-full transition"
                          style={{ backgroundColor: c.activo ? color : "rgba(26,24,48,0.18)" }}>
                      <span className={"absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all " +
                                       (c.activo ? "left-[18px]" : "left-0.5")} />
                    </span>
                  </button>

                  <Link
                    href={`/temas/${topicId}/${c.id}`}
                    className="order-1 rounded-md px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:bg-[#1a1830]/5 hover:text-[#1a1830] sm:order-2"
                  >
                    Preguntas
                  </Link>

                  <button
                    onClick={() => abrirEdicion(c)}
                    className="order-2 rounded-md px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:bg-[#1a1830]/5 hover:text-[#1a1830] sm:order-3"
                  >
                    Editar
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
      </ol>

      {capsulas.length === 0 && !creando && (
        <div className="mt-8 rounded-xl border border-dashed border-[#1a1830]/15 py-14 text-center">
          <p className="text-[14.5px] text-[#8e8ba5]">
            Sin cápsulas, el bot no tiene nada que enviar para este tema.
          </p>
        </div>
      )}
    </>
  );
}