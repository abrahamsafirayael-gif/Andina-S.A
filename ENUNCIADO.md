# Distribuidora Andina S.A. --- Proyecto de limpieza y análisis de datos

## 1. Contexto

Distribuidora Andina S.A. es una mayorista de alimentos no perecederos y
bebidas que vende a almacenes y comercios de Argentina.

Cada vendedor carga las ventas manualmente en un Excel compartido. Al
cierre de octubre de 2026, la gerente comercial, Laura Méndez, recibe el
archivo `ventas_octubre.xlsx`, pero no puede utilizarlo para elaborar el
informe mensual porque los totales no coinciden y existen clientes
repetidos.

**Rol:** analista de datos.

**Objetivo:** entregar un conjunto de datos confiable, documentar los
registros que no pudieron recuperarse y construir una base de datos
consultable.

## 2. Datos de partida

-   **Archivo de origen:** `ventas_octubre.xlsx`
-   **Hoja:** `Ventas`
-   **Cantidad de filas:** 2.000

### Composición real de los datos

  -----------------------------------------------------------------------
  Tipo de registro                                               Cantidad
  ------------------------------ ----------------------------------------
  Ventas reales                                                     1.800

  Duplicados exactos                                                  100

  Filas vacías                                                         50

  Filas basura (encabezados                                            50
  repetidos, `TOTAL`, notas como 
  `revisar`)                     

  **Total**                                                     **2.000**
  -----------------------------------------------------------------------

### Columnas

  Columna             Descripción
  ------------------- -------------------------------------------------------
  `id_venta`          Identificador único de la venta (`V-0001` a `V-1800`)
  `fecha`             Día de la venta
  `cliente`           Nombre del comercio o persona
  `producto`          Nombre del producto
  `cantidad`          Unidades vendidas
  `precio_unitario`   Precio por unidad, en pesos argentinos
  `total`             Cantidad multiplicada por precio unitario
  `vendedor`          Persona que cargó la venta

## 3. Catálogos de referencia

Los catálogos deben generarse **antes de ensuciar los datos** y
utilizarse como referencia durante la limpieza.

-   **Clientes:** 80 clientes únicos. Incluir deliberadamente dos pares
    de nombres parecidos pero correspondientes a personas distintas (por
    ejemplo, `Juan Pérez` y `Juan Pereyra`) para comprobar que la
    normalización no los fusione.
-   **Productos:** 30 productos, cada uno con un precio de lista entre
    \$800 y \$15.000. Ejemplos: `Aceite 900ml`, `Yerba 1kg`,
    `Gaseosa 2.25L`.
-   **Vendedores:** 8 vendedores. Ejemplos: `Marcos Ruiz`, `Ana Torres`,
    etc.

## 4. Reglas de negocio

Estas reglas definen el resultado correcto de la limpieza.

  -----------------------------------------------------------------------------
  Código                              Regla
  ----------------------------------- -----------------------------------------
  **R1**                              La fecha debe estar entre el 01/10/2026 y
                                      el 31/10/2026, inclusive.

  **R2**                              Las fechas ambiguas se interpretan como
                                      día/mes/año, según la convención
                                      argentina.

  **R3**                              La cantidad debe ser un entero positivo
                                      entre 1 y 200, inclusive.

  **R4**                              El precio unitario debe ser un número
                                      positivo expresado en pesos.

  **R5**                              El total correcto es
                                      `round(cantidad × precio_unitario, 2)`.
                                      Si el total cargado no coincide,
                                      prevalece el cálculo.

  **R6**                              Cliente, producto y vendedor no pueden
                                      ser nulos.

  **R7**                              Los nombres de clientes se normalizan a
                                      Formato Título, sin espacios sobrantes,
                                      sin inconsistencias de tildes y con el
                                      orden `Nombre Apellido`.

  **R8**                              Los duplicados exactos se eliminan,
                                      conservando una sola fila.

  **R9**                              Nunca se inventa un dato. Si no puede
                                      recuperarse con certeza, la fila se envía
                                      a rechazados con su motivo.
  -----------------------------------------------------------------------------

