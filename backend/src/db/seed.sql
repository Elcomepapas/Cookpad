-- Cookpad 2.0 | Seed ampliado de desarrollo
-- HU1–HU12, Mi Heladera y video MP4 opcional.
-- Requiere el esquema de Cookpad ya instalado en public.
-- Clave de las cuentas demo nuevas: CookpadDemo2026!
-- Si ya cargaste el seed anterior, se conservan las filas existentes.
-- Los SELECT posteriores al COMMIT permiten comprobar la carga.

BEGIN;

SET LOCAL search_path TO public;

-- HU1: cuentas demo, incluido un administrador y dos lectores
-- para probar heladera con compras y heladera vacía.
WITH cuentas(email, nombre, es_admin) AS (
    VALUES
        ('cookpad.demo.admin@example.com', 'Admin Demo', TRUE),
        ('cookpad.demo.ana@example.com', 'Ana Demo', FALSE),
        ('cookpad.demo.bruno@example.com', 'Bruno Demo', FALSE),
        ('cookpad.demo.clara@example.com', 'Clara Demo', FALSE)
    UNION ALL
    SELECT
        'cookpad.demo.lector' || LPAD(n::text, 2, '0') || '@example.com',
        'Lector Demo ' || LPAD(n::text, 2, '0'),
        FALSE
    FROM generate_series(1, 12) AS lector(n)
)
INSERT INTO usuario (email, nombre, password_hash, es_admin)
SELECT email, nombre,
       '$2b$12$QnyFRUDFy0VNbHSlhZuemOKIjqmQSP4SqXOVlEEKwVXq4Ml8/uSuq',
       es_admin
FROM cuentas
ON CONFLICT (email) DO NOTHING;

-- HU2: catálogo de 15 ingredientes.
INSERT INTO ingrediente (nombre, unidad_base, origen_animal, calorias_por_unidad)
VALUES
    ('Arroz',           'g',      FALSE,   1.30),
    ('Pollo',           'g',      TRUE,    1.65),
    ('Tomate',          'g',      FALSE,   0.18),
    ('Leche',           'ml',     TRUE,    0.61),
    ('Huevo',           'unidad', TRUE,   72.00),
    ('Papa',            'g',      FALSE,   0.77),
    ('Zanahoria',       'g',      FALSE,   0.41),
    ('Cebolla',         'g',      FALSE,   0.40),
    ('Lentejas',        'g',      FALSE,   1.16),
    ('Avena',           'g',      FALSE,   3.89),
    ('Banana',          'unidad', FALSE, 105.00),
    ('Manzana',         'g',      FALSE,   0.52),
    ('Aceite de oliva', 'ml',     FALSE,   8.04),
    ('Harina',          'g',      FALSE,   3.64),
    ('Cacao',           'g',      FALSE,   2.28)
ON CONFLICT (nombre) DO NOTHING;

-- HU3–HU8 y HU11–HU12: 12 recetas, 78 favoritos y 33 comentarios.
DO $recetas$
DECLARE
    datos RECORD;
    id_autor INTEGER;
    id_receta INTEGER;
