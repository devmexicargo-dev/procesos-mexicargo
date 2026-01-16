import unicodedata
import pandas as pd

def normalizar_texto(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip().upper()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return texto
