// @ts-nocheck -- backend simulado, sin tipado estricto
// Backend simulado en memoria que respeta las reglas de las historias de usuario.
// Sólo se usa cuando VITE_API_URL no está configurado.
import type { CategoriaHeladera, Comentario, CompraHeladera, Heladera, Ingrediente, Plan, Receta, RecetaIngrediente, Paso, ProductoHeladera, RecordatorioHeladera, ReciboPreview, SugerenciaHeladera, Tutorial, Usuario } from "./api";

type RecetaDB = Omit<Receta, "es_vegana" | "ingredientes" | "pasos"> & { ingredientes: RecetaIngrediente[]; pasos: Paso[] };

const db = {
  usuarios: [
    { id: 1, email: "ana@cookpad.com", nombre: "Ana", fecha_registro: "2026-01-10", password: "1234" },
    { id: 2, email: "leo@cookpad.com", nombre: "Leo", fecha_registro: "2026-02-03", password: "1234" },
  ] as (Usuario & { password: string })[],
  ingredientes: [
    { id: 1, nombre: "Pollo", unidad_base: "g", origen_animal: true, calorias_por_unidad: 2.39 },
    { id: 2, nombre: "Arroz", unidad_base: "g", origen_animal: false, calorias_por_unidad: 1.3 },
    { id: 3, nombre: "Cebolla", unidad_base: "unidad", origen_animal: false, calorias_por_unidad: 40 },
    { id: 4, nombre: "Tomate", unidad_base: "unidad", origen_animal: false, calorias_por_unidad: 22 },
    { id: 5, nombre: "Aceite de oliva", unidad_base: "ml", origen_animal: false, calorias_por_unidad: 8.8 },
    { id: 6, nombre: "Huevo", unidad_base: "unidad", origen_animal: true, calorias_por_unidad: 78 },
    { id: 7, nombre: "Lentejas", unidad_base: "g", origen_animal: false, calorias_por_unidad: 1.16 },
    { id: 8, nombre: "Leche", unidad_base: "ml", origen_animal: true, calorias_por_unidad: 0.42 },
    { id: 9, nombre: "Harina", unidad_base: "g", origen_animal: false, calorias_por_unidad: 3.64 },
    { id: 10, nombre: "Zanahoria", unidad_base: "unidad", origen_animal: false, calorias_por_unidad: 25 },
  ] as Ingrediente[],
  recetas: [
    { id: 1, autor_id: 1, titulo: "Arroz con pollo", porciones: 4, tiempo_min: 45, dificultad: "media", fecha_publicacion: "2026-03-01",
      ingredientes: [{ ingrediente_id: 1, cantidad: 500 }, { ingrediente_id: 2, cantidad: 300 }, { ingrediente_id: 3, cantidad: 1 }, { ingrediente_id: 5, cantidad: 30 }],
      pasos: [{ orden: 1, descripcion: "Dorar el pollo en aceite." }, { orden: 2, descripcion: "Sumar la cebolla picada." }, { orden: 3, descripcion: "Agregar el arroz y agua, cocinar 20 min." }] },
    { id: 2, autor_id: 2, titulo: "Guiso de lentejas", porciones: 6, tiempo_min: 60, dificultad: "facil", fecha_publicacion: "2026-03-12",
      ingredientes: [{ ingrediente_id: 7, cantidad: 400 }, { ingrediente_id: 3, cantidad: 2 }, { ingrediente_id: 10, cantidad: 2 }, { ingrediente_id: 4, cantidad: 3 }],
      pasos: [{ orden: 1, descripcion: "Remojar las lentejas." }, { orden: 2, descripcion: "Rehogar verduras." }, { orden: 3, descripcion: "Cocinar todo junto 40 min." }] },
    { id: 3, autor_id: 1, titulo: "Panqueques", porciones: 2, tiempo_min: 20, dificultad: "facil", fecha_publicacion: "2026-04-02",
      ingredientes: [{ ingrediente_id: 9, cantidad: 120 }, { ingrediente_id: 6, cantidad: 2 }, { ingrediente_id: 8, cantidad: 250 }],
      pasos: [{ orden: 1, descripcion: "Mezclar todo." }, { orden: 2, descripcion: "Cocinar en sartén caliente." }] },
    { id: 4, autor_id: 2, titulo: "Salsa de tomate casera", porciones: 4, tiempo_min: 30, dificultad: "facil", fecha_publicacion: "2026-04-20",
      ingredientes: [{ ingrediente_id: 4, cantidad: 6 }, { ingrediente_id: 3, cantidad: 1 }, { ingrediente_id: 5, cantidad: 20 }],
      pasos: [{ orden: 1, descripcion: "Picar cebolla y tomates." }, { orden: 2, descripcion: "Cocinar a fuego lento 25 min." }] },
  ] as RecetaDB[],
  tutoriales: [
    { id: 1, titulo: "Técnica para cortar verduras", descripcion: "Mirá una demostración de corte y preparación.", video_url: "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4", miniatura_url: null, categoria: "cortes", duracion_seg: 5, receta_id: 1, fecha_publicacion: "2026-04-20T12:00:00" },
    { id: 2, titulo: "Preparaciones básicas", descripcion: "Una guía visual para inspirarte en la cocina.", video_url: "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4", miniatura_url: null, categoria: "basicos", duracion_seg: 5, receta_id: null, fecha_publicacion: "2026-04-21T12:00:00" },
  ] as Tutorial[],
  guardadas: [{ usuario_id: 2, receta_id: 1, fecha: "2026-05-01" }, { usuario_id: 1, receta_id: 2, fecha: "2026-05-02" }, { usuario_id: 2, receta_id: 3, fecha: "2026-05-03" }],
  comentarios: [{ id: 1, usuario_id: 2, receta_id: 1, texto: "¡Riquísimo!", puntaje: 5, fecha: "2026-05-01" }, { id: 2, usuario_id: 1, receta_id: 2, texto: "Muy rendidor.", puntaje: 4, fecha: "2026-05-04" }] as Comentario[],
  planes: [] as Plan[],
  comprasHeladera: [] as { usuario_id: number; compra: CompraHeladera }[],
  recordatoriosHeladera: [] as { usuario_id: number; recordatorio: RecordatorioHeladera }[],
  seq: 100,
};

