"""
Distribuidora Andina S.A. - Generador de datos sucios
Instalación en Colab: !pip install pandas openpyxl
Ejecución: !python generar_datos.py
"""
from pathlib import Path
from datetime import date, timedelta
import random
import unicodedata
import pandas as pd

SEED = 202610
random.seed(SEED)

ROOT = Path.cwd()
RAW = ROOT / "data/raw"
GEN = ROOT / "data/generated"
CAT = GEN / "catalogos"
for folder in (RAW, GEN, CAT):
    folder.mkdir(parents=True, exist_ok=True)

# 1) Catálogos de referencia (se crean antes de ensuciar los datos)
nombres = ["Juan", "María", "Carlos", "Ana", "Lucía",
           "Martín", "Sofía", "Diego", "Valentina", "Pablo"]
apellidos = ["Pérez", "Pereyra", "Gómez", "Rodríguez",
             "Fernández", "López", "García", "Martínez"]
clientes = [f"{n} {a}" for n in nombres for a in apellidos]
assert len(clientes) == 80 and len(set(clientes)) == 80
assert "Juan Pérez" in clientes and "Juan Pereyra" in clientes

nombres_productos = [
    "Aceite 900ml", "Yerba 1kg", "Gaseosa 2.25L", "Arroz 1kg",
    "Azúcar 1kg", "Harina 000 1kg", "Fideos Spaghetti 500g",
    "Fideos Tirabuzón 500g", "Lentejas 400g", "Porotos 400g",
    "Puré de tomate 520g", "Mayonesa 500g", "Ketchup 250g",
    "Sal fina 500g", "Vinagre 1L", "Café molido 250g",
    "Leche larga vida 1L", "Agua mineral 2L", "Jugo en polvo",
    "Galletitas dulces 300g", "Galletitas saladas 300g",
    "Mermelada 454g", "Dulce de leche 400g", "Atún en lata 170g",
    "Choclo en lata 300g", "Arvejas en lata 300g",
    "Duraznos en lata 820g", "Caldo en cubos",
    "Cacao en polvo 180g", "Té en saquitos"
]
assert len(nombres_productos) == 30
productos = [{"producto": p, "precio_lista": round(random.uniform(800, 15000), 2)}
             for p in nombres_productos]
vendedores = ["Marcos Ruiz", "Ana Torres", "Luciano Díaz", "Carla Gómez",
              "Federico López", "Paula Fernández", "Diego Martínez", "Sofía Castro"]

