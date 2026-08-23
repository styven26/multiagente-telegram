"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import {
  alternarTema, crearTema, editarTema, listarTemas, type Tema,
} from "@/lib/api";

import { SIN_UNIDAD, UNIDADES, type Unidad } from "@/lib/unidades";
import { LIM, validarTema } from "@/lib/limites";

const campo =
  "w-full rounded-md border border-[#1a1830]/15 bg-white px-3 py-2 text-[14.5px] " +
  "text-[#1a1830] placeholder:text-[#a5a2b8] outline-none transition " +
  "focus:border-[#1a1830] focus:ring-4 focus:ring-[#1a1830]/10";

const etiqueta =
  "mb-1.5 block font-mono text-[10.5px] uppercase tracking-[0.14em] text-[#6b6788]";

/* ---------- Glifos ---------- */

function Glifo({ n, color }: { n: number; color: string }) {
  const t = {
    fill: "none", stroke: color, strokeWidth: 1.5,
    strokeLinecap: "round" as const, strokeLinejoin: "round" as const,
  };

  if (n === 1)
    return (
      <svg viewBox="0 0 34 34" className="h-8 w-8" aria-hidden>
        <rect x="4" y="10" width="26" height="15" rx="3.5" {...t} />
        <circle cx="11" cy="17.5" r="2.4" fill={color} />
        <path d="M17 17.5h8" {...t} />
      </svg>
    );

  if (n === 2)
    return (
      <svg viewBox="0 0 34 34" className="h-8 w-8" aria-hidden>
        <path d="M17 5v5" {...t} />
        <path d="M17 10L9.5 16M17 10l7.5 6" {...t} />
        <circle cx="9.5" cy="18.5" r="2.4" {...t} />
        <circle cx="24.5" cy="18.5" r="2.4" {...t} />
        <path d="M24.5 21v3.5a2.5 2.5 0 01-2.5 2.5h-9" {...t} />
        <path d="M15 25l-2 2 2 2" {...t} />
      </svg>
    );

  if (n === 3)
    return (
      <svg viewBox="0 0 34 34" className="h-8 w-8" aria-hidden>
        <rect x="5" y="5" width="24" height="24" rx="3" {...t} />
        <path d="M13 5v24M21 5v24M5 13h24M5 21h24" {...t} opacity="0.45" />
        <rect x="13" y="13" width="8" height="8" fill={color} opacity="0.9" />
      </svg>
    );

  if (n === 4)
    return (
      <svg viewBox="0 0 34 34" className="h-8 w-8" aria-hidden>
        <rect x="12" y="4" width="10" height="7" rx="2" {...t} />
        <rect x="3" y="23" width="10" height="7" rx="2" {...t} />
        <rect x="21" y="23" width="10" height="7" rx="2" {...t} />
        <path d="M17 11v5M17 16H8v7M17 16h9v7" {...t} />
      </svg>
    );

  return (
    <svg viewBox="0 0 34 34" className="h-8 w-8" aria-hidden>
      <circle cx="17" cy="17" r="11" {...t} strokeDasharray="3 3.5" />
      <path d="M17 12v6M17 21.5v.5" {...t} />
    </svg>
  );
}

/* ---------- Selector de prerrequisitos ---------- */

