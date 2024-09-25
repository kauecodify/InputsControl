import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
import datetime
import sqlite3
import hashlib

class GastosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("InputsControl")

        # bd SQLite
        self.conn = sqlite3.connect("gastos.db")
        self.create_tables()

        self.login_frame = tk.Frame(root)
        self.login_frame.pack()

        self.label_usuario = tk.Label(self.login_frame, text="Usuário:")
        self.label_usuario.grid(row=0, column=0)
        self.entry_usuario = tk.Entry(self.login_frame)
        self.entry_usuario.grid(row=0, column=1)

        self.label_senha = tk.Label(self.login_frame, text="Senha:")
        self.label_senha.grid(row=1, column=0)
        self.entry_senha = tk.Entry(self.login_frame, show="*")
        self.entry_senha.grid(row=1, column=1)

        self.btn_login = tk.Button(self.login_frame, text="Login", command=self.login)
        self.btn_login.grid(row=2, columnspan=2)

        self.btn_registrar = tk.Button(self.login_frame, text="Registrar", command=self.registrar)
        self.btn_registrar.grid(row=3, columnspan=2)

        self.gastos = defaultdict(lambda: defaultdict(float))

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
        self.gastos_frame = tk.Frame(self.root)
        self.gastos_frame.pack()

        self.label_data = tk.Label(self.gastos_frame, text="Data (YYYY-MM-DD):")
        self.label_data.pack()
        self.entry_data = tk.Entry(self.gastos_frame)
        self.entry_data.pack()

        self.label_gasto = tk.Label(self.gastos_frame, text="Valor do Insumo:")
        self.label_gasto.pack()
        self.entry_gasto = tk.Entry(self.gastos_frame)
        self.entry_gasto.pack()

        self.btn_adicionar = tk.Button(self.gastos_frame, text="Adicionar Gasto", command=lambda: self.adicionar_gasto(usuario))
        self.btn_adicionar.pack()

        self.btn_consultar = tk.Button(self.gastos_frame, text="Consultar Gastos", command=lambda: self.consultar_gastos(usuario))
        self.btn_consultar.pack()

        self.btn_remover = tk.Button(self.gastos_frame, text="Remover Gasto", command=lambda: self.remover_gasto(usuario))
        self.btn_remover.pack()

        self.label_ano = tk.Label(self.gastos_frame, text="Consultar Gastos por Ano:")
        self.label_ano.pack()
        self.entry_ano = tk.Entry(self.gastos_frame)
        self.entry_ano.pack()
        self.btn_consultar_ano = tk.Button(self.gastos_frame, text="Consultar Ano", command=lambda: self.consultar_gastos_por_ano(usuario))
        self.btn_consultar_ano.pack()

        self.btn_limpar = tk.Button(self.gastos_frame, text="Limpar Todos os Gastos", command=lambda: self.limpar_gastos(usuario))
        self.btn_limpar.pack()

    def adicionar_gasto(self, usuario):
        data_str = self.entry_data.get()
        valor_str = self.entry_gasto.get()

        try:
            data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
            semestre = 1 if data.month <= 6 else 2
            ano = data.year
            valor = float(valor_str)

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO gastos (usuario, ano, semestre, valor) VALUES (?, ?, ?, ?)",
                           (usuario, ano, semestre, valor))
            self.conn.commit()

            messagebox.showinfo("Sucesso", "Gasto adicionado com sucesso!")
            self.entry_data.delete(0, tk.END)
            self.entry_gasto.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erro", "Data ou valor inválido. Tente novamente.")

    def consultar_gastos(self, usuario):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ano, semestre, SUM(valor) FROM gastos WHERE usuario=? GROUP BY ano, semestre", (usuario,))
        resultados = cursor.fetchall()

        resultado = ""
        for ano, semestre, total in resultados:
            resultado += f"Ano: {ano}, Semestre {semestre}: R$ {total:.2f}\n"

        if not resultado:
            resultado = "Nenhum gasto registrado."

        messagebox.showinfo("Consulta de Gastos", resultado)

    def remover_gasto(self, usuario):
        data_str = self.entry_data.get()
        valor_str = self.entry_gasto.get()

        try:
            data = datetime.datetime.strptime(data_str, "%Y-%m-%d")
            semestre = 1 if data.month <= 6 else 2
            ano = data.year
            valor = float(valor_str)

            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM gastos WHERE usuario=? AND ano=? AND semestre=? AND valor=?",
                           (usuario, ano, semestre, valor))
            self.conn.commit()

            if cursor.rowcount > 0:
                messagebox.showinfo("Sucesso", "Gasto removido com sucesso!")
            else:
                messagebox.showerror("Erro", "Gasto não encontrado.")

            self.entry_data.delete(0, tk.END)
            self.entry_gasto.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erro", "Data ou valor inválido. Tente novamente.")

    def consultar_gastos_por_ano(self, usuario):
        ano_str = self.entry_ano.get()

        try:
            ano = int(ano_str)
            cursor = self.conn.cursor()
            cursor.execute("SELECT semestre, SUM(valor) FROM gastos WHERE usuario=? AND ano=? GROUP BY semestre", (usuario, ano))
            resultados = cursor.fetchall()

            if resultados:
                resultado = f"Gastos no Ano: {ano}\n"
                for semestre, total in resultados:
                    resultado += f"  Semestre {semestre}: R$ {total:.2f}\n"
                messagebox.showinfo("Consulta de Gastos por Ano", resultado)
            else:
                messagebox.showinfo("Consulta de Gastos por Ano", "Nenhum gasto registrado para este ano.")
        except ValueError:
            messagebox.showerror("Erro", "Ano inválido. Tente novamente.")

    def limpar_gastos(self, usuario):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM gastos WHERE usuario=?", (usuario,))
        self.conn.commit()
        messagebox.showinfo("Sucesso", "Todos os gastos foram limpos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GastosApp(root)
    root.mainloop()