BEGIN
    FOR datos IN
        SELECT *
        FROM (VALUES
            (1, 'ana', 'Arroz con tomate', 2, 25, 'facil', DATE '2026-11-10',
             '{"Arroz":200,"Tomate":200}'::jsonb,
             ARRAY[
                 'Hervir el arroz hasta que esté tierno.',
                 'Cocinar el tomate picado hasta que se ablande y mezclarlo con el arroz.'
             ]),
            (2, 'ana', 'Arroz con pollo', 2, 40, 'media', DATE '2026-11-09',
             '{"Arroz":200,"Pollo":300,"Tomate":100}'::jsonb,
             ARRAY[
                 'Hervir el arroz hasta que esté tierno.',
                 'Cocinar el pollo en cubos hasta que esté completamente cocido.',
                 'Agregar el tomate picado al pollo, cocinar unos minutos y mezclar con el arroz.'
             ]),
            (3, 'bruno', 'Ensalada de tomate', 2, 10, 'facil', DATE '2026-11-12',
             '{"Tomate":300}'::jsonb,
             ARRAY[
                 'Lavar los tomates y cortarlos en rodajas.',
                 'Disponer las rodajas en un plato y servir.'
             ]),
            (4, 'bruno', 'Tortilla de papa', 3, 35, 'media', DATE '2026-11-13',
             '{"Papa":500,"Huevo":3}'::jsonb,
             ARRAY[
                 'Pelar las papas, cortarlas en láminas y cocinarlas hasta que estén tiernas.',
                 'Batir los huevos y mezclarlos con las papas.',
                 'Cocinar la mezcla en una sartén por ambos lados hasta que cuaje.'
             ]),
            (5, 'ana', 'Pollo al horno con papas', 4, 60, 'dificil', DATE '2026-11-14',
             '{"Pollo":600,"Papa":600}'::jsonb,
             ARRAY[
                 'Precalentar el horno a 200 °C y cortar las papas en gajos.',
                 'Hornear el pollo y las papas hasta que el pollo esté completamente cocido y las papas estén tiernas.'
             ]),
            (6, 'bruno', 'Avena con banana y leche', 1, 12, 'facil', DATE '2026-11-08',
             '{"Avena":40,"Banana":1,"Leche":200}'::jsonb,
             ARRAY[
                 'Calentar la leche con la avena y revolver hasta espesar.',
                 'Cortar la banana en rodajas y agregarla al servir.'
             ]),
            (7, 'ana', 'Sopa de lentejas y zanahoria', 2, 35, 'media', DATE '2026-11-07',
             '{"Lentejas":120,"Zanahoria":100,"Cebolla":60}'::jsonb,
             ARRAY[
                 'Picar la cebolla y la zanahoria.',
                 'Cocinar los vegetales con las lentejas en agua hasta que estén tiernos.'
             ]),
            (8, 'bruno', 'Panqueques de manzana', 4, 30, 'media', DATE '2026-11-11',
             '{"Harina":120,"Leche":250,"Huevo":2,"Manzana":160}'::jsonb,
             ARRAY[
                 'Batir la harina con la leche y los huevos.',
                 'Rallar la manzana e incorporarla a la mezcla.',
                 'Cocinar porciones finas de masa en una sartén antiadherente.'
             ]),
            (9, 'clara', 'Crema de banana y cacao', 2, 8, 'facil', DATE '2026-11-15',
             '{"Banana":2,"Cacao":12,"Leche":80}'::jsonb,
             ARRAY[
                 'Pelar y cortar las bananas.',
                 'Procesarlas con el cacao y la leche hasta obtener una crema.'
             ]),
            (10, 'clara', 'Zanahorias asadas con cebolla', 2, 30, 'facil', DATE '2026-11-06',
             '{"Zanahoria":300,"Cebolla":80,"Aceite de oliva":15}'::jsonb,
             ARRAY[
                 'Cortar las zanahorias y la cebolla.',
                 'Mezclar con el aceite y asar hasta que las verduras estén tiernas.'
             ]),
            (11, 'clara', 'Arroz con lentejas y zanahoria', 3, 45, 'media', DATE '2026-11-05',
             '{"Arroz":180,"Lentejas":150,"Zanahoria":120}'::jsonb,
             ARRAY[
                 'Cocinar las lentejas y el arroz en ollas separadas.',
                 'Hervir la zanahoria en cubos y mezclarla con el arroz y las lentejas.'
             ]),
            (12, 'bruno', 'Papas doradas con cebolla', 2, 32, 'facil', DATE '2026-11-16',
             '{"Papa":360,"Cebolla":70,"Aceite de oliva":20}'::jsonb,
             ARRAY[
                 'Cortar las papas en cubos y la cebolla en tiras.',
                 'Mezclar con el aceite y hornear hasta dorar.'
             ])
        ) AS fixtures(numero, autor, titulo, porciones, tiempo_min, dificultad,
                      dia_publicacion, ingredientes, pasos)
        ORDER BY numero
    LOOP
        SELECT id INTO STRICT id_autor
        FROM usuario
        WHERE email = 'cookpad.demo.' || datos.autor || '@example.com';

        INSERT INTO receta
            (autor_id, titulo, porciones, tiempo_min, dificultad, fecha_publicacion)
        VALUES
            (id_autor, '[Demo] ' || datos.titulo, datos.porciones,
             datos.tiempo_min, datos.dificultad, datos.dia_publicacion + TIME '12:00')
        ON CONFLICT (autor_id, titulo) DO NOTHING;

        SELECT r.id INTO STRICT id_receta
        FROM receta AS r
        WHERE r.autor_id = id_autor
          AND r.titulo = '[Demo] ' || datos.titulo;

        INSERT INTO receta_ingredientes (receta_id, ingrediente_id, cantidad)
        SELECT id_receta, i.id, item.cantidad::numeric
        FROM jsonb_each_text(datos.ingredientes) AS item(nombre, cantidad)
        JOIN ingrediente AS i ON i.nombre = item.nombre
        ON CONFLICT (receta_id, ingrediente_id) DO NOTHING;

        INSERT INTO paso (receta_id, orden, descripcion)
        SELECT id_receta, p.orden::integer, p.descripcion
        FROM unnest(datos.pasos) WITH ORDINALITY AS p(descripcion, orden)
        ON CONFLICT (receta_id, orden) DO NOTHING;

        INSERT INTO recetas_guardadas (usuario_id, receta_id, fecha)
        SELECT u.id, id_receta,
               TIMESTAMP '2026-11-17 09:00:00' + datos.numero * INTERVAL '1 hour'
        FROM generate_series(1, 13 - datos.numero) AS lector(n)
        JOIN usuario AS u
            ON u.email = 'cookpad.demo.lector' || LPAD(lector.n::text, 2, '0')
                         || '@example.com'
        ON CONFLICT (usuario_id, receta_id) DO NOTHING;

        IF datos.numero <= 11 THEN
            INSERT INTO comentario
                (usuario_id, receta_id, texto, puntaje, fecha, fecha_edicion)
            SELECT u.id, id_receta,
                   CASE lector.n
                       WHEN 1 THEN 'Preparé la receta con las porciones indicadas.'
                       WHEN 2 THEN 'La volví a preparar para comparar el resultado.'
                       ELSE 'Probé la receta y dejé mi puntaje.'
                   END,
                   5 - ((datos.numero - 1) / 3)
                     - CASE WHEN datos.numero % 2 = 0 AND lector.n = 3 THEN 1 ELSE 0 END,
                   TIMESTAMP '2026-11-18 09:00:00' + lector.n * INTERVAL '1 hour',
                   CASE WHEN datos.numero = 2 AND lector.n = 2
                        THEN TIMESTAMP '2026-11-19 10:00:00' END
            FROM generate_series(1, 3) AS lector(n)
            JOIN usuario AS u
                ON u.email = 'cookpad.demo.lector' || LPAD(lector.n::text, 2, '0')
                             || '@example.com'
            WHERE u.id <> id_autor
            ON CONFLICT (usuario_id, receta_id) DO NOTHING;
        END IF;
    END LOOP;
