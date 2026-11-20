import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { Search } from "lucide-react";
import { api, type Dificultad, type FiltrosRecetas } from "@/lib/api";
import { Empty, RecetaCard } from "@/components/shell";
import { FOTO_PORTADA } from "@/lib/fotos";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "Recetas — El Rincón del Cocinero" },
    { name: "description", content: "Buscá recetas por título, ingrediente, dificultad y tiempo." },
    { property: "og:title", content: "Recetas — El Rincón del Cocinero" },
    { property: "og:description", content: "Buscá recetas de la comunidad de El Rincón del Cocinero." },
  ] }),
  component: Index,
});

function Index() {
  const [f, setF] = useState<FiltrosRecetas>({ ordenar_por: "fecha" });
  const { data, isLoading, error } = useQuery({ queryKey: ["recetas", f], queryFn: () => api.recetas(f) });
  const set = <K extends keyof FiltrosRecetas,>(k: K, v: FiltrosRecetas[K]) => setF((p) => ({ ...p, [k]: v }));
  const resultados = useRef<HTMLElement>(null);

  return (
    <>
      <section className="relative left-1/2 -mt-8 mb-10 w-screen -translate-x-1/2 overflow-hidden bg-laurel">
        <img src={FOTO_PORTADA} alt="" className="absolute inset-0 h-full w-full object-cover" loading="eager" fetchPriority="high" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgb(30_58_43/0.55)_0%,rgb(30_58_43/0.88)_75%)]" aria-hidden />
        <div className="portada-entra relative mx-auto flex max-w-3xl flex-col items-center px-4 py-20 text-center sm:py-28">
          <h1 className="text-5xl !text-white drop-shadow-[0_2px_12px_rgb(0_0_0/0.35)] sm:text-7xl">¿Qué cocinás hoy?</h1>
          <p className="mt-4 max-w-xl text-lg text-white/85 sm:text-xl">Recetas caseras de la comunidad, escalables a las porciones que necesites.</p>
          <form
            role="search"
            className="mt-8 flex w-full max-w-xl items-center gap-2 rounded-full bg-white p-1.5 pl-5 shadow-[0_20px_40px_-20px_rgb(0_0_0/0.6)]"
            onSubmit={(e) => { e.preventDefault(); resultados.current?.scrollIntoView({ behavior: "smooth", block: "start" }); }}
          >
            <Search className="h-5 w-5 shrink-0 text-muted-foreground" aria-hidden />
            <label htmlFor="buscar-titulo" className="sr-only">Buscar receta por título</label>
            <input
              id="buscar-titulo"
              className="min-w-0 flex-1 bg-transparent py-2 text-base text-foreground outline-none placeholder:text-muted-foreground"
              placeholder="Guiso, panqueques, arroz…"
              value={f.titulo ?? ""}
              onChange={(e) => set("titulo", e.target.value)}
            />
            <button className="btn-primary px-5 py-2.5 text-base">Buscar</button>
          </form>
        </div>
      </section>

      <div className="card mb-10 grid gap-4 p-5 sm:grid-cols-2 md:grid-cols-5 md:items-end">
        <div><label className="label" htmlFor="f-ing">Ingrediente</label><input id="f-ing" className="input" placeholder="pollo" onChange={(e) => set("ingrediente", e.target.value)} /></div>
        <div><label className="label" htmlFor="f-dif">Dificultad</label>
          <select id="f-dif" className="input" onChange={(e) => set("dificultad", e.target.value ? e.target.value as Dificultad : undefined)}><option value="">Todas</option><option value="facil">Fácil</option><option value="media">Media</option><option value="dificil">Difícil</option></select></div>
        <div><label className="label" htmlFor="f-tiempo">Tiempo máx. (min)</label><input id="f-tiempo" type="number" min={1} className="input" onChange={(e) => set("tiempo_max", e.target.value)} /></div>
        <div><label className="label" htmlFor="f-orden">Ordenar</label>
          <select id="f-orden" className="input" value={f.ordenar_por} onChange={(e) => set("ordenar_por", e.target.value as "fecha" | "puntaje")}><option value="fecha">Más nuevas</option><option value="puntaje">Mejor puntaje</option></select></div>
        <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-input px-3 py-2 text-sm font-medium has-[:checked]:border-herb has-[:checked]:bg-herb/10">
          <input type="checkbox" className="accent-[var(--herb)]" onChange={(e) => set("vegana", e.target.checked)} /> Solo veganas
        </label>
      </div>

      <section ref={resultados} className="scroll-mt-32" aria-label="Recetas">
        {isLoading ? <p className="text-center text-muted-foreground">Cargando…</p> : error ? <Empty>{(error as Error).message}</Empty> : !data?.length ? <Empty>No hay recetas con esos filtros. Probá quitando alguno.</Empty> : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">{data.map((r) => <RecetaCard key={r.id} r={r} />)}</div>
        )}
      </section>
    </>
  );
}
