// Cliente del backend FastAPI. Configurá VITE_API_URL (ej: http://localhost:8000).
// Si no está definido, se usa un backend simulado en memoria (src/lib/mock.ts) para la vista previa.
import { mockRequest } from "./mock";

export type Unidad = "g" | "ml" | "unidad";
export type Dificultad = "facil" | "media" | "dificil";
export type Comida = "desayuno" | "almuerzo" | "merienda" | "cena";

export interface Usuario { id: number; email: string; nombre: string; fecha_registro: string }
export interface Ingrediente { id: number; nombre: string; unidad_base: Unidad; origen_animal: boolean; calorias_por_unidad: number }
export interface RecetaIngrediente { ingrediente_id: number; nombre?: string; unidad_base?: Unidad; cantidad: number }
export interface Paso { orden: number; descripcion: string }
export type CategoriaTutorial = "tecnicas" | "cortes" | "reposteria" | "basicos" | "recetas";
export interface Tutorial {
  id: number; titulo: string; descripcion: string | null; video_url: string;
  miniatura_url: string | null; categoria: CategoriaTutorial; duracion_seg: number | null;
  receta_id: number | null; fecha_publicacion: string;
}
export interface Receta {
  id: number; autor_id: number; autor_nombre?: string; titulo: string; porciones: number; tiempo_min: number;
  dificultad: Dificultad; fecha_publicacion: string; es_vegana: boolean; puntaje_promedio?: number | null;
  ingredientes?: RecetaIngrediente[]; pasos?: Paso[]; calorias_totales?: number; calorias_por_porcion?: number;
  veces_guardada?: number; faltante?: { id: number; nombre: string } | null;
}
export interface Comentario { id: number; usuario_id: number; usuario_nombre?: string; receta_id: number; texto: string; puntaje: number; fecha: string }
export interface PlanReceta { receta_id: number; titulo?: string; dia_semana: number; comida: Comida; porciones: number }
export interface Plan { id: number; usuario_id: number; fecha_inicio: string; recetas: PlanReceta[] }
export interface ItemCompra { ingrediente_id: number; nombre: string; unidad_base: Unidad; cantidad: number }
export type CategoriaHeladera =
  | "bebidas" | "aderezos" | "lacteos" | "verduras" | "frutas"
  | "carnes_vacunas" | "carnes_porcinas" | "carnes_aves" | "carnes_ovinas"
  | "pescados" | "mariscos" | "fiambres" | "otras_carnes"
  | "panificados" | "almacen" | "congelados" | "otros";
export interface RecordatorioHeladera { id: number; nombre: string }
export interface ProductoHeladera {
  id: number; ingrediente_id: number; nombre: string; categoria: CategoriaHeladera; cantidad: number; unidad: Unidad;
  precio_total: number; fecha_vencimiento: string | null; dias_para_vencer: number | null;
  proximo_a_vencer: boolean; vencido: boolean;
}
export interface CompraHeladera {
  id: number; comercio: string; fecha_compra: string; total: number; productos: ProductoHeladera[];
}
export interface Heladera { compras: CompraHeladera[]; total_gastado: number }
export interface ProductoReciboPreview {
  nombre: string; ingrediente_id: number | null; categoria: CategoriaHeladera; cantidad: number; unidad: Unidad;
  precio_total: number; fecha_vencimiento: string | null;
}
export interface ReciboPreview {
  comercio: string; fecha_compra: string; productos: ProductoReciboPreview[];
}
export interface SugerenciaHeladera {
  receta_id: number; titulo: string; ingredientes_disponibles: number; total_ingredientes: number;
  productos_a_comprar: { ingrediente_id: number; nombre: string; cantidad: number; unidad: Unidad }[];
}

export const API_URL = import.meta.env["VITE_API_URL"] as string | undefined;
export const USING_MOCK = !API_URL;

const TOKEN_KEY = "cookpad_token";
const USER_KEY = "cookpad_user";
export const session = {
  token: () => (typeof window === "undefined" ? null : localStorage.getItem(TOKEN_KEY)),
  user: (): Usuario | null => {
    if (typeof window === "undefined") return null;
    const u = localStorage.getItem(USER_KEY);
    return u ? JSON.parse(u) : null;
  },
  set(token: string, user: Usuario) { localStorage.setItem(TOKEN_KEY, token); localStorage.setItem(USER_KEY, JSON.stringify(user)); window.dispatchEvent(new Event("auth")); },
  clear() { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); window.dispatchEvent(new Event("auth")); },
};

export class ApiError extends Error { constructor(public status: number, message: string) { super(message); } }

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  if (USING_MOCK) return mockRequest<T>(method, path, body, session.user()?.id ?? null);
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const t = session.token();
  if (t) headers["Authorization"] = `Bearer ${t}`;
  const res = await fetch(`${API_URL!.replace(/\/$/, "")}${path}`, { method, headers, body: body ? JSON.stringify(body) : null });
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const d = data?.detail ?? data?.message ?? res.statusText;
    throw new ApiError(res.status, typeof d === "string" ? d : Array.isArray(d) ? d.map((x: { msg?: string }) => x.msg).join(", ") : JSON.stringify(d));
  }
  return data as T;
}

