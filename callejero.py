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

# Importamos las librerías necesarias
import pandas as pd
from dgt import process_data
from grafo import Grafo
from math import sqrt

# Procesamos los datos de los ficheros y creamos ambos DataFrames
df_cruces, df_direcc = process_data("data/cruces.csv", "data/direcciones.csv")

class Cruce:
    def __init__(self,coord_x,coord_y):
        self.coord_x=coord_x
        self.coord_y=coord_y
        # El objeto cruce tiene una lista de códigos de vía de las calles que pasan por él
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
        """Función que devuelve una lista de los códigos de vía de las calles que pasan por el cruce

        Args:
            cruces (pd.DataFrame): DataFrame de cruces
        Returns:
            list: lista con los códigos de vía de las calles que pasan por el cruce
        """
        return cruces[cruces["coordenadas"] == (self.coord_x, self.coord_y)]["Codigo de vía tratado"].unique()
    

class Calle:
    def __init__(self, ID):
        self.ID = ID
        # DataFrame de direcciones filtrado solo con las direcciones correspondientes a la calle
        self.direcciones = self.get_data(df_cruces, df_direcc)[1]
        # Lista de coordenadas de los cruces que pertenecen a la calle
        self.cruces = self.get_data(df_cruces, df_direcc)[0]

    def get_data(self, cruces: pd.DataFrame, direcciones: pd.DataFrame)-> tuple:
        """Función que busca los datos necesarios para los elementos self.direcciones y self.cruces

        Args:
            cruces (pd.DataFrame): DataFrame de cruces
            direcciones (pd.DataFrame): DataFrame de direcciones
        Returns:
            tuple: tupla cuyo primer elemento es la lista de coordenadas de los cruces que pertenecen a la calle
                   y cuyo segundo elemento es el DataFrame filtrado con las direcciones de la calle
        """
        return (cruces[cruces["Codigo de vía tratado"] == self.ID]["coordenadas"].unique(), direcciones[direcciones["Codigo de via"] == self.ID])

    def get_velocidad(self):
        """Función que busca cuál es la velocidad máxima legal de esa calle gracias a la clase de la vía

        Args: None
        Returns: velocidad máxima de la calle
        """
        if self.direcciones.empty or self.direcciones["Clase de la via"].iloc[0] not in VELOCIDADES_CALLES:
            return VELOCIDAD_CALLES_ESTANDAR
        else:
            return VELOCIDADES_CALLES[self.direcciones["Clase de la via"].iloc[0]]

    def ordenar_cruces(self):
        """Función que ordena los cruces de la calle, rehaciendo la lista self.cruces con las coordenadas
        en orden de aparición

        Args: None
        Returns: None
        """

        # Detecta la Av. De La Paz, única calle de la que no se ordenan los cruces ya que solamente hay una dirección
        # y tiene prefijo de numeración "KM.", por lo que no hay datos suficientes y daría error debido a las decisiones
        # tomadas a lo largo de la función sobre cómo tratar las direcciones con prefijo "KM."
        if len(self.direcciones.loc[self.direcciones["Prefijo de numeración"] != "KM."]) != 0:
            return
        
        cruces_ordenados = {}

        def funcion_aux(x: pd.DataFrame, cruce: tuple):
            """Función auxiliar que calcula la distancia entre la dirección de la calle y el cruce
            y lo introduce en el diccionario distancias si el prefijo de la dirección no es "KM."

            Args:
                x (pd.DataFrame): fila individual del DataFrame self.direcciones de la calle
                cruce (tuple): coordenadas del cruce que está siendo evaluado
            Returns: None
            """
            # Si el prefijo de numeración es "KM.", no se tiene en cuenta y el cruce se compara con las direcciones
            # con prefijo de numeración "NUM" pertenecientes a esa calle, para que el criterio sea viable en estas calles
            # con direcciones de ambos prefijos.
            if x['Prefijo de numeración'] == "KM.":
                pass
            else:
                distancias[dist(x["coordenadas"], cruce)] = x["Número"]

        # Para cada cruce, se calcula la distancia a cada dirección de la calle impar y se toma la distancia mínima,
        # asociando el cruce a ese número de dirección
        for cruce in self.cruces:
            try:
                distancias = {}
                self.direcciones.apply(lambda x: funcion_aux(x, cruce), axis=1)
                distancias = dict(sorted(distancias.items()))
                
                distancias_lista = list(distancias.keys())
                distancia_min = distancias_lista[0]
                num_dist_min = distancias[distancia_min]
                
                # Se busca el número de dirección más cercano que sea impar, para que estén todas en la misma acera
                while num_dist_min % 2 == 0:
                    distancias_lista.pop(0)
                    distancia_min = distancias_lista[0]
                    num_dist_min = distancias[distancia_min]

                # Si el número asociado al cruce no estaba ya en el diccionario, se añade
                if num_dist_min not in cruces_ordenados:
                    cruces_ordenados[num_dist_min] = cruce
                
                # Si ya estaba en el diccionario (hay un empate entre dos cruces), se compara con el el número anterior
                # de la misma acera, decidiendo así cuál va antes y cuál va después
                else:
                    num_anterior = num_dist_min - 2
                    num_siguiente = num_dist_min + 2
                    
                    # Resuelve, perdiendo precisión, el empate entre más de dos cruces, apenas existente en el callejero
                    while num_dist_min + 0.01 in cruces_ordenados:
                        num_dist_min += 0.01
                    
                    error = True
                    while error:
                        try:
                            coords_anterior = self.direcciones.loc[self.direcciones["Número"] == num_anterior]['coordenadas'].values[0]
                            cruce_anterior = cruces_ordenados[num_dist_min]

                            dist_cruce_actual = dist(cruce, coords_anterior)
                            dist_cruce_anterior = dist(cruce_anterior, coords_anterior)
                            
                            # Se suma 0.01 al número asociado al cruce que vaya después, para que no haya empates
                            if dist_cruce_actual < dist_cruce_anterior:
                                cruces_ordenados[num_dist_min + 0.01] = cruce_anterior
                                cruces_ordenados[num_dist_min] = cruce
                            else:
                                cruces_ordenados[num_dist_min + 0.01] = cruce
                            error = False

                        # Si hay un error, por ejemplo, si el empate es en el número 1 y se compara con el inexistente número -1,
                        # se prueba a comparar con el siguiente número de la misma acera
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
                            # Si hay un error por algún motivo, se prueba con dos números más
                            except:
                                num_siguiente += 2
                                # Se capa esta recursión para evitar un bucle infinito
                                if num_siguiente > 9999:
                                    cruces_ordenados[num_dist_min + 0.01] = cruce
                                    error = False                     
            except:
                continue
        
        # Se ordenan los cruces y se guardan en la lista de cruces de la calle como una lista de coordenadas
        cruces_ordenados = dict(sorted(cruces_ordenados.items()))
        cruces_ordenados = list(cruces_ordenados.values())
        self.cruces = cruces_ordenados

