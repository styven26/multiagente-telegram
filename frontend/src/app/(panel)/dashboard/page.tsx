"use client";

import { Fragment, useEffect, useState } from "react";

import {
  detalleEstudiante,
  resumenDocente,
  type CeldaMapa,
  type DetalleEstudiante,
  type DominioTema,
  type ProgresoEstudiante,
  type ResumenDocente,
  type RetornoDia,
} from "@/lib/api";

/* ---------------------------------------------------------------- tokens */

const TINTA = "#1a1830";
const AMBAR = "#e0a030";
const VERDE = "#3aa17e";
const ROJO = "#c0392b";
const AZUL = "#4b6bbd";
const MEDIO = "#6b6788";
const TENUE = "#a5a2b8";

/** Umbrales de dominio. Cambiarlos aquí los cambia en todo el panel. */
const DOMINIO_ALTO = 0.8;
const DOMINIO_MEDIO = 0.5;

/** Color por unidad. Sirve de código visual compartido entre mapa y ficha. */
const COLOR_UNIDAD: Record<number, string> = {
  1: AMBAR,
  2: VERDE,
  3: AZUL,
  4: TINTA,
};

function colorUnidad(u: number | null) {
  return u ? COLOR_UNIDAD[u] ?? MEDIO : MEDIO;
}

function pct(n: number) {
  return `${Math.round(n * 100)}%`;
}

function pct1(n: number) {
  return `${(n * 100).toFixed(1)}%`;
}

function colorDominio(n: number) {
  if (n >= DOMINIO_ALTO) return VERDE;
  if (n >= DOMINIO_MEDIO) return AMBAR;
  return ROJO;
}

function fecha(iso: string) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString("es-EC", {
    day: "2-digit",
    month: "short",
  });
}

function fechaCorta(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("es-EC", {
    day: "2-digit",
    month: "short",
  });
}

function duracion(seg: number) {
  if (!seg || seg < 60) return "menos de 1 min";
  const h = Math.floor(seg / 3600);
  const m = Math.round((seg % 3600) / 60);
  return h ? `${h} h ${m} min` : `${m} min`;
}

/* ------------------------------------------------------- tarjetas de KPI */

/** Medidor semicircular. Solo para métricas con denominador real. */
function Medidor({ valor, color }: { valor: number; color: string }) {
  const arco = Math.PI * 34;
  const v = Math.min(1, Math.max(0, valor));
  return (
    <svg viewBox="0 0 80 48" className="h-12 w-20 shrink-0" aria-hidden>
      <path d="M6 42 A34 34 0 0 1 74 42" fill="none"
            stroke="rgba(26,24,48,0.09)" strokeWidth="7" strokeLinecap="round" />
      <path d="M6 42 A34 34 0 0 1 74 42" fill="none"
            stroke={color} strokeWidth="7" strokeLinecap="round"
            strokeDasharray={arco} strokeDashoffset={arco * (1 - v)}
            style={{ transition: "stroke-dashoffset 800ms ease" }} />
    </svg>
  );
}

