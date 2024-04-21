import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import requests
import pandas as pd
import os
import ctypes

class MercadoLibreAPI:
    def __init__(self, pais='MLA'):
        self.pais = pais
        self.api_base = f'https://api.mercadolibre.com/sites/{pais}/search?limit=50'
        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}

    def fetch_results(self, item, condition, offset, price_min=None, price_max=None):
        try:
            if price_min is not None and price_min != "":
                price_min = float(price_min)
            else:
                price_min = 0
            if price_max is not None and price_max != "":
                price_max = float(price_max)
            else:
                price_max = 9999999999
        except ValueError:
            price_min = 0
            price_max = 9999999999


        price_range = f"&price={price_min}-{price_max}"

        api = f'{self.api_base}&q={item}&condition={condition}&offset={offset}{price_range}'
        response = requests.get(api, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()['results']
        else:
            print(f"Error al obtener resultados: {response.status_code}")
            return []

    def process_results(self, results_list):
        processed_results = []
        for elem in results_list:
            result_dict = {
                'title': elem['title'],
                'price': elem['price'],
                'condition': elem['condition'],
                'url': elem['permalink']
            }
            processed_results.append(result_dict)
        return processed_results

class WindowScaler:
    @staticmethod
    def set_app_dpi_awareness():
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # consciente de la configuración de DPI de la pantalla en la que se está ejecutando
        except AttributeError:
            ctypes.windll.user32.SetProcessDPIAware()  # para versiones anteriores de windows

    @staticmethod
    def adjust_window_scale(master):
        try:
            ctypes.windll.shcore.SetProcessDpiAwarenessContext(2)  # consciente de la configuración de DPI de la pantalla en la que se está ejecutando
        except AttributeError:
            pass  # Versiones anteriores de Windows, el escalado se maneja automáticamente

        master.tk.call('tk', 'scaling', 1.25)

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("MercadoLibre Search")
        master.geometry("460x910")
        master.resizable(False, False)
        
        # Llama a la función para ajustar la DPI de la aplicación
        WindowScaler.set_app_dpi_awareness()

        # Escalar la ventana después de crear todos los elementos
        WindowScaler.adjust_window_scale(master)


        #Rutas de imagenes
        directorio_actual = os.getcwd()
        BG = r'img\ml.png'
        ruta_archivo_b = os.path.join(directorio_actual, BG)
        self.bg_image=tk.PhotoImage(file= ruta_archivo_b)
        
        texto_predeterminado = tk.StringVar(value="🔍Producto")
        texto_predeterminado_minimo = tk.StringVar(value="$Mínimo")
        texto_predeterminado_maximo = tk.StringVar(value="$Máximo")

        # Crear un label para la imagen de fondo
        self.bg_label = tk.Label(master, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)    


        self.entry_product = tk.Entry(master,textvariable= texto_predeterminado, border=0, width=45, font=("Segoe UI Semibold", 11))
        self.entry_product.pack()
        self.entry_product.place(x=35, y=440)
        self.entry_product.config(fg='#BDBFC1')


        self.entry_price_min = tk.Entry(master, textvariable=texto_predeterminado_minimo, border=0, width=15, font=("Segoe UI Semibold", 11))
        self.entry_price_min.pack()
        self.entry_price_min.place(x=120, y=495)
        self.entry_price_min.config(fg='#BDBFC1')


        self.entry_price_max = tk.Entry(master, textvariable=texto_predeterminado_maximo, border=0,width=15, font=("Segoe UI Semibold", 11))
        self.entry_price_max.pack()
        self.entry_price_max.place(x=120, y=550)
        self.entry_price_max.config(fg='#BDBFC1')
    
        def change_cursor(event):
            self.button.configure(cursor="hand2")
      
        self.button = ttk.Button(master,style="NoBorder.TButton", text="🔍 Buscar", command=self.search_product, width=65)
        self.button.pack()
        self.button.place(x=30, y=590, height=40)
        self.button.bind("<Enter>", change_cursor)
        #self.button.bind("<Enter>", self.on_enter)
        #self.button.bind("<Leave>", self.on_leave)

    def search_product(self):
        product_name = self.entry_product.get().strip()
        price_min = self.entry_price_min.get().strip()
        price_max = self.entry_price_max.get().strip()

        if not product_name:
            messagebox.showwarning("Advertencia", "Ingrese un producto")
            return

        ml_api = MercadoLibreAPI()

        # Verificar si los precios mínimos y máximos están vacíos y asignar None en su lugar
        #if not price_min:
            #price_min = None
        #if not price_max:
            #price_max = None

        # Realizar la primera solicitud para obtener la cantidad total de resultados y la primera página de productos nuevos
        offset = 0
        new_results = ml_api.fetch_results(product_name, 'new', offset, price_min, price_max)
        total_new_results = len(new_results)

        # Procesar los resultados de productos nuevos de la primera página
        processed_new_results = ml_api.process_results(new_results)
        df_new = pd.DataFrame(processed_new_results)

        # Obtener el resto de los resultados de productos nuevos utilizando la paginación
        while offset + 50 < total_new_results:
            offset += 50
            next_page_new_results = ml_api.fetch_results(product_name, 'new', offset, price_min, price_max)
            processed_new_results = ml_api.process_results(next_page_new_results)
            df_new = df_new.append(pd.DataFrame(processed_new_results), ignore_index=True)

        # Realizar la solicitud para obtener la primera página de productos usados
        offset = 0
        used_results = ml_api.fetch_results(product_name, 'used', offset, price_min, price_max)
        total_used_results = len(used_results)

        # Procesar los resultados de productos usados de la primera página
        processed_used_results = ml_api.process_results(used_results)
        df_used = pd.DataFrame(processed_used_results)

        # Obtener el resto de los resultados de productos usados utilizando la paginación
        while offset + 50 < total_used_results:
            offset += 50
            next_page_used_results = ml_api.fetch_results(product_name, 'used', offset, price_min, price_max)
            processed_used_results = ml_api.process_results(next_page_used_results)
            df_used = df_used.append(pd.DataFrame(processed_used_results), ignore_index=True)

        # Concatenar los DataFrames de productos nuevos y usados
        df = pd.concat([df_new, df_used], ignore_index=True)

        # Ordenar el DataFrame por precio ascendente
        df_sorted = df.sort_values(by='price', ascending=True)

        # Exportar a Excel
        filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], title="Guardar como...")
        if filename:
            df_sorted.to_excel(filename, index=False)
            messagebox.showinfo("Éxito", "Resultados exportados a Excel correctamente")

    def on_enter(self, event):
        self.button.config(bg="#CCCCCC", cursor="hand2")

    def on_leave(self, event):
        self.button.config(bg="White", cursor="hand2")

def main():
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

