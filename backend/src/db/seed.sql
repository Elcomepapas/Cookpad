-- Cookpad 2.0 | seed.sql para HU1–HU12
-- Requiere el esquema PostgreSQL de backend/src/db/tables.sql ya aplicado.
-- Carga 12 recetas, 15 ingredientes, 16 cuentas, 78 favoritos de lectores,
-- 33 comentarios y dos planes semanales con cuatro comidas cada uno.
--
-- Revisado contra el DDL, los modelos, los esquemas de entrada, los routers
-- y la lógica del backend local. No se ejecutó SQL ni se inspeccionó una base
-- en ejecución. No encontré migraciones Alembic en el backend revisado.
--
-- Todas las escrituras son INSERT ... ON CONFLICT DO NOTHING. Las claves
-- naturales identifican los datos demo y PostgreSQL asigna los IDs. Si ya
-- cargaste el seed anterior, se reutilizan sus cuentas, recetas y planes.
-- Sus favoritos, comentarios, contraseñas y demás valores se conservan.
-- Los resultados numéricos indicados corresponden a una carga inicial con
-- los valores de este script. Las filas previas pueden afectar los resultados.
--
-- Cuentas nuevas de prueba: cookpad.demo.admin@example.com,
-- cookpad.demo.ana@example.com, cookpad.demo.bruno@example.com,
-- cookpad.demo.clara@example.com y cookpad.demo.lector01@example.com
-- hasta cookpad.demo.lector12@example.com. Clave: CookpadDemo2026!
-- Si las cuatro primeras cuentas vienen del seed anterior, conservan su clave
-- original. Usar estas cuentas y credenciales en desarrollo o pruebas.
--
-- FUNCIONALIDADES DISPONIBLES EN LA API REVISADA
-- HU1: registro, login y acceso a la cuenta propia.
-- HU2: catálogo, alta de ingredientes y permisos de administrador.
-- HU3: alta y detalle de recetas con ingredientes y pasos consecutivos.
-- HU4: escalado de cantidades y calorías en el detalle de una receta.
-- HU5: etiqueta vegana calculada y filtro vegano.
-- HU6 y HU12: filtros combinados y orden por fecha o puntaje promedio.
-- HU7: guardar recetas y listar favoritos por usuario.
-- HU8: comentar, puntuar y editar un comentario propio.
-- HU9: crear/consultar planes por ID y agregar/quitar comidas.
-- HU10: calcular la lista de compras con cantidades escaladas y agrupadas.
-- HU11: buscar recetas que se puedan hacer solo con los ingredientes enviados.
-- Las operaciones de alta y los casos de rechazo se prueban mediante la API.
--
-- FUNCIONALIDADES PENDIENTES EN EL BACKEND
-- El frontend pide /api/recetas/top-guardadas, /api/ingredientes/mas-usados,
-- /api/planes/{plan_id}/calorias y /api/usuarios/{uid}/planes. Esas rutas
-- no están implementadas en el backend revisado. Los SELECT del final
-- permiten comprobar rankings, calorías diarias e IDs de planes por SQL.
-- El orden por promedio de puntaje sí existe en GET /api/recetas.

BEGIN;

-- HU1–HU2: cuentas de prueba y catálogo.
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

