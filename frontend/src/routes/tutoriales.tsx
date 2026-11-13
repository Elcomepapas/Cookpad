import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Empty, PageTitle } from "@/components/shell";
import { TutorialCard } from "@/components/tutorial-card";
import { api, type CategoriaTutorial } from "@/lib/api";

export const Route = createFileRoute("/tutoriales")({
  head: () => ({ meta: [{ title: "Tutoriales en video — Cookpad" }] }),
  component: TutorialesPage,
});

const categorias: { value: CategoriaTutorial | ""; label: string }[] = [
  { value: "", label: "Todas las categorías" },
  { value: "tecnicas", label: "Técnicas" },
  { value: "cortes", label: "Cortes" },
  { value: "reposteria", label: "Repostería" },
  { value: "basicos", label: "Básicos" },
  { value: "recetas", label: "Recetas" },
];

function TutorialesPage() {
  const [categoria, setCategoria] = useState<CategoriaTutorial | "">("");
  const [q, setQ] = useState("");
  const { data, isLoading, error } = useQuery({
    queryKey: ["tutoriales", categoria, q],
    queryFn: () => api.tutoriales({ categoria: categoria || undefined, q: q || undefined }),
  });

  return (
    <>
      <PageTitle title="Tutoriales en video" sub="Técnicas y consejos para disfrutar más de la cocina." />
      <div className="card mb-8 grid gap-3 p-4 sm:grid-cols-[2fr_1fr]">
        <div>
          <label className="label" htmlFor="tutorial-search">Buscar por título</label>
          <input id="tutorial-search" className="input" placeholder="Ej: cortar cebolla" value={q} onChange={(event) => setQ(event.target.value)} />
        </div>
        <div>
          <label className="label" htmlFor="tutorial-category">Categoría</label>
          <select id="tutorial-category" className="input" value={categoria} onChange={(event) => setCategoria(event.target.value as CategoriaTutorial | "")}>
            {categorias.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </div>
      </div>
      {isLoading ? <p className="text-muted-foreground">Cargando tutoriales…</p>
        : error ? <Empty>{(error as Error).message}</Empty>
          : !data?.length ? <Empty>No hay tutoriales con esos filtros.</Empty>
            : <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{data.map((tutorial) => <TutorialCard key={tutorial.id} tutorial={tutorial} />)}</div>}
    </>
  );
}
