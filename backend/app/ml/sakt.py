"""SAKT — Self-Attentive Knowledge Tracing. [Ciclo 2]

Pandey & Karypis (2019), "A Self-Attentive model for Knowledge Tracing".

Idea: para predecir si el estudiante acertará el ejercicio t, el modelo atiende
a sus interacciones anteriores y pondera cuáles son relevantes. Un Transformer
de una sola capa, mucho más ligero que DKT con LSTM y con mejor AUC reportado.

    consulta  = destreza del paso t          -> Q
    entrada   = interacciones 0..t-1         -> K, V
    salida    = P(acierto en t)
"""

from __future__ import annotations

import torch
import torch.nn as nn


class SAKT(nn.Module):
    def __init__(self, n_destrezas: int, d_modelo: int = 128, n_cabezas: int = 8,
                 largo_max: int = 100, dropout: float = 0.2):
        super().__init__()
        self.n_destrezas = n_destrezas
        self.largo_max = largo_max

        # Interacción = destreza + acierto * n_destrezas -> rango [0, 2*n]
        self.emb_interaccion = nn.Embedding(2 * n_destrezas + 1, d_modelo,
                                            padding_idx=0)
        self.emb_consulta = nn.Embedding(n_destrezas + 1, d_modelo, padding_idx=0)
        self.emb_posicion = nn.Embedding(largo_max, d_modelo)

        self.atencion = nn.MultiheadAttention(
            d_modelo, n_cabezas, dropout=dropout, batch_first=True)
        self.norma1 = nn.LayerNorm(d_modelo)

        self.ffn = nn.Sequential(
            nn.Linear(d_modelo, d_modelo),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_modelo, d_modelo),
        )
        self.norma2 = nn.LayerNorm(d_modelo)
        self.dropout = nn.Dropout(dropout)
        self.salida = nn.Linear(d_modelo, 1)

        self._inicializar()

    def _inicializar(self) -> None:
        for emb in (self.emb_interaccion, self.emb_consulta, self.emb_posicion):
            nn.init.normal_(emb.weight, mean=0.0, std=0.02)
        with torch.no_grad():
            self.emb_interaccion.weight[0].zero_()
            self.emb_consulta.weight[0].zero_()

    def forward(self, entrada: torch.Tensor, consulta: torch.Tensor) -> torch.Tensor:
        """entrada, consulta: (lote, largo). Devuelve logits (lote, largo)."""
        _, largo = entrada.shape
        posiciones = torch.arange(largo, device=entrada.device)

        clave_valor = self.dropout(
            self.emb_interaccion(entrada) + self.emb_posicion(posiciones))
        consulta_emb = self.dropout(self.emb_consulta(consulta))

        # Máscara causal: el paso t solo ve 0..t. Como `entrada` ya viene
        # desplazada un lugar, eso equivale a ver el pasado y no el presente.
        mascara = torch.triu(
            torch.ones(largo, largo, device=entrada.device, dtype=torch.bool),
            diagonal=1,
        )

        # No se usa key_padding_mask a propósito: el relleno va al final de la
        # secuencia y la máscara causal ya impide que sea atendido. Añadirlo
        # dejaría la primera fila sin ninguna clave visible y saldría NaN.
        atendido, _ = self.atencion(consulta_emb, clave_valor, clave_valor,
                                    attn_mask=mascara, need_weights=False)

        h = self.norma1(atendido + consulta_emb)
        h = self.norma2(h + self.dropout(self.ffn(h)))
        return self.salida(h).squeeze(-1)


def perdida_enmascarada(logits: torch.Tensor, objetivo: torch.Tensor) -> torch.Tensor:
    """Entropía cruzada binaria ignorando el relleno (objetivo == -1)."""
    valido = objetivo >= 0
    if not valido.any():
        return logits.sum() * 0.0
    return nn.functional.binary_cross_entropy_with_logits(
        logits[valido], objetivo[valido])


if __name__ == "__main__":
    modelo = SAKT(n_destrezas=111)
    parametros = sum(p.numel() for p in modelo.parameters())
    print(f"Parámetros: {parametros:,}")

    lote, largo = 4, 100
    entrada = torch.randint(0, 223, (lote, largo))
    consulta = torch.randint(1, 112, (lote, largo))
    objetivo = torch.randint(0, 2, (lote, largo)).float()
    objetivo[:, 60:] = -1                      # simula relleno

    logits = modelo(entrada, consulta)
    print(f"Salida: {tuple(logits.shape)}  ¿NaN? {torch.isnan(logits).any().item()}")
    print(f"Pérdida inicial: {perdida_enmascarada(logits, objetivo).item():.4f}")