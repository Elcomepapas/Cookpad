INSERT INTO ingrediente
(nombre, unidad_base, origen_animal, calorias_por_unidad)
VALUES
('Arroz', 'g', FALSE, 1.30),
('Pollo', 'g', TRUE, 1.65),
('Tomate', 'g', FALSE, 0.18),
('Leche', 'ml', TRUE, 0.61),
('Huevo', 'unidad', TRUE, 72),
('Papa', 'g', FALSE, 0.77);




BEGIN;

-- Crear recetas iniciales
INSERT INTO receta
    (autor_id, titulo, porciones, tiempo_min, dificultad)
SELECT u.id, datos.titulo, datos.porciones, datos.tiempo, datos.dificultad
FROM usuario u
CROSS JOIN (
    VALUES
    ('Arroz con pollo', 2, 40, 'media'),
    ('Ensalada de tomate', 2, 10, 'facil'),
    ('Tortilla de papa', 3, 35, 'media'),
    ('Arroz con tomate', 2, 25, 'facil'),
    ('Pollo al horno con papas', 4, 60, 'media')
) AS datos(titulo, porciones, tiempo, dificultad)
WHERE u.email = 'pruebacookpad2026@gmail.com'
AND NOT EXISTS (
    SELECT 1 FROM receta r
    WHERE r.autor_id = u.id
      AND r.titulo = datos.titulo
);

-- Relacionar recetas con ingredientes
WITH ingredientes_recetas(titulo, ingrediente, cantidad) AS (
    VALUES
    ('Arroz con pollo', 'Arroz', 200),
    ('Arroz con pollo', 'Pollo', 300),
    ('Arroz con pollo', 'Tomate', 100),
    ('Ensalada de tomate', 'Tomate', 300),
    ('Tortilla de papa', 'Papa', 500),
    ('Tortilla de papa', 'Huevo', 3),
    ('Arroz con tomate', 'Arroz', 200),
    ('Arroz con tomate', 'Tomate', 200),
    ('Pollo al horno con papas', 'Pollo', 600),
    ('Pollo al horno con papas', 'Papa', 600)
)
INSERT INTO receta_ingredientes (receta_id, ingrediente_id, cantidad)
SELECT r.id, i.id, ir.cantidad
FROM ingredientes_recetas ir
JOIN receta r ON r.titulo = ir.titulo
JOIN usuario u ON u.id = r.autor_id
JOIN ingrediente i ON i.nombre = ir.ingrediente
WHERE u.email = 'pruebacookpad2026@gmail.com'
ON CONFLICT (receta_id, ingrediente_id) DO NOTHING;

-- Crear pasos de preparación
WITH pasos_recetas(titulo, orden, descripcion) AS (
    VALUES
    ('Arroz con pollo', 1, 'Cortar el pollo y el tomate.'),
    ('Arroz con pollo', 2, 'Cocinar el pollo hasta que esté bien hecho.'),
    ('Arroz con pollo', 3, 'Hervir el arroz y mezclar con el pollo y el tomate.'),

    ('Ensalada de tomate', 1, 'Lavar los tomates.'),
    ('Ensalada de tomate', 2, 'Cortar los tomates y servir.'),

    ('Tortilla de papa', 1, 'Pelar y cortar las papas.'),
    ('Tortilla de papa', 2, 'Cocinar las papas hasta que estén tiernas.'),
    ('Tortilla de papa', 3, 'Batir los huevos y mezclarlos con las papas.'),
    ('Tortilla de papa', 4, 'Cocinar la tortilla de ambos lados.'),

    ('Arroz con tomate', 1, 'Hervir el arroz.'),
    ('Arroz con tomate', 2, 'Cortar y cocinar el tomate.'),
    ('Arroz con tomate', 3, 'Mezclar el arroz con el tomate.'),

    ('Pollo al horno con papas', 1, 'Precalentar el horno a 200 grados.'),
    ('Pollo al horno con papas', 2, 'Cortar las papas y colocarlas con el pollo en una fuente.'),
    ('Pollo al horno con papas', 3, 'Hornear hasta que el pollo esté completamente cocido y las papas tiernas.')
)
INSERT INTO paso (receta_id, orden, descripcion)
SELECT r.id, pr.orden, pr.descripcion
FROM pasos_recetas pr
JOIN receta r ON r.titulo = pr.titulo
JOIN usuario u ON u.id = r.autor_id
WHERE u.email = 'pruebacookpad2026@gmail.com'
AND NOT EXISTS (
    SELECT 1 FROM paso p
    WHERE p.receta_id = r.id AND p.orden = pr.orden
);

COMMIT;
