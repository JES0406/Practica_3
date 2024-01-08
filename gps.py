# Importamos las librerías necesarias
from dgt import process_data
from grafo import Grafo
import networkx as nx
import matplotlib.pyplot as plt
import re

VELOCIDADES_CALLES={"AUTOVIA":100,"AVENIDA":90,"CARRETERA":70,"CALLEJON":30,"CAMINO":30,"ESTACION DE METRO":20,"PASADIZO":20,"PLAZUELA":20,"COLONIA":20}
VELOCIDAD_CALLES_ESTANDAR=50

# Procesamos los datos de cruces y direcciones para obtener los DataFrames definitivos
df_cruces, df_direcc = process_data("data/cruces.csv", "data/direcciones.csv")
# Creamos la expresión regular que nos permitirá interpretar las direcciones introducidas
regex_direcciones = r"([A-ZÁÉÍÓÚÜ]+)\s*(DEL|DE LA|DE LOS|DE LAS|DE)?\s+([A-ZÁÉÍÓÚÜ]-[0-9]+|[A-ZÁÉÍÓÚÜ\s]+),?\s+(NUM|KM)?\s*([0-9]+)([A-Z]{0,2})"

# Importamos las funciones necesarias del módulo callejero
from callejero import Cruce, generar_grafos, dist

def procesar_direccciones(direccion: str):
    """Toma una direccion y la interpreta, separando sus partes, buscando información de la calle y encontrando
    su cruce más cercano

    Args:
        direccion (str): dirección que se desea procesar
    Returns:
        cruce_mas_cercano (Cruce): objeto Cruce dentro de la lista de cruces de la calle de la dirección que esté
                                   más cerca de la dirección introducida
        tuple: coordenadas del cruce más cercano
        ID_calle (int): código de vía de la dirección
        coordenadas (tuple): coordenadas de la dirección
    """

    # Se reemplazan las tildes por vocales sin tilde
    direccion = direccion.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ü", "U")
    # Se usa la expresión regular para obtener datos de la dirección
    clase = re.search(regex_direcciones, direccion).group(1)
    nombre = re.search(regex_direcciones, direccion).group(3)
    numero = re.search(regex_direcciones, direccion).group(5)
    sufijo = re.search(regex_direcciones, direccion).group(6)

    # Filtramos el DataFrame para encontrar la dirección en cuestión
    df_direcc_filtrado = df_direcc[(df_direcc["Clase de la via"] == clase)]
    df_direcc_filtrado = df_direcc_filtrado[(df_direcc_filtrado["Nombre de la vía"] == nombre)]
    df_direcc_filtrado = df_direcc_filtrado[(df_direcc_filtrado["Número"] == int(numero))]
    if sufijo:
        df_direcc_filtrado = df_direcc_filtrado[(df_direcc_filtrado["Sufijo de numeración"] == sufijo)]
    
    # De la dirección nos quedamos con sus coordenadas y su código de vía
    coordenadas = df_direcc_filtrado["coordenadas"].unique()[0]
    ID_calle = df_direcc_filtrado["Codigo de via"].unique()[0]

    # Para cada cruce se hace la distancia con la dirección y se encuentra el cruce más cercano
    cruces_calle = calles_dict[ID_calle].cruces

    distancias = {}
    for cruce in cruces_calle:
        distancias[cruce] = dist(coordenadas, cruce)
    distancias = dict(sorted(distancias.items(), key=lambda x: x[1]))
    distancias = list(distancias.keys())
    cruce_mas_cercano = cruces[distancias[0]]

    return cruce_mas_cercano, distancias[0], ID_calle, coordenadas

def hay_giro(cruce_actual: Cruce, cruce_siguiente2: Cruce) -> bool:
    """Determina si, después de recorrer la arista actual, hay que girar a otra calle o hay que continuar

    Args:
        cruce_actual (Cruce): Primer cruce de la arista actual
        cruce_siguiente2 (Cruce): Cruce último de la siguiente arista a recorrer
    Returns:
        bool: True si hay que girar, False si hay que seguir avanzando por la calle actual
    """
    # Si el cruce actual tiene una calle en común con el cruce siguiente del cruce siguiente, no hay giro
    # Mientras se avance por una calle todos los cruces tendrán en común esa calle
    for calle in cruce_actual.calles:
        if calle in cruce_siguiente2.calles:
            return False
    return True

