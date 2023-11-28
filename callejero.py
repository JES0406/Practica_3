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
from math import sqrt
import numpy as np
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
        return cruces[cruces["coordenadas"] == (self.coord_x, self.coord_y)]["Codigo de vía tratado"].unique()
    

class Calle:
    #Completar esta clase con los datos que sea necesario almacenar de cada calle para poder reconstruir los datos del callejero
    def __init__(self, ID):
        self.ID = ID
        self.direcciones = self.get_data(df_cruces, df_direcc)[1]
        self.cruces = self.get_data(df_cruces, df_direcc)[0]

    def get_data(self, cruces: pd.DataFrame, direcciones: pd.DataFrame)-> tuple:
        return (cruces[cruces["Codigo de vía tratado"] == self.ID].coordenadas.unique(), direcciones[direcciones["Codigo de via"] == self.ID])

    def get_velocidad(self):
        if self.direcciones.empty or self.direcciones["Clase de la via"].iloc[0] not in VELOCIDADES_CALLES:
            return VELOCIDAD_CALLES_ESTANDAR
        else:
            return VELOCIDADES_CALLES[self.direcciones["Clase de la via"].iloc[0]]
        
    def funcion_aux(self, x, distancias, cruce):
        distancias[dist(x["coordenadas"], cruce)] = x["Número"]

    def ordenar_cruces(self):
        cruces_ordenados = {}

        def funcion_aux(x, cruce):
            if x['Prefijo de numeración'] == "KM.":
                pass
            else:
                distancias[dist(x["coordenadas"], cruce)] = x["Número"]

        for cruce in self.cruces:
            try:
                distancias = {}
                self.direcciones.apply(lambda x: funcion_aux(x, cruce), axis=1)
                distancias = dict(sorted(distancias.items()))
                distancia_min = list(distancias.keys())[0]
                num_dist_min = distancias[distancia_min]
                
                if num_dist_min not in cruces_ordenados:
                    cruces_ordenados[num_dist_min] = cruce
                
                else:

                    num_anterior = num_dist_min - 2
                    num_siguiente = num_dist_min + 2
                    
                    while num_dist_min + 0.01 in cruces_ordenados:
                        num_dist_min += 0.01
                    
                    if len(distancias) < 3:
                        cruces_ordenados[num_dist_min + 0.01] = cruce
                        continue

                    error = True
                    while error:
                        try:
                            coords_anterior = self.direcciones.loc[self.direcciones["Número"] == num_anterior]['coordenadas'].values[0]
                            cruce_anterior = cruces_ordenados[num_dist_min]

                            dist_cruce_actual = dist(cruce, coords_anterior)
                            dist_cruce_anterior = dist(cruce_anterior, coords_anterior)
                            
                            if dist_cruce_actual < dist_cruce_anterior:
                                cruces_ordenados[num_dist_min + 0.01] = cruce_anterior
                                cruces_ordenados[num_dist_min] = cruce
                            else:
                                cruces_ordenados[num_dist_min + 0.01] = cruce
                            error = False

                        except:
                            try:
                                coords_siguiente = self.direcciones.loc[self.direcciones["Número"] == num_siguiente]['coordenadas'].values[0]
                                cruce_anterior = cruces_ordenados[num_dist_min]

                                dist_cruce_actual = dist(cruce, coords_siguiente)
                                dist_cruce_siguiente = dist(cruce_anterior, coords_siguiente)

                                if dist_cruce_actual < dist_cruce_siguiente:
                                    cruces_ordenados[num_dist_min + 0.01] = cruce
                                else:
                                    cruces_ordenados[num_dist_min + 0.01] = cruce_anterior
                                    cruces_ordenados[num_dist_min] = cruce
                                error = False
                            except:
                                num_anterior -= 2
                                num_siguiente += 2
                                if num_siguiente > 600:
                                    error = False
                                    cruces_ordenados[num_dist_min + 0.01] = cruce
            except:
                continue
        
        cruces_ordenados = dict(sorted(cruces_ordenados.items()))
        cruces_ordenados = list(cruces_ordenados.values())
        self.cruces = cruces_ordenados

def filtrar_por_radios(R: int):
    df_cruces["coordenadas"] = list(zip(df_cruces["Coordenada X (Guia Urbana) cm (cruce)"], df_cruces["Coordenada Y (Guia Urbana) cm (cruce)"]))
    coordenadas_a_tratar = sorted(df_cruces["coordenadas"].unique())
    coordenadas_limpias = []
    for coordenada in coordenadas_a_tratar:
        for x, y in coordenadas_limpias:
            if dist(coordenada, (x, y)) <= R:
                break
        else:
            coordenadas_limpias.append(coordenada)

    df_cruces["coordenadas"] = df_cruces["coordenadas"].apply(lambda x: x if x in coordenadas_limpias else closest(x, coordenadas_limpias, R))
    return coordenadas_limpias

def dist(coordenada1, coordenada2):
    return sqrt((coordenada1[0] - coordenada2[0])**2 + (coordenada1[1] - coordenada2[1])**2)

def closest(coordenada, coordenadas_limpias, R):
    coor_x, coor_y = coordenada[0], coordenada[1]
    for x, y in coordenadas_limpias:
        if (coor_x - R <= x <= coor_x + R) and (coor_y - R <= y <= coor_y + R):
            return (x, y)

if __name__ == "__main__":
    # 1500 centímetros = 15 metros, se considera que un cruce está dentro del radio de otro si está a
    # menos de 15 metros de distancia según las observaciones
    coordenadas_limpias = filtrar_por_radios(1500)

    # Creamos los cruces
    cruces = {}
    for coordenada in coordenadas_limpias:
        cruces[coordenada] = Cruce(coordenada[0], coordenada[1])
    list_cruces:list[Cruce] = list(cruces.values())

    # Creamos las calles
    calles = []
    for cruce in list_cruces: # Escogemos los cruces
        for calle in cruce.calles: # Escogemos las calles de cada cruce
            if calle not in calles: # Si la calle no está en la lista de calles, la añadimos
                calles.append(calle)  
    calles = [Calle(calle) for calle in calles] # Creamos los objetos calle

    # Creamos el grafo  
    grafo = Grafo(False)

    # Añadir vértices al grafo
    for cruce in list_cruces:
        grafo.agregar_vertice(cruce)
    
    # Para las aristas, se añaden las calles que conectan dos cruces como aristas del grafo
    for calle in calles:
        cruces_calle = calle.cruces
        for i in range(len(cruces_calle)):
            if i != len(cruces_calle) - 1:
                grafo.agregar_arista(cruces[cruces_calle[i]], cruces[cruces_calle[i+1]], None, calle.get_velocidad())

    # Pasemoslo a networkx
    import networkx as nx
    import matplotlib.pyplot as plt
    G = grafo.convertir_a_NetworkX()

    pos = {}
    for cruce in list_cruces:
        pos[cruce] = (cruce.coord_x, cruce.coord_y)

    nx.draw_networkx_nodes(G, pos=pos, node_size=1)
    nx.draw_networkx_edges(G, pos=pos, width=0.5, edge_color="black")
    plt.show()