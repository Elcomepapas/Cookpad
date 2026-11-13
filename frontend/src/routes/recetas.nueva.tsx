import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { Trash2 } from "lucide-react";
import { api, type Dificultad } from "@/lib/api";
import { PageTitle, RequireUser } from "@/components/shell";

export const Route = createFileRoute("/recetas/nueva")({
  head: () => ({ meta: [
    { title: "Publicar receta — Cookpad" },
    { name: "description", content: "Compartí tu receta con ingredientes y pasos." },
    { property: "og:title", content: "Publicar receta — Cookpad" },
    { property: "og:description", content: "Compartí tu receta con la comunidad." },
  ] }),
  component: () => <RequireUser>{() => <Nueva />}</RequireUser>,
});

function Nueva() {
  const nav = useNavigate();
  const { data: ings } = useQuery({ queryKey: ["ingredientes"], queryFn: api.ingredientes });
  const [titulo, setTitulo] = useState(""); const [porciones, setPorciones] = useState(4); const [tiempo, setTiempo] = useState(30);
  const [dif, setDif] = useState<Dificultad>("facil");
  const [items, setItems] = useState<{ ingrediente_id: number; cantidad: number }[]>([]);
  const [pasos, setPasos] = useState<string[]>([""]);
  const m = useMutation({
    mutationFn: () => api.crearReceta({ titulo, porciones, tiempo_min: tiempo, dificultad: dif, ingredientes: items, pasos: pasos.filter((p) => p.trim()).map((d, i) => ({ orden: i + 1, descripcion: d })) }),
    onSuccess: (r) => { toast.success("¡Receta publicada!"); nav({ to: "/recetas/$id", params: { id: String(r.id) } }); },
    onError: (e: Error) => toast.error(e.message),
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!items.length || items.some((i) => !(i.cantidad > 0))) { toast.error("Agregá al menos un ingrediente con cantidad mayor a 0"); return; }
    if (!pasos.some((p) => p.trim())) { toast.error("Agregá al menos un paso"); return; }
    m.mutate();
  };
  return (
    <form onSubmit={submit} className="mx-auto max-w-3xl space-y-6">
      <PageTitle title="Publicar receta" />
      <div className="card grid gap-4 p-5 md:grid-cols-4">
        <div className="md:col-span-4"><label className="label">Título</label><input className="input" required value={titulo} onChange={(e) => setTitulo(e.target.value)} /></div>
        <div><label className="label">Porciones</label><input type="number" min={1} required className="input" value={porciones} onChange={(e) => setPorciones(+e.target.value)} /></div>
        <div><label className="label">Tiempo (min)</label><input type="number" min={1} required className="input" value={tiempo} onChange={(e) => setTiempo(+e.target.value)} /></div>
        <div className="md:col-span-2"><label className="label">Dificultad</label><select className="input" value={dif} onChange={(e) => setDif(e.target.value as Dificultad)}><option value="facil">Fácil</option><option value="media">Media</option><option value="dificil">Difícil</option></select></div>
      </div>
      <div className="card space-y-3 p-5">
        <h2 className="text-xl font-semibold">Ingredientes</h2>
        {items.map((it, i) => (
          <div key={i} className="flex gap-2">
            <select className="input" value={it.ingrediente_id} onChange={(e) => setItems(items.map((x, j) => (j === i ? { ...x, ingrediente_id: +e.target.value } : x)))}>
              {ings?.map((g) => <option key={g.id} value={g.id}>{g.nombre} ({g.unidad_base})</option>)}
            </select>
            <input type="number" min={0} step="any" className="input w-32" value={it.cantidad} onChange={(e) => setItems(items.map((x, j) => (j === i ? { ...x, cantidad: +e.target.value } : x)))} />
            <button type="button" className="btn-ghost px-3" onClick={() => setItems(items.filter((_, j) => j !== i))}><Trash2 className="h-4 w-4" /></button>
          </div>
        ))}
        <button type="button" className="btn-ghost" disabled={!ings?.length} onClick={() => setItems([...items, { ingrediente_id: ings?.[0]?.id ?? 0, cantidad: 1 }])}>+ Ingrediente</button>
      </div>
      <div className="card space-y-3 p-5">
        <h2 className="text-xl font-semibold">Pasos</h2>
        {pasos.map((p, i) => (
          <div key={i} className="flex gap-2">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary font-bold text-primary-foreground">{i + 1}</span>
            <textarea className="input" rows={2} value={p} onChange={(e) => setPasos(pasos.map((x, j) => (j === i ? e.target.value : x)))} />
            <button type="button" className="btn-ghost px-3" onClick={() => setPasos(pasos.filter((_, j) => j !== i))}><Trash2 className="h-4 w-4" /></button>
          </div>
        ))}
        <button type="button" className="btn-ghost" onClick={() => setPasos([...pasos, ""])}>+ Paso</button>
      </div>
      <button className="btn-primary w-full py-3" disabled={m.isPending}>Publicar</button>
    </form>
  );
}
