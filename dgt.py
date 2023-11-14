import pandas as pd
import re


def cruces_read(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="iso-8859-1", delimiter=";")


def clean_names(df_cruces: pd.DataFrame) -> pd.DataFrame:
    """Función que limpia los nombres de las columnas del dataframe de cruces

    Args:
        df_cruces (pd.DataFrame): DataFrame de cruces

    Returns:
        pd.DataFrame: DataFrame de cruces con los nombres de las columnas limpios
    """
    columnas_a_corregir = ["Literal completo del vial tratado", "Literal completo del vial que cruza", "Clase de la via tratado", "Clase de la via que cruza", "Particula de la via tratado", "Particula de la via que cruza", "Nombre de la via tratado", "Nombre de la via que cruza"]

    for i in columnas_a_corregir:
        df_cruces[i] = df_cruces[i].apply(lambda x: x.strip() if x!="nan" and x.strip() != "" else "nan") # Eliminamos espacios en blanco y nan
    return df_cruces

def cruces_as_int(df_cruces: pd.DataFrame) -> pd.DataFrame:
    """Función que convierte a int las columnas que deben serlo

    Args:
        df_cruces (pd.DataFrame): DataFrame de cruces

    Returns:
        pd.DataFrame: DataFrame de cruces con las columnas convertidas a int
    """
    columnas_a_corregir = ["Codigo de vía tratado", "Codigo de via que cruza o enlaza", "Coordenada X (Guia Urbana) cm (cruce)", "Coordenada X (Guia Urbana) cm (cruce)"]
    for i in columnas_a_corregir:
        # Si no es int, lo convertimos
        if df_cruces[i].dtype != "int64":
            df_cruces[i] = df_cruces[i].to_numeric()
    return df_cruces

def direcciones_read(path: str) -> pd.DataFrame:
    return pd.read_csv(path, encoding="iso-8859-1", delimiter=";")


def direcciones_as_int(df_direcc: pd.DataFrame) -> pd.DataFrame:
    """Función que convierte a int las columnas que deben serlo

    Args:
        df_direcc (pd.DataFrame): dataframe de direcciones

    Returns:
        pd.DataFrame: dataframe de direcciones con las columnas convertidas a int
    """
    columnas_a_corregir = ["Codigo de numero", "Codigo de via", "Coordenada X (Guia Urbana) cm", "Coordenada Y (Guia Urbana) cm"]
    for i in columnas_a_corregir:
        if df_direcc[i].dtype != "int64":
            df_direcc[i] = df_direcc[i].apply(lambda x: int(x) if re.match(r"^\d+$", str(x)) else "Nan")
    return df_direcc

def literal_split(df_direc: pd.DataFrame) -> pd.DataFrame:
    df_direc["Prefijo de numeración"] = df_direc["Literal de numeracion"].apply(lambda x: re.match(r"^([^\d]+)(\d+)([^\d]*)$", x).group(1))
    df_direc["numero"] = df_direc["Literal de numeracion"].apply(lambda x: re.match(r"^([^\d]+)(\d+)([^\d]*)$", x).group(2))
    df_direc["Sufijo de numeración"] = df_direc["Literal de numeracion"].apply(lambda x: re.match(r"^([^\d]+)(\d+)([^\d]*)$", x).group(3))

    df_direc[["Prefijo de numeración", "numero", "Sufijo de numeración"]]

    return df_direc


def process_data(path_1: str, path_2: str) -> [pd.DataFrame, pd.DataFrame]:
    """Función que procesa los datos de los ficheros

    Args:
        path_1 (str): ruta del fichero de cruces
        path_2 (str): ruta del fichero de direcciones

    Returns:
        [pd.DataFrame, pd.DataFrame]: [dataframe de cruces, dataframe de direcciones]
    """
    # Apliquemos las funciones anteriores de manera secuencial
    return [cruces_as_int(clean_names(cruces_read(path_1))), literal_split(direcciones_as_int(direcciones_read(path_2)))]