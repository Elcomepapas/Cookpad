import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { api, type Unidad } from "@/lib/api";
import { PageTitle } from "@/components/shell";

export const Route = createFileRoute("/ingredientes")({
  head: () => ({ meta: [
    { title: "Catálogo de ingredientes — Cookpad" },
    { name: "description", content: "Administrá el catálogo de ingredientes." },
    { property: "og:title", content: "Catálogo de ingredientes — Cookpad" },
    { property: "og:description", content: "Catálogo de ingredientes de Cookpad." },
  ] }),
  component: Ingredientes,
});

function Ingredientes() {
  const qc = useQueryClient();
  const { data } = useQuery({ queryKey: ["ingredientes"], queryFn: api.ingredientes });
  const [f, setF] = useState({ nombre: "", unidad_base: "g" as Unidad, origen_animal: false, calorias_por_unidad: 0 });
  const m = useMutation({ mutationFn: () => api.crearIngrediente(f), onSuccess: () => { qc.invalidateQueries({ queryKey: ["ingredientes"] }); setF({ ...f, nombre: "" }); toast.success("Ingrediente agregado"); }, onError: (e: Error) => toast.error(e.message) });
  return (
    <>
      <PageTitle title="Catálogo de ingredientes" sub="Sección de administración." />
      <form className="card mb-6 grid items-end gap-3 p-4 md:grid-cols-5" onSubmit={(e) => { e.preventDefault(); m.mutate(); }}>
        <div className="md:col-span-2"><label className="label">Nombre</label><input required className="input" value={f.nombre} onChange={(e) => setF({ ...f, nombre: e.target.value })} /></div>
        <div><label className="label">Unidad</label><select className="input" value={f.unidad_base} onChange={(e) => setF({ ...f, unidad_base: e.target.value as Unidad })}><option value="g">g</option><option value="ml">ml</option><option value="unidad">unidad</option></select></div>
        <div><label className="label">Kcal / unidad</label><input type="number" min={0} step="any" required className="input" value={f.calorias_por_unidad} onChange={(e) => setF({ ...f, calorias_por_unidad: +e.target.value })} /></div>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={f.origen_animal} onChange={(e) => setF({ ...f, origen_animal: e.target.checked })} />Origen animal</label>
        <button className="btn-primary md:col-span-5">Agregar</button>
      </form>
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted text-left text-xs uppercase text-muted-foreground"><tr><th className="p-3">Nombre</th><th>Unidad</th><th>Kcal/unidad</th><th>Origen</th></tr></thead>
          <tbody>{data?.map((i) => <tr key={i.id} className="border-t border-border"><td className="p-3 font-medium">{i.nombre}</td><td>{i.unidad_base}</td><td>{i.calorias_por_unidad}</td><td>{i.origen_animal ? "Animal" : <span className="chip-herb">Vegetal</span>}</td></tr>)}</tbody>
        </table>
      </div>
    </>
  );
}
