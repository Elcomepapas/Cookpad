import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { api, session } from "@/lib/api";
import { MarcoCuenta } from "@/components/shell";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [
    { title: "Ingresar — El Rincón del Cocinero" },
    { name: "description", content: "Ingresá a tu cuenta de El Rincón del Cocinero." },
    { property: "og:title", content: "Ingresar — El Rincón del Cocinero" },
    { property: "og:description", content: "Ingresá a tu cuenta de El Rincón del Cocinero." },
  ] }),
  component: Login,
});

function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [busy, setBusy] = useState(false);
  return (
    <MarcoCuenta><form className="space-y-4 p-6 sm:p-8" onSubmit={async (e) => {
      e.preventDefault(); setBusy(true);
      try { const r = await api.login({ email, password }); session.set(r.access_token, r.usuario); nav({ to: "/" }); }
      catch (er) { toast.error((er as Error).message); } finally { setBusy(false); }
    }}>
      <h1 className="text-3xl font-bold">Ingresar</h1>
      <div><label className="label">Email</label><input type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} /></div>
      <div><label className="label">Contraseña</label><input type="password" required className="input" value={password} onChange={(e) => setPassword(e.target.value)} /></div>
      <button className="btn-primary w-full" disabled={busy}>Ingresar</button>
      <p className="text-center text-sm text-muted-foreground">¿No tenés cuenta? <Link to="/registro" className="font-semibold text-laurel underline decoration-primary decoration-2 underline-offset-2">Registrate</Link></p>
    </form></MarcoCuenta>
  );
}
