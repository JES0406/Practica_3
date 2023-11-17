"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP02A
Integrantes:
    - JAVIER ESCOBAR SERRANO
    - ENRIQUE FERNÁNDEZ-BAILLO RODRIÍGUEZ DE TEMBLEQUE

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

#Constantes con las velocidades máximas establecidas por el enunciado para cada tipo de vía.
VELOCIDADES_CALLES={"AUTOVIA":100,"AVENIDA":90,"CARRETERA":70,"CALLEJON":30,"CAMINO":30,"ESTACION DE METRO":20,"PASADIZO":20,"PLAZUELA":20,"COLONIA":20}
VELOCIDAD_CALLES_ESTANDAR=50

import pandas as pd
from dgt import process_data
from grafo import Grafo
df_cruces, df_direcc = process_data("data/cruces.csv", "data/direcciones.csv")


class Cruce:

    #Completar esta clase con los datos y métodos que se necesite asociar a cada cruce

    def __init__(self,coord_x,coord_y):
        self.coord_x=coord_x
        self.coord_y=coord_y
        self.calles = self.get_calles(df_cruces)
   
    
    """Se hace que la clase Cruce sea "hashable" mediante la implementación de los métodos
    __eq__ y __hash__, haciendo que dos objetos de tipo Cruce se consideren iguales cuando
    sus coordenadas coincidan (es decir, C1==C2 si y sólo si C1 y C2 tienen las mismas coordenadas),
    independientemente de los otros campos que puedan estar almacenados en los objetos.
    La función __hash__ se adapta en consecuencia para que sólo dependa del par (coord_x, coord_y).
    """
    def __eq__(self,other) -> int:
        if type(other) is type(self):
            return ((self.coord_x==other.coord_x) and (self.coord_y==other.coord_y))
        else:
            return False
    
    def __hash__(self) -> int:
        return hash((self.coord_x,self.coord_y))

    def get_calles(self, cruces: pd.DataFrame):
        return cruces[(cruces["Coordenada X (Guia Urbana) cm (cruce)"] == self.coord_x) & (cruces["Coordenada Y (Guia Urbana) cm (cruce)"] == self.coord_y)]["Codigo de vía tratado"].unique()
    


class Calle:
    #Completar esta clase con los datos que sea necesario almacenar de cada calle para poder reconstruir los datos del 
    def __init__(self, ID):
        self.ID = ID
        self.direcciones = pd.DataFrame()
        self.cruces = pd.DataFrame()

    def get_data(self, cruces: pd.DataFrame, direcciones: pd.DataFrame):
        self.direcciones = direcciones.loc[direcciones["Codigo de via"]==self.ID]
        self.cruces = cruces.loc[cruces["Codigo de via"]==self.ID]

    def get_velocidad(self):
        if self.direcciones.empty or self.direcciones["Clase de la via"].iloc[0] not in VELOCIDADES_CALLES:
            return VELOCIDAD_CALLES_ESTANDAR
        else:
            return VELOCIDADES_CALLES[self.direcciones["Clase de la via"].iloc[0]]

def filtrar_por_radios(R: int):
    df_cruces["coordenadas"] = list(zip(df_cruces["Coordenada X (Guia Urbana) cm (cruce)"], df_cruces["Coordenada Y (Guia Urbana) cm (cruce)"]))
    coordenadas_a_tratar = df_cruces["coordenadas"].sort_values().unique()
    coordenadas_limpias = []
    for coordenada in coordenadas_a_tratar:
        coor_x = coordenada[0]
        coor_y = coordenada[1]
        if not any((coor_x - R <= x <= coor_x + R) and (coor_y - R <= y <= coor_y + R) for x, y in coordenadas_limpias):
            coordenadas_limpias.append(coordenada)
    return coordenadas_limpias

if __name__ == "__main__":
    coordenadas_limpias = filtrar_por_radios(8000)
    grafo = Grafo(False)
    print(len(coordenadas_limpias))
    for coordenada in coordenadas_limpias:
        grafo.agregar_vertice(Cruce(coordenada[0], coordenada[1]))