## 5. Errores que deben inyectarse

Los errores se deben introducir sobre las 1.800 ventas reales. Una fila
puede contener más de un error.

### 5.1. Fechas

-   Distribución de formatos:
    -   40 %: `05/10/2026`
    -   30 %: `2026-10-05`
    -   20 %: `5 oct 26`
    -   10 %: `2026-10-05 14:30`
-   40 fechas vacías → rechazar con `FECHA_NULA`.
-   20 fechas fuera de octubre → rechazar con `FECHA_FUERA_RANGO`.
-   15 fechas imposibles (por ejemplo, `31/11/2026`) → rechazar con
    `FECHA_INVALIDA`.

### 5.2. Clientes

-   Aproximadamente 450 filas con variantes: minúsculas, MAYÚSCULAS,
    espacios al final, apellido y nombre invertidos (por ejemplo,
    `PEREZ JUAN`) o ausencia de tildes.
-   15 clientes nulos → rechazar con `CLIENTE_NULO`.

### 5.3. Productos

-   Aproximadamente 90 filas con errores de tipeo o mayúsculas,
    recuperables mediante comparación con el catálogo.
-   10 productos inexistentes → rechazar con `PRODUCTO_DESCONOCIDO`.

### 5.4. Cantidad

-   60 cantidades expresadas como texto (por ejemplo, `3 unidades`,
    `x5`) → recuperar si la cantidad es inequívoca.
-   25 cantidades decimales (por ejemplo, `3.75`) → rechazar con
    `CANTIDAD_INVALIDA`.
-   15 cantidades negativas y 10 cantidades iguales a cero → rechazar
    con `CANTIDAD_INVALIDA`.

### 5.5. Precio unitario

-   Utilizar formatos mezclados, por ejemplo: `$1.250,50`, `1250.5` y
    `1,250.50` → recuperar cuando la interpretación sea inequívoca.
-   12 precios con texto no numérico (por ejemplo, `mil`) → rechazar con
    `PRECIO_INVALIDO`.
-   10 precios negativos → rechazar con `PRECIO_INVALIDO`.
-   15 precios nulos → rechazar con `PRECIO_NULO`.

### 5.6. Total

-   Inyectar 90 totales que no coincidan con
    `cantidad × precio_unitario`.
-   Corregirlos recalculando el total y contabilizar cada corrección.

### 5.7. Vendedor

-   Aproximadamente 200 filas con variantes de mayúsculas o espacios →
    normalizar mediante el catálogo.
-   20 vendedores nulos → rechazar con `VENDEDOR_NULO`.

### 5.8. Errores estructurales

-   100 duplicados exactos → eliminar y conservar una sola copia.
-   50 filas vacías → descartar.
-   50 filas basura (encabezados repetidos, `TOTAL`, notas, etc.) →
    descartar.

### 5.9. Registro de errores inyectados

Generar `errores_inyectados.csv`, que debe registrar qué error se
introdujo en cada `id_venta`. Este archivo constituye la **verdad de
referencia** para validar el proceso de limpieza y medir su desempeño.

## 6. Entregables

El proyecto debe generar los siguientes archivos:

  -----------------------------------------------------------------------
  Archivo                             Contenido
  ----------------------------------- -----------------------------------
  `ventas_limpias.csv`                Datos de ventas depurados y
                                      normalizados.

  `ventas_limpias.xlsx`               Versión Excel de los datos
                                      depurados.

  `rechazados.csv`                    Registros no recuperables, con
                                      `id_venta`, fila original y código
                                      de motivo.

  `reporte_calidad`                   Reporte con filas originales,
                                      limpias, rechazadas y errores
                                      corregidos por tipo. Puede
                                      entregarse en un formato
                                      documentado, por ejemplo CSV, JSON,
                                      Markdown o XLSX.

  `ventas.db`                         Base SQLite con las tablas
                                      `ventas`, `clientes`, `productos` y
                                      `vendedores`.

  `queries.sql`                       Consultas SQL que respondan las
                                      preguntas de la gerente (sección
                                      7).

  Tests automáticos                   Pruebas que validen las reglas R1 a
                                      R9.
  -----------------------------------------------------------------------