def filtrar_por_radios(R: int) -> list:
    """Función que filtra el DataFrame por radio, juntando todos los cruces que estén unidos entre ellos
    dentro de un radio R

    Args:
        R (int): radio por el que filtrar el DataFrame, en centímetros
    Returns:
        coordenadas_limpias (list[tuple]): lista de las nuevas coordenadas únicas entre todos los cruces
    """
    # Lista con todas las coordenadas únicas de los cruces del DataFrame de cruces
    coordenadas_a_tratar = sorted(df_cruces["coordenadas"].unique())
    coordenadas_limpias = []
    for coordenada in coordenadas_a_tratar:
        # Si alguna coordenada a tratar está dentro del radio de otra coordenada ya tratada, no se añade
        for x, y in coordenadas_limpias:
            if dist(coordenada, (x, y)) <= R:
                break
        else:
            coordenadas_limpias.append(coordenada)

    # Se sustituyen las coordenadas de los cruces del DataFrame de cruces por las coordenadas limpias
    df_cruces["coordenadas"] = df_cruces["coordenadas"].apply(lambda x: x if x in coordenadas_limpias else closest(x, coordenadas_limpias, R))
    return coordenadas_limpias

def dist(coordenada1: tuple, coordenada2:tuple) -> float:
    """Calcula la distancia euclídea entre dos puntos en un espacio de dos dimensiones

    Args:
        coordenada1, coordenada2 (tuple): coordenadas de dos puntos en el espacio
    Return:
        float: distancia euclídea entre la coordenada1 y la coordenada2
    """
    # Fórmula de la distancia euclídea en dos dimensiones
    return sqrt((coordenada1[0] - coordenada2[0])**2 + (coordenada1[1] - coordenada2[1])**2)

