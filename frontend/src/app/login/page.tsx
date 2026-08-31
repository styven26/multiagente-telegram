"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { guardarToken, login } from "@/lib/api";
import { validarClave, validarEmail } from "@/lib/limites";

const NODOS = [
  { id: "UNIDAD: 1", nombre: "Conceptos básicos", x: 58, y: 62 },
  { id: "UNIDAD: 2", nombre: "Estructuras de programación", x: 168, y: 190 },
  { id: "UNIDAD: 3", nombre: "Vectores y matrices", x: 68, y: 318 },
  { id: "UNIDAD: 4", nombre: "Programación modular", x: 172, y: 442 },
];

const ARISTAS = [
  ["UNIDAD: 1", "UNIDAD: 2"], ["UNIDAD: 2", "UNIDAD: 3"], ["UNIDAD: 3", "UNIDAD: 4"],
] as const;

function GrafoPrerrequisitos() {
  const pos = (id: string) => NODOS.find((n) => n.id === id)!;

  return (
    <svg viewBox="0 0 340 500" className="h-full w-full" aria-hidden>
      {ARISTAS.map(([a, b], i) => {
        const o = pos(a);
        const d = pos(b);
        return (
          <path
            key={`${a}${b}`}
            d={`M ${o.x} ${o.y} C ${o.x} ${(o.y + d.y) / 2}, ${d.x} ${(o.y + d.y) / 2}, ${d.x} ${d.y}`}
            fill="none"
            stroke="#5c5890"
            strokeWidth="1.25"
            className="arista"
            style={{ animationDelay: `${0.2 + i * 0.18}s` }}
          />
        );
      })}

      {NODOS.map((n, i) => (
        <g key={n.id} className="nodo" style={{ animationDelay: `${0.35 + i * 0.18}s` }}>
          <circle cx={n.x} cy={n.y} r="6.5" fill="#1a1830" stroke="#e0a030" strokeWidth="1.5" />
          <text
            x={n.x + 16}
            y={n.y - 3}
            fill="#e0a030"
            fontSize="10.5"
            fontFamily="var(--font-code)"
            letterSpacing="0.08em"
          >
            {n.id}
          </text>
          <text
            x={n.x + 16}
            y={n.y + 11}
            fill="#8e8ab8"
            fontSize="11"
            fontFamily="var(--font-body)"
          >
            {n.nombre}
          </text>
        </g>
      ))}
    </svg>
  );
}