async function uploadReceipt<T>(file: File): Promise<T> {
  if (USING_MOCK) return mockRequest<T>("POST", "/heladera/recibos/preview", file, session.user()?.id ?? null);
  const headers: Record<string, string> = {};
  const token = session.token();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_URL!.replace(/\/$/, "")}/heladera/recibos/preview`, {
    method: "POST",
    headers,
    body: form,
  });
  const data = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail ?? data?.message ?? response.statusText;
    throw new ApiError(response.status, typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

const qs = (p: Record<string, unknown>) => {
  const s = new URLSearchParams();
  Object.entries(p).forEach(([k, v]) => { if (v !== undefined && v !== "" && v !== null) s.set(k, String(v)); });
  const r = s.toString();
  return r ? `?${r}` : "";
};

export interface FiltrosRecetas { q?: string; dificultad?: string; tiempo_max?: number | string; ingrediente?: string; vegana?: boolean; orden?: "puntaje" | "fecha" }

export const api = {
  register: (b: { email: string; nombre: string; password: string }) => request<Usuario>("POST", "/auth/register", b),
  login: (b: { email: string; password: string }) => request<{ access_token: string; usuario: Usuario }>("POST", "/auth/login", b),

  ingredientes: () => request<Ingrediente[]>("GET", "/ingredientes"),
  crearIngrediente: (b: Omit<Ingrediente, "id">) => request<Ingrediente>("POST", "/ingredientes", b),
  ingredientesMasUsados: () => request<(Ingrediente & { cantidad_recetas: number })[]>("GET", "/ingredientes/mas-usados"),

  recetas: (f: FiltrosRecetas = {}) => request<Receta[]>("GET", `/recetas${qs({ ...f, vegana: f.vegana ? true : undefined })}`),
  receta: (id: number, porciones?: number) => request<Receta>("GET", `/recetas/${id}${qs({ porciones })}`),
  crearReceta: (b: { titulo: string; porciones: number; tiempo_min: number; dificultad: Dificultad; ingredientes: RecetaIngrediente[]; pasos: Paso[] }) => request<Receta>("POST", "/recetas", b),
  conIngredientes: (ids: number[]) => request<{ completas: Receta[]; falta_uno: Receta[] }>("POST", "/recetas/con-ingredientes", { ingredientes: ids }),
  topGuardadas: () => request<Receta[]>("GET", "/recetas/top-guardadas"),

  tutoriales: (f: { categoria?: CategoriaTutorial; q?: string } = {}) => request<Tutorial[]>("GET", `/tutoriales${qs(f)}`),
  tutorial: (id: number) => request<Tutorial>("GET", `/tutoriales/${id}`),
  tutorialesDeReceta: (recipeId: number) => request<Tutorial[]>("GET", `/recetas/${recipeId}/tutoriales`),

  heladera: () => request<Heladera>("GET", "/heladera"),
  sugerenciasHeladera: () => request<SugerenciaHeladera[]>("GET", "/heladera/sugerencias"),
  cambiarCategoriaProductoHeladera: (id: number, categoria: CategoriaHeladera) => request<ProductoHeladera>("PATCH", `/heladera/productos/${id}`, { categoria }),
  recordatoriosHeladera: () => request<RecordatorioHeladera[]>("GET", "/heladera/recordatorios"),
  agregarRecordatoriosHeladera: (productos: string[]) => request<RecordatorioHeladera[]>("POST", "/heladera/recordatorios", { productos }),
  quitarRecordatorioHeladera: (id: number) => request<null>("DELETE", `/heladera/recordatorios/${id}`),
  previsualizarRecibo: (file: File) => uploadReceipt<ReciboPreview>(file),
  crearCompraHeladera: (body: { comercio: string; fecha_compra: string; productos: { ingrediente_id: number; nombre_producto: string; categoria: CategoriaHeladera; cantidad: number; precio_total: number; fecha_vencimiento: string | null }[] }) => request<CompraHeladera>("POST", "/heladera/compras", body),

  guardadas: (uid: number) => request<Receta[]>("GET", `/usuarios/${uid}/guardadas`),
  guardar: (recetaId: number) => request<unknown>("POST", `/recetas/${recetaId}/guardar`),
  quitarGuardada: (recetaId: number) => request<unknown>("DELETE", `/recetas/${recetaId}/guardar`),

  comentarios: (recetaId: number) => request<Comentario[]>("GET", `/recetas/${recetaId}/comentarios`),
  comentar: (recetaId: number, b: { texto: string; puntaje: number }) => request<Comentario>("POST", `/recetas/${recetaId}/comentarios`, b),
  editarComentario: (id: number, b: { texto: string; puntaje: number }) => request<Comentario>("PUT", `/comentarios/${id}`, b),

  planes: (uid: number) => request<Plan[]>("GET", `/usuarios/${uid}/planes`),
  crearPlan: (fecha_inicio: string) => request<Plan>("POST", "/planes", { fecha_inicio }),
  plan: (id: number) => request<Plan>("GET", `/planes/${id}`),
  agregarAlPlan: (planId: number, b: PlanReceta) => request<Plan>("POST", `/planes/${planId}/recetas`, b),
  quitarDelPlan: (planId: number, dia: number, comida: Comida) => request<Plan>("DELETE", `/planes/${planId}/recetas${qs({ dia_semana: dia, comida })}`),
  listaCompras: (planId: number) => request<ItemCompra[]>("GET", `/planes/${planId}/lista-compras`),
  caloriasPlan: (planId: number) => request<{ dia_semana: number; calorias: number }[]>("GET", `/planes/${planId}/calorias`),
};

export const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
export const COMIDAS: Comida[] = ["desayuno", "almuerzo", "merienda", "cena"];
export const DIFICULTAD_LABEL: Record<Dificultad, string> = { facil: "Fácil", media: "Media", dificil: "Difícil" };