def closest(coordenada: tuple, coordenadas_limpias: list, R: int) -> tuple:
    """Para los cruces cuyas coordenadas no están dentro de coordenadas_limpias, busca cuáles son las coordenadas
    de esa lista que están a menos de una distancia R del cruce, y sustituye las coordenadas del cruce por esas

    Args:
        coordenada (tuple): coordenadas del cruce
        coordenadas_limpias (list[tuple]): lista de coordenadas únicas tras filtrar el DataFrame por radio
        R (int): radio por el que se están unificando los cruces en centímetros
    """
    coor_x, coor_y = coordenada[0], coordenada[1]
    # Busca cuál es la coordenada limpia que está dentro del radio R de la coordenada a tratar y se sustituye por ella
    for x, y in coordenadas_limpias:
        if (coor_x - R <= x <= coor_x + R) and (coor_y - R <= y <= coor_y + R):
            return (x, y)

def generar_grafos():
    """Función que, haciendo uso de todas las anteriores, genera dos grafos, uno tal que los pesos de las aristas
    sean las distancias de las aristas en el espacio, y otro cuyo peso sea el tiempo que un coche tarda en recorrerla

    Args: None
    Returns:
        grafo_d (grafo.Grafo): grafo de distancias que representa el callejero de Madrid
        grafo_t (grafo.Grafo): grafo de tiempos que representa el callejero de Madrid
        cruces (dict): diccionario con el formato {coordenada: Cruce} con todos los cruces de Madrid
        calles_dict (dict): diccionario con el formato {código de vía: Calle} con todas las calles de
                            Madrid que tengan cruces
    """
    # 2000 centímetros = 20 metros, se considera que un cruce está dentro del radio de otro si está a
    # menos de 20 metros de distancia según las observaciones
    coordenadas_limpias = filtrar_por_radios(2000)

    # Creamos los cruces
    cruces = {}
    for coordenada in coordenadas_limpias:
        cruces[coordenada] = Cruce(coordenada[0], coordenada[1])
    list_cruces:list[Cruce] = list(cruces.values())

    # Creamos las calles
    calles_dict = {}
    calles = []
    for cruce in list_cruces: # Escogemos los cruces
        for calle in cruce.calles: # Escogemos las calles de cada cruce
            if calle not in calles: # Si la calle no está en la lista de calles, la añadimos
                calles.append(calle)
                calles_dict[calle] = Calle(calle)
    calles = [Calle(calle) for calle in calles] # Creamos los objetos calle

    # Creamos el grafo  
    grafo_d = Grafo(False)
    grafo_t = Grafo(False)

    # Añadir vértices al grafo
    for cruce in list_cruces:
        grafo_d.agregar_vertice(cruce)
        grafo_t.agregar_vertice(cruce)

    # Para las aristas, se añaden las calles que conectan dos cruces como aristas del grafo
    for calle in calles:
        calle.ordenar_cruces()
        cruces_calle = calle.cruces
        for i in range(len(cruces_calle)):
            if i != len(cruces_calle) - 1:
                coords_actual, coords_siguiente = cruces_calle[i], cruces_calle[i+1]
                cruce_actual, cruce_siguiente = cruces[coords_actual], cruces[coords_siguiente]

                # Calculamos la distancia y el tiempo que se tarda en recorrer la arista
                distancia = dist(coords_actual, coords_siguiente)
                tiempo = ((distancia / 100000) / calle.get_velocidad()) * 60 # En minutos

                # Añadimos las aristas a cada grafo con su peso correspondiente
                grafo_d.agregar_arista(cruce_actual, cruce_siguiente, None, distancia)
                grafo_t.agregar_arista(cruce_actual, cruce_siguiente, None, tiempo)
    
    return grafo_d, grafo_t, cruces, calles_dict