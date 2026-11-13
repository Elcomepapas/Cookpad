import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { X } from "lucide-react";
import { api, COMIDAS, DIAS, type Comida } from "@/lib/api";
import { Empty, PageTitle, RequireUser } from "@/components/shell";

export const Route = createFileRoute("/plan")({
  head: () => ({ meta: [
    { title: "Plan semanal — Cookpad" },
    { name: "description", content: "Armá tu plan de comidas y generá la lista de compras." },
    { property: "og:title", content: "Plan semanal — Cookpad" },
    { property: "og:description", content: "Plan de comidas semanal con lista de compras." },
  ] }),
  component: () => <RequireUser>{(u) => <PlanPage uid={u.id} />}</RequireUser>,
});

function nextMonday() {
  const d = new Date(); const diff = (8 - d.getDay()) % 7; d.setDate(d.getDate() + diff);
  return d.toISOString().slice(0, 10);
}

function PlanPage({ uid }: { uid: number }) {
  const qc = useQueryClient();
  const onErr = (e: Error) => toast.error(e.message);
  const { data: planes } = useQuery({ queryKey: ["planes", uid], queryFn: () => api.planes(uid) });
  const [planId, setPlanId] = useState<number | null>(null);
  const [fecha, setFecha] = useState(nextMonday());
  useEffect(() => { if (!planId && planes?.[0]) setPlanId(planes[0].id); }, [planes]);

  const crear = useMutation({ mutationFn: () => api.crearPlan(fecha), onSuccess: (p) => { qc.invalidateQueries({ queryKey: ["planes"] }); setPlanId(p.id); toast.success("Plan creado"); }, onError: onErr });
  const plan = planes?.find((p) => p.id === planId);
  const { data: recetas } = useQuery({ queryKey: ["recetas", {}], queryFn: () => api.recetas() });
  const { data: lista } = useQuery({ queryKey: ["lista", planId, plan?.recetas.length], queryFn: () => api.listaCompras(planId!), enabled: !!planId });
  const { data: cal } = useQuery({ queryKey: ["cal", planId, plan?.recetas.length], queryFn: () => api.caloriasPlan(planId!), enabled: !!planId });

  const [slot, setSlot] = useState<{ dia: number; comida: Comida } | null>(null);
  const [recId, setRecId] = useState<number>(0); const [porc, setPorc] = useState(2);
  const refresh = () => qc.invalidateQueries({ queryKey: ["planes"] });
  const agregar = useMutation({ mutationFn: () => api.agregarAlPlan(planId!, { receta_id: recId || recetas?.[0]?.id || 0, dia_semana: slot!.dia, comida: slot!.comida, porciones: porc }), onSuccess: () => { refresh(); setSlot(null); }, onError: onErr });
  const quitar = useMutation({ mutationFn: (s: { dia: number; comida: Comida }) => api.quitarDelPlan(planId!, s.dia, s.comida), onSuccess: refresh, onError: onErr });

  return (
    <>
      <PageTitle title="Mi plan semanal" />
      <div className="card mb-6 flex flex-wrap items-end gap-3 p-4">
        {!!planes?.length && <div><label className="label">Semana</label><select className="input" value={planId ?? ""} onChange={(e) => setPlanId(+e.target.value)}>{planes.map((p) => <option key={p.id} value={p.id}>Lunes {p.fecha_inicio}</option>)}</select></div>}
        <div><label className="label">Nueva semana (lunes)</label><input type="date" className="input" value={fecha} onChange={(e) => setFecha(e.target.value)} /></div>
        <button className="btn-primary" onClick={() => crear.mutate()}>Crear plan</button>
      </div>

      {!plan ? <Empty>Creá un plan empezando un lunes.</Empty> : (
        <div className="grid gap-8 xl:grid-cols-[1fr_300px]">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] border-separate border-spacing-1 text-sm">
              <thead><tr><th />{DIAS.map((d, i) => <th key={d} className="font-display text-base">{d}<div className="text-xs font-normal text-muted-foreground">{cal?.find((c) => c.dia_semana === i + 1)?.calorias ?? 0} kcal</div></th>)}</tr></thead>
              <tbody>{COMIDAS.map((c) => (
                <tr key={c}><th className="pr-2 text-right text-xs uppercase text-muted-foreground">{c}</th>
                  {DIAS.map((_, i) => {
                    const pr = plan.recetas.find((r) => r.dia_semana === i + 1 && r.comida === c);
                    return <td key={i} className="h-20 align-top">{pr ? (
                      <div className="relative h-full rounded-lg bg-secondary p-2 text-xs"><b>{pr.titulo}</b><div className="text-muted-foreground">{pr.porciones} porc.</div>
                        <button className="absolute right-1 top-1" onClick={() => quitar.mutate({ dia: i + 1, comida: c })}><X className="h-3 w-3" /></button></div>
                    ) : <button className="h-full w-full rounded-lg border border-dashed border-border text-muted-foreground hover:bg-muted" onClick={() => setSlot({ dia: i + 1, comida: c })}>+</button>}</td>;
                  })}</tr>
              ))}</tbody>
            </table>
            {slot && (
              <div className="card mt-4 flex flex-wrap items-end gap-3 p-4">
                <p className="w-full text-sm font-semibold">{DIAS[slot.dia - 1]} · {slot.comida}</p>
                <div className="flex-1"><label className="label">Receta</label><select className="input" value={recId} onChange={(e) => setRecId(+e.target.value)}>{recetas?.map((r) => <option key={r.id} value={r.id}>{r.titulo}</option>)}</select></div>
                <div><label className="label">Porciones</label><input type="number" min={1} className="input w-24" value={porc} onChange={(e) => setPorc(+e.target.value)} /></div>
                <button className="btn-primary" onClick={() => agregar.mutate()}>Agregar</button>
                <button className="btn-ghost" onClick={() => setSlot(null)}>Cancelar</button>
              </div>
            )}
          </div>
          <aside className="card h-fit p-5">
            <h2 className="mb-3 text-2xl font-semibold">Lista de compras</h2>
            {!lista?.length ? <p className="text-sm text-muted-foreground">Agregá recetas al plan.</p> : (
              <ul className="divide-y divide-border">{lista.map((i) => <li key={i.ingrediente_id} className="flex justify-between py-2 text-sm"><label className="flex gap-2"><input type="checkbox" />{i.nombre}</label><b>{i.cantidad} {i.unidad_base}</b></li>)}</ul>
            )}
          </aside>
        </div>
      )}
    </>
  );
}