def calle_actual(cruce_actual:Cruce, cruce_siguiente:Cruce, df_cruces=df_cruces):
    """Determina cuál es la calle que se está recorriendo en la arista actual del camino

    Args:
        cruce_actual (Cruce): primer cruce de la arista actual
        cruce_siguiente (Cruce): último (segundo) cruce de la arista actual
        df_cruces (pd.DataFrame): DataFrame de cruces
    Returns:
        clase (string): Clase de la vía actual (CALLE, AVENIDA, AUTOVÍA, etc.)
        particula (string): Partícula de la vía actual (DE, DE LA, DE LOS, DEL, DE LAS o None)
        calle (string): Nombre de la vía actual (ALBERTO AGUILERA, AMERICA, etc.)
    """
    for calle in cruce_actual.calles:
        if calle in cruce_siguiente.calles:
            clase = df_cruces[df_cruces["Codigo de vía tratado"] == calle].iloc[0]["Clase de la via tratado"]
            particula = df_cruces[df_cruces["Codigo de vía tratado"] == calle].iloc[0]["Particula de la via tratado"]
            calle = df_cruces[df_cruces["Codigo de vía tratado"] == calle].iloc[0]["Nombre de la via tratado"]

            return clase, particula, calle

def hay_giro_origen_destino(cruce:Cruce, ID: int) -> bool:
    """Misma función que hay_giro pero para los casos especiales de si hay o no que girar cuando vas del origen
    al primer cruce del camino, o del último cruce a la dirección de destino

    Args:
        cruce (Cruce): cruce último de la primera arista del camino, o primer cruce de la última arista
        ID (int): código de vía del origen o del destino
    Returns:
        bool: True si hay que girar, False si hay que seguir avanzando por la calle anterior
    """
    # El cruce es el cruce siguiente al cruce más cercano del origen, siguiendo el mismo método
    # que en la función hay_giro pero con las coordenadas de la dirección de origen o de destino
    for calle in cruce.calles:
        if calle == ID:
            return False
    return True

def calle_origen_destino(ID: int):
    """Misma función que calle_actual, pero para la dirección de destino y de origen

    Args:
        ID (int): código de vía de la calle de origen o de destino
    Returns:
        clase (string): Clase de la vía actual (CALLE, AVENIDA, AUTOVÍA, etc.)
        particula (string): Partícula de la vía actual (DE, DE LA, DE LOS, DEL, DE LAS o None)
        calle (string): Nombre de la vía actual (ALBERTO AGUILERA, AMERICA, etc.)
    """
    # Se obtiene la clase, la partícula y el nombre de la calle de la dirección de origen o de destino
    clase = df_cruces[df_cruces["Codigo de vía tratado"] == ID].iloc[0]["Clase de la via tratado"]
    particula = df_cruces[df_cruces["Codigo de vía tratado"] == ID].iloc[0]["Particula de la via tratado"]
    calle = df_cruces[df_cruces["Codigo de vía tratado"] == ID].iloc[0]["Nombre de la via tratado"]
    return clase, particula, calle

def tipo_de_giro(p1: tuple, p2: tuple, p3: tuple) -> str:
    """Determina, mediante el signo del producto vectorial, si los vectores que se generan mediante unir
    un punto 1 con un punto 2, y ese punto 2 con un punto 3, producen un giro hacia la derecha o izquierda

    Args:
        p1, p2, p3 (tuple): coordenadas en un espacio de dos dimensiones
    Return:
        giro (string): "izquierda" si el giro es hacia la izquierda, "derecho" para giro hacia la derecha
    """
    # Se generan dos vectores equivalentes al vector de la arista que se recorre actualmente y la siguiente
    v1 = (p2[0]-p1[0], p2[1]-p1[1])
    v2 = (p3[0]-p2[0], p3[1]-p2[1])
    
    producto_vectorial = v1[0] * v2[1] - v1[1] * v2[0]
    # Se determina si el giro es a la derecha o a la izquierda en función del signo del producto vectorial
    if producto_vectorial > 0:
        giro = "izquierda"
    else:
        giro = "derecha"
    return giro

