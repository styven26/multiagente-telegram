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

      {/* Rail — solo escritorio */}
      <nav className="sticky top-0 hidden h-screen w-[68px] shrink-0 flex-col items-center border-r border-[#1a1830]/10 bg-white py-6 md:flex">
        <Link href="/dashboard" className="mb-6 font-mono text-[12px] tracking-[0.15em] text-[#1a1830]">
          STI
        </Link>

        <ul className="flex flex-1 flex-col gap-1.5">
          {NAV.map((item) => (
            <li key={item.href} className="relative">
              {activa(item.href) && (
                <span className="absolute -left-[13px] top-1/2 h-6 w-[2px] -translate-y-1/2 rounded-full bg-[#e0a030]" />
              )}
              <Link
                href={item.href}
                title={item.etiqueta}
                aria-current={activa(item.href) ? "page" : undefined}
                className={
                  "flex h-11 w-11 items-center justify-center rounded-lg transition " +
                  (activa(item.href)
                    ? "bg-[#1a1830] text-white"
                    : "text-[#8e8ba5] hover:bg-[#1a1830]/5 hover:text-[#1a1830]")
                }
              >
                <svg viewBox="0 0 24 24" className="h-[19px] w-[19px]" fill="none"
                     stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"
                     strokeLinejoin="round" aria-hidden>
                  <path d={item.d} />
                </svg>
              </Link>
            </li>
          ))}
        </ul>

        {docente && (
          <div className="mb-6 px-1 text-center">
            <p className="truncate text-[12px] leading-tight text-[#1a1830]">{docente.nombre}</p>
            <p className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.1em] text-[#a5a2b8]">
              {docente.rol}
            </p>
          </div>
        )}

        <button
          onClick={salir}
          title="Salir"
          className="flex h-11 w-11 items-center justify-center rounded-lg text-[#8e8ba5] transition hover:bg-[#c0392b]/10 hover:text-[#c0392b]"
        >
          <svg viewBox="0 0 24 24" className="h-[19px] w-[19px]" fill="none" stroke="currentColor"
               strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
            <path d={ICONO_SALIR} />
          </svg>
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
              "flex flex-1 flex-col items-center gap-1 py-2.5 transition " +
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