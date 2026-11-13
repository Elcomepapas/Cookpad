import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageTitle, RecetaCard } from "@/components/shell";

export const Route = createFileRoute("/estadisticas")({
  head: () => ({ meta: [
    { title: "Lo más popular — Cookpad" },
    { name: "description", content: "Las recetas más guardadas y los ingredientes más usados." },
    { property: "og:title", content: "Lo más popular — Cookpad" },
    { property: "og:description", content: "Top recetas e ingredientes de la comunidad." },
  ] }),
  component: Stats,
});

function Stats() {
  const { data: top } = useQuery({ queryKey: ["top"], queryFn: api.topGuardadas });
  const { data: ings } = useQuery({ queryKey: ["masusados"], queryFn: api.ingredientesMasUsados });
  const max = Math.max(1, ...(ings?.map((i) => i.cantidad_recetas) ?? [1]));
  return (
    <>
      <PageTitle title="Lo más popular" />
      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <section><h2 className="mb-3 text-2xl font-semibold">Top 10 más guardadas</h2>
          <div className="grid gap-4 sm:grid-cols-2">{top?.map((r) => <RecetaCard key={r.id} r={r} />)}</div></section>
        <section className="card h-fit p-5"><h2 className="mb-4 text-2xl font-semibold">Ingredientes más usados</h2>
          <ul className="space-y-3">{ings?.map((i) => (
            <li key={i.id} className="text-sm"><div className="flex justify-between"><span>{i.nombre}</span><b>{i.cantidad_recetas}</b></div>
              <div className="mt-1 h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-primary" style={{ width: `${(i.cantidad_recetas / max) * 100}%` }} /></div></li>
          ))}</ul></section>
      </div>
    </>
  );
}
