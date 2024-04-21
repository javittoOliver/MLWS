El script despliega una ventana emergente, interface construída con tkinter. Donde se puede tipear el nombre de un producto, y un rango de precios.
El botón acciona la busqueda con éstos parámetros en Mercadolibre, a través de su Api con un límite de 100 resultados. Concatenando productos nuevos y usados y 
la url de cada publicación. Luego abre windows explorer para que se elija el nombre y ruta del archivo con la lista de productos en excel.

Debe descargarse la imagen ml.png y guardarse en la misma carpeta que el script para que funcione.
Está construído integramente con soporte de GPT.

Python 3.9.13
Librerias necesarias:

pip intall pandas
pip install requests
