"use client";

import { useEffect, useState } from "react";

import {
  resumenDocente,
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
      detalle: "Abrieron una cápsula",
      cifra: pct1(registrados ? iniciaron / registrados : 0),
      color: AMBAR,
    },
    {
      etiqueta: "Tasa de finalización",
      valor: completaron,
      detalle: "Terminaron un quiz",
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

  const ANCHO = 640;
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

  return (
    <div className="rounded-xl border border-[#1a1830]/10 bg-white p-6">
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${ANCHO} ${ALTO}`}
             style={{ minWidth: `${Math.max(420, utiles.length * 88)}px` }}
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
                {fecha(pt.d.dia)}
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

/* --------------------------------------------------------------- por tema */

function BarrasTema({ temas }: { temas: DominioTema[] }) {
  if (temas.length === 0) {
    return (
      <div className="mt-5 rounded-xl border border-dashed border-[#1a1830]/15 py-12 text-center">
        <p className="text-[14px] text-[#8e8ba5]">
          Sin respuestas registradas todavía.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-5 overflow-hidden rounded-xl border border-[#1a1830]/10 bg-white">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[34rem] text-left">

          <thead>
            <tr className="border-b border-[#1a1830]/10">
              {["Tema", "Nivel de dominio", "Promedio", "Respuestas"].map((h) => (
                <th key={h}
                    className="px-5 py-3 font-mono text-[10px] font-normal uppercase tracking-[0.14em] text-[#a5a2b8]">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1a1830]/[0.07]">
            {temas.map((t) => {
              const color = colorDominio(t.dominio);
              return (
                <tr key={t.topic_id} className="transition hover:bg-[#faf8f5]">
                  <td className="max-w-[15rem] truncate px-5 py-3.5 text-[14px] text-[#1a1830]"
                      title={t.nombre}>
                    {t.nombre}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="h-2 w-full max-w-[18rem] overflow-hidden rounded-full bg-[#1a1830]/[0.07]">
                      <div className="h-full rounded-full"
                          style={{ width: pct(t.dominio), backgroundColor: color,
                                    transition: "width 700ms ease" }} />
                    </div>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-[12.5px]" style={{ color }}>
                    {pct(t.dominio)}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-[12px] text-[#a5a2b8]">
                    {t.respuestas}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

/* ------------------------------------------------------- tabla individual */

function TablaEstudiantes({ filas }: { filas: ProgresoEstudiante[] }) {
  const [orden, setOrden] = useState<"actividad" | "aciertos" | "avance">("actividad");

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
    return (
      new Date(b.ultima_actividad ?? 0).getTime() -
      new Date(a.ultima_actividad ?? 0).getTime()
    );
  });

  const opciones = [
    { clave: "actividad", texto: "Actividad reciente" },
    { clave: "avance", texto: "Avance" },
    { clave: "aciertos", texto: "Aciertos" },
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

      <div className="mt-4 max-h-[26rem] overflow-auto rounded-xl border border-[#1a1830]/10 bg-white">
        <table className="w-full min-w-[34rem] text-left">
          <thead className="sticky top-0 z-10 bg-white">
            <tr className="border-b border-[#1a1830]/10">
              {["Código", "Avance por temas", "Aciertos", "Última actividad"].map((h) => (
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
              return (
                <tr key={e.codigo_anonimo} className="transition hover:bg-[#faf8f5]">
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
                  <td className="px-5 py-3.5 text-[13px] text-[#6b6788]">
                    {e.ultima_actividad
                      ? new Date(e.ultima_actividad).toLocaleDateString("es-EC", {
                          day: "2-digit",
                          month: "short",
                        })
                      : "Nunca"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
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
            titulo="Dominio por tema · promedio del grupo"
            nota={`Media entre los estudiantes que respondieron cada tema. Verde sobre ${pct(DOMINIO_ALTO)}, ámbar sobre ${pct(DOMINIO_MEDIO)}, rojo por debajo. El detalle por persona está en la tabla de abajo.`}
          >
            <BarrasTema temas={datos.dominio_por_tema} />
          </Seccion>

          <Seccion
            titulo="Progreso individual"
            nota="Una fila por estudiante. Usa el scroll cuando el grupo crezca."
          >
            <TablaEstudiantes filas={datos.estudiantes} />
          </Seccion>
        </>
      )}
    </>
  );
}
