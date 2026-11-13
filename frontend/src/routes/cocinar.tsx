import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Empty, PageTitle, RecetaCard } from "@/components/shell";

export const Route = createFileRoute("/cocinar")({
  head: () => ({ meta: [
    { title: "¿Qué cocino con lo que tengo? — Cookpad" },
    { name: "description", content: "Elegí los ingredientes que tenés y encontrá recetas posibles." },
    { property: "og:title", content: "¿Qué cocino con lo que tengo? — Cookpad" },
    { property: "og:description", content: "Recetas con los ingredientes que tenés en casa." },
  ] }),
  component: Cocinar,
});

function Cocinar() {
  const { data: ings } = useQuery({ queryKey: ["ingredientes"], queryFn: api.ingredientes });
  const [sel, setSel] = useState<number[]>([]);
  const m = useMutation({ mutationFn: () => api.conIngredientes(sel) });
  return (
    <>
      <PageTitle title="¿Qué cocino con lo que tengo?" sub="Marcá lo que hay en tu heladera." />
      <div className="card mb-6 flex flex-wrap gap-2 p-4">
        {ings?.map((i) => {
          const on = sel.includes(i.id);
          return <button key={i.id} onClick={() => setSel(on ? sel.filter((x) => x !== i.id) : [...sel, i.id])} className={on ? "btn-primary" : "btn-ghost"}>{i.nombre}</button>;
        })}
      </div>
      <button className="btn-primary mb-8" disabled={!sel.length || m.isPending} onClick={() => m.mutate()}>Buscar recetas ({sel.length})</button>
      {m.data && (
        <div className="space-y-8">
          <section><h2 className="mb-3 text-2xl font-semibold">Podés hacerlas ya</h2>
            {m.data.completas.length ? <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{m.data.completas.map((r) => <RecetaCard key={r.id} r={r} />)}</div> : <Empty>Ninguna con exactamente esos ingredientes.</Empty>}</section>
          <section><h2 className="mb-3 text-2xl font-semibold">Te falta un ingrediente</h2>
            {m.data.falta_uno.length ? <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{m.data.falta_uno.map((r) => <RecetaCard key={r.id} r={r} extra={<p className="text-sm font-semibold text-primary">Falta: {r.faltante?.nombre}</p>} />)}</div> : <Empty>Nada por acá.</Empty>}</section>
        </div>
      )}
    </>
  );
}