function Prerreq({
  todos, excluir, valor, cambiar, color,
}: {
  todos: Tema[]; excluir?: string; valor: string[];
  cambiar: (v: string[]) => void; color: string;
}) {
  const opciones = todos.filter((t) => t.id !== excluir);

  return (
    <div>
      <label className={etiqueta}>Prerrequisitos</label>
      {opciones.length === 0 ? (
        <p className="text-[13px] text-[#a5a2b8]">No hay otros temas todavía.</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {opciones.map((t) => {
            const puesto = valor.includes(t.id);
            return (
              <button
                key={t.id}
                type="button"
                onClick={() =>
                  cambiar(puesto ? valor.filter((x) => x !== t.id) : [...valor, t.id])
                }
                className="rounded-full border px-2.5 py-1 text-[12px] transition"
                style={{
                  borderColor: puesto ? color : "rgba(26,24,48,0.15)",
                  backgroundColor: puesto ? `${color}14` : "transparent",
                  color: puesto ? color : "#6b6788",
                }}
              >
                {puesto && "✓ "}{t.nombre}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ---------- Fila de tema ---------- */

function FilaTema({
  t, todos, editando, ocupado, color,
  eNombre, eEmoji, eDesc, eUnidad, ePrereq,
  setENombre, setEEmoji, setEDesc, setEUnidad, setEPrereq,
  abrirEdicion, cancelar, guardar, alternar, nombreDe,
}: {
  t: Tema; todos: Tema[]; editando: string | null; ocupado: string | null; color: string;
  eNombre: string; eEmoji: string; eDesc: string; eUnidad: number | null; ePrereq: string[];
  setENombre: (v: string) => void; setEEmoji: (v: string) => void;
  setEDesc: (v: string) => void; setEUnidad: (v: number | null) => void;
  setEPrereq: (v: string[]) => void;
  abrirEdicion: (t: Tema) => void; cancelar: () => void;
  guardar: (t: Tema) => void; alternar: (t: Tema) => void;
  nombreDe: (id: string) => string;
}) {
  if (editando === t.id) {
    return (
      <li className="space-y-4 py-5">
        <div className="flex flex-wrap items-end gap-3">
          <div className="w-16">
            <label className={etiqueta}>Emoji</label>
            <input
              value={eEmoji}
              onChange={(e) => setEEmoji(e.target.value)}
              maxLength={LIM.temaEmoji}
              className={campo + " text-center"}
            />
          </div>
          <div className="min-w-40 flex-1">
            <label className={etiqueta}>Nombre</label>
            <input
              value={eNombre}
              onChange={(e) => setENombre(e.target.value)}
              maxLength={LIM.temaNombre}
              className={campo}
            />
          </div>
          <div className="w-40">
            <label className={etiqueta}>Unidad</label>
            <select
              value={eUnidad ?? ""}
              onChange={(e) => setEUnidad(e.target.value ? Number(e.target.value) : null)}
              className={campo}
            >
              <option value="">Sin unidad</option>
              {UNIDADES.map((u) => (
                <option key={u.numero} value={u.numero}>{u.numero}. {u.nombre}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className={etiqueta}>Descripción</label>
            <input
              value={eDesc}
              onChange={(e) => setEDesc(e.target.value)}
              maxLength={LIM.temaDesc}
              className={campo}
            />
        </div>

        <Prerreq todos={todos} excluir={t.id} valor={ePrereq} cambiar={setEPrereq} color={color} />

        <div className="flex gap-2">
          <button
            disabled={ocupado === t.id || !validarTema({ nombre: eNombre, emoji: eEmoji, descripcion: eDesc }).ok}
            onClick={() => guardar(t)}
            className="rounded-md bg-[#1a1830] px-4 py-2 text-[14px] font-medium text-white transition hover:bg-[#2a2750] disabled:bg-[#1a1830]/25"
          >
            {ocupado === t.id ? "Guardando…" : "Guardar"}
          </button>
          <button
            onClick={cancelar}
            className="rounded-md px-3 py-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] hover:text-[#1a1830]"
          >
            Cancelar
          </button>
        </div>
      </li>
    );
  }

  return (
    <li className="flex items-center gap-4 py-4">
      <span className="text-xl" aria-hidden>{t.emoji}</span>

      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-3">
          <h3 className="text-[15px] font-medium text-[#1a1830]">{t.nombre}</h3>
          <span className="font-mono text-[10.5px] text-[#a5a2b8]">{t.id}</span>
        </div>
        {t.descripcion && <p className="mt-0.5 text-[13px] text-[#6b6788]">{t.descripcion}</p>}
        {t.prerrequisitos.length > 0 && (
          <p className="mt-1 text-[12px] text-[#8e8ba5]">
            Requiere: {t.prerrequisitos.map(nombreDe).join(" · ")}
          </p>
        )}
      </div>

      <Link
        href={`/temas/${t.id}`}
        className="rounded-md px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:bg-[#1a1830]/5 hover:text-[#1a1830]"
      >
        Micro-Cápsulas
      </Link>

      <button
        onClick={() => abrirEdicion(t)}
        className="rounded-md px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] transition hover:bg-[#1a1830]/5 hover:text-[#1a1830]"
      >
        Editar
      </button>

      <button
        disabled={ocupado === t.id}
        onClick={() => alternar(t)}
        aria-pressed={t.activo}
        title={t.activo ? "Ocultar a los estudiantes" : "Mostrar a los estudiantes"}
        className="flex w-24 items-center justify-end gap-2.5 disabled:opacity-40"
      >
        <span className="font-mono text-[10.5px] uppercase tracking-[0.14em]"
              style={{ color: t.activo ? color : "#a5a2b8" }}>
          {t.activo ? "Visible" : "Oculto"}
        </span>
        <span className="relative h-5 w-9 shrink-0 rounded-full transition"
              style={{ backgroundColor: t.activo ? color : "rgba(26,24,48,0.18)" }}>
          <span className={"absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all " +
                           (t.activo ? "left-[18px]" : "left-0.5")} />
        </span>
      </button>
    </li>
  );
}

/* ---------- Página ---------- */

export default function PaginaTemas() {
  const [temas, setTemas] = useState<Tema[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);
  const [ocupado, setOcupado] = useState<string | null>(null);
  const [abierta, setAbierta] = useState<Unidad | null>(null);

  const [creando, setCreando] = useState(false);
  const [nNombre, setNNombre] = useState("");
  const [nEmoji, setNEmoji] = useState("📘");
  const [nDesc, setNDesc] = useState("");
  const [nPrereq, setNPrereq] = useState<string[]>([]);

  const [editando, setEditando] = useState<string | null>(null);
  const [eNombre, setENombre] = useState("");
  const [eEmoji, setEEmoji] = useState("");
  const [eDesc, setEDesc] = useState("");
  const [eUnidad, setEUnidad] = useState<number | null>(null);
  const [ePrereq, setEPrereq] = useState<string[]>([]);

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch((e) => setError(e instanceof Error ? e.message : "Error inesperado"))
      .finally(() => setCargando(false));
  }, []);

  const cerrar = useCallback(() => {
    setAbierta(null); setEditando(null); setCreando(false); setError(null);
  }, []);

  useEffect(() => {
    if (!abierta) return;
    const alTeclear = (e: KeyboardEvent) => e.key === "Escape" && cerrar();
    document.addEventListener("keydown", alTeclear);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", alTeclear);
      document.body.style.overflow = "";
    };
  }, [abierta, cerrar]);

  const validas = UNIDADES.map((u) => u.numero);
  const porUnidad = (u: Unidad) =>
    u.numero === 0
      ? temas.filter((t) => t.unidad === null || !validas.includes(t.unidad))
      : temas.filter((t) => t.unidad === u.numero);

  const nombreDe = (id: string) => temas.find((t) => t.id === id)?.nombre ?? id;

  function reemplazar(t: Tema) {
    setTemas((prev) => prev.map((x) => (x.id === t.id ? t : x)));
  }

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

  function abrirEdicion(t: Tema) {
    setEditando(t.id);
    setENombre(t.nombre);
    setEEmoji(t.emoji ?? "");
    setEDesc(t.descripcion ?? "");
    setEUnidad(t.unidad);
    setEPrereq([...t.prerrequisitos]);
  }

  function guardar(t: Tema) {
    const v = validarTema({ nombre: eNombre, emoji: eEmoji, descripcion: eDesc });
    if (!v.ok) { setError(v.errores[0]); return; }
    accion(
      t.id,
      () => editarTema(t.id, {
        nombre: eNombre.trim(),
        emoji: eEmoji.trim(),
        descripcion: eDesc.trim() || null,
        unidad: eUnidad,
        prerrequisitos: ePrereq,
      }),
      (r) => { reemplazar(r); setEditando(null); },
    );
  }

  const listaAbierta = abierta ? porUnidad(abierta) : [];
  const huerfanos = porUnidad(SIN_UNIDAD);
  const tarjetas = huerfanos.length > 0 ? [...UNIDADES, SIN_UNIDAD] : UNIDADES;

  return (
    <>
      <h1 className="font-display text-[2rem] font-medium tracking-tight text-[#1a1830]">
        Contenido
      </h1>

      {error && !abierta && (
        <div role="alert" className="mt-6 border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-4 pr-3">
          <p className="text-[13.5px] text-[#8c2b20]">{error}</p>
        </div>
      )}

      <div className="mt-9 grid gap-4 sm:grid-cols-2">
        {tarjetas.map((u) => {
          const lista = porUnidad(u);
          const visibles = lista.filter((t) => t.activo).length;
          const pct = lista.length ? (visibles / lista.length) * 100 : 0;

          return (
            <button
              key={u.numero}
              onClick={() => setAbierta(u)}
              className="group relative overflow-hidden rounded-xl border bg-white p-6 text-left transition-all hover:-translate-y-0.5 hover:shadow-[0_8px_24px_-12px_rgba(26,24,48,0.35)]"
              style={{ borderColor: `${u.color}33` }}
            >
              <span aria-hidden
                className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full opacity-[0.07] transition-transform duration-500 group-hover:scale-125"
                style={{ backgroundColor: u.color }} />

              <div className="relative flex items-start justify-between">
                <Glifo n={u.numero} color={u.color} />
                <span className="font-mono text-[10.5px] uppercase tracking-[0.16em]" style={{ color: u.color }}>
                  {u.numero > 0 ? `Unidad ${u.numero}` : "Pendiente"}
                </span>
              </div>

              <h2 className="relative mt-5 font-display text-[1.3rem] font-medium leading-tight tracking-tight text-[#1a1830]">
                {u.nombre}
              </h2>
              {u.detalle && (
                <p className="relative mt-2 text-[13.5px] leading-relaxed text-[#6b6788]">{u.detalle}</p>
              )}

              <div className="relative mt-6 flex items-center gap-3">
                <div className="h-1 flex-1 overflow-hidden rounded-full bg-[#1a1830]/[0.07]">
                  <div className="h-full rounded-full transition-[width] duration-700"
                       style={{ width: `${pct}%`, backgroundColor: u.color }} />
                </div>
                <span className="shrink-0 font-mono text-[11px] text-[#6b6788]">
                  {visibles}/{lista.length}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {abierta && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-[#1a1830]/45 backdrop-blur-[2px] sm:items-center sm:p-6"
             onClick={cerrar}>
          <div
            role="dialog" aria-modal="true" aria-labelledby="titulo-unidad"
            onClick={(e) => e.stopPropagation()}
            className="flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-t-2xl bg-white shadow-2xl sm:rounded-2xl"
          >
            <header className="relative shrink-0 px-7 pb-6 pt-7"
                    style={{ backgroundColor: `${abierta.color}0d` }}>
              <span aria-hidden className="absolute inset-x-0 top-0 h-1"
                    style={{ backgroundColor: abierta.color }} />

              <div className="flex items-start gap-4">
                <Glifo n={abierta.numero} color={abierta.color} />
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-[10.5px] uppercase tracking-[0.16em]" style={{ color: abierta.color }}>
                    {abierta.numero > 0 ? `Unidad ${abierta.numero}` : "Pendiente"}
                  </p>
                  <h2 id="titulo-unidad" className="mt-1 font-display text-[1.5rem] font-medium tracking-tight text-[#1a1830]">
                    {abierta.nombre}
                  </h2>
                  {abierta.detalle && (
                    <p className="mt-1.5 text-[13.5px] leading-relaxed text-[#6b6788]">{abierta.detalle}</p>
                  )}
                </div>
                <button onClick={cerrar} aria-label="Cerrar" autoFocus
                        className="-mr-2 -mt-1 shrink-0 rounded-md p-2 text-[#8e8ba5] transition hover:bg-[#1a1830]/5 hover:text-[#1a1830]">
                  <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor"
                       strokeWidth="1.8" strokeLinecap="round" aria-hidden>
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </header>

            <div className="min-h-0 flex-1 overflow-y-auto px-7">
              {error && (
                <div role="alert" className="mt-5 border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-4 pr-3">
                  <p className="text-[13.5px] text-[#8c2b20]">{error}</p>
                </div>
              )}

              {listaAbierta.length > 0 ? (
                <ul className="divide-y divide-[#1a1830]/[0.07]">
                  {listaAbierta.map((t) => (
                    <FilaTema
                      key={t.id} t={t} todos={temas} color={abierta.color}
                      editando={editando} ocupado={ocupado}
                      eNombre={eNombre} eEmoji={eEmoji} eDesc={eDesc}
                      eUnidad={eUnidad} ePrereq={ePrereq}
                      setENombre={setENombre} setEEmoji={setEEmoji} setEDesc={setEDesc}
                      setEUnidad={setEUnidad} setEPrereq={setEPrereq}
                      abrirEdicion={abrirEdicion} cancelar={() => setEditando(null)}
                      guardar={guardar} nombreDe={nombreDe}
                      alternar={(x) => accion(x.id, () => alternarTema(x.id), reemplazar)}
                    />
                  ))}
                </ul>
              ) : (
                <p className="py-10 text-center text-[14px] text-[#a5a2b8]">
                  Esta unidad todavía no tiene temas.
                </p>
              )}

              {creando && (
                <div className="mb-6 mt-2 space-y-4 rounded-lg border border-[#1a1830]/10 bg-[#faf8f5] p-5">
                  <div className="flex gap-4">
                    <div className="w-20">
                      <label className={etiqueta}>Emoji</label>
                      <input value={nEmoji} onChange={(e) => setNEmoji(e.target.value)} className={campo + " text-center"} />
                    </div>
                    <div className="flex-1">
                      <label className={etiqueta}>Nombre</label>
                      <input value={nNombre} onChange={(e) => setNNombre(e.target.value)}
                             placeholder="Bucle for" className={campo} />
                    </div>
                  </div>

                  <div>
                    <label className={etiqueta}>Descripción</label>
                    <input value={nDesc} onChange={(e) => setNDesc(e.target.value)}
                           placeholder="Opcional" className={campo} />
                  </div>

                  <Prerreq todos={temas} valor={nPrereq} cambiar={setNPrereq} color={abierta.color} />

                  <button
                    disabled={ocupado === "nuevo" || !validarTema({ nombre: nNombre, emoji: nEmoji, descripcion: nDesc }).ok}
                    onClick={() =>
                      accion(
                        "nuevo",
                        () => crearTema({
                          nombre: nNombre.trim(),
                          emoji: nEmoji.trim() || "📘",
                          descripcion: nDesc.trim() || null,
                          unidad: abierta.numero > 0 ? abierta.numero : null,
                          prerrequisitos: nPrereq,
                        }),
                        (t) => {
                          setTemas((prev) => [...prev, t]);
                          setNNombre(""); setNDesc(""); setNEmoji("📘"); setNPrereq([]);
                          setCreando(false);
                        },
                      )
                    }
                    className="rounded-md px-4 py-2 text-[14px] font-medium text-white transition disabled:opacity-30"
                    style={{ backgroundColor: abierta.color }}
                  >
                    {ocupado === "nuevo" ? "Creando…" : `Crear en ${abierta.numero > 0 ? `Unidad ${abierta.numero}` : "Sin unidad"}`}
                  </button>
                </div>
              )}
            </div>

            <footer className="flex shrink-0 items-center justify-between border-t border-[#1a1830]/[0.09] px-7 py-4">
              <span className="font-mono text-[11px] tracking-wide text-[#a5a2b8]">
                {listaAbierta.filter((t) => t.activo).length} de {listaAbierta.length} visibles
              </span>
              <button
                onClick={() => setCreando((v) => !v)}
                className="rounded-md px-4 py-2 text-[14px] font-medium transition"
                style={{ color: creando ? "#6b6788" : "#fff", backgroundColor: creando ? "transparent" : "#1a1830" }}
              >
                {creando ? "Cancelar" : "Nuevo tema"}
              </button>
            </footer>
          </div>
        </div>
      )}
    </>
  );
}