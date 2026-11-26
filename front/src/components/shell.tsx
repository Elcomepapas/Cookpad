import { Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import { Bookmark, ChefHat, Clock, Leaf, Star, Users } from "lucide-react";
import { session, USING_MOCK, DIFICULTAD_LABEL, type Receta, type Usuario } from "@/lib/api";
import { fotoReceta } from "@/lib/fotos";
import { tituloVisible } from "@/lib/utils";

export const NOMBRE_SITIO = "El Rincón del Cocinero";

export function useUser() {
  const [u, setU] = useState<Usuario | null>(null);
  useEffect(() => { const f = () => setU(session.user()); f(); window.addEventListener("auth", f); return () => window.removeEventListener("auth", f); }, []);
  return u;
}

const nav = [
  { to: "/", label: "Recetas" },
  { to: "/cocinar", label: "¿Qué cocino?" },
  { to: "/plan", label: "Mi plan" },
  { to: "/guardadas", label: "Guardadas" },
  { to: "/estadisticas", label: "Popular" },
  { to: "/tutoriales", label: "Tutoriales" },
  { to: "/heladera", label: "Mi heladera" },
  { to: "/ingredientes", label: "Ingredientes" },
] as const;

function Logo() {
  return (
    <Link to="/" className="group flex items-center gap-2.5 text-laurel-foreground" aria-label={`${NOMBRE_SITIO}, inicio`}>
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-laurel transition-transform group-hover:-rotate-12">
        <ChefHat className="h-6 w-6" strokeWidth={2.2} />
      </span>
      <span className="font-display text-xl leading-none sm:text-2xl">{NOMBRE_SITIO}</span>
    </Link>
  );
}

export function Shell({ children }: { children: ReactNode }) {
  const user = useUser();
  const navigate = useNavigate();
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-20 bg-laurel text-laurel-foreground shadow-[0_1px_0_rgb(0_0_0/0.15)]">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 pt-3">
          <Logo />
          {user ? (
            <div className="flex items-center gap-2">
              <span className="hidden text-sm text-laurel-foreground/75 sm:inline">Hola, {user.nombre}</span>
              <Link to="/recetas/nueva" className="btn-primary">+ Publicar</Link>
              <button className="btn border border-white/25 text-laurel-foreground hover:bg-white/10" onClick={() => { session.clear(); navigate({ to: "/" }); }}>Salir</button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Link to="/login" className="btn border border-white/25 text-laurel-foreground hover:bg-white/10">Ingresar</Link>
              <Link to="/registro" className="btn-primary">Crear cuenta</Link>
            </div>
          )}
        </div>
        <nav className="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4 pt-2 pb-2.5 text-sm [scrollbar-width:none]" aria-label="Secciones">
          {nav.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              activeOptions={{ exact: n.to === "/" }}
              className="shrink-0 rounded-full px-3 py-1.5 text-laurel-foreground/75 transition-colors hover:bg-white/10 hover:text-laurel-foreground"
              activeProps={{ className: "bg-white/15 !text-laurel-foreground font-semibold" }}
            >
              {n.label}
            </Link>
          ))}
        </nav>
        {USING_MOCK && <div className="bg-accent px-4 py-1 text-center text-xs text-accent-foreground">Modo demo: datos simulados. Configurá <b>VITE_API_URL</b> para conectar tu backend FastAPI. Probá con ana@cookpad.com / 1234</div>}
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">{children}</main>
      <footer className="bg-laurel text-laurel-foreground/70">
        <div className="mx-auto flex max-w-6xl flex-col items-center gap-1 px-4 py-8 text-center text-sm sm:flex-row sm:justify-between sm:text-left">
          <span className="font-display text-lg text-laurel-foreground">{NOMBRE_SITIO}</span>
          <span>Recetas caseras de la comunidad, para cocinar con lo que hay.</span>
        </div>
      </footer>
    </div>
  );
}

