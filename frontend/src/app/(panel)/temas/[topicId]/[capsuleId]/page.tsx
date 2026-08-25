"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import SubirImagen from "@/components/SubirImagen";

import {
  alternarPregunta, crearPregunta, editarPregunta, listarCapsulas,
  listarPreguntas, listarTemas, urlImagen, type Capsula, type Pregunta,
} from "@/lib/api";

import { colorDeUnidad } from "@/lib/unidades";
import { LIM, largo, validarPregunta } from "@/lib/limites";

const campo =
  "w-full rounded-md border border-[#1a1830]/15 bg-white px-3 py-2 text-[14.5px] " +
  "text-[#1a1830] placeholder:text-[#a5a2b8] outline-none transition " +
  "focus:border-[#1a1830] focus:ring-4 focus:ring-[#1a1830]/10";

const etiqueta =
  "mb-1.5 block font-mono text-[10.5px] uppercase tracking-[0.14em] text-[#6b6788]";

const LETRAS = ["A", "B", "C", "D", "E", "F"];
const DIFICULTAD = ["", "Básica", "Media", "Alta"];

type Borrador = {
  tipo: string; enunciado: string; imagen_url: string | null; opciones: string[];
  correcta: number; retroalimentacion: string; dificultad: number;
};

const VACIO: Borrador = {
  tipo: "opcion_multiple", enunciado: "", imagen_url: null,
  opciones: ["", "", "", ""],
  correcta: 0, retroalimentacion: "", dificultad: 1,
};