END;
$recetas$;

-- HU9–HU10: dos planes con cuatro comidas cada uno.
INSERT INTO plan_semanal (usuario_id, fecha_inicio)
SELECT u.id, DATE '2026-11-16'
FROM usuario AS u
WHERE u.email IN ('cookpad.demo.ana@example.com', 'cookpad.demo.bruno@example.com')
ON CONFLICT (usuario_id, fecha_inicio) DO NOTHING;

INSERT INTO plan_recetas (plan_id, receta_id, dia_semana, comida, porciones)
SELECT p.id, r.id, d.dia, d.comida, d.porciones
FROM (VALUES
    ('ana',   'ana',   'Arroz con pollo',             1, 'almuerzo', 4),
    ('ana',   'ana',   'Arroz con tomate',            1, 'cena',     1),
    ('ana',   'bruno', 'Ensalada de tomate',          3, 'almuerzo', 2),
    ('ana',   'bruno', 'Tortilla de papa',            7, 'cena',     1),
    ('bruno', 'bruno', 'Avena con banana y leche',    1, 'desayuno', 1),
    ('bruno', 'ana',   'Sopa de lentejas y zanahoria', 1, 'cena',     3),
    ('bruno', 'bruno', 'Panqueques de manzana',       3, 'merienda', 2),
    ('bruno', 'ana',   'Arroz con tomate',            7, 'almuerzo', 3)
) AS d(titular, autor, titulo, dia, comida, porciones)
JOIN usuario AS titular
    ON titular.email = 'cookpad.demo.' || d.titular || '@example.com'
JOIN usuario AS autor
    ON autor.email = 'cookpad.demo.' || d.autor || '@example.com'
JOIN receta AS r
    ON r.autor_id = autor.id AND r.titulo = '[Demo] ' || d.titulo
JOIN plan_semanal AS p
    ON p.usuario_id = titular.id AND p.fecha_inicio = DATE '2026-11-16'
ON CONFLICT (plan_id, dia_semana, comida) DO NOTHING;

-- Mi Heladera: Lector01 recibe dos compras. Lector12 queda sin compras demo.
-- Las tablas permiten tickets repetidos, así que se bloquean durante
-- la carga y se comprueba si cada compra o producto demo ya existe.
-- Los vencimientos relativos se fijan en la primera inserción.
LOCK TABLE compra, heladera_producto IN SHARE ROW EXCLUSIVE MODE;

