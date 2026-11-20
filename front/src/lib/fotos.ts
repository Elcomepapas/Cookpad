// Fotos decorativas (Unsplash). El backend no guarda imágenes de recetas, así que
// elegimos una foto según palabras del título; si ninguna coincide, se usa una
// foto genérica fija por id para que cada receta conserve siempre la misma.
const u = (id: string, w: number) => `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=${w}&q=75`;

const POR_PALABRA: [RegExp, string][] = [
  [/panquec|panqueq|crep|waffle|hotcake/, "1567620905732-2d1ec7ab7445"],
  [/torta|postre|bizcoch|budin|tarta dulce/, "1565958011703-44f9829ba187"],
  [/pollo|gallina|pechuga|suprema/, "1598103442097-8b74394b95c6"],
  [/carne|bife|asado|vacio|milanesa|lomo/, "1600891964092-4316c288032e"],
  [/lenteja|guiso|garbanzo|estofado|locro/, "1585937421612-70a008356fbe"],
  [/fideo|pasta|tallarin|noqui|ravio/, "1447279506476-3faec8071eee"],
  [/sopa|crema de|calabaza|zanahoria/, "1476718406336-bb5a9690ee2a"],
  [/papa|pure/, "1518977676601-b53f82aba655"],
  [/ensalada/, "1540189549336-e6e99c3679fe"],
  [/tomate|salsa/, "1592417817098-8fd3d9eb14a5"],
  [/arroz|risotto/, "1516684732162-798a0062be99"],
  [/salteado|wok|verdura/, "1604908176997-125f25cc6f3d"],
];

const GENERICAS = [
  "1504674900247-0877df9cc836",
  "1547592180-85f173990554",
  "1512621776951-a57141f2eefd",
  "1490645935967-10de6ba17061",
  "1546069901-ba9599a7e63c",
];

const normalizar = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function fotoReceta(r: { id: number; titulo: string }, ancho = 800) {
  const t = normalizar(r.titulo);
  const hit = POR_PALABRA.find(([re]) => re.test(t));
  return u(hit ? hit[1] : GENERICAS[Math.abs(r.id) % GENERICAS.length] ?? GENERICAS[0]!, ancho);
}

export const FOTO_PORTADA = u("1466637574441-749b8f19452f", 2000);
