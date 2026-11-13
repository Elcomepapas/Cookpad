import { createFileRoute } from "@tanstack/react-router";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";
import { AlertTriangle, Refrigerator, Upload } from "lucide-react";
import { Empty, PageTitle, RequireUser } from "@/components/shell";
import { api, type ReciboPreview } from "@/lib/api";

export const Route = createFileRoute("/heladera")({
  head: () => ({ meta: [{ title: "Mi heladera — Cookpad" }] }),
  component: () => <RequireUser>{(user) => <HeladeraPage userId={user.id} />}</RequireUser>,
});

const money = (amount: number) => new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
}).format(amount);

function HeladeraPage({ userId }: { userId: number }) {
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ReciboPreview | null>(null);
  const { data: fridge, isLoading, error } = useQuery({
    queryKey: ["heladera", userId],
    queryFn: api.heladera,
  });
  const { data: suggestions } = useQuery({
    queryKey: ["heladera-sugerencias", userId],
    queryFn: api.sugerenciasHeladera,
  });
  const { data: ingredients } = useQuery({
    queryKey: ["ingredientes"],
    queryFn: api.ingredientes,
  });
  const expiringProducts = fridge?.compras.flatMap((purchase) =>
    purchase.productos
      .filter((product) => product.proximo_a_vencer)
      .map((product) => ({ ...product, comercio: purchase.comercio })),
  ) ?? [];

  const upload = useMutation({
    mutationFn: (receipt: File) => api.previsualizarRecibo(receipt),
    onSuccess: (value) => {
      setPreview(value);
      toast.success("Recibo leído. Revisá los productos antes de guardarlos.");
    },
    onError: (cause: Error) => toast.error(cause.message),
  });
  const save = useMutation({
    mutationFn: () => {
      if (!preview) throw new Error("Primero cargá un recibo.");
      const products = preview.productos.map((product) => {
        if (product.ingrediente_id == null) {
          throw new Error(`Elegí un ingrediente del catálogo para «${product.nombre}».`);
        }
        return {
          ingrediente_id: product.ingrediente_id,
          nombre_producto: product.nombre,
          cantidad: product.cantidad,
          precio_total: product.precio_total,
          fecha_vencimiento: product.fecha_vencimiento,
        };
      });
      return api.crearCompraHeladera({
        comercio: preview.comercio,
        fecha_compra: preview.fecha_compra,
        productos: products,
      });
    },
    onSuccess: () => {
      setPreview(null);
      setFile(null);
      void queryClient.invalidateQueries({ queryKey: ["heladera", userId] });
      void queryClient.invalidateQueries({ queryKey: ["heladera-sugerencias", userId] });
      toast.success("Compra agregada a tu heladera.");
    },
    onError: (cause: Error) => toast.error(cause.message),
  });

  const updateProduct = (index: number, patch: Partial<ReciboPreview["productos"][number]>) => {
    setPreview((current) => current ? {
      ...current,
      productos: current.productos.map((product, productIndex) =>
        productIndex === index ? { ...product, ...patch } : product),
    } : current);
  };
  const submitReceipt = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (file) upload.mutate(file);
  };

  return (
    <>
      <PageTitle title="Mi heladera" sub="Tus compras, vencimientos y recetas que podés completar." />
      <section className="card mb-8 p-5">
        <div className="mb-4 flex items-center gap-3">
          <Upload className="h-5 w-5 text-primary" />
          <div>
            <h2 className="text-xl font-semibold">Agregar una compra desde un recibo</h2>
            <p className="text-sm text-muted-foreground">Subí un PDF simulado en formato Cookpad. El archivo se procesa y no se conserva.</p>
          </div>
        </div>
        <form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={submitReceipt}>
          <div className="flex-1">
            <label className="label" htmlFor="receipt-file">Recibo PDF</label>
            <input id="receipt-file" className="input" type="file" accept="application/pdf,.pdf" required
              onChange={(event) => { setFile(event.target.files?.[0] ?? null); setPreview(null); }} />
          </div>
          <button className="btn-primary" type="submit" disabled={!file || upload.isPending}>
            {upload.isPending ? "Leyendo recibo…" : "Leer recibo"}
          </button>
        </form>
        <details className="mt-4 text-sm text-muted-foreground">
          <summary className="cursor-pointer font-semibold">Formato del PDF simulado</summary>
          <pre className="mt-2 overflow-x-auto rounded-lg bg-muted p-3 text-xs leading-5">{`COOKPAD_RECIBO|1
COMERCIO|Supermercado
FECHA|2026-11-13
PRODUCTO|Arroz|500|g|1800.00|2026-12-01
PRODUCTO|Cebolla|2|unidad|700.00|`}</pre>
          <p className="mt-2">Cada producto usa cantidad, unidad (g, ml o unidad), precio total de esa línea y vencimiento (YYYY-MM-DD; puede quedar vacío si no aplica). Si el recibo no trae el vencimiento, podés completarlo en la revisión.</p>
        </details>

        {preview && (
          <div className="mt-6 border-t border-border pt-5">
            <h3 className="mb-3 text-lg font-semibold">Revisá la compra</h3>
            <div className="mb-4 grid gap-3 sm:grid-cols-2">
              <div><label className="label" htmlFor="purchase-store">Comercio</label>
                <input id="purchase-store" className="input" maxLength={120} required value={preview.comercio}
                  onChange={(event) => setPreview({ ...preview, comercio: event.target.value })} /></div>
              <div><label className="label" htmlFor="purchase-date">Fecha de compra</label>
                <input id="purchase-date" className="input" type="date" required value={preview.fecha_compra}
                  onChange={(event) => setPreview({ ...preview, fecha_compra: event.target.value })} /></div>
            </div>
            <div className="space-y-3">
              {preview.productos.map((product, index) => {
                const match = ingredients?.find((ingredient) => ingredient.id === product.ingrediente_id);
                return (
                  <div key={`${product.nombre}-${index}`} className="grid gap-3 rounded-xl border border-border p-3 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="sm:col-span-2 lg:col-span-1">
                      <label className="label" htmlFor={`receipt-ingredient-${index}`}>Producto: {product.nombre}</label>
                      <select id={`receipt-ingredient-${index}`} className="input" required
                        value={product.ingrediente_id ?? ""}
                        onChange={(event) => updateProduct(index, { ingrediente_id: event.target.value ? Number(event.target.value) : null })}>
                        <option value="">Elegí del catálogo</option>
                        {ingredients?.filter((ingredient) => ingredient.unidad_base === product.unidad)
                          .map((ingredient) => <option key={ingredient.id} value={ingredient.id}>{ingredient.nombre}</option>)}
                      </select>
                      {match && <span className="text-xs text-muted-foreground">Unidad del catálogo: {match.unidad_base}</span>}
                    </div>
                    <div><label className="label" htmlFor={`receipt-quantity-${index}`}>Cantidad ({product.unidad})</label>
                      <input id={`receipt-quantity-${index}`} className="input" type="number" min="0.01" step="0.01" required value={product.cantidad}
                        onChange={(event) => updateProduct(index, { cantidad: Number(event.target.value) })} /></div>
                    <div><label className="label" htmlFor={`receipt-price-${index}`}>Precio de la línea</label>
                      <input id={`receipt-price-${index}`} className="input" type="number" min="0" step="0.01" required value={product.precio_total}
                        onChange={(event) => updateProduct(index, { precio_total: Number(event.target.value) })} /></div>
                    <div><label className="label" htmlFor={`receipt-expiry-${index}`}>Vencimiento (si aplica)</label>
                      <input id={`receipt-expiry-${index}`} className="input" type="date" value={product.fecha_vencimiento ?? ""}
                        onChange={(event) => updateProduct(index, { fecha_vencimiento: event.target.value || null })} />
                      <span className="text-xs text-muted-foreground">Ingresá la fecha si no figuraba en el recibo.</span></div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
              <span className="font-semibold">Total de la compra: {money(preview.productos.reduce((sum, product) => sum + product.precio_total, 0))}</span>
              <button className="btn-primary" type="button" disabled={save.isPending || !preview.productos.length}
                onClick={() => save.mutate()}>{save.isPending ? "Guardando…" : "Confirmar compra"}</button>
            </div>
          </div>
        )}
      </section>

      <section className="mb-10">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div><h2 className="text-2xl font-semibold">Compras e inventario</h2>
            <p className="text-sm text-muted-foreground">Los productos se mantienen agrupados por cada compra.</p></div>
          <div className="card px-4 py-2 text-sm">Total de todas las compras: <b>{money(fridge?.total_gastado ?? 0)}</b></div>
        </div>
        {expiringProducts.length > 0 && (
          <div role="status" className="mb-4 flex items-start gap-3 rounded-xl border border-accent bg-accent/40 p-4 text-sm">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
            <p><b>Hay productos próximos a vencer:</b> {expiringProducts.map((product) =>
              `${product.nombre} (${product.dias_para_vencer === 0 ? "vence hoy" : `${product.dias_para_vencer} días`})`,
            ).join(", ")}.</p>
          </div>
        )}
        {isLoading ? <p className="text-muted-foreground">Cargando heladera…</p>
          : error ? <Empty>{(error as Error).message}</Empty>
            : !fridge?.compras.length ? <Empty><Refrigerator className="mx-auto mb-2 h-8 w-8" />Todavía no cargaste compras en tu heladera.</Empty>
              : <div className="space-y-5">{fridge.compras.map((purchase) => (
                <article key={purchase.id} className="card overflow-hidden">
                  <header className="flex flex-wrap items-center justify-between gap-2 border-b border-border bg-muted/50 px-4 py-3">
                    <div><h3 className="font-semibold">{purchase.comercio}</h3><p className="text-xs text-muted-foreground">{purchase.fecha_compra}</p></div>
                    <span className="font-semibold">{money(purchase.total)}</span>
                  </header>
                  <ul className="divide-y divide-border">
                    {purchase.productos.map((product) => (
                      <li key={product.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 text-sm">
                        <div>
                          <p className="font-medium">{product.nombre} · {product.cantidad} {product.unidad}</p>
                          <p className="text-xs text-muted-foreground">
                            {product.fecha_vencimiento ? `Vence ${product.fecha_vencimiento}` : "Sin fecha de vencimiento"}
                            {product.dias_para_vencer !== null && !product.vencido && ` · ${product.dias_para_vencer === 0 ? "vence hoy" : `faltan ${product.dias_para_vencer} días`}`}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <span>{money(product.precio_total)}</span>
                          {product.proximo_a_vencer && <span className="chip bg-accent text-accent-foreground"><AlertTriangle className="h-3 w-3" />Vence pronto</span>}
                          {product.vencido && <span className="chip bg-destructive text-destructive-foreground">Vencido</span>}
                        </div>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}</div>}
      </section>

      <section>
        <h2 className="mb-1 text-2xl font-semibold">Recetas que podés completar</h2>
        <p className="mb-4 text-sm text-muted-foreground">Solo se consideran tus recetas guardadas y productos que no estén vencidos.</p>
        {!suggestions?.length ? <Empty>No hay recetas guardadas con ingredientes disponibles que necesiten completar.</Empty>
          : <div className="grid gap-4 md:grid-cols-2">{suggestions.map((suggestion) => (
            <article key={suggestion.receta_id} className="card p-5">
              <h3 className="text-xl font-semibold">{suggestion.titulo}</h3>
              <p className="mb-3 text-sm text-muted-foreground">Tenés {suggestion.ingredientes_disponibles} de {suggestion.total_ingredientes} ingredientes.</p>
              <h4 className="mb-2 text-sm font-semibold">Para completar, podrías comprar:</h4>
              <ul className="list-inside list-disc space-y-1 text-sm">
                {suggestion.productos_a_comprar.map((product) => (
                  <li key={product.ingrediente_id}>{product.nombre} — {product.cantidad} {product.unidad}</li>
                ))}
              </ul>
            </article>
          ))}</div>}
      </section>
    </>
  );
}