WITH compras_demo(comercio, fecha_compra) AS (
    VALUES
        ('[Demo Cookpad] Almacén', DATE '2026-11-16'),
        ('[Demo Cookpad] Almacén', DATE '2026-11-17')
)
INSERT INTO compra (usuario_id, comercio, fecha_compra)
SELECT u.id, d.comercio, d.fecha_compra
FROM compras_demo AS d
JOIN usuario AS u ON u.email = 'cookpad.demo.lector01@example.com'
WHERE NOT EXISTS (
    SELECT 1
    FROM compra AS c
    WHERE c.usuario_id = u.id
      AND c.comercio = d.comercio
      AND c.fecha_compra = d.fecha_compra
);

WITH productos_demo(fecha_compra, ingrediente, producto, categoria,
                    cantidad, precio_total, vencimiento) AS (
    VALUES
        (DATE '2026-11-16', 'Arroz', '[Demo] Arroz lote 1', 'almacen',
         100.00, 1000.00, NULL::date),
        (DATE '2026-11-16', 'Tomate', '[Demo] Tomate fresco', 'verduras',
         350.00, 750.00, CURRENT_DATE + 3),
        (DATE '2026-11-16', 'Pollo', '[Demo] Pollo vencido', 'carnes_aves',
         300.00, 2100.00, CURRENT_DATE - 1),
        (DATE '2026-11-17', 'Arroz', '[Demo] Arroz lote 2', 'almacen',
         50.00, 500.00, NULL::date)
)
INSERT INTO heladera_producto
    (compra_id, ingrediente_id, nombre_producto, categoria,
     cantidad, precio_total, fecha_vencimiento)
SELECT c.id, i.id, d.producto, d.categoria, d.cantidad, d.precio_total, d.vencimiento
FROM productos_demo AS d
JOIN usuario AS u ON u.email = 'cookpad.demo.lector01@example.com'
JOIN ingrediente AS i ON i.nombre = d.ingrediente
JOIN LATERAL (
    SELECT compra_existente.id
    FROM compra AS compra_existente
    WHERE compra_existente.usuario_id = u.id
      AND compra_existente.comercio = '[Demo Cookpad] Almacén'
      AND compra_existente.fecha_compra = d.fecha_compra
    ORDER BY compra_existente.id
    LIMIT 1
) AS c ON TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM heladera_producto AS h
    WHERE h.compra_id = c.id
      AND h.nombre_producto = d.producto
);

-- Video opcional: clip MP4 de MDN para probar el reproductor.
-- Arroz con tomate recibe el clip. Ensalada de tomate queda sin video demo.
INSERT INTO tutorial (titulo, descripcion, video_url, categoria, receta_id, orden)
SELECT '[Demo] Prueba del reproductor MP4',
       'Clip de muestra de MDN para comprobar el reproductor de la receta.',
       'https://developer.mozilla.org/shared-assets/videos/flower.mp4',
       'recetas',
       r.id,
       0
FROM receta AS r
JOIN usuario AS u ON u.id = r.autor_id
WHERE u.email = 'cookpad.demo.ana@example.com'
  AND r.titulo = '[Demo] Arroz con tomate'
ON CONFLICT (video_url) DO NOTHING;

COMMIT;

-- Comprobaciones de solo lectura.

-- IDs de los planes demo para probar sus comidas y listas de compras.
SELECT p.id AS plan_id, u.email, p.fecha_inicio
FROM public.plan_semanal AS p
JOIN public.usuario AS u ON u.id = p.usuario_id
WHERE p.fecha_inicio = DATE '2026-11-16'
  AND u.email IN ('cookpad.demo.ana@example.com', 'cookpad.demo.bruno@example.com')
ORDER BY u.email;

-- IDs de Arroz y Tomate para probar HU11 con ingredientes_ids.
SELECT id AS ingrediente_id, nombre
FROM public.ingrediente
WHERE nombre IN ('Arroz', 'Tomate')
ORDER BY nombre;

-- Receta con video y receta sin video.
SELECT r.id AS receta_id, r.titulo, COUNT(t.id) AS cantidad_videos
FROM public.receta AS r
JOIN public.usuario AS u ON u.id = r.autor_id
LEFT JOIN public.tutorial AS t ON t.receta_id = r.id
WHERE (u.email = 'cookpad.demo.ana@example.com'
       AND r.titulo = '[Demo] Arroz con tomate')
   OR (u.email = 'cookpad.demo.bruno@example.com'
       AND r.titulo = '[Demo] Ensalada de tomate')
GROUP BY r.id, r.titulo
ORDER BY r.titulo;

