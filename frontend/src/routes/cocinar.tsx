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
  const [q, setQ] = useState("");
  const m = useMutation({ mutationFn: () => api.conIngredientes(sel) });
  const toggle = (id: number) => setSel((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  const norm = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const filtrados = (ings ?? []).filter((i) => norm(i.nombre).includes(norm(q.trim())));
  const elegidos = (ings ?? []).filter((i) => sel.includes(i.id));
  return (
    <>
      <PageTitle title="¿Qué cocino con lo que tengo?" sub="Buscá y marcá lo que hay en tu heladera." />
      <div className="card mb-6 space-y-4 p-4">
        <div>
          <label className="label" htmlFor="buscar-ing">Buscar ingrediente</label>
          <input
            id="buscar-ing"
            className="input"
            placeholder="Ej: tomate, huevo, arroz…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && filtrados[0]) { e.preventDefault(); if (!sel.includes(filtrados[0].id)) toggle(filtrados[0].id); setQ(""); }
            }}
          />
          <p className="mt-1 text-xs text-muted-foreground">Escribí para filtrar y tocá un ingrediente (o Enter para elegir el primero).</p>
        </div>
        {elegidos.length > 0 && (
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-semibold">Tengo:</span>
            {elegidos.map((i) => <button key={i.id} type="button" onClick={() => toggle(i.id)} className="btn-primary" title="Quitar">{i.nombre} ✕</button>)}
            <button type="button" className="text-sm text-muted-foreground underline" onClick={() => setSel([])}>Limpiar</button>
          </div>
        )}
        <div className="flex max-h-64 flex-wrap gap-2 overflow-y-auto">
          {!ings ? <p className="text-sm text-muted-foreground">Cargando ingredientes…</p>
            : !ings.length ? <p className="text-sm text-muted-foreground">El catálogo de ingredientes está vacío. Cargá ingredientes en la sección Ingredientes.</p>
            : !filtrados.length ? <p className="text-sm text-muted-foreground">No hay ingredientes que coincidan con “{q}”.</p>
            : filtrados.map((i) => {
              const on = sel.includes(i.id);
              return <button key={i.id} type="button" onClick={() => toggle(i.id)} className={on ? "btn-primary" : "btn-ghost"}>{i.nombre}</button>;
            })}
        </div>
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