function Editor({
  valor, cambiar, color, onGuardar, onCancelar, guardando, textoBoton,
}: {
  valor: Borrador; cambiar: (v: Borrador) => void; color: string;
  onGuardar: () => void; onCancelar: () => void;
  guardando: boolean; textoBoton: string;
}) {
  const vf = valor.tipo === "verdadero_falso";
  const { ok: listo, errores } = validarPregunta(valor);

  function cambiarTipo(tipo: string) {
    if (tipo === "verdadero_falso") {
      cambiar({ ...valor, tipo, opciones: ["Verdadero", "Falso"], correcta: 0 });
    } else {
      cambiar({ ...valor, tipo, opciones: ["", "", "", ""], correcta: 0 });
    }
  }

  function editarOpcion(i: number, texto: string) {
    const ops = [...valor.opciones];
    ops[i] = texto;
    cambiar({ ...valor, opciones: ops });
  }

  function quitarOpcion(i: number) {
    const ops = valor.opciones.filter((_, x) => x !== i);
    let cor = valor.correcta;
    if (i === cor) cor = 0;
    else if (i < cor) cor -= 1;
    cambiar({ ...valor, opciones: ops, correcta: cor });
  }

  return (
    <div className="space-y-5">
      <div className="flex gap-4">
        <div className="flex-1">
          <label className={etiqueta}>Tipo</label>
          <select value={valor.tipo} onChange={(e) => cambiarTipo(e.target.value)} className={campo}>
            <option value="opcion_multiple">Opción múltiple</option>
            <option value="verdadero_falso">Verdadero / Falso</option>
          </select>
        </div>
        <div className="w-44">
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

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div>
          <label className={etiqueta}>Enunciado</label>
          <textarea
            value={valor.enunciado}
            onChange={(e) => cambiar({ ...valor, enunciado: e.target.value })}
            rows={10}
            placeholder="Si x = 5 y luego escribes x = 8, ¿qué contiene x?"
            className={campo + " resize-y font-mono text-[13.5px] leading-relaxed"}
          />
        </div>

        <SubirImagen
          valor={valor.imagen_url}
          cambiar={(u) => cambiar({ ...valor, imagen_url: u })}
          color={color}
        />
      </div>

      <div>
        <label className={etiqueta}>Opciones · marca la correcta</label>
        <div className="space-y-2">
          {valor.opciones.map((op, i) => {
            const esCorrecta = valor.correcta === i;
            return (
              <div key={i} className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => cambiar({ ...valor, correcta: i })}
                  aria-label={`Marcar opción ${LETRAS[i]} como correcta`}
                  className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 font-mono text-[11px] transition"
                  style={{
                    borderColor: esCorrecta ? color : "rgba(26,24,48,0.2)",
                    backgroundColor: esCorrecta ? color : "transparent",
                    color: esCorrecta ? "#fff" : "#8e8ba5",
                  }}
                >
                  {LETRAS[i]}
                </button>

                <input
                  value={op}
                  onChange={(e) => editarOpcion(i, e.target.value)}
                  disabled={vf}
                  placeholder={`Opción ${LETRAS[i]}`}
                  maxLength={LIM.preOpcion}
                  className={campo + (vf ? " bg-[#faf8f5] text-[#8e8ba5]" : "")}
                />

                {largo(op) > 45 && (                              // ← ④ todo este bloque
                  <span className="shrink-0 font-mono text-[10.5px] text-[#a5a2b8]">
                    {largo(op)}/{LIM.preOpcion}
                  </span>
                )}

                {!vf && valor.opciones.length > 2 && (
                  <button
                    type="button"
                    onClick={() => quitarOpcion(i)}
                    aria-label="Quitar opción"
                    className="shrink-0 rounded-md p-1.5 text-[#a5a2b8] transition hover:bg-[#c0392b]/10 hover:text-[#c0392b]"
                  >
                    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor"
                         strokeWidth="1.8" strokeLinecap="round" aria-hidden>
                      <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                  </button>
                )}
              </div>
            );
          })}
        </div>

        {!vf && valor.opciones.length < 6 && (
          <button
            type="button"
            onClick={() => cambiar({ ...valor, opciones: [...valor.opciones, ""] })}
            className="mt-2.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] hover:text-[#1a1830]"
          >
            + Añadir opción
          </button>
        )}
      </div>

      <div>
        <label className={etiqueta}>Retroalimentación</label>
        <textarea
          value={valor.retroalimentacion}
          onChange={(e) => cambiar({ ...valor, retroalimentacion: e.target.value })}
          rows={2}
          placeholder="Lo que se muestra al estudiante después de responder"
          className={campo + " resize-y"}
        />
      </div>

      {errores.length > 0 && (
        <ul className="border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-4 pr-3">
          {errores.map((e) => (
            <li key={e} className="text-[13.5px] text-[#8c2b20]">{e}</li>
          ))}
        </ul>
      )}

      <div className="flex gap-2">
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

export default function PaginaPreguntas() {
  const { topicId, capsuleId } = useParams<{ topicId: string; capsuleId: string }>();

  const [capsula, setCapsula] = useState<Capsula | null>(null);
  const [color, setColor] = useState("#8e8ba5");
  const [preguntas, setPreguntas] = useState<Pregunta[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  const [ocupado, setOcupado] = useState<string | null>(null);

  const [creando, setCreando] = useState(false);
  const [nueva, setNueva] = useState<Borrador>(VACIO);
  const [editando, setEditando] = useState<number | null>(null);
  const [borrador, setBorrador] = useState<Borrador>(VACIO);

  useEffect(() => {
    Promise.all([listarTemas(), listarCapsulas(topicId), listarPreguntas(capsuleId)])
      .then(([ts, cs, qs]) => {
        setColor(colorDeUnidad(ts.find((t) => t.id === topicId)?.unidad ?? null));
        setCapsula(cs.find((c) => c.id === capsuleId) ?? null);
        setPreguntas(qs);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Error inesperado"))
      .finally(() => setCargando(false));
  }, [topicId, capsuleId]);

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

  function abrirEdicion(p: Pregunta) {
    setEditando(p.id);
    setCreando(false);
    setBorrador({
      tipo: p.tipo, enunciado: p.enunciado, imagen_url: p.imagen_url,
      opciones: [...p.opciones],
      correcta: p.correcta, retroalimentacion: p.retroalimentacion ?? "",
      dificultad: p.dificultad,
    });
  }

  const activas = preguntas.filter((p) => p.activo).length;

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
        href={`/temas/${topicId}`}
        className="inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:text-[#1a1830]"
      >
        <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor"
             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Micro-Cápsulas
      </Link>

      <div className="mt-5 flex items-start justify-between gap-6">
        <div className="min-w-0">
          <p className="font-mono text-[10.5px] uppercase tracking-[0.16em]" style={{ color }}>
            Cápsula {capsula?.orden ?? ""} · {capsuleId}
          </p>
          <h1 className="mt-1.5 font-display text-[2rem] font-medium tracking-tight text-[#1a1830]">
            {capsula?.titulo ?? "Preguntas"}
          </h1>
          <p className="mt-2 text-[15px] text-[#6b6788]">
            {preguntas.length === 0
              ? "Sin preguntas, esta cápsula no evalúa nada."
              : `${preguntas.length} ${preguntas.length === 1 ? "pregunta" : "preguntas"} · ${activas} ${activas === 1 ? "activa" : "activas"}.`}
          </p>
        </div>

        <button
          onClick={() => { setCreando((v) => !v); setEditando(null); setNueva(VACIO); }}
          className="shrink-0 rounded-md px-4 py-2.5 text-[14px] font-medium text-white transition"
          style={{ backgroundColor: creando ? "#8e8ba5" : "#1a1830" }}
        >
          {creando ? "Cancelar" : "Nueva pregunta"}
        </button>
      </div>

      {preguntas.length > 0 && preguntas.length < 3 && (
        <div className="mt-6 border-l-2 border-[#e0a030] bg-[#e0a030]/[0.07] py-2.5 pl-4 pr-3">
          <p className="text-[13.5px] text-[#7a5a12]">
            Con menos de tres preguntas, el quiz da poca evidencia para estimar el dominio.
          </p>
        </div>
      )}

      {error && (
        <div role="alert" className="mt-6 border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-4 pr-3">
          <p className="text-[13.5px] text-[#8c2b20]">{error}</p>
        </div>
      )}

      {creando && (
        <div className="mt-7 rounded-xl border bg-white p-6" style={{ borderColor: `${color}33` }}>
          <h2 className="mb-5 font-display text-[1.2rem] font-medium text-[#1a1830]">
            Nueva pregunta
          </h2>
          <Editor
            valor={nueva} cambiar={setNueva} color={color}
            guardando={ocupado === "nueva"} textoBoton="Crear pregunta"
            onCancelar={() => { setCreando(false); setNueva(VACIO); }}
            onGuardar={() =>
              accion("nueva",
                () => crearPregunta(capsuleId, {
                  tipo: nueva.tipo,
                  enunciado: nueva.enunciado.trim(),
                  imagen_url: nueva.imagen_url,
                  opciones: nueva.opciones.map((o) => o.trim()),
                  correcta: nueva.correcta,
                  retroalimentacion: nueva.retroalimentacion.trim() || null,
                  dificultad: nueva.dificultad,
                }),
                (p) => { setPreguntas((x) => [...x, p]); setNueva(VACIO); setCreando(false); })
            }
          />
        </div>
      )}

      <ol className="mt-8 space-y-3">
        {preguntas.map((p, i) => (
          <li key={p.id} className="overflow-hidden rounded-xl border border-[#1a1830]/10 bg-white">
            {editando === p.id ? (
              <div className="p-6">
                <h2 className="mb-5 font-display text-[1.2rem] font-medium text-[#1a1830]">
                  Editar pregunta
                </h2>
                <Editor
                  valor={borrador} cambiar={setBorrador} color={color}
                  guardando={ocupado === String(p.id)} textoBoton="Guardar cambios"
                  onCancelar={() => setEditando(null)}
                  onGuardar={() =>
                    accion(String(p.id),
                      () => editarPregunta(p.id, {
                        tipo: borrador.tipo,
                        enunciado: borrador.enunciado.trim(),
                        imagen_url: borrador.imagen_url,
                        opciones: borrador.opciones.map((o) => o.trim()),
                        correcta: borrador.correcta,
                        retroalimentacion: borrador.retroalimentacion.trim() || null,
                        dificultad: borrador.dificultad,
                      }),
                      (r) => {
                        setPreguntas((x) => x.map((q) => (q.id === r.id ? r : q)));
                        setEditando(null);
                      })
                  }
                />
              </div>
            ) : (
              <div className="flex gap-5 p-5">
                <span
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md font-mono text-[13px]"
                  style={{ backgroundColor: `${color}1a`, color }}
                >
                  {i + 1}
                </span>

                <div className="min-w-0 flex-1">
                  <h2 className="text-[15.5px] font-medium leading-snug text-[#1a1830]">
                    {p.enunciado}
                  </h2>

                  {p.imagen_url && (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={urlImagen(p.imagen_url)!} alt=""
                         className="mt-3 max-h-40 w-auto rounded-md border border-[#1a1830]/10" />
                  )}

                  <ul className="mt-3 space-y-1.5">
                    {p.opciones.map((op, k) => {
                      const ok = k === p.correcta;
                      return (
                        <li key={k} className="flex items-center gap-2.5">
                          <span
                            className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border font-mono text-[10px]"
                            style={{
                              borderColor: ok ? color : "rgba(26,24,48,0.18)",
                              backgroundColor: ok ? color : "transparent",
                              color: ok ? "#fff" : "#a5a2b8",
                            }}
                          >
                            {LETRAS[k]}
                          </span>
                          <span className="text-[13.5px]" style={{ color: ok ? "#1a1830" : "#6b6788" }}>
                            {op}
                          </span>
                        </li>
                      );
                    })}
                  </ul>

                  {p.retroalimentacion && (
                    <p className="mt-3 border-l-2 border-[#1a1830]/10 pl-3 text-[13px] italic text-[#8e8ba5]">
                      {p.retroalimentacion}
                    </p>
                  )}

                  <p className="mt-3 font-mono text-[10.5px] uppercase tracking-[0.12em] text-[#a5a2b8]">
                    {DIFICULTAD[p.dificultad]} · {p.tipo.replace("_", " ")} · #{p.id}
                  </p>
                </div>

                <div className="flex shrink-0 flex-col items-end justify-between">
                  <button
                    disabled={ocupado === String(p.id)}
                    onClick={() => accion(String(p.id), () => alternarPregunta(p.id),
                      (r) => setPreguntas((x) => x.map((q) => (q.id === r.id ? r : q))))}
                    aria-pressed={p.activo}
                    className="flex items-center gap-2.5 disabled:opacity-40"
                  >
                    <span className="font-mono text-[10.5px] uppercase tracking-[0.14em]"
                          style={{ color: p.activo ? color : "#a5a2b8" }}>
                      {p.activo ? "Activa" : "Inactiva"}
                    </span>
                    <span className="relative h-5 w-9 rounded-full transition"
                          style={{ backgroundColor: p.activo ? color : "rgba(26,24,48,0.18)" }}>
                      <span className={"absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all " +
                                       (p.activo ? "left-[18px]" : "left-0.5")} />
                    </span>
                  </button>

                  <button
                    onClick={() => abrirEdicion(p)}
                    className="rounded-md px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:bg-[#1a1830]/5 hover:text-[#1a1830]"
                  >
                    Editar
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
      </ol>

      {preguntas.length === 0 && !creando && (
        <div className="mt-8 rounded-xl border border-dashed border-[#1a1830]/15 py-14 text-center">
          <p className="text-[14.5px] text-[#8e8ba5]">
            Sin preguntas no hay filas en <code className="font-mono text-[13px]">responses</code>,
            y sin ellas el Knowledge Tracing no tiene con qué entrenarse.
          </p>
        </div>
      )}
    </>
  );
}