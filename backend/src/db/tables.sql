-- =====================================================================
-- Cookpad - Esquema de base de datos (PostgreSQL)
-- =====================================================================
-- Convenciones (para que todo el equipo agregue features igual):
--   * Tablas y columnas en snake_case, singular para entidades.
--   * PK "id" con GENERATED ALWAYS AS IDENTITY.
--   * FKs con nombre <tabla>_id y ON DELETE CASCADE salvo que se aclare.
--   * Restricciones con nombre explícito (ck_, uq_, fk_) para poder
--     modificarlas fácil con ALTER TABLE ... DROP CONSTRAINT <nombre>.
--   * Valores tipo "enum" con TEXT + CHECK (más fácil de ampliar que ENUM).
--   * Campos calculados (es_vegana, calorías, puntaje promedio) NO se
--     guardan: se calculan en consultas.
-- =====================================================================

-- Borrado en orden inverso a las dependencias (para re-ejecutar en desarrollo)
DROP TABLE IF EXISTS plan_recetas       CASCADE;
DROP TABLE IF EXISTS recetas_guardadas  CASCADE;
DROP TABLE IF EXISTS receta_ingredientes CASCADE;
DROP TABLE IF EXISTS comentario         CASCADE;
DROP TABLE IF EXISTS plan_semanal       CASCADE;
DROP TABLE IF EXISTS paso               CASCADE;
DROP TABLE IF EXISTS receta             CASCADE;
DROP TABLE IF EXISTS ingrediente        CASCADE;
DROP TABLE IF EXISTS usuario            CASCADE;


-- ---------------------------------------------------------------------
-- HU1 - Usuario
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email           VARCHAR(255) NOT NULL,
    nombre          VARCHAR(100) NOT NULL,
    fecha_registro  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_usuario_email UNIQUE (email)
);


-- ---------------------------------------------------------------------
-- HU2 - Ingrediente (catálogo administrado)
-- ---------------------------------------------------------------------
CREATE TABLE ingrediente (
    id                   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre               VARCHAR(100)  NOT NULL,
    unidad_base          VARCHAR(10)   NOT NULL,
    origen_animal        BOOLEAN       NOT NULL DEFAULT FALSE,
    calorias_por_unidad  NUMERIC(10,2) NOT NULL DEFAULT 0,

    CONSTRAINT uq_ingrediente_nombre      UNIQUE (nombre),
    CONSTRAINT ck_ingrediente_unidad_base CHECK (unidad_base IN ('g', 'ml', 'unidad')),
    CONSTRAINT ck_ingrediente_calorias    CHECK (calorias_por_unidad >= 0)
);


-- ---------------------------------------------------------------------
-- HU3 - Receta
-- ---------------------------------------------------------------------
CREATE TABLE receta (
    id                 INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    autor_id           INTEGER      NOT NULL,
    titulo             VARCHAR(200) NOT NULL,
    porciones          INTEGER      NOT NULL,
    tiempo_min         INTEGER      NOT NULL,
    dificultad         VARCHAR(10)  NOT NULL,
    fecha_publicacion  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_receta_autor       FOREIGN KEY (autor_id) REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT uq_receta_autor_titulo UNIQUE (autor_id, titulo),
    CONSTRAINT ck_receta_porciones   CHECK (porciones > 0),
    CONSTRAINT ck_receta_tiempo      CHECK (tiempo_min > 0),
    CONSTRAINT ck_receta_dificultad  CHECK (dificultad IN ('facil', 'media', 'dificil'))
);


-- ---------------------------------------------------------------------
-- HU3 - Paso de una receta
-- ---------------------------------------------------------------------
CREATE TABLE paso (
    id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    receta_id    INTEGER NOT NULL,
    orden        INTEGER NOT NULL,
    descripcion  TEXT    NOT NULL,

    CONSTRAINT fk_paso_receta       FOREIGN KEY (receta_id) REFERENCES receta(id) ON DELETE CASCADE,
    CONSTRAINT uq_paso_receta_orden UNIQUE (receta_id, orden),   -- sin repetidos
    CONSTRAINT ck_paso_orden        CHECK (orden >= 1)           -- empieza en 1
    -- "Consecutivo" (1,2,3 sin huecos) se valida en el back end.
);