pd.DataFrame({"cliente": clientes}).to_csv(CAT/"clientes.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(productos).to_csv(CAT/"productos.csv", index=False, encoding="utf-8-sig")
pd.DataFrame({"vendedor": vendedores}).to_csv(CAT/"vendedores.csv", index=False, encoding="utf-8-sig")

def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def fecha_texto(f, tipo):
    meses = ["ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]
    if tipo == 0: return f.strftime("%d/%m/%Y")
    if tipo == 1: return f.strftime("%Y-%m-%d")
    if tipo == 2: return f"{f.day} {meses[f.month-1]} {str(f.year)[2:]}"
    return f.strftime("%Y-%m-%d") + " 14:30"

errores = []
def log(df, i, codigo, valor):
    errores.append({"id_venta": df.at[i, "id_venta"],
                    "codigo_error": codigo, "valor_inyectado": str(valor)})

# 2) 1.800 ventas válidas originales
registros = []
for n in range(1, 1801):
    f = date(2026, 10, 1) + timedelta(days=random.randrange(31))
    p = random.choice(productos)
    q = random.randint(1, 200)
    precio = p["precio_lista"]
    registros.append({
        "id_venta": f"V-{n:04d}", "fecha": f, "cliente": random.choice(clientes),
        "producto": p["producto"], "cantidad": q, "precio_unitario": precio,
        "total": round(q*precio, 2), "vendedor": random.choice(vendedores)
    })
df = pd.DataFrame(registros)
indices = list(df.index)
def sample(n): return random.sample(indices, n)
def sample_excluding(n, used):
    return random.sample([i for i in indices if i not in used], n)

# 3) Formatos de fecha en proporción 40/30/20/10
tipos = [0]*720 + [1]*540 + [2]*360 + [3]*180
random.shuffle(tipos)
df["fecha"] = [fecha_texto(f, t) for f, t in zip(df["fecha"], tipos)]

used_fecha = set()
for i in sample_excluding(40, used_fecha):
    used_fecha.add(i)
    df.at[i, "fecha"] = None; log(df, i, "FECHA_NULA", None)
for i in sample_excluding(20, used_fecha):
    used_fecha.add(i)
    v = random.choice(["05/09/2026", "2026-11-05", "01/12/2026"])
    df.at[i, "fecha"] = v; log(df, i, "FECHA_FUERA_RANGO", v)
for i in sample_excluding(15, used_fecha):
    used_fecha.add(i)
    df.at[i, "fecha"] = "31/11/2026"; log(df, i, "FECHA_INVALIDA", "31/11/2026")

# 4) Variantes y nulos de clientes
used_cliente = set()
for i in sample_excluding(450, used_cliente):
    used_cliente.add(i)
    original = df.at[i, "cliente"]
    transformaciones = [
        original.lower(), original.upper(), original + "   ",
        sin_tildes(original), " ".join(reversed(original.split())).upper()
    ]
    v = random.choice(transformaciones)
    df.at[i, "cliente"] = v; log(df, i, "CLIENTE_VARIANTE", v)
for i in sample_excluding(15, used_cliente):
    used_cliente.add(i)
    df.at[i, "cliente"] = None; log(df, i, "CLIENTE_NULO", None)

# 5) Variantes y desconocidos de productos
used_producto = set()
for i in sample_excluding(90, used_producto):
    used_producto.add(i)
    original = df.at[i, "producto"]
    opciones = [original.upper(), original.lower(), original+" ",
                original.replace("a", "á", 1) if "a" in original else original+"s",
                original[:-1]]
    v = random.choice(opciones)
    df.at[i, "producto"] = v; log(df, i, "PRODUCTO_VARIANTE", v)
for i in sample_excluding(10, used_producto):
    used_producto.add(i)
    v = f"Producto Inexistente {i}"
    df.at[i, "producto"] = v; log(df, i, "PRODUCTO_DESCONOCIDO", v)

# 6) Cantidades: textos recuperables y valores inválidos
used_cantidad = set()
for i in sample_excluding(60, used_cantidad):
    used_cantidad.add(i)
    q = int(df.at[i, "cantidad"])
    v = f"{q} unidades" if random.random() < .5 else f"x{q}"
    df.at[i, "cantidad"] = v; log(df, i, "CANTIDAD_TEXTO", v)
for i in sample_excluding(25, used_cantidad):
    used_cantidad.add(i)
    df.at[i, "cantidad"] = "3.75"; log(df, i, "CANTIDAD_DECIMAL", "3.75")
for i in sample_excluding(15, used_cantidad):
    used_cantidad.add(i)
    v = -random.randint(1, 200)
    df.at[i, "cantidad"] = v; log(df, i, "CANTIDAD_NEGATIVA", v)
for i in sample_excluding(10, used_cantidad):
    used_cantidad.add(i)
    df.at[i, "cantidad"] = 0; log(df, i, "CANTIDAD_CERO", 0)

# 7) Precios: formatos recuperables y valores inválidos
used_precio = set()
for i in sample_excluding(150, used_precio):
    used_precio.add(i)
    precio = float(df.at[i, "precio_unitario"])
    tipo = random.choice(["ar", "decimal", "usa"])
    if tipo == "ar":
        v = f"${precio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif tipo == "decimal":
        v = f"{precio:.2f}"
    else:
        v = f"{precio:,.2f}"
    df.at[i, "precio_unitario"] = v
    log(df, i, "PRECIO_FORMATO", v)
for i in sample_excluding(12, used_precio):
    used_precio.add(i)
    df.at[i, "precio_unitario"] = "mil"; log(df, i, "PRECIO_INVALIDO", "mil")
for i in sample_excluding(10, used_precio):
    used_precio.add(i)
    v = -round(random.uniform(800, 15000), 2)
    df.at[i, "precio_unitario"] = v; log(df, i, "PRECIO_NEGATIVO", v)
for i in sample_excluding(15, used_precio):
    used_precio.add(i)
    df.at[i, "precio_unitario"] = None; log(df, i, "PRECIO_NULO", None)

# 8) Totales incorrectos
for i in sample(90):
    v = round(float(df.at[i, "total"]) + random.uniform(10, 500), 2)
    df.at[i, "total"] = v; log(df, i, "TOTAL_NO_COINCIDE", v)

# 9) Variantes y nulos de vendedores
used_vendedor = set()
for i in sample_excluding(200, used_vendedor):
    used_vendedor.add(i)
    original = df.at[i, "vendedor"]
    v = random.choice([original.lower(), original.upper(), "  "+original+" "])
    df.at[i, "vendedor"] = v; log(df, i, "VENDEDOR_VARIANTE", v)
for i in sample_excluding(20, used_vendedor):
    used_vendedor.add(i)
    df.at[i, "vendedor"] = None; log(df, i, "VENDEDOR_NULO", None)

# 10) Estructura: 100 duplicados exactos + 50 vacías + 50 basura
duplicados = df.sample(n=100, random_state=SEED).copy()
vacias = pd.DataFrame([{c: None for c in df.columns} for _ in range(50)])
basura = []
for n in range(50):
    if n % 3 == 0:
        basura.append(dict(zip(df.columns, df.columns)))
    elif n % 3 == 1:
        basura.append({c: ("TOTAL" if c == "id_venta" else None) for c in df.columns})
    else:
        basura.append({"id_venta": None, "fecha": "revisar", "cliente": "revisar",
                       "producto": None, "cantidad": None, "precio_unitario": None,
                       "total": None, "vendedor": None})
df_final = pd.concat([df, duplicados, vacias, pd.DataFrame(basura)], ignore_index=True)
assert len(df_final) == 2000

# 11) Guardar archivos
with pd.ExcelWriter(RAW/"ventas_octubre.xlsx", engine="openpyxl") as writer:
    df_final.to_excel(writer, sheet_name="Ventas", index=False)
pd.DataFrame(errores).to_csv(GEN/"errores_inyectados.csv", index=False, encoding="utf-8-sig")

print("GENERACIÓN COMPLETADA")
print("Ventas originales:", len(df))
print("Filas del Excel sucio:", len(df_final))
print("Errores registrados:", len(errores))
print("Excel:", RAW/"ventas_octubre.xlsx")
print("Registro de errores:", GEN/"errores_inyectados.csv")
print("Catálogos:", CAT)
print("Este programa genera datos de prueba; la limpieza se implementará en otro script.")
