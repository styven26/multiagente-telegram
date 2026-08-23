"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { borrarToken, leerToken, yo, type Docente } from "@/lib/api";

const NAV = [
  { href: "/dashboard", etiqueta: "Resumen", d: "M3 12l9-8 9 8v8a1 1 0 01-1 1h-5v-6H9v6H4a1 1 0 01-1-1z" },
  { href: "/temas", etiqueta: "Temas", d: "M4 5h16M4 12h16M4 19h10" },
];

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
    <div className="flex min-h-screen bg-[#faf8f5]">
      {/* Rail de navegación */}
      <nav className="sticky top-0 flex h-screen w-[68px] flex-col items-center border-r border-[#1a1830]/10 bg-white py-6">
        <Link
          href="/dashboard"
          className="mb-6 font-mono text-[12px] tracking-[0.15em] text-[#1a1830]"
        >
          STI
        </Link>

        <ul className="flex flex-1 flex-col gap-1.5">
          {NAV.map((item) => {
            const activo = ruta === item.href;
            return (
              <li key={item.href} className="relative">
                {activo && (
                  <span className="absolute -left-[13px] top-1/2 h-6 w-[2px] -translate-y-1/2 rounded-full bg-[#e0a030]" />
                )}
                <Link
                  href={item.href}
                  title={item.etiqueta}
                  aria-current={activo ? "page" : undefined}
                  className={
                    "flex h-11 w-11 items-center justify-center rounded-lg transition " +
                    (activo
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
            );
          })}
        </ul>

        {docente && (
          <div className="mb-6 text-center">
            <p className="text-[12px] leading-tight text-[#1a1830]">{docente.nombre}</p>
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
          <svg viewBox="0 0 24 24" className="h-[19px] w-[19px]" fill="none"
               stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"
               strokeLinejoin="round" aria-hidden>
            <path d="M15 17l5-5-5-5M20 12H9M11 3H5a1 1 0 00-1 1v16a1 1 0 001 1h6" />
          </svg>
        </button>
      </nav>

      {/* Contenido */}
      <div className="min-w-0 flex-1">
        <div className="mx-auto max-w-5xl px-8 pt-6 pb-10">{children}</div>
      </div>
    </div>
  );
}