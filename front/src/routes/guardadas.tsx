import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Empty, PageTitle, RecetaCard, RequireUser } from "@/components/shell";

export const Route = createFileRoute("/guardadas")({
  head: () => ({ meta: [
    { title: "Mis guardadas — Cookpad" },
    { name: "description", content: "Tus recetas favoritas, ordenadas por fecha." },
    { property: "og:title", content: "Mis guardadas — Cookpad" },
    { property: "og:description", content: "Tus recetas favoritas en Cookpad." },
  ] }),
  component: () => <RequireUser>{(u) => <Guardadas uid={u.id} />}</RequireUser>,
});

function Guardadas({ uid }: { uid: number }) {
  const { data } = useQuery({ queryKey: ["guardadas", uid], queryFn: () => api.guardadas(uid) });
  return (
    <>
      <PageTitle title="Mis guardadas" sub="Ordenadas de la más reciente a la más vieja." />
      {!data?.length ? <Empty>Todavía no guardaste recetas.</Empty> : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{data.map((r) => <RecetaCard key={r.id} r={r} />)}</div>}
    </>
  );
}