-- HU3–HU8 y HU11–HU12: recetas, pasos, ingredientes, favoritos y puntajes.
-- El número de cada receta se usa para generar favoritos y puntajes.
-- Los gramos, mililitros y unidades corresponden a las porciones base.
DO $seed$
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
        WHERE r.autor_id = id_autor AND r.titulo = '[Demo] ' || datos.titulo;

        INSERT INTO receta_ingredientes (receta_id, ingrediente_id, cantidad)
        SELECT id_receta, i.id, item.cantidad::numeric
        FROM jsonb_each_text(datos.ingredientes) AS item(nombre, cantidad)
        JOIN ingrediente AS i ON i.nombre = item.nombre
        ON CONFLICT (receta_id, ingrediente_id) DO NOTHING;

        INSERT INTO paso (receta_id, orden, descripcion)
        SELECT id_receta, p.orden::integer, p.descripcion
        FROM unnest(datos.pasos) WITH ORDINALITY AS p(descripcion, orden)
        ON CONFLICT (receta_id, orden) DO NOTHING;

        -- De 12 a 1 favoritos por receta. Lector01 tiene las 12 guardadas,
        -- con distintas fechas para comprobar el orden de su lista personal.
        INSERT INTO recetas_guardadas (usuario_id, receta_id, fecha)
        SELECT u.id, id_receta,
               TIMESTAMP '2026-11-17 09:00:00' + datos.numero * INTERVAL '1 hour'
        FROM generate_series(1, 13 - datos.numero) AS lector(n)
        JOIN usuario AS u
            ON u.email = 'cookpad.demo.lector' || LPAD(lector.n::text, 2, '0')
                         || '@example.com'
        ON CONFLICT (usuario_id, receta_id) DO NOTHING;

        -- Tres puntajes de terceros en cada una de las primeras 11 recetas.
        -- Hay promedios distintos, empates, una edición y una receta sin votos.
        IF datos.numero <= 11 THEN
            INSERT INTO comentario (usuario_id, receta_id, texto, puntaje, fecha, fecha_edicion)
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
$seed$;

-- HU9–HU10: dos titulares, el mismo lunes fijo y cuatro comidas por plan.
-- Hay días con dos comidas, días vacíos y escalado entero y fraccionario.
INSERT INTO plan_semanal (usuario_id, fecha_inicio)
SELECT u.id, DATE '2026-11-16'
FROM usuario AS u
WHERE u.email IN ('cookpad.demo.ana@example.com', 'cookpad.demo.bruno@example.com')
ON CONFLICT (usuario_id, fecha_inicio) DO NOTHING;

INSERT INTO plan_recetas (plan_id, receta_id, dia_semana, comida, porciones)
SELECT p.id, r.id, d.dia, d.comida, d.porciones
FROM (VALUES
    ('ana',   'ana',   'Arroz con pollo',            1, 'almuerzo', 4),
    ('ana',   'ana',   'Arroz con tomate',           1, 'cena',     1),
    ('ana',   'bruno', 'Ensalada de tomate',         3, 'almuerzo', 2),
    ('ana',   'bruno', 'Tortilla de papa',           7, 'cena',     1),
    ('bruno', 'bruno', 'Avena con banana y leche',   1, 'desayuno', 1),
    ('bruno', 'ana',   'Sopa de lentejas y zanahoria', 1, 'cena',   3),
    ('bruno', 'bruno', 'Panqueques de manzana',      3, 'merienda', 2),
    ('bruno', 'ana',   'Arroz con tomate',           7, 'almuerzo', 3)
) AS d(titular, autor, titulo, dia, comida, porciones)
JOIN usuario AS titular ON titular.email = 'cookpad.demo.' || d.titular || '@example.com'
JOIN usuario AS autor ON autor.email = 'cookpad.demo.' || d.autor || '@example.com'
JOIN receta AS r ON r.autor_id = autor.id AND r.titulo = '[Demo] ' || d.titulo
JOIN plan_semanal AS p
    ON p.usuario_id = titular.id AND p.fecha_inicio = DATE '2026-11-16'
ON CONFLICT (plan_id, dia_semana, comida) DO NOTHING;

COMMIT;

-- COMPROBACIONES DE SOLO LECTURA
--
-- HU9–HU10. Consultar GET /api/planes/{plan_id}/lista-compras con el token
-- del titular. Para Ana, la lista esperada es Arroz 500 g, Huevo 1 unidad,
-- Papa 166.67 g, Pollo 600 g y Tomate 600 g. Para Bruno contiene diez
-- ingredientes, entre ellos Arroz 300 g, Leche 325 ml y Lentejas 180 g.
-- Consultar el plan de otro titular debe devolver 403. Para probar una lista
-- vacía, crear mediante POST /api/planes un plan para otro lunes.
SELECT p.id AS plan_id, u.email, p.fecha_inicio
FROM plan_semanal AS p
JOIN usuario AS u ON u.id = p.usuario_id
WHERE p.fecha_inicio = DATE '2026-11-16'
  AND u.email IN ('cookpad.demo.ana@example.com', 'cookpad.demo.bruno@example.com')
