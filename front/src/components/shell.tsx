import { Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import { Bookmark, ChefHat, Clock, Leaf, Star } from "lucide-react";
import { session, USING_MOCK, DIFICULTAD_LABEL, type Receta, type Usuario } from "@/lib/api";

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

export function Shell({ children }: { children: ReactNode }) {
  const user = useUser();
  const navigate = useNavigate();
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-4 py-3">
          <Link to="/" className="flex items-center gap-2 font-display text-2xl font-bold text-primary"><ChefHat className="h-7 w-7" />cookpad</Link>
          <nav className="flex flex-1 flex-wrap gap-1 text-sm">
            {nav.map((n) => (
              <Link key={n.to} to={n.to} activeOptions={{ exact: n.to === "/" }} className="rounded-full px-3 py-1.5 text-muted-foreground hover:text-foreground" activeProps={{ className: "bg-secondary text-foreground font-semibold" }}>{n.label}</Link>
            ))}
          </nav>
          {user ? (
            <div className="flex items-center gap-2">
              <Link to="/recetas/nueva" className="btn-primary">+ Publicar</Link>
              <span className="text-sm text-muted-foreground">Hola, {user.nombre}</span>
              <button className="btn-ghost" onClick={() => { session.clear(); navigate({ to: "/" }); }}>Salir</button>
            </div>
          ) : (
            <div className="flex gap-2"><Link to="/login" className="btn-ghost">Ingresar</Link><Link to="/registro" className="btn-primary">Crear cuenta</Link></div>
          )}
        </div>
        {USING_MOCK && <div className="bg-accent px-4 py-1 text-center text-xs text-accent-foreground">Modo demo: datos simulados. Configurá <b>VITE_API_URL</b> para conectar tu backend FastAPI. Probá con ana@cookpad.com / 1234</div>}
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
    </div>
  );
}

export function PageTitle({ title, sub }: { title: string; sub?: string }) {
  return <div className="mb-6"><h1 className="text-4xl font-bold">{title}</h1>{sub && <p className="mt-1 text-muted-foreground">{sub}</p>}</div>;
}

export function RecetaCard({ r, extra }: { r: Receta; extra?: ReactNode }) {
  return (
    <Link to="/recetas/$id" params={{ id: String(r.id) }} className="card group flex flex-col gap-3 p-5 transition-transform hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-xl font-semibold group-hover:text-primary">{r.titulo}</h3>
        {r.es_vegana && <span className="chip-herb"><Leaf className="h-3 w-3" />Vegana</span>}
      </div>
      <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
        <span className="chip"><Clock className="h-3 w-3" />{r.tiempo_min} min</span>
        <span className="chip">{DIFICULTAD_LABEL[r.dificultad]}</span>
        <span className="chip">{r.porciones} porc.</span>
        {r.puntaje_promedio != null && <span className="chip"><Star className="h-3 w-3" />{r.puntaje_promedio}</span>}
        {r.veces_guardada != null && <span className="chip"><Bookmark className="h-3 w-3" />{r.veces_guardada}</span>}
      </div>
      {r.autor_nombre && <p className="text-xs text-muted-foreground">por {r.autor_nombre}</p>}
      {extra}
    </Link>
  );
}

export function RequireUser({ children }: { children: (u: Usuario) => ReactNode }) {
  const u = useUser();
  if (!u) return <div className="card p-8 text-center"><p className="mb-4">Necesitás iniciar sesión para ver esto.</p><Link to="/login" className="btn-primary">Ingresar</Link></div>;
  return <>{children(u)}</>;
}

export const Empty = ({ children }: { children: ReactNode }) => <div className="rounded-2xl border border-dashed border-border p-10 text-center text-muted-foreground">{children}</div>;
