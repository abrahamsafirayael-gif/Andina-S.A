# Distribuidora Andina S.A. — Proyecto de limpieza y análisis de datos

> **Estado: en desarrollo.** Hoy el repositorio incluye el generador de datos de prueba con errores conocidos. La limpieza, la base de datos SQL y los tests están en progreso (ver [Estado del proyecto](#estado-del-proyecto)).

## De qué trata

Distribuidora Andina S.A. es una mayorista ficticia de alimentos y bebidas. Sus vendedores cargan las ventas a mano en un Excel compartido y, al cierre de octubre de 2026, el archivo `ventas_octubre.xlsx` no se puede usar: los totales no coinciden, hay clientes repetidos y filas rotas.

El objetivo del proyecto es, desde el rol de analista de datos:

1. Generar un dataset de ventas con errores **inyectados a propósito** y registrados.
2. Limpiar los datos recuperables y rechazar (con motivo) los que no se pueden recuperar.
3. Medir la calidad de la limpieza contra los errores conocidos.
4. Cargar el resultado en una base SQLite y responder preguntas de negocio con SQL.

La consigna completa está en [`ENUNCIADO.md`](ENUNCIADO.md).

## Enfoque QA

La idea central es la **inyección de defectos**: como sé exactamente qué errores sembré y en qué filas (`errores_inyectados.csv`), puedo comprobar después cuántos detectó y recuperó el proceso de limpieza, en lugar de confiar en una revisión a ojo.

## Estado del proyecto

- [x] Consigna y reglas de negocio (`ENUNCIADO.md`)
- [x] Generador de datos sucios (`generar_datos.py`)
- [ ] Script de limpieza (`limpiar_datos.py`)
- [ ] Archivo de rechazados con código de motivo
- [ ] Reporte de calidad
- [ ] Base SQLite (`ventas`, `clientes`, `productos`, `vendedores`) y `queries.sql`
- [ ] Tests automáticos de las reglas R1 a R9
- [ ] Notebook de Google Colab con el análisis

## Qué hace `generar_datos.py`

1. Crea los **catálogos de referencia**: 80 clientes, 30 productos con precio de lista y 8 vendedores.
2. Genera **1.800 ventas válidas** de octubre de 2026.
3. Les inyecta errores de 18 tipos (una fila puede tener más de uno).
4. Agrega **100 duplicados exactos, 50 filas vacías y 50 filas basura**, hasta llegar a **2.000 filas**.
5. Guarda el Excel sucio y el registro de errores inyectados.

Usa una semilla fija (`SEED = 202610`), por lo que los datos son reproducibles.

### Errores inyectados

| Campo | Error | Cantidad |
|---|---|---|
| Fecha | Vacía (`FECHA_NULA`) | 40 |
| Fecha | Fuera de octubre (`FECHA_FUERA_RANGO`) | 20 |
| Fecha | Imposible, p. ej. 31/11 (`FECHA_INVALIDA`) | 15 |
| Fecha | Cuatro formatos mezclados (40/30/20/10 %) | todas |
| Cliente | Variantes de mayúsculas, tildes, espacios u orden (`CLIENTE_VARIANTE`) | 450 |
| Cliente | Nulo (`CLIENTE_NULO`) | 15 |
| Producto | Errores de tipeo (`PRODUCTO_VARIANTE`) | 90 |
| Producto | Inexistente (`PRODUCTO_DESCONOCIDO`) | 10 |
| Cantidad | Texto, p. ej. `x5` (`CANTIDAD_TEXTO`) | 60 |
| Cantidad | Decimal (`CANTIDAD_DECIMAL`) | 25 |
| Cantidad | Negativa (`CANTIDAD_NEGATIVA`) | 15 |
| Cantidad | Cero (`CANTIDAD_CERO`) | 10 |
| Precio | Formatos mezclados (`PRECIO_FORMATO`) | 150 |
| Precio | Texto no numérico (`PRECIO_INVALIDO`) | 12 |
| Precio | Negativo (`PRECIO_NEGATIVO`) | 10 |
| Precio | Nulo (`PRECIO_NULO`) | 15 |
| Total | No coincide con cantidad × precio (`TOTAL_NO_COINCIDE`) | 90 |
| Vendedor | Variantes de mayúsculas o espacios (`VENDEDOR_VARIANTE`) | 200 |
| Vendedor | Nulo (`VENDEDOR_NULO`) | 20 |
| Estructura | Duplicados exactos / filas vacías / filas basura | 100 / 50 / 50 |

## Cómo ejecutarlo

### En Google Colab

```python
!pip install pandas openpyxl
!git clone https://github.com/abrahamsafirayael-gif/Andina-S.A.git
%cd Andina-S.A
!python generar_datos.py
```

### En local

```bash
git clone https://github.com/abrahamsafirayael-gif/Andina-S.A.git
cd Andina-S.A
pip install pandas openpyxl
python generar_datos.py
```

### Archivos que genera

```
data/
├── raw/
│   └── ventas_octubre.xlsx        # Excel sucio de 2.000 filas (hoja "Ventas")
└── generated/
    ├── errores_inyectados.csv     # id_venta, codigo_error, valor_inyectado
    └── catalogos/
        ├── clientes.csv
        ├── productos.csv
        └── vendedores.csv
```

## Reglas de negocio (resumen)

- **R1–R2:** fechas entre el 01/10/2026 y el 31/10/2026; las ambiguas se leen como día/mes/año.
- **R3–R4:** cantidad entera entre 1 y 200; precio unitario positivo.
- **R5:** el total correcto es `round(cantidad × precio_unitario, 2)`.
- **R6–R7:** cliente, producto y vendedor no nulos; nombres normalizados.
- **R8:** los duplicados exactos se eliminan.
- **R9:** nunca se inventa un dato; si no se puede recuperar con certeza, la fila va a rechazados con su motivo.

## Preguntas de negocio a responder con SQL

1. ¿Cuánto se vendió en total en octubre?
2. ¿Cuánto vendió cada vendedor?
3. ¿Cuáles son los 10 mejores clientes?
4. ¿Cuál fue el producto más vendido, en unidades y en pesos?
5. ¿Cuál fue el mejor y el peor día de ventas?
6. ¿Qué porcentaje de filas tenía errores y de qué tipo?

## Tecnologías

Python · pandas · openpyxl · Google Colab · (próximamente) SQLite y pytest

## Próximos pasos

1. Escribir `limpiar_datos.py`, empezando por fechas y cantidades.
2. Medir el porcentaje de errores recuperados contra `errores_inyectados.csv`.
3. Agregar tests con pytest para las reglas R1 a R9.
4. Cargar la base SQLite y escribir `queries.sql`.

## Autora

**Safira Yael Abraham** — QA Junior · [GitHub](https://github.com/abrahamsafirayael-gif)