-- ---------------------------------------------------------------------
-- HU3 - N a M receta <-> ingrediente
-- ---------------------------------------------------------------------
CREATE TABLE receta_ingredientes (
    receta_id       INTEGER       NOT NULL,
    ingrediente_id  INTEGER       NOT NULL,
    cantidad        NUMERIC(10,2) NOT NULL,

    CONSTRAINT pk_receta_ingredientes PRIMARY KEY (receta_id, ingrediente_id),
    CONSTRAINT fk_ri_receta      FOREIGN KEY (receta_id)      REFERENCES receta(id)      ON DELETE CASCADE,
    CONSTRAINT fk_ri_ingrediente FOREIGN KEY (ingrediente_id) REFERENCES ingrediente(id) ON DELETE RESTRICT,
    CONSTRAINT ck_ri_cantidad    CHECK (cantidad > 0)
);


-- ---------------------------------------------------------------------
-- HU7 - N a M recetas guardadas (favoritas)
-- ---------------------------------------------------------------------
CREATE TABLE recetas_guardadas (
    usuario_id  INTEGER   NOT NULL,
    receta_id   INTEGER   NOT NULL,
    fecha       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_recetas_guardadas PRIMARY KEY (usuario_id, receta_id),  -- no se guarda dos veces
    CONSTRAINT fk_rg_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT fk_rg_receta  FOREIGN KEY (receta_id)  REFERENCES receta(id)  ON DELETE CASCADE
);


-- ---------------------------------------------------------------------
-- HU8 - Comentario y puntaje
-- ---------------------------------------------------------------------
CREATE TABLE comentario (
    id                 INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id         INTEGER   NOT NULL,
    receta_id          INTEGER   NOT NULL,
    texto              TEXT      NOT NULL,
    puntaje            INTEGER   NOT NULL,
    fecha              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_edicion      TIMESTAMP NULL,   -- se completa cuando el usuario lo edita

    CONSTRAINT fk_comentario_usuario  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT fk_comentario_receta   FOREIGN KEY (receta_id)  REFERENCES receta(id)  ON DELETE CASCADE,
    CONSTRAINT uq_comentario_usuario_receta UNIQUE (usuario_id, receta_id),  -- máx. uno por usuario y receta
    CONSTRAINT ck_comentario_puntaje  CHECK (puntaje BETWEEN 1 AND 5)
    -- "No puntuar la propia receta" se valida en el back end.
);


-- ---------------------------------------------------------------------
-- HU9 - Plan semanal
-- ---------------------------------------------------------------------
CREATE TABLE plan_semanal (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id    INTEGER NOT NULL,
    fecha_inicio  DATE    NOT NULL,

    CONSTRAINT fk_plan_usuario       FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    CONSTRAINT uq_plan_usuario_semana UNIQUE (usuario_id, fecha_inicio),     -- un plan por semana
    CONSTRAINT ck_plan_inicio_lunes  CHECK (EXTRACT(ISODOW FROM fecha_inicio) = 1)  -- 1 = lunes
);


-- ---------------------------------------------------------------------
-- HU9 - N a M plan <-> receta
-- ---------------------------------------------------------------------
CREATE TABLE plan_recetas (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plan_id     INTEGER     NOT NULL,
    receta_id   INTEGER     NOT NULL,
    dia_semana  INTEGER     NOT NULL,
    comida      VARCHAR(10) NOT NULL,
    porciones   INTEGER     NOT NULL,

    CONSTRAINT fk_pr_plan       FOREIGN KEY (plan_id)   REFERENCES plan_semanal(id) ON DELETE CASCADE,
    CONSTRAINT fk_pr_receta     FOREIGN KEY (receta_id) REFERENCES receta(id)       ON DELETE CASCADE,
    CONSTRAINT uq_pr_dia_comida UNIQUE (plan_id, dia_semana, comida),   -- una receta por día y comida
    CONSTRAINT ck_pr_dia        CHECK (dia_semana BETWEEN 1 AND 7),
    CONSTRAINT ck_pr_comida     CHECK (comida IN ('desayuno', 'almuerzo', 'merienda', 'cena')),
    CONSTRAINT ck_pr_porciones  CHECK (porciones > 0)
);


-- ---------------------------------------------------------------------
-- Índices para búsquedas y estadísticas (HU6, HU7, HU11, HU12)
-- ---------------------------------------------------------------------
CREATE INDEX ix_receta_autor            ON receta (autor_id);
CREATE INDEX ix_receta_fecha            ON receta (fecha_publicacion);
CREATE INDEX ix_ri_ingrediente          ON receta_ingredientes (ingrediente_id);
CREATE INDEX ix_rg_receta               ON recetas_guardadas (receta_id);
CREATE INDEX ix_rg_usuario_fecha        ON recetas_guardadas (usuario_id, fecha);
CREATE INDEX ix_comentario_receta       ON comentario (receta_id);
CREATE INDEX ix_pr_receta               ON plan_recetas (receta_id);