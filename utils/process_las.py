import laspy
import os
import numpy as np

# Cargar el archivo .las
input_file = "./37AZ1_20.las"  # Coloca aquí la ruta de tu archivo
output_file = "./archivo_filtrado.las"  # Ruta para el nuevo archivo filtrado

# Abrir archivo .las
las = laspy.read(input_file)

# Filtrar puntos por altura (modifica el umbral según tus necesidades)
# Por ejemplo, elimina puntos con altura (z) menor a un cierto valor
umbral_altura = 2.0  # Ajusta este valor según el terreno y características de tus datos
filtered_points = las.points[las.z > umbral_altura]

# Crear un nuevo archivo .las con los puntos filtrados
header = las.header  # Obtener el encabezado original
filtered_las = laspy.create(point_format=las.point_format, file_version=las.header.version)
filtered_las.points = filtered_points  # Guardar los puntos filtrados
filtered_las.write(output_file)

print("Archivo filtrado guardado exitosamente en:", output_file)

def dividir_nube_las(input_file, output_dir, num_partes):
    # Abrir el archivo LAS para obtener la cantidad de puntos y el header original
    archivo_las = laspy.read(input_file)
    total_puntos = archivo_las.header.point_count
    header_original = archivo_las.header  # Guardar el header original
    
    # Calcular cuántos puntos por parte
    puntos_por_parte = total_puntos // num_partes

    # Leer todos los puntos
    puntos = archivo_las.points

    # Dividir y guardar las partes
    for i in range(num_partes):
        inicio = i * puntos_por_parte
        fin = inicio + puntos_por_parte if i < num_partes - 1 else total_puntos
        puntos_divididos = puntos[inicio:fin]
        
        # Crear nuevo header para la parte dividida, copiando el original
        header_nuevo = laspy.LasHeader(point_format=archivo_las.header.point_format, version=archivo_las.header.version)
        header_nuevo.offsets = header_original.offsets  # Mantener el offset original
        header_nuevo.scales = header_original.scales    # Mantener el scale factor original
        
        # Crear nuevo archivo LAS
        archivo_las_dividido = laspy.LasData(header_nuevo)
        archivo_las_dividido.points = puntos_divididos
        
        # Guardar el archivo dividido
        output_file = os.path.join(output_dir, f"parte_{i + 1}.las")
        archivo_las_dividido.write(output_file)
        print(f"Parte {i + 1} guardada en {output_file}")

def las_a_txt(input_dir, output_dir):
    # Obtener lista de archivos LAS en el directorio de entrada
    archivos_las = [f for f in os.listdir(input_dir) if f.endswith(".las")]

    # Inicializar contador para los nombres de los archivos
    contador = 1

    # Procesar cada archivo LAS
    for archivo in archivos_las:
        input_path = os.path.join(input_dir, archivo)

        # Leer el archivo LAS
        with laspy.open(input_path) as archivo_las:
            points = archivo_las.read().points
            coords = np.vstack((points.X, points.Y, points.Z)).T
            rgb = np.vstack((points.red, points.green, points.blue)).T
            escalar = points.user_data  # Suponiendo que el escalar está en 'user_data'

        # Combinar las columnas XYZ, RGB y el escalar
        datos_combinados = np.hstack((coords, rgb, escalar.reshape(-1, 1)))

        # Formatear el nombre del archivo en "CC_000001.txt" y continuar el conteo
        output_file = os.path.join(output_dir, f"CC_{contador:06d}.txt")
        np.savetxt(output_file, datos_combinados, fmt="%.6f %.6f %.6f %d %d %d %.6f", delimiter=" ")

        print(f"Guardado archivo: {output_file}")
        contador += 1  # Incrementar el contador para el siguiente archivo

# Divisiones de archivo las:
input_file = "./archivo_filtrado.las"
output_dir = "./nube_separada/"
num_partes = 1000

dividir_nube_las(input_file, output_dir, num_partes)

# :
input_dir = "./nube_separada/"  # Directorio donde están los archivos .las
output_dir = "./nube_en_txt/"  # Directorio de salida para los archivos .txt

las_a_txt(input_dir, output_dir)
