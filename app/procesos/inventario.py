from fastapi import APIRouter, UploadFile, File
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd
import re

router = APIRouter(prefix="/inventario", tags=["Inventario Cajas"])

def obtener_cantidad_cajas(texto: str) -> int:
    if not texto:
        return 0

    texto = texto.lower()

    # Normalización de errores reales
    texto = texto.replace("vaja", "caja")
    texto = texto.replace("vajas", "cajas")

    total = 0
    palabras = texto.split()

    for i in range(len(palabras) - 1):
        if palabras[i].isdigit() and palabras[i + 1].startswith("caja"):
            total += int(palabras[i])

    # Caso especial: "venta de caja(s)"
    if total == 0 and ("venta de caja" in texto or "venta de cajas" in texto):
        total = 1

    return total

def obtener_resumen_dimensiones(df: pd.DataFrame) -> dict:
    resumen = {}

    for texto in df["COMENTARIOS"].dropna():
        texto = texto.lower()

        # Normalización fuerte
        reemplazos = {
            "vaja": "caja",
            "vajas": "cajas",
            "cjas": "cajas",
            "cja": "caja",
            "1caja": "1 caja",
            "2caja": "2 caja",
            "3caja": "3 caja",
            "4caja": "4 caja",
        }

        for k, v in reemplazos.items():
            texto = texto.replace(k, v)

        partes = texto.split()

        for i, palabra in enumerate(partes):
            if re.match(r"\d+\.\d+\.\d+", palabra):
                dimension = palabra
                cantidad = 1

                if i > 0 and partes[i - 1].isdigit():
                    cantidad = int(partes[i - 1])
                elif i > 1 and partes[i - 2].isdigit():
                    cantidad = int(partes[i - 2])

                resumen[dimension] = resumen.get(dimension, 0) + cantidad

    return resumen

@router.post("/procesar")
async def procesar_inventario(file: UploadFile = File(...)):
    df = pd.read_excel(file.file)

    # Construir detalle
    registros = []

    for _, row in df.iterrows():
        cajas = obtener_cantidad_cajas(str(row.iloc[10]))  # COMENTARIOS (col K)

        if cajas > 0:
            registros.append({
                "GUIA#": row.iloc[1],
                "PZ": row.iloc[3],
                "FECHA": row.iloc[7],
                "REMITENTE": row.iloc[8],
                "DESTINATARIO": row.iloc[9],
                "COMENTARIOS": row.iloc[10],
                "CANTIDAD_CAJAS": cajas
            })

    df_detalle = pd.DataFrame(registros)

    # Resumen
    resumen = obtener_resumen_dimensiones(df_detalle)
    df_resumen = pd.DataFrame(
        resumen.items(),
        columns=["DIMENSION", "CANTIDAD"]
    )

    # Generar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_detalle.to_excel(writer, index=False, sheet_name="Detalle_Venta_Cajas")
        df_resumen.to_excel(writer, index=False, sheet_name="Resumen_Cajas")

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=Inventario_Cajas.xlsx"
        }
    )
