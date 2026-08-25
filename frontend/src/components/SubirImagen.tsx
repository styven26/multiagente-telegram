"use client";

import { useRef, useState } from "react";

import { subirImagen, urlImagen } from "@/lib/api";

/** Alto fijo de la previsualización. Toda imagen se ajusta dentro de este
 *  recuadro con object-contain, así una captura ancha y una alta ocupan lo
 *  mismo y el formulario no salta al subir o quitar. */
const ALTO_PREVIA = "h-40";

export default function SubirImagen({
  valor, cambiar, color,
}: {
  valor: string | null;
  cambiar: (url: string | null) => void;
  color: string;
}) {
  const entrada = useRef<HTMLInputElement>(null);
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function elegir(archivo: File | undefined) {
    if (!archivo) return;
    setError(null);
    setSubiendo(true);
    try {
      cambiar(await subirImagen(archivo));
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo subir");
    } finally {
      setSubiendo(false);
      if (entrada.current) entrada.current.value = "";
    }
  }

  const previa = urlImagen(valor);

  return (
    <div>
      <label className="mb-1.5 block font-mono text-[10.5px] uppercase tracking-[0.14em] text-[#6b6788]">
        Imagen (opcional)
      </label>

      {previa ? (
        <div className="rounded-md border border-[#1a1830]/15 bg-[#faf8f5] p-3">
          <div className={`flex ${ALTO_PREVIA} items-center justify-center overflow-hidden rounded bg-white`}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={previa} alt="Vista previa"
                 className="max-h-full max-w-full object-contain" />
          </div>
          <div className="mt-3 flex gap-2">
            <button type="button" onClick={() => entrada.current?.click()}
                    className="rounded-md px-3 py-1.5 font-mono text-[10.5px] uppercase tracking-[0.14em] text-[#6b6788] hover:bg-[#1a1830]/5 hover:text-[#1a1830]">
              Reemplazar
            </button>
            <button type="button" onClick={() => cambiar(null)}
                    className="rounded-md px-3 py-1.5 font-mono text-[10.5px] uppercase tracking-[0.14em] text-[#c0392b] hover:bg-[#c0392b]/10">
              Quitar
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          disabled={subiendo}
          onClick={() => entrada.current?.click()}
          className={`flex ${ALTO_PREVIA} w-full items-center justify-center rounded-md border border-dashed border-[#1a1830]/20 text-center transition hover:border-[#1a1830]/40 disabled:opacity-50`}
        >
          <span className="text-[14px] text-[#8e8ba5]">
            {subiendo ? "Subiendo…" : "Elegir imagen · PNG, JPG, WEBP o GIF · máx. 5 MB"}
          </span>
        </button>
      )}

      <input
        ref={entrada}
        type="file"
        accept="image/png,image/jpeg,image/webp,image/gif"
        className="hidden"
        onChange={(e) => elegir(e.target.files?.[0])}
      />

      {error && (
        <p className="mt-2 text-[13px] text-[#8c2b20]">{error}</p>
      )}
    </div>
  );
}