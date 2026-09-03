export type Unidad = {
  numero: number;
  nombre: string;
  detalle: string | null;
  color: string;
};

export const UNIDADES: Unidad[] = [
  { numero: 1, nombre: "Conceptos básicos", detalle: "Generalidades, variables, tipos de datos y operadores", color: "#c8862a" },
  { numero: 2, nombre: "Estructuras de programación", detalle: "Condicionales (if, switch) y bucles (for, while, do-while)", color: "#2f7d8c" },
  { numero: 3, nombre: "Vectores y matrices", detalle: "Arreglos unidimensionales y bidimensionales", color: "#7355ba" },
  { numero: 4, nombre: "Programación modular", detalle: "Funciones, parámetros y descomposición de problemas", color: "#b4593a" },
];

export const SIN_UNIDAD: Unidad = {
  numero: 0, nombre: "Sin unidad",
  detalle: "Temas que aún no pertenecen a ninguna unidad", color: "#8e8ba5",
};

export const colorDeUnidad = (n: number | null) =>
  UNIDADES.find((u) => u.numero === n)?.color ?? SIN_UNIDAD.color;