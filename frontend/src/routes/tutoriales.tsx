import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { Empty, PageTitle, useUser } from "@/components/shell";
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
  const user = useUser();
  const [categoria, setCategoria] = useState<CategoriaTutorial | "">("");
  const [q, setQ] = useState("");
  const { data, isLoading, error } = useQuery({
    queryKey: ["tutoriales", categoria, q],
    queryFn: () => api.tutoriales({ categoria: categoria || undefined, q: q || undefined }),
  });

  return (
    <>
      <PageTitle title="Tutoriales en video" sub="Técnicas y consejos para disfrutar más de la cocina." />
      {user?.es_admin && <AdminTutorialForm />}
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

function AdminTutorialForm() {
  const queryClient = useQueryClient();
  const [titulo, setTitulo] = useState("");
  const [videoUrl, setVideoUrl] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [categoria, setCategoria] = useState<CategoriaTutorial>("tecnicas");
  const createTutorial = useMutation({
    mutationFn: () => api.crearTutorial({
      titulo,
      video_url: videoUrl,
      descripcion: descripcion || null,
      categoria,
    }),
    onSuccess: () => {
      setTitulo("");
      setVideoUrl("");
      setDescripcion("");
      void queryClient.invalidateQueries({ queryKey: ["tutoriales"] });
      toast.success("Tutorial agregado.");
    },
    onError: (error: Error) => toast.error(error.message),
  });

  return (
    <form
      className="card mb-8 grid gap-3 p-4 sm:grid-cols-2"
      onSubmit={(event) => {
        event.preventDefault();
        createTutorial.mutate();
      }}
    >
      <h2 className="text-xl font-semibold sm:col-span-2">Agregar tutorial (administrador)</h2>
      <div>
        <label className="label" htmlFor="tutorial-title">Título</label>
        <input id="tutorial-title" className="input" required maxLength={200} value={titulo}
          onChange={(event) => setTitulo(event.target.value)} />
      </div>
      <div>
        <label className="label" htmlFor="tutorial-url">URL directa del video MP4</label>
        <input id="tutorial-url" className="input" type="url" required maxLength={500} value={videoUrl}
          placeholder="https://servidor/video.mp4" onChange={(event) => setVideoUrl(event.target.value)} />
      </div>
      <div>
        <label className="label" htmlFor="tutorial-category">Categoría</label>
        <select id="tutorial-category" className="input" value={categoria}
          onChange={(event) => setCategoria(event.target.value as CategoriaTutorial)}>
          {categorias.filter((item) => item.value).map((item) => (
            <option key={item.value} value={item.value}>{item.label}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="label" htmlFor="tutorial-description">Descripción (opcional)</label>
        <input id="tutorial-description" className="input" maxLength={2000} value={descripcion}
          onChange={(event) => setDescripcion(event.target.value)} />
      </div>
      <button className="btn-primary sm:col-span-2 sm:justify-self-start" type="submit"
        disabled={createTutorial.isPending}>
        {createTutorial.isPending ? "Guardando…" : "Agregar video"}
      </button>
    </form>
  );
}
