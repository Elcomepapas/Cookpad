import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Bookmark, Clock, Flame, Leaf, Star } from "lucide-react";
import { api, DIFICULTAD_LABEL } from "@/lib/api";
import { useUser } from "@/components/shell";

export const Route = createFileRoute("/recetas/$id")({
  head: () => ({ meta: [
    { title: "Receta — Cookpad" },
    { name: "description", content: "Ingredientes, pasos y calorías de la receta, escalable a cualquier porción." },
    { property: "og:title", content: "Receta — Cookpad" },
    { property: "og:description", content: "Mirá la receta completa en Cookpad." },
  ] }),
  component: RecetaPage,
});

function RecetaPage() {
  const id = Number(Route.useParams().id);
  const user = useUser();
  const qc = useQueryClient();
  const [porc, setPorc] = useState<number | undefined>();
  const { data: r, error } = useQuery({ queryKey: ["receta", id, porc], queryFn: () => api.receta(id, porc), placeholderData: (p) => p });
  const { data: coms } = useQuery({ queryKey: ["coms", id], queryFn: () => api.comentarios(id) });
  const { data: guardadas } = useQuery({ queryKey: ["guardadas", user?.id], queryFn: () => api.guardadas(user!.id), enabled: !!user });
  const saved = guardadas?.some((g) => g.id === id);
  const mine = coms?.find((c) => c.usuario_id === user?.id);
  const [texto, setTexto] = useState(""); const [pts, setPts] = useState(5);
  useEffect(() => { if (mine) { setTexto(mine.texto); setPts(mine.puntaje); } }, [mine?.id]);

  const onErr = (e: Error) => toast.error(e.message);
  const toggle = useMutation({ mutationFn: () => (saved ? api.quitarGuardada(id) : api.guardar(id)), onSuccess: () => { qc.invalidateQueries({ queryKey: ["guardadas"] }); toast.success(saved ? "Quitada de guardadas" : "¡Guardada!"); }, onError: onErr });
  const comentar = useMutation({ mutationFn: () => (mine ? api.editarComentario(mine.id, { texto, puntaje: pts }) : api.comentar(id, { texto, puntaje: pts })), onSuccess: () => { qc.invalidateQueries({ queryKey: ["coms", id] }); qc.invalidateQueries({ queryKey: ["receta", id] }); toast.success("Comentario guardado"); }, onError: onErr });

  if (error) return <p>{(error as Error).message}</p>;
  if (!r) return <p className="text-muted-foreground">Cargando…</p>;
  const esAutor = user?.id === r.autor_id;

  return (
    <div className="grid gap-8 lg:grid-cols-[1fr_340px]">
      <div>
        <div className="mb-2 flex flex-wrap gap-2">
          {r.es_vegana && <span className="chip-herb"><Leaf className="h-3 w-3" />Vegana</span>}
          <span className="chip"><Clock className="h-3 w-3" />{r.tiempo_min} min</span>
          <span className="chip">{DIFICULTAD_LABEL[r.dificultad]}</span>
          {r.puntaje_promedio != null && <span className="chip"><Star className="h-3 w-3" />{r.puntaje_promedio}</span>}
        </div>
        <h1 className="text-5xl font-bold">{r.titulo}</h1>
        <p className="mt-2 text-muted-foreground">por {r.autor_nombre ?? `usuario #${r.autor_id}`} · {r.fecha_publicacion.slice(0, 10)}</p>
        {user && <button className={saved ? "btn-ghost mt-4" : "btn-primary mt-4"} onClick={() => toggle.mutate()}><Bookmark className="h-4 w-4" />{saved ? "Guardada" : "Guardar"}</button>}

        <h2 className="mt-10 mb-4 text-2xl font-semibold">Pasos</h2>
        <ol className="space-y-4">
          {r.pasos?.map((p) => (
            <li key={p.orden} className="flex gap-4"><span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary font-display font-bold text-primary-foreground">{p.orden}</span><p className="pt-1">{p.descripcion}</p></li>
          ))}
        </ol>

        <h2 className="mt-10 mb-4 text-2xl font-semibold">Comentarios</h2>
        {user && !esAutor && (
          <form className="card mb-6 space-y-3 p-4" onSubmit={(e) => { e.preventDefault(); comentar.mutate(); }}>
            <div className="flex gap-1">{[1, 2, 3, 4, 5].map((n) => <button type="button" key={n} onClick={() => setPts(n)}><Star className={`h-6 w-6 ${n <= pts ? "fill-primary text-primary" : "text-muted-foreground"}`} /></button>)}</div>
            <textarea className="input" rows={3} required value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="¿Qué te pareció?" />
            <button className="btn-primary">{mine ? "Editar mi comentario" : "Comentar"}</button>
          </form>
        )}
        {esAutor && <p className="mb-4 text-sm text-muted-foreground">No podés puntuar tu propia receta.</p>}
        <div className="space-y-3">
          {coms?.length ? coms.map((c) => (
            <div key={c.id} className="border-b border-border pb-3"><div className="flex items-center gap-2 text-sm font-semibold">{c.usuario_nombre ?? `#${c.usuario_id}`}<span className="flex">{Array.from({ length: c.puntaje }).map((_, i) => <Star key={i} className="h-3 w-3 fill-primary text-primary" />)}</span></div><p className="text-sm">{c.texto}</p></div>
          )) : <p className="text-sm text-muted-foreground">Todavía no hay comentarios.</p>}
        </div>
      </div>

      <aside className="card h-fit space-y-4 p-5 lg:sticky lg:top-24">
        <div>
          <label className="label">Porciones</label>
          <div className="flex items-center gap-2">
            <button className="btn-ghost px-3" onClick={() => setPorc(Math.max(1, r.porciones - 1))}>−</button>
            <span className="w-10 text-center font-display text-2xl font-bold">{r.porciones}</span>
            <button className="btn-ghost px-3" onClick={() => setPorc(r.porciones + 1)}>+</button>
            {porc && <button className="text-xs text-primary underline" onClick={() => setPorc(undefined)}>original</button>}
          </div>
        </div>
        <ul className="divide-y divide-border">
          {r.ingredientes?.map((i) => <li key={i.ingrediente_id} className="flex justify-between py-2 text-sm"><span>{i.nombre}</span><span className="font-semibold">{i.cantidad} {i.unidad_base}</span></li>)}
        </ul>
        <div className="flex gap-3 rounded-xl bg-secondary p-3 text-sm"><Flame className="h-5 w-5 text-primary" /><div><b>{r.calorias_totales} kcal</b> totales<br /><span className="text-muted-foreground">{r.calorias_por_porcion} kcal por porción</span></div></div>
      </aside>
    </div>
  );
}
