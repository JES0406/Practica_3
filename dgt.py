import pandas as pd
import re
import numpy as np

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
    columnas = ['Codigo de numero', 'Codigo de via',
                'Coordenada X (Guia Urbana) cm', 'Coordenada Y (Guia Urbana) cm']
    direcciones_enteros = df_direcc.copy()

    # Tras comprobar qué datos eran erróneos a la hora de convertirlos a enteros, se ha visto que
    # todos ellos tenían el valor '000000-100', por lo que se asume que este valor es el valor nulo.
    # Se ha creado una función que cambia este valor por np.nan y se ha aplicado a las columnas,
    # eliminando posteriormente los valores nulos (no tiene sentido estudiar un cruce del que no
    # se conocen sus coordenadas). Finalmente, se convierten las columnas a enteros.
    def change_to_nan(x):
        if x == '000000-100':
            return np.nan
        else:
            return x
        
    for columna in columnas:
        direcciones_enteros[columna] = direcciones_enteros[columna].apply(lambda x: change_to_nan(x))
        direcciones_enteros = direcciones_enteros.dropna(subset=[columna])
        direcciones_enteros[columna] = direcciones_enteros[columna].astype(int)

    return direcciones_enteros

def literal_split(df_direc: pd.DataFrame) -> pd.DataFrame:
    
    # Expresión regular para dividir el literal de numeración en prefijo, número y sufijo
    literal_splitter = re.compile(r"([A-Z]+\.?)([0-9]+)\s*([A-Z]*)")

    literal_splitted = df_direc.copy()

    # Función que aplica la expresión regular a cada valor de la columna 'Literal de numeración'
    def listas(x):
        matches = re.search(literal_splitter, str(x))
        pref_num = matches.group(1)
        num = int(matches.group(2))
        if matches.group(3) == '':
            suf_num = None
        else:
            suf_num = matches.group(3)
        return pref_num, num, suf_num

    # Se crean las tres nuevas columnas a partir de la división del literal de numeración
    columnas = ['Prefijo de numeración', 'Número', 'Sufijo de numeración']
    literal_splitted[columnas] = literal_splitted['Literal de numeracion'].apply(lambda x: pd.Series(listas(x)))
    return literal_splitted


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