const err = (status: number, msg: string) => Object.assign(new Error(msg), { status });
const today = () => new Date().toISOString().slice(0, 10);
const addDays = (days: number) => {
  const value = new Date();
  value.setDate(value.getDate() + days);
  return value.toISOString().slice(0, 10);
};
const ing = (id: number) => db.ingredientes.find((i) => i.id === id)!;
const round = (n: number) => Math.round(n * 100) / 100;

function expand(r: RecetaDB, porciones?: number): Receta {
  const f = porciones ? porciones / r.porciones : 1;
  const ingredientes = r.ingredientes.map((x) => ({ ...x, nombre: ing(x.ingrediente_id).nombre, unidad_base: ing(x.ingrediente_id).unidad_base, cantidad: round(x.cantidad * f) }));
  const cal = ingredientes.reduce((s, x) => s + x.cantidad * ing(x.ingrediente_id).calorias_por_unidad, 0);
  const pts = db.comentarios.filter((c) => c.receta_id === r.id);
  const p = porciones ?? r.porciones;
  return {
    ...r, porciones: p, ingredientes, pasos: [...r.pasos].sort((a, b) => a.orden - b.orden),
    autor_nombre: db.usuarios.find((u) => u.id === r.autor_id)?.nombre,
    es_vegana: !r.ingredientes.some((x) => ing(x.ingrediente_id).origen_animal),
    puntaje_promedio: pts.length ? round(pts.reduce((s, c) => s + c.puntaje, 0) / pts.length) : null,
    calorias_totales: Math.round(cal), calorias_por_porcion: Math.round(cal / p),
    veces_guardada: db.guardadas.filter((g) => g.receta_id === r.id).length,
  };
}

function need(uid: number | null) { if (!uid) throw err(401, "Necesitás iniciar sesión"); return uid; }
function planOf(id: number, uid: number | null) {
  const p = db.planes.find((x) => x.id === id); if (!p) throw err(404, "Plan no encontrado");
  if (p.usuario_id !== uid) throw err(403, "No es tu plan"); return p;
}
const planView = (p: Plan): Plan => ({ ...p, recetas: p.recetas.map((r) => ({ ...r, titulo: db.recetas.find((x) => x.id === r.receta_id)?.titulo })) });

