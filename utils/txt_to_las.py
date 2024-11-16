import laspy
import numpy as np
import os

# Data Join in one txt file
def onefile(carpeta_origen, archivo_salida):
    # Crear o vaciar el archivo de salida
    with open(archivo_salida, 'w') as f_salida:
       # pass  # Simplemente se abre en modo 'w' para vaciar el contenido si existe

        # Procesar cada archivo en la carpeta de origen
        for archivo in os.listdir(carpeta_origen):
            if archivo.endswith(".txt"):
                ruta_archivo = os.path.join(carpeta_origen, archivo)
            
                with open(ruta_archivo, 'r') as f_entrada:
                    for linea in f_entrada:
                        columnas = linea.split()
                    
                        # Formatear la cuarta columna a seis decimales
                        cuarto_valor = float(columnas[3])
                        cuarto_formateado = f"{cuarto_valor:.6f}"
                    
                        # Asignar valores RGB según el valor en la cuarta columna
                        if cuarto_valor == 0:
                            rgb = "0 255 0"
                        elif cuarto_valor == 1:
                            rgb = "0 0 255"
                        else:
                            rgb = "255 0 0"
                    
                        # Crear la línea de salida y escribirla en el archivo
                        linea_salida = f"{columnas[0]} {columnas[1]} {columnas[2]} {rgb} {cuarto_formateado}\n"
                        f_salida.write(linea_salida)

    print(f"Todos los archivos se han procesado y combinado en {archivo_salida}")

carpeta_origen = "../runs/shapenet.pvcnn.c0p5/segmented_outputs"

    # Ruta del archivo de salida combinado
archivo_salida = "../segmented_file/segmented_file.txt"

#onefile(carpeta_origen, archivo_salida)

def txt_a_las(input_txt, output_las):
    # Cargar los datos del archivo .txt
    puntos = np.loadtxt(input_txt, delimiter=' ')  # Cambia el delimitador si es necesario
    
    # Crear un header para el archivo .LAS
    header = laspy.LasHeader(point_format=8, version="1.4")
    
    # Configurar el bounding box basado en los datos
    header.x_scale = header.y_scale = header.z_scale = 0.001  # Precisión del archivo LAS
    header.x_offset = np.min(puntos[:, 0])
    header.y_offset = np.min(puntos[:, 1])
    header.z_offset = np.min(puntos[:, 2])
    
    # Crear el archivo .LAS con el header
    las = laspy.LasData(header)
    
    # Asignar los puntos XYZ
    las.x = puntos[:, 0]
    las.y = puntos[:, 1]
    las.z = puntos[:, 2]
    
    # Asignar los valores de color RGB
    las.red = puntos[:, 3].astype(np.uint16)   # Los valores RGB deben ser enteros de 16 bits
    las.green = puntos[:, 4].astype(np.uint16)
    las.blue = puntos[:, 5].astype(np.uint16)
   
    # Definir condiciones y valores correspondientes
    condiciones = [
        (puntos[:, 6] == 1),  
        (puntos[:, 6] == 0)   
    ]
    valores = [
        14,  
        1    
    ]
    
    default_value = 30
    # Asignar clasificación aplicando las condiciones
    las.classification = np.select(condiciones, valores, default=default_value).astype(np.uint8)    # mapped to standar classification

    # Guardar el archivo como .LAS o .LAZ
    las.write(output_las)
    print(f"Archivo convertido y guardado en: {output_las}")


# Ejemplo de uso:
input_txt = "../segmented_file/segmented_file.txt"  # Ruta al archivo .txt
output_las = "../segmented_file/segmented_file.las"  # Ruta de salida para el archivo .LAS

txt_a_las(input_txt, output_las)

def filter(input_las):
    las = laspy.read(input_las)

    umbral_altura = 2000.0

    new_file = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    new_file.points = las.points[(las.z > umbral_altura) & (las.classification == 14)]

    new_file.write('../segmented_file/cables.las')

    print(f"El archivo ha sido filtrado exitosamente")

input_las = output_las

filter(input_las)