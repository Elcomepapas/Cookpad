import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { api, session } from "@/lib/api";
import { MarcoCuenta } from "@/components/shell";

export const Route = createFileRoute("/registro")({
  head: () => ({ meta: [
    { title: "Crear cuenta — El Rincón del Cocinero" },
    { name: "description", content: "Registrate para publicar y guardar recetas." },
    { property: "og:title", content: "Crear cuenta — El Rincón del Cocinero" },
    { property: "og:description", content: "Sumate a la comunidad de recetas." },
  ] }),
  component: Registro,
});

function Registro() {
  const nav = useNavigate();
  const [f, setF] = useState({ nombre: "", email: "", password: "" }); const [busy, setBusy] = useState(false);
  return (
    <MarcoCuenta><form className="space-y-4 p-6 sm:p-8" onSubmit={async (e) => {
      e.preventDefault(); setBusy(true);
      try {
        await api.register(f);
        const r = await api.login({ email: f.email, password: f.password });
        session.set(r.access_token, r.usuario); toast.success("¡Bienvenido/a!"); nav({ to: "/" });
      } catch (er) { toast.error((er as Error).message); } finally { setBusy(false); }
    }}>
      <h1 className="text-3xl font-bold">Crear cuenta</h1>
      {(["nombre", "email", "password"] as const).map((k) => (
        <div key={k}><label className="label">{k === "password" ? "Contraseña" : k}</label>
          <input required type={k === "email" ? "email" : k === "password" ? "password" : "text"} className="input" value={f[k]} onChange={(e) => setF({ ...f, [k]: e.target.value })} /></div>
      ))}
      <button className="btn-primary w-full" disabled={busy}>Registrarme</button>
      <p className="text-center text-sm text-muted-foreground">¿Ya tenés cuenta? <Link to="/login" className="font-semibold text-laurel underline decoration-primary decoration-2 underline-offset-2">Ingresá</Link></p>
    </form></MarcoCuenta>
  );
}