ORDER BY u.email;

-- HU11. Enviar los IDs de Arroz y Tomate en ingredientes_ids de
-- POST /api/recetas/con-ingredientes. Entre las demo, devuelve Arroz con
-- tomate y Ensalada de tomate. Arroz con pollo requiere un ingrediente extra.
SELECT id AS ingrediente_id, nombre
FROM ingrediente
WHERE nombre IN ('Arroz', 'Tomate')
ORDER BY nombre;

-- HU4. En GET /api/recetas/{id}?porciones=1, la receta demo Arroz con tomate
-- da 100 g de arroz, 100 g de tomate y 148.00 kcal totales y por porción.
-- HU6/HU12. Con ingrediente=tom, vegana=true, dificultad=facil y
-- tiempo_max=25, aparecen las mismas dos recetas del caso HU11.
-- Entre estas dos, ordenar_por=fecha deja primero Ensalada de tomate.
SELECT r.id AS receta_id, r.titulo, u.email AS autor
FROM receta AS r
JOIN usuario AS u ON u.id = r.autor_id
WHERE r.titulo LIKE '[Demo] %'
  AND u.email IN (
      'cookpad.demo.ana@example.com',
      'cookpad.demo.bruno@example.com',
      'cookpad.demo.clara@example.com'
  )
ORDER BY r.titulo;

-- Referencia SQL para el top 10 de recetas guardadas.
-- Con una carga inicial, los conteos del top 10 van de 12 a 3.
SELECT r.id AS receta_id, r.titulo, COUNT(*) AS cantidad_guardados
FROM recetas_guardadas AS g
JOIN receta AS r ON r.id = g.receta_id
GROUP BY r.id, r.titulo
ORDER BY cantidad_guardados DESC, r.id
LIMIT 10;

-- Referencia SQL para el top 10 de ingredientes usados.
-- Cuenta recetas que usan cada ingrediente. El catálogo demo tiene 15 usados.
SELECT i.id AS ingrediente_id, i.nombre, COUNT(*) AS cantidad_recetas
FROM receta_ingredientes AS ri
JOIN ingrediente AS i ON i.id = ri.ingrediente_id
GROUP BY i.id, i.nombre
ORDER BY cantidad_recetas DESC, i.nombre, i.id
LIMIT 10;

-- HU8/HU12. Referencia del top 10 por promedio entre recetas con puntaje.
-- Comparar con GET /api/recetas?ordenar_por=puntaje. El orden usa el promedio
-- sin redondear y desempata por fecha de publicación e ID descendentes.
SELECT r.id AS receta_id, r.titulo, COUNT(*) AS cantidad_puntajes,
       ROUND(AVG(c.puntaje), 2) AS puntaje_promedio
FROM comentario AS c
JOIN receta AS r ON r.id = c.receta_id
GROUP BY r.id, r.titulo, r.fecha_publicacion
ORDER BY AVG(c.puntaje) DESC, r.fecha_publicacion DESC, r.id DESC
LIMIT 10;

-- Referencia SQL para calorías diarias. Replica el redondeo del detalle
-- de receta: cantidad escalada a dos decimales por ingrediente y luego
-- total a dos decimales por comida. Suma las comidas de cada día.
-- Ana, lunes/miércoles/domingo: 1694.00 / 54.00 / 200.34 kcal.
-- Bruno, lunes/miércoles/domingo: 688.90 / 408.25 / 444.00 kcal.
-- Los otros cuatro días de cada plan devuelven 0.00 kcal.
WITH planes_demo AS (
    SELECT p.id, u.email, p.fecha_inicio
    FROM plan_semanal AS p
    JOIN usuario AS u ON u.id = p.usuario_id
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
    JOIN plan_recetas AS pr ON pr.plan_id = p.id
    JOIN receta AS r ON r.id = pr.receta_id
    JOIN receta_ingredientes AS ri ON ri.receta_id = r.id
    JOIN ingrediente AS i ON i.id = ri.ingrediente_id
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