También debe conservarse `errores_inyectados.csv` como archivo de
validación del generador y del proceso de limpieza.

## 7. Preguntas de negocio

La gerente comercial necesita responder:

1.  ¿Cuánto se vendió en total durante octubre?
2.  ¿Cuánto vendió cada vendedor?
3.  ¿Cuáles son los 10 mejores clientes?
4.  ¿Cuál fue el producto más vendido, tanto en unidades como en pesos?
5.  ¿Cuál fue el mejor y el peor día de ventas?
6.  ¿Qué porcentaje de las filas tenía errores y cuáles fueron los tipos
    de error?

Las consultas correspondientes deben incluirse en `queries.sql`. Para
evitar ambigüedades, documentar el criterio utilizado para definir
"mejor" y "peor" día (por ejemplo, importe total vendido por día).

## 8. Criterios de aceptación

El trabajo se considera correcto si cumple con todos los puntos
siguientes:

-   [ ] Las filas limpias + rechazadas + descartadas (duplicados, vacías
    y basura) suman exactamente 2.000.
-   [ ] Ninguna fila se pierde sin explicación.
-   [ ] No quedan valores nulos en las columnas clave.
-   [ ] No existen identificadores `id_venta` duplicados en la salida
    limpia.
-   [ ] Todas las fechas de la salida limpia pertenecen a octubre de
    2026.
-   [ ] En el 100 % de las filas limpias se cumple
    `total = cantidad × precio_unitario`, redondeado a dos decimales.
-   [ ] Hay exactamente 80 clientes únicos, excepto aquellos que solo
    aparecían en filas rechazadas.
-   [ ] Los homónimos o nombres parecidos permanecen separados.
-   [ ] Se mide el porcentaje de errores recuperados comparando el
    resultado de la limpieza con `errores_inyectados.csv`.
-   [ ] Los tests automáticos verifican las reglas R1 a R9.

## 9. Decisiones que deben poder justificarse

El análisis debe explicar y documentar las siguientes decisiones:

1.  **Interpretación de fechas:** ¿Por qué se utiliza día/mes/año y no
    mes/día/año?
2.  **Recalculo de totales:** ¿Por qué prevalece el cálculo de cantidad
    por precio unitario sobre el total cargado?
3.  **Valores no interpretables:** ¿Por qué se rechaza un precio como
    `mil` en lugar de adivinar su valor?
4.  **Identidad de clientes:** ¿Cómo se evitó fusionar dos clientes
    distintos durante la normalización?

## 10. Organización sugerida del repositorio

Una estructura posible para GitHub:

``` text
distribuidora-andina/
├── README.md
├── ENUNCIADO.md
├── data/
│   ├── raw/
│   │   └── ventas_octubre.xlsx
│   ├── generated/
│   │   ├── errores_inyectados.csv
│   │   └── catalogos/
│   └── processed/
│       ├── ventas_limpias.csv
│       ├── ventas_limpias.xlsx
│       └── rechazados.csv
├── database/
│   └── ventas.db
├── sql/
│   └── queries.sql
├── reports/
│   └── reporte_calidad.md
├── src/
│   ├── generar_datos.py
│   ├── limpiar_datos.py
│   └── cargar_base.py
└── tests/
    └── test_reglas_calidad.py
```

La estructura es orientativa y puede adaptarse a la implementación. Si
los archivos de datos son pesados, sensibles o no corresponde
publicarlos, no deben subirse al repositorio público; se pueden excluir
mediante `.gitignore` y documentar cómo generarlos.

------------------------------------------------------------------------

**Resultado esperado:** un proceso reproducible que genere datos de
prueba, introduzca errores conocidos, limpie los registros recuperables,
separe los no recuperables, mida la calidad obtenida y permita responder
las preguntas comerciales mediante SQL.
