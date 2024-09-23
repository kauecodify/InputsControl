import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
import datetime

class GastosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InputsControl")

        self.gastos = defaultdict(lambda: defaultdict(float))

        self.label_data = tk.Label(root, text="Data (YYYY-MM-DD):")
        self.label_data.pack()
        self.entry_data = tk.Entry(root)
        self.entry_data.pack()

        self.label_gasto = tk.Label(root, text="Valor do Insumo:")
        self.label_gasto.pack()
        self.entry_gasto = tk.Entry(root)
        self.entry_gasto.pack()

        self.btn_adicionar = tk.Button(root, text="Adicionar Gasto", command=self.adicionar_gasto)
        self.btn_adicionar.pack()

        self.btn_consultar = tk.Button(root, text="Consultar Gastos", command=self.consultar_gastos)
        self.btn_consultar.pack()

    def adicionar_gasto(self):
        data_str = self.entry_data.get()
        valor_str = self.entry_gasto.get()

        try:
            data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
            semestre = 1 if data.month <= 6 else 2
            ano = data.year
            valor = float(valor_str)

            self.gastos[ano][semestre] += valor

            messagebox.showinfo("Sucesso", "Gasto adicionado com sucesso!")
            self.entry_data.delete(0, tk.END)
            self.entry_gasto.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erro", "Data ou valor inválido. Tente novamente.")

    def consultar_gastos(self):
        resultado = ""
        for ano, semestres in self.gastos.items():
            resultado += f"Ano: {ano}\n"
            for semestre, total in semestres.items():
                resultado += f"  Semestre {semestre}: R$ {total:.2f}\n"
        
        if not resultado:
            resultado = "Nenhum gasto registrado."

        messagebox.showinfo("Consulta de Gastos", resultado)

if __name__ == "__main__":
    root = tk.Tk()
    app = GastosApp(root)
    root.mainloop()