def instrucciones(camino: list, coord_o: tuple, coord_d: tuple, ID_origen: int, ID_destino: int):
    """Imprime en la terminal instrucciones detalladas sobre como ir desde la dirección de origen hasta
    la dirección de destino

    Args:
        camino (list[Cruce]): camino mínimo entre un cruce de origen y otro de destino
        coord_o (tuple): coordenadas de la dirección de origen
        coord_d (tuple): coordenadas de la dirección de destino
        ID_origen (int): código de vía de la dirección de origen
        ID_destino (int): código de vía de la dirección de destino
    Returns: None
    """
    # Para cada arista se calcula la distancia que se recorre y se determina si hay giro o no.
    # Si no hay giro, se sigue avanzando por la misma calle y se acumulan las distancias.
    # Si hay giro, se calcula el tipo de giro y se imprimen las instrucciones. Se reinicia la distancia

    # Se marginalizan los casos del origen al primer cruce y del último cruce al destino
    cruce_actual = camino[0]
    cruce_siguiente = camino[1]
    coords_actual = (cruce_actual.coord_x, cruce_actual.coord_y)
    coords_siguiente = (cruce_siguiente.coord_x, cruce_siguiente.coord_y)
    distancia = dist(coord_o, coords_actual)
    clase, particula, calle = calle_origen_destino(ID_origen)
    clase_2, particula_2, calle_2 = calle_actual(cruce_actual, cruce_siguiente)
    
    if hay_giro_origen_destino(cruce_siguiente, ID_origen):
        giro = tipo_de_giro(coord_o, coords_actual, coords_siguiente)
        if particula:
            print(f"Avanza {round(distancia)/100} metros por {clase} {particula} {calle}")
            print(f"Gira a la {giro} hacia {clase_2} {particula_2} {calle_2}")
        else:
            print(f"Avanza {round(distancia)/100} metros por {clase} {calle}")
            print(f"Gira a la {giro} hacia {clase_2} {calle_2}")

    # Iteramos el camino calculando las instrucciones
    for i in range(len(camino)-2):
        cruce_actual = camino[i]
        cruce_siguiente = camino[i+1]
        cruce_siguiente2 = camino[i+2]
        
        coords_0 = (cruce_actual.coord_x, cruce_actual.coord_y)
        coords_1 = (cruce_siguiente.coord_x, cruce_siguiente.coord_y)
        coords_2 = (cruce_siguiente2.coord_x, cruce_siguiente2.coord_y)
        distancia += dist(coords_0, coords_1)
        
        if hay_giro(cruce_actual, cruce_siguiente2):
            clase, particula, calle = calle_actual(cruce_actual, cruce_siguiente)
            clase_2, particula_2, calle_2 = calle_actual(cruce_siguiente, cruce_siguiente2)
            giro = tipo_de_giro(coords_0, coords_1, coords_2)
            if particula:
                print(f"Avanza {round(distancia)/100} metros por {clase} {particula} {calle}")
                print(f"Gira a la {giro} hacia {clase_2} {particula_2} {calle_2}")
            else:
                print(f"Avanza {round(distancia)/100} metros por {clase} {calle}")
                print(f"Gira a la {giro} hacia {clase_2} {calle_2}")
            distancia = 0

    # Se marginaliza la última arista ya que no existe el cruce siguiente del cruce siguiente.
    cruce_penultimo = camino[-2]
    cruce_ultimo = camino[-1]
    coords_penultimo = (cruce_penultimo.coord_x, cruce_penultimo.coord_y)
    coords_ultimo = (cruce_ultimo.coord_x, cruce_ultimo.coord_y)
    distancia += dist(coords_penultimo, coords_ultimo)
    clase, particula, calle = calle_actual(cruce_penultimo, cruce_ultimo)
    clase_2, particula_2, calle_2 = calle_origen_destino(ID_destino)

    if hay_giro_origen_destino(cruce_penultimo, ID_destino):
        giro = tipo_de_giro(coords_penultimo, coords_ultimo, coord_d)
        if particula:
            print(f"Avanza {round(distancia)/100} metros por {clase} {particula} {calle}")
            print(f"Gira a la {giro} hacia {clase_2} {particula_2} {calle_2}")
        else:
            print(f"Avanza {round(distancia)/100} metros por {clase} {calle}")
            print(f"Gira a la {giro} hacia {clase_2} {calle_2}")
    
    distancia += dist(coords_ultimo, coord_d)
    print(f"Avanza {round(distancia)/100} metros por {clase_2} {particula_2} {calle_2}")

    print("\nHa llegado a su destino.\n")