export async function mockRequest<T>(method: string, fullPath: string, body: any, uid: number | null): Promise<T> {
  await new Promise((r) => setTimeout(r, 120));
  const [path, query = ""] = fullPath.split("?");
  const q = new URLSearchParams(query);
  const seg = path.split("/").filter(Boolean);
  const M = `${method} /${seg.map((s) => (/^\d+$/.test(s) ? ":id" : s)).join("/")}`;
  const id = Number(seg.find((s) => /^\d+$/.test(s)));
  const out = (v: unknown) => structuredClone(v) as T;

  switch (M) {
    case "POST /auth/register": {
      if (db.usuarios.some((u) => u.email.toLowerCase() === body.email.toLowerCase())) throw err(409, "El email ya está registrado");
      const u = { id: ++db.seq, email: body.email, nombre: body.nombre, password: body.password, fecha_registro: today() };
      db.usuarios.push(u); const { password, ...pub } = u; void password; return out(pub);
    }
    case "POST /auth/login": {
      const u = db.usuarios.find((x) => x.email.toLowerCase() === body.email.toLowerCase() && x.password === body.password);
      if (!u) throw err(401, "Email o contraseña incorrectos");
      const { password, ...pub } = u; void password; return out({ access_token: "mock-" + u.id, usuario: pub });
    }
    case "GET /ingredientes": return out([...db.ingredientes].sort((a, b) => a.nombre.localeCompare(b.nombre)));
    case "POST /ingredientes": {
      if (db.ingredientes.some((i) => i.nombre.toLowerCase() === body.nombre.toLowerCase())) throw err(409, "Ya existe un ingrediente con ese nombre");
      if (!["g", "ml", "unidad"].includes(body.unidad_base)) throw err(422, "unidad_base inválida");
      if (body.calorias_por_unidad < 0) throw err(422, "Las calorías deben ser ≥ 0");
      const i = { ...body, id: ++db.seq }; db.ingredientes.push(i); return out(i);
    }
    case "GET /ingredientes/mas-usados":
      return out(db.ingredientes.map((i) => ({ ...i, cantidad_recetas: db.recetas.filter((r) => r.ingredientes.some((x) => x.ingrediente_id === i.id)).length }))
        .filter((i) => i.cantidad_recetas > 0).sort((a, b) => b.cantidad_recetas - a.cantidad_recetas).slice(0, 10));
    case "POST /heladera/recibos/preview": {
      need(uid);
      return out({
        comercio: "Supermercado Demo",
        fecha_compra: today(),
        productos: [
          { nombre: "Arroz", ingrediente_id: 2, categoria: "almacen", cantidad: 500, unidad: "g", precio_total: 1800, fecha_vencimiento: addDays(5) },
          { nombre: "Cebolla", ingrediente_id: 3, categoria: "verduras", cantidad: 2, unidad: "unidad", precio_total: 700, fecha_vencimiento: null },
        ],
      } satisfies ReciboPreview);
    }
    case "POST /heladera/compras": {
      const user = need(uid);
      const items: ProductoHeladera[] = body.productos.map((item: { ingrediente_id: number; nombre_producto: string; categoria: CategoriaHeladera; cantidad: number; precio_total: number; fecha_vencimiento: string | null }) => {
        const ingredient = db.ingredientes.find((value) => value.id === item.ingrediente_id);
        if (!ingredient) throw err(404, "Ingrediente no encontrado");
        const days = item.fecha_vencimiento ? Math.ceil((new Date(`${item.fecha_vencimiento}T00:00:00`).getTime() - new Date(`${today()}T00:00:00`).getTime()) / 86400000) : null;
        return {
          id: ++db.seq, ingrediente_id: ingredient.id, nombre: item.nombre_producto, categoria: item.categoria,
          cantidad: item.cantidad, unidad: ingredient.unidad_base, precio_total: item.precio_total,
          fecha_vencimiento: item.fecha_vencimiento, dias_para_vencer: days,
          proximo_a_vencer: days !== null && days >= 0 && days <= 7,
          vencido: days !== null && days < 0,
        };
      });
      const purchase = {
        id: ++db.seq, comercio: body.comercio, fecha_compra: body.fecha_compra,
        total: items.reduce((sum, item) => sum + item.precio_total, 0), productos: items,
      };
      db.comprasHeladera.unshift({ usuario_id: user, compra: purchase });
      const acquiredNames = new Set(items.flatMap((item) => [
        item.nombre.trim().toLocaleLowerCase(),
        ing(item.ingrediente_id).nombre.trim().toLocaleLowerCase(),
      ]));
      for (let index = db.recordatoriosHeladera.length - 1; index >= 0; index--) {
        const entry = db.recordatoriosHeladera[index];
        if (entry.usuario_id === user && acquiredNames.has(entry.recordatorio.nombre.trim().toLocaleLowerCase())) {
          db.recordatoriosHeladera.splice(index, 1);
        }
      }
      return out(purchase);
    }
    case "GET /heladera": {
      const user = need(uid);
      const purchases = db.comprasHeladera.filter((entry) => entry.usuario_id === user).map((entry) => entry.compra);
      return out({
        compras: purchases,
        total_gastado: purchases.reduce((sum, purchase) => sum + purchase.total, 0),
      } satisfies Heladera);
    }
    case "PATCH /heladera/productos/:id": {
      const user = need(uid);
      const entry = db.comprasHeladera.find((purchaseEntry) =>
        purchaseEntry.usuario_id === user && purchaseEntry.compra.productos.some((item) => item.id === id));
      const product = entry?.compra.productos.find((item) => item.id === id);
      if (!product) throw err(404, "Producto de heladera no encontrado");
      product.categoria = body.categoria as CategoriaHeladera;
      return out(product);
    }
    case "GET /heladera/sugerencias": {
      const user = need(uid);
      const available = new Set(db.comprasHeladera.filter((entry) => entry.usuario_id === user).flatMap((entry) => entry.compra.productos)
        .filter((item) => !item.vencido).map((item) => item.ingrediente_id));
      const suggestions: SugerenciaHeladera[] = db.guardadas
        .filter((saved) => saved.usuario_id === user)
        .flatMap((saved) => {
          const recipe = db.recetas.find((item) => item.id === saved.receta_id);
          if (!recipe) return [];
          const existing = recipe.ingredientes.filter((item) => available.has(item.ingrediente_id));
          const missing = recipe.ingredientes.filter((item) => !available.has(item.ingrediente_id));
          if (!existing.length || !missing.length) return [];
          return [{
            receta_id: recipe.id, titulo: recipe.titulo,
            ingredientes_disponibles: existing.length, total_ingredientes: recipe.ingredientes.length,
            productos_a_comprar: missing.map((item) => ({
              ingrediente_id: item.ingrediente_id, nombre: ing(item.ingrediente_id).nombre,
              cantidad: item.cantidad, unidad: ing(item.ingrediente_id).unidad_base,
            })),
          }];
        });
      return out(suggestions);
    }
    case "GET /heladera/recordatorios": {
      const user = need(uid);
      return out(db.recordatoriosHeladera.filter((entry) => entry.usuario_id === user).map((entry) => entry.recordatorio));
    }
    case "POST /heladera/recordatorios": {
      const user = need(uid);
      const current = db.recordatoriosHeladera.filter((entry) => entry.usuario_id === user);
      const names = new Set(current.map((entry) => entry.recordatorio.nombre.toLocaleLowerCase()));
      for (const rawName of body.productos as string[]) {
        const name = rawName.trim();
        const normalized = name.toLocaleLowerCase();
        if (!name || name.length > 120) throw err(422, "Cada producto debe tener entre 1 y 120 caracteres");
        if (names.has(normalized)) continue;
        names.add(normalized);
        db.recordatoriosHeladera.push({ usuario_id: user, recordatorio: { id: ++db.seq, nombre: name } });
      }
      return out(db.recordatoriosHeladera.filter((entry) => entry.usuario_id === user).map((entry) => entry.recordatorio));
    }
    case "DELETE /heladera/recordatorios/:id": {
      const user = need(uid);
      const index = db.recordatoriosHeladera.findIndex((entry) => entry.usuario_id === user && entry.recordatorio.id === id);
      if (index < 0) throw err(404, "Producto recordatorio no encontrado");
      db.recordatoriosHeladera.splice(index, 1);
      return out(null);
    }
    case "GET /tutoriales": {
      let tutorials = [...db.tutoriales];
      const categoria = q.get("categoria"); if (categoria) tutorials = tutorials.filter((t) => t.categoria === categoria);
      const text = q.get("q")?.toLocaleLowerCase(); if (text) tutorials = tutorials.filter((t) => t.titulo.toLocaleLowerCase().includes(text));
      tutorials.sort((a, b) => a.orden - b.orden || a.id - b.id);
      return out(tutorials);
    }
    case "GET /tutoriales/:id": {
      const tutorial = db.tutoriales.find((item) => item.id === id);
      if (!tutorial) throw err(404, "Tutorial no encontrado");
      return out(tutorial);
    }
    case "GET /recetas/:id/tutoriales": {
      if (!db.recetas.some((recipe) => recipe.id === id)) throw err(404, "Receta no encontrada");
      return out(db.tutoriales.filter((tutorial) => tutorial.receta_id === id).sort((a, b) => a.orden - b.orden || a.id - b.id));
    }
    case "GET /recetas": {
      let rs = db.recetas.map((r) => expand(r));
      const t = q.get("q")?.toLowerCase(); if (t) rs = rs.filter((r) => r.titulo.toLowerCase().includes(t));
      if (q.get("dificultad")) rs = rs.filter((r) => r.dificultad === q.get("dificultad"));
      if (q.get("tiempo_max")) rs = rs.filter((r) => r.tiempo_min <= Number(q.get("tiempo_max")));
      const ig = q.get("ingrediente")?.toLowerCase(); if (ig) rs = rs.filter((r) => r.ingredientes!.some((x) => x.nombre!.toLowerCase().includes(ig)));
      if (q.get("vegana") === "true") rs = rs.filter((r) => r.es_vegana);
      if (q.get("orden") === "puntaje") rs.sort((a, b) => (b.puntaje_promedio ?? 0) - (a.puntaje_promedio ?? 0));
      else rs.sort((a, b) => b.fecha_publicacion.localeCompare(a.fecha_publicacion));
      return out(rs);
    }
    case "GET /recetas/top-guardadas":
      return out(db.recetas.map((r) => expand(r)).sort((a, b) => b.veces_guardada! - a.veces_guardada!).slice(0, 10));
    case "GET /recetas/:id": {
      const r = db.recetas.find((x) => x.id === id); if (!r) throw err(404, "Receta no encontrada");
      const p = q.get("porciones"); return out(expand(r, p ? Number(p) : undefined));
    }
    case "POST /recetas": {
      const u = need(uid);
      if (db.recetas.some((r) => r.autor_id === u && r.titulo.toLowerCase() === body.titulo.toLowerCase())) throw err(409, "Ya publicaste una receta con ese título");
      if (!(body.porciones > 0) || !(body.tiempo_min > 0)) throw err(422, "Porciones y tiempo deben ser mayores a 0");
      if (!body.ingredientes?.length || body.ingredientes.some((i: RecetaIngrediente) => !(i.cantidad > 0))) throw err(422, "Necesitás al menos un ingrediente con cantidad > 0");
      if (!body.pasos?.length) throw err(422, "Necesitás al menos un paso");
      const ords = body.pasos.map((p: Paso) => p.orden).sort((a: number, b: number) => a - b);
      if (ords.some((o: number, i: number) => o !== i + 1)) throw err(422, "Los pasos deben numerarse 1, 2, 3… sin repetir");
      const r: RecetaDB = { id: ++db.seq, autor_id: u, fecha_publicacion: today(), titulo: body.titulo, porciones: body.porciones, tiempo_min: body.tiempo_min, dificultad: body.dificultad, ingredientes: body.ingredientes.map((i: RecetaIngrediente) => ({ ingrediente_id: i.ingrediente_id, cantidad: i.cantidad })), pasos: body.pasos };
      db.recetas.push(r); return out(expand(r));
    }
    case "POST /recetas/con-ingredientes": {
      const have = new Set<number>(body.ingredientes);
      const completas: Receta[] = []; const falta_uno: Receta[] = [];
      db.recetas.forEach((r) => {
        const miss = r.ingredientes.filter((x) => !have.has(x.ingrediente_id));
        if (miss.length === 0) completas.push(expand(r));
        else if (miss.length === 1) falta_uno.push({ ...expand(r), faltante: { id: miss[0].ingrediente_id, nombre: ing(miss[0].ingrediente_id).nombre } });
      });
      return out({ completas, falta_uno });
    }
    case "GET /usuarios/:id/guardadas":
      return out(db.guardadas.filter((g) => g.usuario_id === id).sort((a, b) => b.fecha.localeCompare(a.fecha)).map((g) => expand(db.recetas.find((r) => r.id === g.receta_id)!)));
    case "POST /recetas/:id/guardar": {
      const u = need(uid);
      if (db.guardadas.some((g) => g.usuario_id === u && g.receta_id === id)) throw err(409, "Ya guardaste esta receta");
      db.guardadas.push({ usuario_id: u, receta_id: id, fecha: new Date().toISOString() }); return out({ ok: true });
    }
    case "DELETE /recetas/:id/guardar": {
      const u = need(uid); db.guardadas = db.guardadas.filter((g) => !(g.usuario_id === u && g.receta_id === id)); return out(null);
    }
    case "GET /recetas/:id/comentarios":
      return out(db.comentarios.filter((c) => c.receta_id === id).map((c) => ({ ...c, usuario_nombre: db.usuarios.find((u) => u.id === c.usuario_id)?.nombre })));
    case "POST /recetas/:id/comentarios": {
      const u = need(uid); const r = db.recetas.find((x) => x.id === id)!;
      if (r.autor_id === u) throw err(403, "No podés puntuar tu propia receta");
      if (!(body.puntaje >= 1 && body.puntaje <= 5)) throw err(422, "El puntaje va de 1 a 5");
      if (db.comentarios.some((c) => c.usuario_id === u && c.receta_id === id)) throw err(409, "Ya comentaste esta receta, podés editarlo");
      const c = { id: ++db.seq, usuario_id: u, receta_id: id, texto: body.texto, puntaje: body.puntaje, fecha: today() }; db.comentarios.push(c); return out(c);
    }
    case "PUT /comentarios/:id": {
      const u = need(uid); const c = db.comentarios.find((x) => x.id === id);
      if (!c || c.usuario_id !== u) throw err(403, "No podés editar este comentario");
      if (!(body.puntaje >= 1 && body.puntaje <= 5)) throw err(422, "El puntaje va de 1 a 5");
      Object.assign(c, { texto: body.texto, puntaje: body.puntaje }); return out(c);
    }
    case "GET /usuarios/:id/planes": return out(db.planes.filter((p) => p.usuario_id === id).sort((a, b) => b.fecha_inicio.localeCompare(a.fecha_inicio)).map(planView));
    case "POST /planes": {
      const u = need(uid);
      if (new Date(body.fecha_inicio + "T12:00:00").getDay() !== 1) throw err(422, "La fecha de inicio tiene que ser un lunes");
      if (db.planes.some((p) => p.usuario_id === u && p.fecha_inicio === body.fecha_inicio)) throw err(409, "Ya tenés un plan para esa semana");
      const p: Plan = { id: ++db.seq, usuario_id: u, fecha_inicio: body.fecha_inicio, recetas: [] }; db.planes.push(p); return out(planView(p));
    }
    case "GET /planes/:id": return out(planView(planOf(id, uid)));
    case "POST /planes/:id/recetas": {
      const p = planOf(id, uid);
      if (p.recetas.some((r) => r.dia_semana === body.dia_semana && r.comida === body.comida)) throw err(409, "Ya hay una receta en ese día y comida");
      p.recetas.push({ receta_id: body.receta_id, dia_semana: body.dia_semana, comida: body.comida, porciones: body.porciones }); return out(planView(p));
    }
    case "DELETE /planes/:id/recetas": {
      const p = planOf(id, uid); p.recetas = p.recetas.filter((r) => !(r.dia_semana === Number(q.get("dia_semana")) && r.comida === q.get("comida"))); return out(planView(p));
    }
    case "GET /planes/:id/lista-compras": {
      const p = planOf(id, uid); const tot = new Map<number, number>();
      p.recetas.forEach((pr) => { const r = db.recetas.find((x) => x.id === pr.receta_id)!; r.ingredientes.forEach((x) => tot.set(x.ingrediente_id, (tot.get(x.ingrediente_id) ?? 0) + (x.cantidad * pr.porciones) / r.porciones)); });
      return out([...tot].map(([iid, c]) => ({ ingrediente_id: iid, nombre: ing(iid).nombre, unidad_base: ing(iid).unidad_base, cantidad: round(c) })).sort((a, b) => a.nombre.localeCompare(b.nombre)));
    }
    case "GET /planes/:id/calorias": {
      const p = planOf(id, uid);
      return out([1, 2, 3, 4, 5, 6, 7].map((d) => ({ dia_semana: d, calorias: Math.round(p.recetas.filter((r) => r.dia_semana === d).reduce((s, pr) => s + expand(db.recetas.find((x) => x.id === pr.receta_id)!, pr.porciones).calorias_totales!, 0)) })));
    }
  }
  throw err(404, `Endpoint simulado no encontrado: ${M}`);
}