export default function PaginaLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [verClave, setVerClave] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);
  const [tocado, setTocado] = useState({ email: false, clave: false });

  const errEmail = validarEmail(email);
  const errClave = validarClave(password);
  const listo = !errEmail && !errClave;

  async function enviar() {
    setTocado({ email: true, clave: true });
    if (!listo || cargando) return;
    setError(null);
    setCargando(true);
    try {
      const datos = await login(email.trim().toLowerCase(), password);
      guardarToken(datos.access_token);
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo conectar con el servidor.");
    } finally {
      setCargando(false);
    }
  }

  const etiqueta =
    "mb-2 block font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788]";

  const campo =
    "w-full rounded-md border border-[#1a1830]/15 bg-white px-3.5 py-2.5 text-[15px] " +
    "text-[#1a1830] placeholder:text-[#a5a2b8] transition outline-none " +
    "focus:border-[#1a1830] focus:ring-4 focus:ring-[#e0a030]/25";

  return (
    <main className="flex min-h-screen bg-[#faf8f5]">
      {/* Grafo de conocimiento */}
      <aside className="relative hidden w-[46%] flex-col overflow-hidden bg-[#1a1830] px-12 py-11 lg:flex">
        <div
          aria-hidden
          className="pointer-events-none absolute -left-24 top-1/3 h-[28rem] w-[28rem] rounded-full bg-[#2a2750] blur-3xl"
        />

        <header className="relative flex items-baseline gap-3">
          <span className="font-mono text-sm tracking-[0.2em] text-[#e0a030]">STI</span>
          <span className="h-px w-8 bg-[#4a4670]" />
          <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6790]">
            Tutoría inteligente
          </span>
        </header>

        <div className="relative mt-14 max-w-sm">
          <h2 className="font-display text-[2.6rem] font-medium leading-[1.08] tracking-tight text-white">
            Fundamentos de Programación
          </h2>
        </div>

        <div className="relative mt-8 min-h-0 flex-1">
          <GrafoPrerrequisitos />
        </div>
      </aside>

      {/* Acceso */}
      <div className="flex flex-1 items-center justify-center px-6 py-14">
        <div className="w-full max-w-[368px]">
          <div className="mb-12 flex items-baseline gap-3 lg:hidden">
            <span className="font-mono text-sm tracking-[0.2em] text-[#1a1830]">STI</span>
            <span className="h-px w-8 bg-[#1a1830]/20" />
            <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#6b6788]">
              Tutoría inteligente
            </span>
          </div>

          <h1 className="font-display text-[2rem] font-medium tracking-tight text-[#1a1830]">
            Panel del Docente
          </h1>
          <p className="mt-2 text-[15px] leading-relaxed text-[#6b6788]">
            Gestiona los temas y revisa el avance de tus estudiantes.
          </p>

          <div className="mt-10 space-y-6">
            <div>
              <label htmlFor="email" className={etiqueta}>Correo</label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="docente@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  onBlur={() => setTocado((t) => ({ ...t, email: true }))}
                  onKeyDown={(e) => e.key === "Enter" && enviar()}
                  aria-invalid={tocado.email && !!errEmail}
                  className={campo + (tocado.email && errEmail ? " border-[#c0392b]" : "")}
                />
                {tocado.email && errEmail && (
                  <p className="mt-1.5 text-[12.5px] text-[#c0392b]">{errEmail}</p>
                )}
            </div>

            <div>
              <div className="flex items-baseline justify-between">
                <label htmlFor="password" className={etiqueta}>Contraseña</label>
                <button
                  type="button"
                  onClick={() => setVerClave((v) => !v)}
                  className="mb-2 font-mono text-[11px] uppercase tracking-[0.14em] text-[#6b6788] underline-offset-4 hover:text-[#1a1830] hover:underline"
                >
                  {verClave ? "Ocultar" : "Mostrar"}
                </button>
              </div>
                <input
                  id="password"
                  type={verClave ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onBlur={() => setTocado((t) => ({ ...t, clave: true }))}
                  onKeyDown={(e) => e.key === "Enter" && enviar()}
                  aria-invalid={tocado.clave && !!errClave}
                  className={campo + (tocado.clave && errClave ? " border-[#c0392b]" : "")}
                />
                {tocado.clave && errClave && (
                  <p className="mt-1.5 text-[12.5px] text-[#c0392b]">{errClave}</p>
                )}
            </div>

            {error && (
              <div
                role="alert"
                className="border-l-2 border-[#c0392b] bg-[#c0392b]/[0.06] py-2.5 pl-3.5 pr-3"
              >
                <p className="text-[13.5px] leading-snug text-[#8c2b20]">{error}</p>
              </div>
            )}

            <button
              onClick={enviar}
              disabled={cargando}
              className="w-full rounded-md bg-[#1a1830] px-4 py-3 text-[15px] font-medium text-white transition
                         hover:bg-[#2a2750] focus:outline-none focus:ring-4 focus:ring-[#e0a030]/30
                         disabled:cursor-not-allowed disabled:bg-[#1a1830]/25"
            >
              {cargando ? "Verificando…" : "Entrar"}
            </button>
          </div>

          <p className="mt-10 border-t border-[#1a1830]/10 pt-5 font-mono text-[11px] leading-relaxed tracking-wide text-[#8e8ba5]">
            Acceso restringido. Si olvidaste tu contraseña, pídele al
            administrador que la restablezca.
          </p>
        </div>
      </div>
    </main>
  );
}