def generar_edgelist(camino: list) -> list:
    """Convierte el camino al formato correcto para ser representado en el grafo

    Args:
        camino (list): camino entre dos vértices en formato [v1, v2, v3, ..., vn]
    Returns:
        aristas (list[tuple]): lista del formato [(cruce1, cruce2), (cruce2, cruce3),..., (crucen-1, crucen)]
    """
    # Esto es necesario ya que el argumento 'edgelist' de la función nx.draw_networkx_edges requiere
    # una lista de tuplas de aristas, y el camino generado por 'camino_minimo' es una lista de vértices.
    aristas = []
    for i in range(len(camino)-1):
        aristas.append((camino[i], camino[i+1]))
    return aristas

def mostrar_ruta(grafo:Grafo, camino_min_aristas:list):
    """Representa el grafo en NetworkX, con el camino mínimo entre las dos direcciones resaltado en rojo

    Args:
        grafo (grafo.Grafo): grafo a representar
        camino_min_aristas (list[tuple]): camino a resaltar encima del grafo
    """
    G = grafo.convertir_a_NetworkX()

    # Diccionario de posiciones para colocar correctamente los cruces en el espacio al dibujar el grafo.
    pos = {}
    for cruce in grafo.lista_vertices():
        pos[cruce] = (cruce.coord_x, cruce.coord_y)

    # Se dibuja el grafo
    nx.draw_networkx_nodes(G, pos=pos, node_size=1)
    nx.draw_networkx_edges(G, pos=pos, width=0.5, edge_color="black")
    # Se dibuja el camino mínimo en rojo, ligeramente más grueso para remarcarlo mejor.
    nx.draw_networkx_edges(G, pos=pos, arrows=True, edgelist=camino_min_aristas, edge_color='r', width=2.0)
    # Mostramos el grafo
    plt.show()


if __name__ == "__main__":

    # Generamos ambos grafos y los diccionarios de cruces y calles, útiles para otros procesos
    grafo_d, grafo_t, cruces, calles_dict = generar_grafos()

    # Bucle para poder introducir direcciones indefinidamente hasta que se indique la salida
    while True:
        error = True
        while error:
            origen = input("DIRECCIÓN DE ORIGEN: ").upper()
            destino = input("DIRECCIÓN DE DESTINO: ").upper()
            if origen == "" or destino == "":
                break
            # Try y except para comprobar que las direcciones introducidas existen
            try:
                cruce_origen, coordenadas_origen, ID_origen, coord_o = procesar_direccciones(origen)
            except:
                # Control de errores para que el programa no se cierre si se introduce una dirección incorrecta
                print("ERROR: La dirección de origen es incorrecta o no existe.\n")
                continue
            try:
                cruce_destino, coordenadas_destino, ID_destino, coord_d = procesar_direccciones(destino)
            except:
                print("ERROR: La dirección de destino es incorrecta o no existe.\n")
                continue
            
            if coord_o == coord_d:
                print("ERROR: La dirección de origen y la dirección de destino son la misma.\n")
                continue

            # Si ambas direcciones son correctas, se sale del bucle que pide direcciones hasta que se introduzcan
            # direcciones válidas o se indique la salida
            if cruce_origen and cruce_destino:
                error = False
            else:
                print("ERROR: Alguna dirección es incorrecta.\n")
                
        # Como hay dos bucles anidados, vuelve a hacer un break si alguna dirección es vacía para cerrar el programa
        if origen == "" or destino == "":
            break

        # Bucle que pide el tipo de grafo a usar hasta que se introduzca un tipo válido
        error = True
        while error:
            modo = input("¿ENCONTRAR RUTA MÁS CORTA O RUTA MÁS RÁPIDA?\nEscribe '1' para ruta más corta, '2' para ruta más rápida: ")
            print("\n")
            if modo == '1':
                grafo = grafo_d
                error = False
            elif modo == '2':
                grafo = grafo_t
                error = False
            else:
                print("ERROR: Seleccione un modo correcto.\n")

        # Camino mínimo entre el cruce origen y el cruce destino haciendo uso del algoritmo de Dijkstra
        camino_min = grafo.camino_minimo(cruce_origen, cruce_destino)
        camino_min_aristas = generar_edgelist(camino_min)
        # Se imprimen las instrucciones en la terminal
        instrucciones(camino_min, coord_o, coord_d, ID_origen, ID_destino)
        # Se muestra el grafo con el camino mínimo en rojo
        mostrar_ruta(grafo, camino_min_aristas)