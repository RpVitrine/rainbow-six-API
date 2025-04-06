import tkinter as tk
from threading import Thread
import api
import database_data


def start_fetching():
    def progress_callback(processed, total):
        progress_var.set(f"Operadores processados: {processed}/{total}")

    # Chama a função de coleta de dados passando o callback
    database_data.main_database_data(callback=progress_callback)
    progress_var.set("Processamento concluído!")


def start_api():
    progress_var.set(f"API INICIADA")
    api.main_api()


def fetch_thread():
    Thread(target=start_fetching).start()


def api_thread():
    Thread(target=start_api).start()


root = tk.Tk()
root.title("Seleção de Operação")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

progress_var = tk.StringVar()
progress_var.set("Nenhum operador processado ainda.")

progress_label = tk.Label(frame, textvariable=progress_var)
progress_label.pack(pady=(0, 10))

fetch_button = tk.Button(frame, text="Buscar Dados", command=fetch_thread)
fetch_button.pack(side="left", padx=10)

api_button = tk.Button(frame, text="Iniciar API", command=api_thread)
api_button.pack(side="right", padx=10)

root.mainloop()