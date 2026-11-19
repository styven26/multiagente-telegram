"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { borrarToken, leerToken, yo, type Docente } from "@/lib/api";

const NAV = [
  { href: "/dashboard", etiqueta: "Resumen", d: "M3 12l9-8 9 8v8a1 1 0 01-1 1h-5v-6H9v6H4a1 1 0 01-1-1z" },
  { href: "/temas", etiqueta: "Contenido", d: "M4 5h16M4 12h16M4 19h10" },
];

const ICONO_SALIR = "M15 17l5-5-5-5M20 12H9M11 3H5a1 1 0 00-1 1v16a1 1 0 001 1h6";

export default function PanelLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const ruta = usePathname();
  const [docente, setDocente] = useState<Docente | null>(null);
  const [listo, setListo] = useState(false);

  useEffect(() => {
    if (!leerToken()) {
      router.replace("/login");
      return;
    }
    yo()
      .then(setDocente)
      .catch(() => {
        borrarToken();
        router.replace("/login");
      })
      .finally(() => setListo(true));
  }, [router]);

  function salir() {
    borrarToken();
    router.replace("/login");
  }

  const activa = (href: string) => ruta === href || ruta.startsWith(`${href}/`);

  if (!listo) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#faf8f5]">
        <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6788]">
          Cargando…
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#faf8f5] md:flex">
      {/* Cabecera — solo móvil */}
      <header className="sticky top-0 z-40 flex items-center justify-between border-b border-[#1a1830]/10 bg-white px-4 py-3 md:hidden">
        <Link href="/dashboard" className="font-mono text-[13px] tracking-[0.18em] text-[#1a1830]">
          STI
        </Link>
        <div className="flex items-center gap-3">
          {docente && (
            <span className="max-w-[9rem] truncate text-[13px] text-[#6b6788]">
              {docente.nombre}
            </span>
          )}
          <button
            onClick={salir}
            aria-label="Salir"
            className="rounded-lg p-2 text-[#8e8ba5] transition hover:bg-[#c0392b]/10 hover:text-[#c0392b]"
          >
            <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" fill="none" stroke="currentColor"
                 strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d={ICONO_SALIR} />
            </svg>
          </button>
        </div>
      </header>

      {/* Barra lateral — solo escritorio.
          Con solo iconos había que adivinar a qué pertenecía el bloque activo;
          el nombre al lado lo resuelve sin depender del tooltip. */}
      <nav className="sticky top-0 hidden h-screen w-[212px] shrink-0 flex-col border-r border-[#1a1830]/10 bg-white px-3 py-6 md:flex">
        <Link href="/dashboard"
              className="mb-7 px-3 font-mono text-[12px] tracking-[0.15em] text-[#1a1830]">
          STI
        </Link>

        <ul className="flex flex-1 flex-col gap-1">
          {NAV.map((item) => {
            const act = activa(item.href);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={act ? "page" : undefined}
                  className={
                    "relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13.5px] transition " +
                    (act
                      ? "bg-[#1a1830]/[0.06] font-medium text-[#1a1830]"
                      : "text-[#6b6788] hover:bg-[#1a1830]/[0.04] hover:text-[#1a1830]")
                  }
                >
                  {act && (
                    <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-[#e0a030]" />
                  )}
                  <svg viewBox="0 0 24 24" className="h-[18px] w-[18px] shrink-0" fill="none"
                       stroke={act ? "#e0a030" : "currentColor"} strokeWidth="1.7"
                       strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                    <path d={item.d} />
                  </svg>
                  {item.etiqueta}
                </Link>
              </li>
            );
          })}
        </ul>

        {docente && (
          <div className="mt-4 border-t border-[#1a1830]/10 px-3 pt-4">
            <p className="truncate text-[13px] leading-tight text-[#1a1830]">
              {docente.nombre}
            </p>
            <p className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.12em] text-[#a5a2b8]">
              {docente.rol}
            </p>
          </div>
        )}

        <button
          onClick={salir}
          className="mt-2 flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13.5px] text-[#8e8ba5] transition hover:bg-[#c0392b]/[0.08] hover:text-[#c0392b]"
        >
          <svg viewBox="0 0 24 24" className="h-[18px] w-[18px] shrink-0" fill="none"
               stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"
               strokeLinejoin="round" aria-hidden>
            <path d={ICONO_SALIR} />
          </svg>
          Cerrar sesión
        </button>
      </nav>

      {/* Contenido */}
      <div className="min-w-0 flex-1">
        <div className="mx-auto max-w-5xl px-4 pb-28 pt-5 sm:px-6 md:px-8 md:pb-10 md:pt-6">
          {children}
        </div>
      </div>

      {/* Barra inferior — solo móvil */}
      <nav
        className="fixed inset-x-0 bottom-0 z-40 flex border-t border-[#1a1830]/10 bg-white md:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            aria-current={activa(item.href) ? "page" : undefined}
            className={
              "relative flex flex-1 flex-col items-center gap-1 py-2.5 transition " +
              (activa(item.href) ? "text-[#1a1830]" : "text-[#a5a2b8]")
            }
          >
            <svg viewBox="0 0 24 24" className="h-[20px] w-[20px]" fill="none"
                 stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"
                 strokeLinejoin="round" aria-hidden>
              <path d={item.d} />
            </svg>
            <span className="font-mono text-[9.5px] uppercase tracking-[0.12em]">
              {item.etiqueta}
            </span>
            {activa(item.href) && (
              <span className="absolute bottom-0 h-[2px] w-10 rounded-full bg-[#e0a030]" />
            )}
          </Link>
        ))}
      </nav>
    </div>
  );
}