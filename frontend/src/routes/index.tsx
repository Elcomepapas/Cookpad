import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, type FiltrosRecetas } from "@/lib/api";
import { Empty, PageTitle, RecetaCard } from "@/components/shell";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "Recetas — Cookpad" },
    { name: "description", content: "Buscá recetas por título, ingrediente, dificultad y tiempo." },
    { property: "og:title", content: "Recetas — Cookpad" },
    { property: "og:description", content: "Buscá recetas de la comunidad Cookpad." },
  ] }),
  component: Index,
});

function Index() {
  const [f, setF] = useState<FiltrosRecetas>({ orden: "fecha" });
  const { data, isLoading, error } = useQuery({ queryKey: ["recetas", f], queryFn: () => api.recetas(f) });
  const set = (k: keyof FiltrosRecetas, v: unknown) => setF((p) => ({ ...p, [k]: v }));
  return (
    <>
      <div className="mb-8 overflow-hidden rounded-2xl">
        <img
          src="https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=1600&q=80"
          alt="Persona cocinando en su cocina"
          className="h-56 w-full object-cover md:h-80"
          loading="eager"
        />
      </div>
      <PageTitle title="¿Qué cocinamos hoy?" sub="Recetas de la comunidad, para cualquier cantidad de porciones." />
      <div className="card mb-8 grid gap-3 p-4 md:grid-cols-6">
        <div className="md:col-span-2"><label className="label">Título</label><input className="input" placeholder="Ej: guiso" onChange={(e) => set("q", e.target.value)} /></div>
        <div><label className="label">Ingrediente</label><input className="input" placeholder="pollo" onChange={(e) => set("ingrediente", e.target.value)} /></div>
        <div><label className="label">Dificultad</label>
          <select className="input" onChange={(e) => set("dificultad", e.target.value)}><option value="">Todas</option><option value="facil">Fácil</option><option value="media">Media</option><option value="dificil">Difícil</option></select></div>
        <div><label className="label">Tiempo máx (min)</label><input type="number" min={1} className="input" onChange={(e) => set("tiempo_max", e.target.value)} /></div>
        <div><label className="label">Ordenar</label>
          <select className="input" value={f.orden} onChange={(e) => set("orden", e.target.value)}><option value="fecha">Más nuevas</option><option value="puntaje">Mejor puntaje</option></select></div>
        <label className="flex items-center gap-2 text-sm md:col-span-6"><input type="checkbox" onChange={(e) => set("vegana", e.target.checked)} /> Solo veganas</label>
      </div>
      {isLoading ? <p className="text-muted-foreground">Cargando…</p> : error ? <Empty>{(error as Error).message}</Empty> : !data?.length ? <Empty>No hay recetas con esos filtros.</Empty> : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{data.map((r) => <RecetaCard key={r.id} r={r} />)}</div>
      )}
    </>
  );
}
