from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
from app.core.utils import normalizar_texto
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter(prefix="/agendamiento", tags=["Agendamiento"])

@router.post("/procesar")
async def procesar_agendamiento(
    export_file: UploadFile = File(...),
    base_file: UploadFile = File(...)
):
    df_export = pd.read_excel(export_file.file)
    df_base = pd.read_excel(base_file.file)

    # Copiar solo columnas A:M
    df_destino = df_export.iloc[:, :13].copy()

    # Llaves normalizadas
    df_destino["KEY"] = df_destino.iloc[:, 2].apply(normalizar_texto)
    df_base["KEY"] = df_base.iloc[:, 8].apply(normalizar_texto)

    # 🔹 QUEDARSE CON LA PRIMERA OCURRENCIA (como BUSCARV)
    df_base_unica = df_base.drop_duplicates(subset=["KEY"], keep="first")

    # BUSCARV 1 → Valor (col 21)
    valor_map = df_base_unica.set_index("KEY").iloc[:, 20]

    # BUSCARV 2 → #Guía (col 2)
    guia_map = df_base_unica.set_index("KEY").iloc[:, 1]

    df_destino["Valor"] = df_destino["KEY"].map(valor_map)
    df_destino["#Guia"] = df_destino["KEY"].map(guia_map)

    # -------------------------------
    # PASO 6: eliminar duplicados bien
    # -------------------------------

    # Filas con #Guia válida
    df_con_guia = df_destino[df_destino["#Guia"].notna()].copy()

    # Filas sin #Guia (pendientes de validación)
    df_sin_guia = df_destino[df_destino["#Guia"].isna()].copy()

    # Eliminar duplicados SOLO donde hay #Guia
    df_con_guia_limpio = df_con_guia.drop_duplicates(
        subset=["#Guia"],
        keep="first"
    )

    # Unir todo de nuevo
    df_final = pd.concat(
        [df_con_guia_limpio, df_sin_guia],
        ignore_index=True
    )

    # Métricas
    duplicados_eliminados = len(df_con_guia) - len(df_con_guia_limpio)

    # Eliminar columna técnica
    df_final = df_final.drop(columns=["KEY"])

    # (Opcional) ordenar por #Guia para mejor lectura
    df_final = df_final.sort_values(by=["#Guia"], na_position="last")


    # -------------------------------
    # PASO 7: generar Excel final
    # -------------------------------

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Hoja principal
        df_final.to_excel(
            writer,
            index=False,
            sheet_name="Agendamiento"
        )

        # Hoja de pendientes (opcional pero recomendado)
        if not df_sin_guia.empty:
            df_sin_guia.drop(columns=["KEY"], errors="ignore").to_excel(
                writer,
                index=False,
                sheet_name="Pendientes_Validacion"
            )

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=Agendamiento_procesado.xlsx"
        }
    )