function Tarjeta({
  etiqueta, valor, nota, color, ratio, marca,
}: {
  etiqueta: string;
  valor: string;
  nota: string;
  color: string;
  ratio?: number;
  marca?: string;
}) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-[#1a1830]/10 bg-white p-5">
      <span className="absolute inset-x-0 top-0 h-[3px]"
            style={{ background: `linear-gradient(90deg, ${color}, ${color}22)` }} />

      <p className="font-mono text-[9.5px] uppercase tracking-[0.15em] text-[#6b6788]">
        {etiqueta}
      </p>

      <div className="mt-4 flex items-end justify-between gap-3">
        <div>
          <p className="font-display text-[2.3rem] font-medium leading-none"
             style={{ color: ratio === undefined ? TINTA : color }}>
            {valor}
          </p>
          <p className="mt-2 text-[12px] leading-snug text-[#a5a2b8]">{nota}</p>
        </div>

        {ratio !== undefined ? (
          <Medidor valor={ratio} color={color} />
        ) : (
          <span
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full font-mono text-[15px]"
            style={{ backgroundColor: `${color}1a`, color }}
          >
            {marca}
          </span>
        )}
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------- embudo */

/**
 * Embudo vertical. La altura de cada columna es proporcional a su valor, así
 * la caída se ve como diferencia de altura sin leer un solo número.
 */
function Embudo({ registrados, iniciaron, completaron }: {
  registrados: number; iniciaron: number; completaron: number;
}) {
  const base = Math.max(registrados, 1);

  const pasos = [
    {
      etiqueta: "Registrados",
      valor: registrados,
      detalle: "Aceptaron el consentimiento",
      cifra: String(registrados),
      color: TINTA,
    },
    {
      etiqueta: "Tasa de inicio",
      valor: iniciaron,
      detalle: "Abrieron y cerraron una cápsula",
      cifra: pct1(registrados ? iniciaron / registrados : 0),
      color: AMBAR,
    },
    {
      etiqueta: "Tasa de finalización",
      valor: completaron,
      detalle: "Terminaron al menos un quiz",
      cifra: pct1(iniciaron ? completaron / iniciaron : 0),
      color: VERDE,
    },
  ];

  return (
    <div className="rounded-xl border border-[#1a1830]/10 bg-white p-6">
      <div className="flex items-end gap-6" style={{ height: 190 }}>
        {pasos.map((p) => {
          const alto = `${Math.max(4, (p.valor / base) * 100)}%`;
          return (
            <div key={p.etiqueta} className="flex h-full flex-1 flex-col justify-end">
              <p className="mb-2 text-center font-mono text-[12px]" style={{ color: p.color }}>
                {p.valor}
              </p>
              <div className="w-full rounded-t-md"
                   style={{ height: alto, backgroundColor: p.color,
                            transition: "height 800ms ease" }} />
            </div>
          );
        })}
      </div>

      <div className="mt-5 grid grid-cols-3 gap-3 border-t border-[#1a1830]/10 pt-5 sm:gap-6">
        {pasos.map((p) => (
          <div key={p.etiqueta}>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-sm" style={{ backgroundColor: p.color }} />
              <p className="font-mono text-[9.5px] uppercase tracking-[0.14em] text-[#6b6788]">
                {p.etiqueta}
              </p>
            </div>
            <p className="mt-2 font-display text-[1.15rem] font-medium leading-none sm:text-[1.5rem]"
               style={{ color: p.color }}>
              {p.cifra}
            </p>
            <p className="mt-1.5 text-[12px] text-[#a5a2b8]">{p.detalle}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------- retorno D1 */

/**
 * Serie diaria de retorno. Se omiten los días marcados como parciales: el día
 * en curso saldría en 0% porque su "día siguiente" todavía no ocurre.
 */
function SerieRetorno({ dias }: { dias: RetornoDia[] }) {
  const utiles = dias.filter((d) => !d.parcial);

  if (utiles.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-[#1a1830]/15 py-12 text-center">
        <p className="text-[14px] text-[#8e8ba5]">
          Todavía no hay días cerrados. El retorno aparece cuando pase el primer
          día completo de uso.
        </p>
      </div>
    );
  }

  /* El ancho del viewBox crece con los días para que el SVG se dibuje a
     escala 1:1 con su minWidth. Con un ancho fijo, estirarlo agrandaba
     también la altura y amontonaba las fechas unas sobre otras. */
  const POR_DIA = 58;
  const ANCHO = Math.max(420, utiles.length * POR_DIA);
  const ALTO = 190;
  const PAD_X = 34;
  const PAD_ARRIBA = 26;
  const PAD_ABAJO = 34;
  const util = ANCHO - PAD_X * 2;
  const alturaUtil = ALTO - PAD_ARRIBA - PAD_ABAJO;

  const puntos = utiles.map((d, i) => {
    const p = d.activos ? d.volvieron / d.activos : 0;
    const x = utiles.length === 1
      ? ANCHO / 2
      : PAD_X + (i / (utiles.length - 1)) * util;
    const y = PAD_ARRIBA + alturaUtil * (1 - p);
    return { x, y, p, d };
  });

  const linea = puntos.map((pt) => `${pt.x},${pt.y}`).join(" ");
  const area = `${puntos[0].x},${PAD_ARRIBA + alturaUtil} ${linea} ${
    puntos[puntos.length - 1].x
  },${PAD_ARRIBA + alturaUtil}`;

  const promedio = puntos.reduce((acc, pt) => acc + pt.p, 0) / puntos.length;

  /* "29/08": ancho fijo y sin construir un Date, que volvería a traer el
     problema de zona horaria que ya corregimos en las métricas. */
  const diaMes = (iso: string) => `${iso.slice(8, 10)}/${iso.slice(5, 7)}`;

  return (
    <div className="rounded-xl border border-[#1a1830]/10 bg-white p-6">
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${ANCHO} ${ALTO}`}
            style={{ minWidth: `${ANCHO}px` }}
            className="h-auto w-full" role="img"
            aria-label="Retorno al día siguiente por fecha">
          <defs>
            <linearGradient id="degradadoRetorno" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={VERDE} stopOpacity="0.22" />
              <stop offset="100%" stopColor={VERDE} stopOpacity="0" />
            </linearGradient>
          </defs>

          {[0, 0.5, 1].map((g) => (
            <g key={g}>
              <line x1={PAD_X} x2={ANCHO - PAD_X}
                    y1={PAD_ARRIBA + alturaUtil * (1 - g)}
                    y2={PAD_ARRIBA + alturaUtil * (1 - g)}
                    stroke="rgba(26,24,48,0.08)" strokeWidth="1" />
              <text x={0} y={PAD_ARRIBA + alturaUtil * (1 - g) + 4}
                    fontSize="10" fill={TENUE} fontFamily="ui-monospace, monospace">
                {pct(g)}
              </text>
            </g>
          ))}

          {utiles.length > 1 && <polygon points={area} fill="url(#degradadoRetorno)" />}
          {utiles.length > 1 && (
            <polyline points={linea} fill="none" stroke={VERDE}
                      strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          )}

          {puntos.map((pt) => (
            <g key={pt.d.dia}>
              <circle cx={pt.x} cy={pt.y} r="5" fill="#fff"
                      stroke={VERDE} strokeWidth="2.5" />
              <text x={pt.x} y={pt.y - 13} fontSize="11" textAnchor="middle"
                    fill={TINTA} fontFamily="ui-monospace, monospace">
                {pct(pt.p)}
              </text>
              <text x={pt.x} y={ALTO - 14} fontSize="10.5" textAnchor="middle"
                    fill={MEDIO} fontFamily="ui-monospace, monospace">
                {diaMes(pt.d.dia)}
              </text>
              <text x={pt.x} y={ALTO - 2} fontSize="9.5" textAnchor="middle"
                    fill={TENUE} fontFamily="ui-monospace, monospace">
                {pt.d.volvieron}/{pt.d.activos}
              </text>
            </g>
          ))}
        </svg>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-6 gap-y-1 border-t border-[#1a1830]/10 pt-4">
        <p className="font-mono text-[11px] text-[#6b6788]">
          Promedio: <span style={{ color: VERDE }}>{pct1(promedio)}</span>
        </p>
        <p className="text-[12.5px] text-[#a5a2b8]">
          {utiles.length} {utiles.length === 1 ? "día cerrado" : "días cerrados"} ·
          el día en curso no se grafica
        </p>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------- mapa del curso */

/** Una casilla: relleno = tema terminado, contorno = empezado sin terminar. */
function Celda({ c }: { c: CeldaMapa | undefined }) {
  const vacia = !c || (c.dominio === null && c.respuestas === 0);

  if (vacia) {
    return (
      <div className="mx-auto h-9 w-14 rounded-md bg-[#1a1830]/[0.07]"
           title="Sin iniciar" />
    );
  }

  const nivel = c!.dominio;
  const col = colorDominio(nivel ?? 0);
  const terminado = c!.completadas > 0;

  return (
    <div
      className="mx-auto flex h-9 w-14 items-center justify-center rounded-md font-mono text-[12px]"
      style={terminado
        ? { backgroundColor: col, color: "#fff" }
        : { border: `2px solid ${col}`, color: col }}
      title={terminado
        ? `Dominio ${pct(nivel ?? 0)} · ${c!.respuestas} respuestas`
        : `Empezado sin terminar · ${c!.respuestas} respuestas`}
    >
      {nivel === null ? "·" : Math.round(nivel * 100)}
    </div>
  );
}

/**
 * Mapa de calor del curso: una fila por estudiante, una columna por tema.
 *
 * Es la vista que responde "dónde se traba el grupo" sin leer un solo número:
 * una columna roja señala un tema mal calibrado, y una fila gris completa es
 * un estudiante que no ha entrado. Con una tabla de texto, las dos cosas se
 * pierden entre las celdas.
 */
function MapaCurso({ temas, estudiantes }: {
  temas: DominioTema[]; estudiantes: ProgresoEstudiante[];
}) {
  const [unidad, setUnidad] = useState<number | null>(null);   // null = todas
  if (temas.length === 0 || estudiantes.length === 0) {
    return (
      <div className="mt-5 rounded-xl border border-dashed border-[#1a1830]/15 py-12 text-center">
        <p className="text-[14px] text-[#8e8ba5]">
          El mapa aparece cuando haya temas activos y estudiantes registrados.
        </p>
      </div>
    );
  }

  /* Columnas por unidad. Ordenadas por Topic.orden salían U1, U2, U4, U3, U1…
    y había que ir leyendo cada etiqueta; por unidad, el avance se lee como
    una diagonal y los huecos saltan solos. */
  const ordenadas = [...temas].sort((a, b) => (a.unidad ?? 99) - (b.unidad ?? 99));

  const unidades = [...new Set(
    ordenadas.map((t) => t.unidad).filter((u): u is number => u !== null),
  )].sort((a, b) => a - b);

  const columnas = unidad === null
    ? ordenadas
    : ordenadas.filter((t) => t.unidad === unidad);

  const filtros: { clave: number | null; texto: string }[] = [
    { clave: null, texto: "Todas" },
    ...unidades.map((u) => ({ clave: u, texto: `U${u}` })),
  ];

  /* Los que menos avanzaron, arriba: el que no ha entrado es el que urge ver.
     A igual avance, primero el que menos ha respondido. */
  const filas = [...estudiantes].sort(
    (a, b) =>
      a.temas_completados - b.temas_completados || a.respuestas - b.respuestas,
  );

  const leyenda = [
    { etiqueta: "80% o más", estilo: { backgroundColor: VERDE } },
    { etiqueta: "50 a 79%", estilo: { backgroundColor: AMBAR } },
    { etiqueta: "menos de 50%", estilo: { backgroundColor: ROJO } },
    { etiqueta: "empezado, sin terminar", estilo: { border: `2px solid ${MEDIO}` } },
    { etiqueta: "sin iniciar", estilo: { backgroundColor: "rgba(26,24,48,0.07)" } },
  ];

  return (
    <>
      {unidades.length > 1 && (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-[#a5a2b8]">
            Unidad
          </span>
          {filtros.map((f) => (
            <button
              key={String(f.clave)}
              onClick={() => setUnidad(f.clave)}
              className={
                "rounded-md px-2.5 py-1 font-mono text-[10.5px] uppercase tracking-[0.12em] transition " +
                (unidad === f.clave
                  ? "bg-[#1a1830] text-white"
                  : "text-[#6b6788] hover:bg-[#1a1830]/5 hover:text-[#1a1830]")
              }
            >
              {f.texto}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 overflow-hidden rounded-xl border border-[#1a1830]/10 bg-white">
        <div className="max-h-[34rem] overflow-auto">
          <table className="w-full text-left">
            <thead>
              <tr>
                {/* La esquina es pegajosa en los dos ejes: es la única celda
                    que se cruza con la cabecera y con la columna del código. */}
                <th className="sticky left-0 top-0 z-30 bg-white px-5" />
                {columnas.map((t) => (
                  <th key={t.topic_id}
                      className="sticky top-0 z-20 h-[140px] bg-white px-1 align-bottom">
                    <div className="flex h-full flex-col items-center justify-end gap-2 pb-1">
                      <span className="whitespace-nowrap text-[9.5px] text-[#6b6788] [writing-mode:vertical-rl] rotate-180">
                        {t.nombre}
                      </span>
                      <span className="font-mono text-[9px] font-semibold"
                            style={{ color: colorUnidad(t.unidad) }}>
                        U{t.unidad ?? "—"}
                      </span>
                      <span className="h-[3px] w-8 rounded-full"
                            style={{ backgroundColor: colorUnidad(t.unidad) }} />
                    </div>
                  </th>
                ))}
                <th className="sticky top-0 z-20 bg-white px-5 pb-3 align-bottom">
                  <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-[#a5a2b8]">
                    Avance
                  </span>
                </th>
              </tr>
            </thead>

            <tbody>
              {filas.map((e) => {
                // El panel y la API se despliegan por separado: mientras una
                // va por delante de la otra, `celdas` puede no venir.
                const porTema = new Map((e.celdas ?? []).map((c) => [c.topic_id, c]));
                const inactivo = e.respuestas === 0;
                return (
                  <tr key={e.codigo_anonimo} className="transition hover:bg-[#faf8f5]">
                    <td className="sticky left-0 z-10 whitespace-nowrap bg-white px-5 py-1.5 font-mono text-[12px]"
                        style={{ color: inactivo ? ROJO : TINTA }}>
                      {e.codigo_anonimo}
                    </td>
                    {columnas.map((t) => (
                      <td key={t.topic_id} className="px-1 py-1.5">
                        <Celda c={porTema.get(t.topic_id)} />
                      </td>
                    ))}
                    <td className="px-5 py-1.5 font-mono text-[12px] text-[#6b6788]">
                      {e.temas_completados}/{e.total_temas}
                    </td>
                  </tr>
                );
              })}
            </tbody>

            <tfoot>
              {/* El promedio se queda abajo mientras se recorren las filas:
                  es la lectura que convierte el mapa en una decisión. */}
              <tr className="sticky bottom-0 z-20 bg-white">
                <td className="sticky left-0 z-30 border-t border-[#1a1830]/10 bg-white px-5 py-4 text-[13px] font-medium text-[#1a1830]">
                  Promedio
                </td>
                {columnas.map((t) => (
                  <td key={t.topic_id}
                      className="border-t border-[#1a1830]/10 bg-white px-1 py-4 text-center font-mono text-[13px]"
                      style={{ color: colorDominio(t.dominio) }}>
                    {pct(t.dominio)}
                  </td>
                ))}
                <td className="border-t border-[#1a1830]/10 bg-white" />
              </tr>
            </tfoot>
          </table>
        </div>

        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-[#1a1830]/10 px-5 py-4">
          {leyenda.map((l) => (
            <div key={l.etiqueta} className="flex items-center gap-2">
              <span className="h-4 w-7 rounded-[5px]" style={l.estilo} />
              <span className="text-[12px] text-[#6b6788]">{l.etiqueta}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

/* ----------------------------------------------- ficha de un estudiante */

function Dato({ etiqueta, valor, color }: {
  etiqueta: string; valor: string; color?: string;
}) {
  return (
    <div>
      <p className="font-mono text-[9px] uppercase tracking-[0.14em] text-[#a5a2b8]">
        {etiqueta}
      </p>
      <p className="mt-1.5 text-[14px] font-medium" style={{ color: color ?? TINTA }}>
        {valor}
      </p>
    </div>
  );
}

function FichaEstudiante({ d }: { d: DetalleEstudiante }) {
  const ahora = Date.now();

  return (
    <div className="border-l-[3px] bg-[#faf8f5] px-6 py-5" style={{ borderColor: AMBAR }}>
      <div className="flex flex-wrap gap-x-10 gap-y-4">
        <Dato etiqueta="Registrado" valor={fechaCorta(d.registrado_en)} />
        <Dato etiqueta="Última actividad"
              valor={d.ultima_actividad ? fechaCorta(d.ultima_actividad) : "Nunca"}
              color={d.ultima_actividad ? undefined : ROJO} />
        <Dato etiqueta="Tiempo de estudio" valor={duracion(d.tiempo_estudio_seg)} />
        <Dato etiqueta="Sesiones"
              valor={`${d.sesiones_iniciadas} · ${d.sesiones_completadas} hechas · ${d.sesiones_abandonadas} dejadas`} />
        <Dato etiqueta="Tasa de finalización"
              valor={d.sesiones_iniciadas
                ? pct(d.sesiones_completadas / d.sesiones_iniciadas)
                : "—"} />
        <Dato etiqueta="Repasos"
              valor={d.repasos_vencidos
                ? `${d.repasos_vencidos} vencidos`
                : d.proximo_repaso
                  ? `siguiente ${fechaCorta(d.proximo_repaso)}`
                  : "sin programar"}
              color={d.repasos_vencidos ? ROJO : undefined} />
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[46rem] text-left">
          <thead>
            <tr className="border-b border-[#1a1830]/10">
              {["Unidad", "Tema", "Dominio", "Resp.", "Aciertos",
                "Cápsulas", "Últ. repaso", "Próximo"].map((h) => (
                <th key={h}
                    className="px-3 py-2 font-mono text-[9px] font-normal uppercase tracking-[0.14em] text-[#a5a2b8]">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1a1830]/[0.05]">
            {d.temas.map((t) => {
              const vencido = !!t.proximo_repaso
                && new Date(t.proximo_repaso).getTime() <= ahora;
              const hecho = t.capsulas_completadas > 0;
              return (
                <tr key={t.topic_id}>
                  <td className="px-3 py-2.5">
                    <span className="flex h-7 w-9 items-center justify-center rounded-md font-mono text-[11px] text-white"
                          style={{ backgroundColor: colorUnidad(t.unidad) }}>
                      {t.unidad ?? "—"}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-[13.5px] text-[#1a1830]">{t.nombre}</td>
                  <td className="px-3 py-2.5">
                    {t.dominio === null ? (
                      <span className="text-[13px] text-[#a5a2b8]">—</span>
                    ) : (
                      <div className="flex items-center gap-2.5">
                        <div className="h-1.5 w-16 overflow-hidden rounded-full bg-[#1a1830]/[0.07]">
                          <div className="h-full rounded-full"
                               style={{ width: pct(t.dominio),
                                        backgroundColor: colorDominio(t.dominio) }} />
                        </div>
                        <span className="font-mono text-[12px]"
                              style={{ color: colorDominio(t.dominio) }}>
                          {pct(t.dominio)}
                        </span>
                      </div>
                    )}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[12.5px] text-[#6b6788]">
                    {t.respuestas}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[12.5px] text-[#6b6788]">
                    {t.aciertos}
                  </td>
                  <td className="px-3 py-2.5 font-mono text-[12.5px]"
                      style={{ color: hecho ? MEDIO : TENUE }}>
                    {t.capsulas_completadas} de {t.capsulas_total}
                  </td>
                  <td className="px-3 py-2.5 text-[13px] text-[#6b6788]">
                    {fechaCorta(t.ultimo_repaso)}
                  </td>
                  <td className="px-3 py-2.5 text-[13px]"
                      style={{ color: vencido ? ROJO : MEDIO,
                               fontWeight: vencido ? 500 : 400 }}>
                    {t.proximo_repaso
                      ? (vencido ? "vencido" : fechaCorta(t.proximo_repaso))
                      : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-[12px] text-[#a5a2b8]">
        Un dominio en «—» significa que todavía no hay evidencia, no que esté en
        cero: son cosas distintas y conviene no confundirlas.
      </p>
    </div>
  );
}

/* ------------------------------------------------------- tabla individual */

type Orden = "actividad" | "aciertos" | "avance" | "sin_iniciar";

function TablaEstudiantes({ filas }: { filas: ProgresoEstudiante[] }) {
  const [orden, setOrden] = useState<Orden>("actividad");
  const [abierta, setAbierta] = useState<string | null>(null);
  const [detalles, setDetalles] = useState<Record<string, DetalleEstudiante>>({});
  const [cargando, setCargando] = useState<string | null>(null);
  const [fallo, setFallo] = useState<string | null>(null);

  /* El detalle se pide una vez por estudiante y se guarda: volver a abrir la
     misma fila no debería costar otro viaje al servidor. */
  async function alternar(codigo: string) {
    if (abierta === codigo) {
      setAbierta(null);
      return;
    }
    setAbierta(codigo);
    setFallo(null);
    if (detalles[codigo]) return;

    setCargando(codigo);
    try {
      const d = await detalleEstudiante(codigo);
      setDetalles((previos) => ({ ...previos, [codigo]: d }));
    } catch (e) {
      setFallo(e instanceof Error ? e.message : "No se pudo cargar el detalle.");
    } finally {
      setCargando(null);
    }
  }

  if (filas.length === 0) {
    return (
      <div className="mt-5 rounded-xl border border-dashed border-[#1a1830]/15 py-12 text-center">
        <p className="text-[14px] text-[#8e8ba5]">
          Ningún estudiante se ha registrado en el bot todavía.
        </p>
      </div>
    );
  }

  const ordenadas = [...filas].sort((a, b) => {
    if (orden === "aciertos") {
      const pa = a.respuestas ? a.aciertos / a.respuestas : -1;
      const pb = b.respuestas ? b.aciertos / b.respuestas : -1;
      return pb - pa;
    }
    if (orden === "avance") {
      const pa = a.total_temas ? a.temas_completados / a.total_temas : 0;
      const pb = b.total_temas ? b.temas_completados / b.total_temas : 0;
      return pb - pa;
    }
    if (orden === "sin_iniciar") {
      return a.respuestas - b.respuestas;
    }
    return (
      new Date(b.ultima_actividad ?? 0).getTime() -
      new Date(a.ultima_actividad ?? 0).getTime()
    );
  });

  const opciones = [
    { clave: "actividad", texto: "Actividad reciente" },
    { clave: "avance", texto: "Avance" },
    { clave: "aciertos", texto: "Aciertos" },
    { clave: "sin_iniciar", texto: "Sin iniciar" },
  ] as const;

  return (
    <>
      <div className="mt-4 flex flex-wrap items-center gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-[#a5a2b8]">
          Ordenar por
        </span>
        {opciones.map((o) => (
          <button
            key={o.clave}
            onClick={() => setOrden(o.clave)}
            className={
              "rounded-md px-2.5 py-1 font-mono text-[10.5px] uppercase tracking-[0.12em] transition " +
              (orden === o.clave
                ? "bg-[#1a1830] text-white"
                : "text-[#6b6788] hover:bg-[#1a1830]/5 hover:text-[#1a1830]")
            }
          >
            {o.texto}
          </button>
        ))}
      </div>

      {fallo && (
        <p className="mt-3 text-[13px] text-[#c0392b]">{fallo}</p>
      )}

      <div className="mt-4 overflow-hidden rounded-xl border border-[#1a1830]/10 bg-white">
        <div className="max-h-[40rem] overflow-auto">
          <table className="w-full min-w-[52rem] text-left">
            <thead className="sticky top-0 z-20 bg-white">
              <tr className="border-b border-[#1a1830]/10">
                {["Código", "Avance por temas", "En qué va", "Aciertos",
                  "Última actividad", ""].map((h) => (
                  <th key={h}
                      className="bg-white px-5 py-3 font-mono text-[10px] font-normal uppercase tracking-[0.14em] text-[#a5a2b8]">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1a1830]/[0.07]">
              {ordenadas.map((e) => {
                const avance = e.total_temas ? e.temas_completados / e.total_temas : 0;
                const acierto = e.respuestas ? e.aciertos / e.respuestas : null;
                const activa = abierta === e.codigo_anonimo;
                return (
                  <Fragment key={e.codigo_anonimo}>
                    <tr onClick={() => alternar(e.codigo_anonimo)}
                        className={"cursor-pointer transition " +
                          (activa ? "bg-[#faf8f5]" : "hover:bg-[#faf8f5]")}>
                      <td className="px-5 py-3.5 font-mono text-[12.5px] text-[#1a1830]">
                        {e.codigo_anonimo}
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="h-1.5 w-24 overflow-hidden rounded-full bg-[#1a1830]/[0.07]">
                            <div className="h-full rounded-full"
                                 style={{ width: pct(avance), backgroundColor: AMBAR }} />
                          </div>
                          <span className="font-mono text-[12px] text-[#6b6788]">
                            {e.temas_completados}/{e.total_temas}
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-[13.5px]">
                        {e.tema_actual ? (
                          <span className="text-[#1a1830]">
                            <span className="font-mono text-[11.5px]"
                                  style={{ color: colorUnidad(e.unidad_actual) }}>
                              U{e.unidad_actual ?? "—"}
                            </span>
                            {" · "}
                            {e.tema_actual}
                          </span>
                        ) : (
                          <span className="text-[#a5a2b8]">— sin iniciar —</span>
                        )}
                      </td>
                      <td className="px-5 py-3.5 font-mono text-[12.5px]">
                        {acierto === null ? (
                          <span className="text-[#a5a2b8]">Sin respuestas</span>
                        ) : (
                          <>
                            <span style={{ color: colorDominio(acierto) }}>{pct(acierto)}</span>
                            <span className="ml-2 text-[11px] text-[#a5a2b8]">
                              ({e.respuestas})
                            </span>
                          </>
                        )}
                      </td>
                      <td className="px-5 py-3.5 text-[13px]"
                          style={{ color: e.ultima_actividad ? MEDIO : ROJO }}>
                        {e.ultima_actividad ? fechaCorta(e.ultima_actividad) : "Nunca"}
                      </td>
                      <td className="px-5 py-3.5 text-center text-[13px] text-[#a5a2b8]">
                        {cargando === e.codigo_anonimo ? "…" : activa ? "▲" : "▼"}
                      </td>
                    </tr>

                    {activa && detalles[e.codigo_anonimo] && (
                      <tr>
                        <td colSpan={6} className="p-0">
                          <FichaEstudiante d={detalles[e.codigo_anonimo]} />
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

/* ----------------------------------------------------------------- página */

function Seccion({ titulo, nota, children }: {
  titulo: string; nota?: string; children: React.ReactNode;
}) {
  return (
    <section className="mt-12">
      <h2 className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6788]">
        {titulo}
      </h2>
      {nota && <p className="mt-1.5 text-[13px] text-[#a5a2b8]">{nota}</p>}
      {children}
    </section>
  );
}

export default function PaginaResumen() {
  const [datos, setDatos] = useState<ResumenDocente | null>(null);
  const [sinEndpoint, setSinEndpoint] = useState(false);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    resumenDocente()
      .then(setDatos)
      .catch(() => setSinEndpoint(true))
      .finally(() => setCargando(false));
  }, []);

  if (cargando) {
    return (
      <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6788]">
        Cargando…
      </p>
    );
  }

  const pocosDatos = !!datos && datos.total_estudiantes < 10;
  const diasCerrados = datos
    ? datos.embudo.retorno.filter((d) => !d.parcial).length
    : 0;

  return (
    <>
      <h1 className="font-display text-[2rem] font-medium tracking-tight text-[#1a1830]">
        Resumen
      </h1>
      <p className="mt-2 text-[15px] text-[#6b6788]">
        Avance del grupo y de cada estudiante. Los estudiantes se identifican por
        código anónimo.
      </p>

      {sinEndpoint && (
        <div className="mt-8 border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-3 pl-4 pr-4">
          <p className="text-[13.5px] leading-relaxed text-[#8c2b20]">
            No se pudo leer <code className="font-mono">/api/teacher/metrics/overview</code>.
            Revisa que el backend esté corriendo.
          </p>
        </div>
      )}

      {pocosDatos && (
        <div className="mt-8 border-l-2 border-[#e0a030] bg-[#e0a030]/[0.07] py-3 pl-4 pr-4">
          <p className="text-[13.5px] leading-relaxed text-[#7a5a12]">
            Con {datos!.total_estudiantes}{" "}
            {datos!.total_estudiantes === 1 ? "estudiante" : "estudiantes"}, los
            porcentajes se mueven mucho con cada respuesta. Léelos junto al número
            de casos, no solos.
          </p>
        </div>
      )}

      {datos && (
        <>
          <section className="mt-9 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Tarjeta
              etiqueta="Activos (7 días)"
              valor={String(datos.estudiantes_activos)}
              nota={`de ${datos.total_estudiantes} registrados`}
              color={AZUL}
              ratio={datos.total_estudiantes
                ? datos.estudiantes_activos / datos.total_estudiantes : 0}
            />
            <Tarjeta
              etiqueta="Tasa de acierto"
              valor={pct(datos.tasa_acierto)}
              nota="Sobre todas las respuestas"
              color={colorDominio(datos.tasa_acierto)}
              ratio={datos.tasa_acierto}
            />
            <Tarjeta
              etiqueta="Cápsulas completadas"
              valor={String(datos.capsulas_entregadas)}
              nota="Quizzes terminados"
              color={AMBAR}
              marca="✓"
            />
            <Tarjeta
              etiqueta="Días con datos"
              valor={String(diasCerrados)}
              nota="Días cerrados y medibles"
              color={MEDIO}
              marca="◷"
            />
          </section>

          <Seccion
            titulo="Embudo de adopción"
            nota="Cada escalón se calcula sobre el anterior. La diferencia de altura muestra dónde se pierde gente."
          >
            <div className="mt-5">
              <Embudo
                registrados={datos.embudo.registrados}
                iniciaron={datos.embudo.iniciaron}
                completaron={datos.embudo.completaron}
              />
            </div>
          </Seccion>

          <Seccion
            titulo="Retorno al día siguiente"
            nota="De los estudiantes activos cada día, cuántos volvieron al día siguiente."
          >
            <div className="mt-5">
              <SerieRetorno dias={datos.embudo.retorno} />
            </div>
          </Seccion>

          <Seccion
            titulo="Mapa del curso"
            nota="Cada fila es un estudiante y cada columna un tema. El número es su nivel de dominio. Una columna entera en rojo significa que ese tema le costó a todo el curso. Una fila vacía, que ese estudiante aún no ha empezado. Primero aparecen los que menos han avanzado."
          >
            <MapaCurso temas={datos.dominio_por_tema} estudiantes={datos.estudiantes} />
          </Seccion>

          <Seccion
            titulo="Progreso individual"
            nota="Una fila por estudiante. Toca una fila para ver su ficha completa: tiempo de estudio, sesiones, y el detalle tema por tema."
          >
            <TablaEstudiantes filas={datos.estudiantes} />
          </Seccion>
        </>
      )}
    </>
  );
}