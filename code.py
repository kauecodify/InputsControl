import tkinter as tk
from tkinter import messagebox, ttk
from collections import defaultdict
import datetime
import sqlite3
import hashlib
import csv
from matplotlib import pyplot as plt

class GastosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InputsControl")

        # bd sqlite
        self.conn = sqlite3.connect("gastos.db")
        self.create_tables()

        # log
        self.login_frame = ttk.Frame(root)
        self.login_frame.pack(pady=10)

        ttk.Label(self.login_frame, text="Usuário:").grid(row=0, column=0)
        self.entry_usuario = ttk.Entry(self.login_frame)
        self.entry_usuario.grid(row=0, column=1, padx=5)

        ttk.Label(self.login_frame, text="Senha:").grid(row=1, column=0)
        self.entry_senha = ttk.Entry(self.login_frame, show="*")
        self.entry_senha.grid(row=1, column=1, padx=5)

        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, columnspan=2, pady=5)
        ttk.Button(self.login_frame, text="Registrar", command=self.registrar).grid(row=3, columnspan=2)

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL,
                ano INTEGER NOT NULL,
                semestre INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                valor REAL NOT NULL
            )
        ''')
        self.conn.commit()

    def hash_password(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def login(self):
        usuario = self.entry_usuario.get()
        senha = self.hash_password(self.entry_senha.get())

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
        user = cursor.fetchone()

        if user:
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            self.login_frame.pack_forget()
            self.setup_gastos_interface(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos.")

    def registrar(self):
        usuario = self.entry_usuario.get()
        senha = self.hash_password(self.entry_senha.get())

        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Usuário registrado com sucesso!")
            self.entry_usuario.delete(0, tk.END)
            self.entry_senha.delete(0, tk.END)
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Usuário já existe.")

    def setup_gastos_interface(self, usuario):
        self.usuario = usuario
        self.gastos_frame = ttk.Frame(self.root)
        self.gastos_frame.pack(pady=10)

        ttk.Label(self.gastos_frame, text="Data (YYYY-MM-DD):").pack()
        self.entry_data = ttk.Entry(self.gastos_frame)
        self.entry_data.pack()

        ttk.Label(self.gastos_frame, text="Valor do Insumo:").pack()
        self.entry_gasto = ttk.Entry(self.gastos_frame)
        self.entry_gasto.pack()

        ttk.Label(self.gastos_frame, text="Categoria:").pack()
        self.entry_categoria = ttk.Entry(self.gastos_frame)
        self.entry_categoria.pack()

        ttk.Button(self.gastos_frame, text="Adicionar Gasto", command=self.adicionar_gasto).pack(pady=5)
        ttk.Button(self.gastos_frame, text="Consultar Gastos", command=self.consultar_gastos).pack(pady=5)
        ttk.Button(self.gastos_frame, text="Exportar Gastos", command=self.exportar_gastos).pack(pady=5)
        ttk.Button(self.gastos_frame, text="Exibir Gráfico", command=self.exibir_grafico).pack(pady=5)

    def adicionar_gasto(self):
        data_str = self.entry_data.get()
        valor_str = self.entry_gasto.get()
        categoria = self.entry_categoria.get()

        try:
            data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
            semestre = 1 if data.month <= 6 else 2
            ano = data.year
            valor = float(valor_str)

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO gastos (usuario, ano, semestre, categoria, valor) VALUES (?, ?, ?, ?, ?)",
                           (self.usuario, ano, semestre, categoria, valor))
            self.conn.commit()

            messagebox.showinfo("Sucesso", "Gasto adicionado com sucesso!")
            self.entry_data.delete(0, tk.END)
            self.entry_gasto.delete(0, tk.END)
            self.entry_categoria.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erro", "Data, valor ou categoria inválida. Tente novamente.")

    def consultar_gastos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ano, semestre, categoria, SUM(valor) FROM gastos WHERE usuario=? GROUP BY ano, semestre, categoria", (self.usuario,))
        resultados = cursor.fetchall()

        resultado = ""
        for ano, semestre, categoria, total in resultados:
            resultado += f"Ano: {ano}, Semestre: {semestre}, Categoria: {categoria}, Total: R$ {total:.2f}\n"

        if not resultado:
            resultado = "Nenhum gasto registrado."

        messagebox.showinfo("Consulta de Gastos", resultado)

    def exportar_gastos(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM gastos WHERE usuario=?", (self.usuario,))
        resultados = cursor.fetchall()

        with open("gastos.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Usuário", "Ano", "Semestre", "Categoria", "Valor"])
            writer.writerows(resultados)

        messagebox.showinfo("Exportação", "Gastos exportados para 'gastos.csv' com sucesso.")

    def exibir_grafico(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT categoria, SUM(valor) FROM gastos WHERE usuario=? GROUP BY categoria", (self.usuario,))
        resultados = cursor.fetchall()

        categorias = [row[0] for row in resultados]
        valores = [row[1] for row in resultados]

        plt.bar(categorias, valores)
        plt.xlabel("Categorias")
        plt.ylabel("Total de Gastos (R$)")
        plt.title("Gastos por Categoria")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = GastosApp(root)
    root.mainloop()


if __name__ == " __main__":
    root = tk.Tk()
    app = GastosApp(root)
    root.mainloop()