-- Heladeras demo. Sin otras compras, se espera:
-- Lector01: 2 compras, 4 productos, 4350.00.
-- Lector12: 0 compras, 0 productos, 0.00.
SELECT u.email,
       COUNT(DISTINCT c.id) AS cantidad_compras,
       COUNT(h.id) AS cantidad_productos,
       COALESCE(SUM(h.precio_total), 0.00) AS total_gastado
FROM public.usuario AS u
LEFT JOIN public.compra AS c ON c.usuario_id = u.id
LEFT JOIN public.heladera_producto AS h ON h.compra_id = c.id
WHERE u.email IN ('cookpad.demo.lector01@example.com', 'cookpad.demo.lector12@example.com')
GROUP BY u.email
ORDER BY u.email;

-- IDs vigentes de la heladera de Lector01 para probar HU11.
SELECT DISTINCT i.id AS ingrediente_id, i.nombre
FROM public.usuario AS u
JOIN public.compra AS c ON c.usuario_id = u.id
JOIN public.heladera_producto AS h ON h.compra_id = c.id
JOIN public.ingrediente AS i ON i.id = h.ingrediente_id
WHERE u.email = 'cookpad.demo.lector01@example.com'
  AND (h.fecha_vencimiento IS NULL OR h.fecha_vencimiento >= CURRENT_DATE)
ORDER BY i.nombre, i.id;

-- Referencia para GET /api/recetas/top-guardadas.
SELECT r.id AS receta_id, r.titulo, COUNT(*) AS cantidad_guardados
FROM public.recetas_guardadas AS g
JOIN public.receta AS r ON r.id = g.receta_id
GROUP BY r.id, r.titulo
ORDER BY cantidad_guardados DESC, r.id
LIMIT 10;

-- Referencia para GET /api/ingredientes/mas-usados.
SELECT i.id AS ingrediente_id, i.nombre, COUNT(*) AS cantidad_recetas
FROM public.receta_ingredientes AS ri
JOIN public.ingrediente AS i ON i.id = ri.ingrediente_id
GROUP BY i.id, i.nombre
ORDER BY cantidad_recetas DESC, i.nombre, i.id
LIMIT 10;

-- Referencia del top 10 por promedio de puntaje.
SELECT r.id AS receta_id, r.titulo, COUNT(*) AS cantidad_puntajes,
       ROUND(AVG(c.puntaje), 2) AS puntaje_promedio
FROM public.comentario AS c
JOIN public.receta AS r ON r.id = c.receta_id
GROUP BY r.id, r.titulo, r.fecha_publicacion
ORDER BY AVG(c.puntaje) DESC, r.fecha_publicacion DESC, r.id DESC
LIMIT 10;

-- Referencia para GET /api/planes/{plan_id}/calorias.
-- Ana, lunes/miércoles/domingo: 1694.00 / 54.00 / 200.34 kcal.
-- Bruno, lunes/miércoles/domingo: 688.90 / 408.25 / 444.00 kcal.
WITH planes_demo AS (
    SELECT p.id, u.email, p.fecha_inicio
    FROM public.plan_semanal AS p
    JOIN public.usuario AS u ON u.id = p.usuario_id
    WHERE p.fecha_inicio = DATE '2026-11-16'
      AND u.email IN ('cookpad.demo.ana@example.com', 'cookpad.demo.bruno@example.com')
),
calorias_por_comida AS (
    SELECT pr.plan_id, pr.dia_semana, pr.id,
           ROUND(SUM(
               ROUND(ri.cantidad * pr.porciones / r.porciones, 2)
               * i.calorias_por_unidad
           ), 2) AS calorias
    FROM planes_demo AS p
    JOIN public.plan_recetas AS pr ON pr.plan_id = p.id
    JOIN public.receta AS r ON r.id = pr.receta_id
    JOIN public.receta_ingredientes AS ri ON ri.receta_id = r.id
    JOIN public.ingrediente AS i ON i.id = ri.ingrediente_id
    GROUP BY pr.plan_id, pr.dia_semana, pr.id
)
SELECT p.id AS plan_id, p.email, d.dia_semana,
       p.fecha_inicio + (d.dia_semana - 1) AS fecha,
       COALESCE(SUM(c.calorias), 0.00) AS calorias
FROM planes_demo AS p
CROSS JOIN generate_series(1, 7) AS d(dia_semana)
LEFT JOIN calorias_por_comida AS c
    ON c.plan_id = p.id AND c.dia_semana = d.dia_semana
GROUP BY p.id, p.email, p.fecha_inicio, d.dia_semana
ORDER BY p.email, d.dia_semana;