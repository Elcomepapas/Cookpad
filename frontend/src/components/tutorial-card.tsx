import type { Tutorial } from "@/lib/api";

const categoryLabels: Record<Tutorial["categoria"], string> = {
  tecnicas: "Técnicas",
  cortes: "Cortes",
  reposteria: "Repostería",
  basicos: "Básicos",
  recetas: "Recetas",
};

export function TutorialCard({ tutorial }: { tutorial: Tutorial }) {
  return (
    <article className="card overflow-hidden">
      <video
        className="aspect-video w-full bg-foreground object-cover"
        controls
        playsInline
        preload="metadata"
        poster={tutorial.miniatura_url ?? undefined}
        src={tutorial.video_url}
        aria-label={`Video: ${tutorial.titulo}`}
      >
        Tu navegador no puede reproducir este video.
      </video>
      <div className="space-y-2 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="chip">{categoryLabels[tutorial.categoria]}</span>
          {tutorial.duracion_seg != null && (
            <span className="text-xs text-muted-foreground">
              {Math.floor(tutorial.duracion_seg / 60)}:{String(tutorial.duracion_seg % 60).padStart(2, "0")}
            </span>
          )}
        </div>
        <h3 className="text-xl font-semibold">{tutorial.titulo}</h3>
        {tutorial.descripcion && <p className="text-sm text-muted-foreground">{tutorial.descripcion}</p>}
      </div>
    </article>
  );
}