export function PageTitle({ title, sub }: { title: string; sub?: string }) {
  return (
    <div className="mb-8">
      <h1 className="text-4xl sm:text-5xl">{title}</h1>
      {sub && <p className="mt-2 max-w-2xl text-lg text-muted-foreground">{sub}</p>}
    </div>
  );
}

export function FotoReceta({ r, ancho, className }: { r: Pick<Receta, "id" | "titulo">; ancho?: number; className?: string }) {
  const [rota, setRota] = useState(false);
  if (rota) return <div className={`bg-secondary ${className ?? ""}`} aria-hidden />;
  return <img src={fotoReceta(r, ancho)} alt="" loading="lazy" onError={() => setRota(true)} className={`object-cover ${className ?? ""}`} />;
}

export function RecetaCard({ r, extra }: { r: Receta; extra?: ReactNode }) {
  return (
    <Link to="/recetas/$id" params={{ id: String(r.id) }} className="card group flex flex-col overflow-hidden transition-shadow hover:shadow-[0_18px_36px_-18px_rgb(30_58_43/0.45)]">
      <div className="relative aspect-[4/3] overflow-hidden bg-secondary">
        <FotoReceta r={r} ancho={640} className="h-full w-full transition-transform duration-500 group-hover:scale-[1.04]" />
        {r.es_vegana && <span className="chip-herb absolute top-3 left-3 shadow"><Leaf className="h-3 w-3" />Vegana</span>}
        {r.puntaje_promedio != null && (
          <span className="absolute top-3 right-3 inline-flex items-center gap-1 rounded-full bg-white/95 px-2.5 py-0.5 text-xs font-bold text-laurel shadow">
            <Star className="h-3 w-3 fill-primary text-primary" />{r.puntaje_promedio}
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-3 p-5">
        <h3 className="text-xl text-laurel group-hover:underline group-hover:decoration-primary group-hover:decoration-2 group-hover:underline-offset-4">{tituloVisible(r.titulo)}</h3>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-1"><Clock className="h-4 w-4" />{r.tiempo_min} min</span>
          <span>{DIFICULTAD_LABEL[r.dificultad]}</span>
          <span className="inline-flex items-center gap-1"><Users className="h-4 w-4" />{r.porciones} porc.</span>
          {r.veces_guardada != null && <span className="inline-flex items-center gap-1"><Bookmark className="h-4 w-4" />{r.veces_guardada}</span>}
        </div>
        {r.autor_nombre && <p className="mt-auto text-sm text-muted-foreground">por <span className="font-semibold text-foreground">{r.autor_nombre}</span></p>}
        {extra}
      </div>
    </Link>
  );
}

export function MarcoCuenta({ children }: { children: ReactNode }) {
  return (
    <div className="card mx-auto grid max-w-3xl overflow-hidden md:grid-cols-[1fr_1.1fr]">
      <div className="relative hidden bg-laurel md:block">
        <img src="https://images.unsplash.com/photo-1495521821757-a1efb6729352?auto=format&fit=crop&w=900&q=75" alt="" className="absolute inset-0 h-full w-full object-cover opacity-80" />
        <div className="absolute inset-0 bg-gradient-to-t from-laurel/90 to-transparent" aria-hidden />
        <p className="absolute inset-x-0 bottom-0 p-6 font-display text-2xl leading-tight text-white">Tu lugar para guardar, planear y compartir lo que cocinás.</p>
      </div>
      {children}
    </div>
  );
}

export function RequireUser({ children }: { children: (u: Usuario) => ReactNode }) {
  const u = useUser();
  if (!u) return <div className="card mx-auto max-w-md p-8 text-center"><p className="mb-4">Necesitás iniciar sesión para ver esto.</p><Link to="/login" className="btn-primary">Ingresar</Link></div>;
  return <>{children(u)}</>;
}

export const Empty = ({ children }: { children: ReactNode }) => <div className="rounded-2xl border-2 border-dashed border-border bg-card/60 p-10 text-center text-muted-foreground">{children}</div>;
