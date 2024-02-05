import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import requests
import json


class HomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serpros Consultas")
        self.root.geometry("300x200")
        self.root.configure(bg="#2E2E2E")  # Cor de fundo escura

        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")  # Use o tema clam para obter uma aparência mais amigável em dark mode

        label = ttk.Label(self.root, text="Consultas Serpros:", foreground="#FFFFFF", background="#2E2E2E",
                          font=("Helvetica", 12))
        label.pack(pady=10)

        button_nf = ttk.Button(self.root, text="Consultar Nota Fiscal", command=self.open_nf_consultation)
        button_nf.pack(pady=5)

        button_cnpj = ttk.Button(self.root, text="Consultar CNPJ", command=self.open_cnpj_consultation)
        button_cnpj.pack(pady=5)

        button_cpf = ttk.Button(self.root, text="Consultar CPF", command=self.open_cpf_consultation)
        button_cpf.pack(pady=5)

    def open_nf_consultation(self):
        nf_window = tk.Toplevel(self.root)
        nf_app = NFConsultationApp(nf_window)

    def open_cnpj_consultation(self):
        nf_window = tk.Toplevel(self.root)
        nf_app = CNPJConsultationApp(nf_window)

    def open_cpf_consultation(self):
        nf_window = tk.Toplevel(self.root)
        nf_app = CPFConsultationApp(nf_window)


class NFConsultationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta Nota Fiscal")
        self.root.geometry("500x600")
        self.root.minsize(200, 200)
        self.root.resizable(True, True)

        self.authorization_token = "06aef429-a981-3ec5-a1f8-71d38d86481e"
        self.historico_notas = []  # Lista para armazenar o histórico (número da NF e payload)

        self.create_widgets()

    def create_widgets(self):
        self.frame_consulta = ttk.Frame(self.root)
        self.frame_consulta.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.label_nf = ttk.Label(self.frame_consulta, text="Número da Nota Fiscal:")
        self.label_nf.grid(row=0, column=0, padx=10, pady=10)

        self.entry_nf = ttk.Entry(self.frame_consulta)
        self.entry_nf.grid(row=0, column=1, padx=10, pady=10)

        self.btn_consultar = ttk.Button(self.frame_consulta, text="Consultar", command=self.consultar_nf)
        self.btn_consultar.grid(row=0, column=2, padx=10, pady=10)

        self.resultado_label = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, state="disabled")
        self.resultado_label.grid(row=1, column=0, columnspan=3, pady=10)

        self.listbox_historico = tk.Listbox(self.root, width=40, height=10)
        self.listbox_historico.grid(row=2, column=0, columnspan=3, pady=10)

        self.label_buscar = ttk.Label(self.root, text="Buscar Nota Fiscal:")
        self.label_buscar.grid(row=3, column=0, padx=10, pady=10)

        self.entry_buscar = ttk.Entry(self.root)
        self.entry_buscar.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self.root, text="Buscar", command=self.buscar_nota_fiscal).grid(row=3, column=2, padx=10, pady=10)

        # Usando o evento <<ListboxSelect>> para chamar a função de exibir detalhes no double-click
        self.listbox_historico.bind("<<ListboxSelect>>", self.on_item_selected)

        ttk.Button(self.root, text="Baixar JSON", command=self.baixar_json).grid(row=4, column=0, columnspan=3, pady=10)

    def consultar_nf(self):
        numero_nf = self.entry_nf.get()
        url = f"https://gateway.apiserpro.serpro.gov.br/consulta-nfe-df-trial/api/v1/nfe/{numero_nf}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                resultado_json = json.dumps(response.json(), indent=2)
                self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
                self.resultado_label.delete(1.0, tk.END)
                self.resultado_label.insert(tk.INSERT, resultado_json)
                self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

                # Adicionar a nota e o payload ao histórico
                self.historico_notas.append({'numero_nf': numero_nf, 'payload': response.json()})

                # Atualizar a Listbox com o histórico
                self.atualizar_listbox_historico()
            else:
                self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
                self.resultado_label.delete(1.0, tk.END)
                self.resultado_label.insert(tk.INSERT, f"Erro na consulta: {response.status_code}")
                self.resultado_label.config(state="disabled")  # Desabilitar edição novamente
        except Exception as e:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, f"Erro na consulta: {str(e)}")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def atualizar_listbox_historico(self):
        self.listbox_historico.delete(0, tk.END)  # Limpar a Listbox
        for item in self.historico_notas:
            self.listbox_historico.insert(tk.END, f"Nota Fiscal: {item['numero_nf']}")

    def on_item_selected(self, event):
        selected_index = self.listbox_historico.curselection()
        if selected_index:
            selected_item = self.historico_notas[selected_index[0]]
            payload = json.dumps(selected_item['payload'], indent=2)
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, f"Detalhes da Nota Fiscal {selected_item['numero_nf']}:\n{payload}")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente
        else:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, "Selecione um item no histórico para ver os detalhes")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def baixar_json(self):
        selected_index = self.listbox_historico.curselection()
        if selected_index:
            selected_item = self.historico_notas[selected_index[0]]
            payload = json.dumps(selected_item['payload'], indent=2)

            # Abrir a janela de salvar arquivo e permitir que o usuário escolha o local
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

            if file_path:
                with open(file_path, 'w') as file:
                    file.write(payload)
        else:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, "Selecione um item no histórico para baixar o JSON")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def buscar_nota_fiscal(self):
        termo_busca = self.entry_buscar.get().lower()
        notas_filtradas = [item for item in self.historico_notas if termo_busca in item['numero_nf'].lower()]

        self.listbox_historico.delete(0, tk.END)  # Limpar a Listbox
        for item in notas_filtradas:
            self.listbox_historico.insert(tk.END, f"Nota Fiscal: {item['numero_nf']}")


class CPFConsultationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta CPF")
        self.root.geometry("600x600")
        self.root.minsize(200, 200)
        self.root.resizable(True, True)

        self.authorization_token = "06aef429-a981-3ec5-a1f8-71d38d86481e"
        self.historico_cpfs = []  # Lista para armazenar o histórico (CPF e payload)

        self.create_widgets()

    def create_widgets(self):
        self.frame_consulta = ttk.Frame(self.root)
        self.frame_consulta.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.label_cpf = ttk.Label(self.frame_consulta, text="Número do CPF:")
        self.label_cpf.grid(row=0, column=0, padx=10, pady=10)

        self.entry_cpf = ttk.Entry(self.frame_consulta)
        self.entry_cpf.grid(row=0, column=1, padx=10, pady=10)

        self.btn_consultar = ttk.Button(self.frame_consulta, text="Consultar", command=self.consultar_cpf)
        self.btn_consultar.grid(row=0, column=2, padx=10, pady=10)

        self.resultado_label = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, state="disabled")
        self.resultado_label.grid(row=1, column=0, columnspan=3, pady=10)

        self.listbox_historico = tk.Listbox(self.root, width=40, height=10)
        self.listbox_historico.grid(row=2, column=0, columnspan=3, pady=10)

        self.label_buscar = ttk.Label(self.root, text="Buscar CPF:")
        self.label_buscar.grid(row=3, column=0, padx=10, pady=10)

        self.entry_buscar = ttk.Entry(self.root)
        self.entry_buscar.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self.root, text="Buscar", command=self.buscar_cpf).grid(row=3, column=2, padx=10, pady=10)

        # Usando o evento <<ListboxSelect>> para chamar a função de exibir detalhes no double-click
        self.listbox_historico.bind("<<ListboxSelect>>", self.on_item_selected)

        ttk.Button(self.root, text="Baixar JSON", command=self.baixar_json).grid(row=4, column=0, columnspan=3, pady=10)

    def consultar_cpf(self):
        numero_cpf = self.entry_cpf.get()
        url = f"https://gateway.apiserpro.serpro.gov.br/consulta-cpf-df-trial/v1/cpf/{numero_cpf}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                resultado_json = json.dumps(response.json(), indent=2)
                self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
                self.resultado_label.delete(1.0, tk.END)
                self.resultado_label.insert(tk.INSERT, resultado_json)
                self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

                # Adicionar o CPF e o payload ao histórico
                self.historico_cpfs.append({'CPF': numero_cpf, 'payload': response.json()})

                # Atualizar a Listbox com o histórico
                self.atualizar_listbox_historico()
            else:
                self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
                self.resultado_label.delete(1.0, tk.END)
                self.resultado_label.insert(tk.INSERT, f"Erro na consulta: {response.status_code}")
                self.resultado_label.config(state="disabled")  # Desabilitar edição novamente
        except Exception as e:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, f"Erro na consulta: {str(e)}")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def atualizar_listbox_historico(self):
        self.listbox_historico.delete(0, tk.END)  # Limpar a Listbox
        for item in self.historico_cpfs:
            self.listbox_historico.insert(tk.END, f"CPF: {item['CPF']}")

    def on_item_selected(self, event):
        selected_index = self.listbox_historico.curselection()
        if selected_index:
            selected_item = self.historico_cpfs[selected_index[0]]
            payload = json.dumps(selected_item['payload'], indent=2)
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, f"Detalhes do CPF {selected_item['CPF']}:\n{payload}")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente
        else:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, "Selecione um item no histórico para ver os detalhes")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def baixar_json(self):
        selected_index = self.listbox_historico.curselection()
        if selected_index:
            selected_item = self.historico_cpfs[selected_index[0]]
            payload = json.dumps(selected_item['payload'], indent=2)

            # Abrir a janela de salvar arquivo e permitir que o usuário escolha o local
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

            if file_path:
                with open(file_path, 'w') as file:
                    file.write(payload)
        else:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, "Selecione um item no histórico para baixar o JSON")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def buscar_cpf(self):
        termo_busca = self.entry_buscar.get().lower()
        cpfs_filtrados = [item for item in self.historico_cpfs if termo_busca in item['CPF'].lower()]

        self.listbox_historico.delete(0, tk.END)  # Limpar a Listbox
        for item in cpfs_filtrados:
            self.listbox_historico.insert(tk.END, f"CPF: {item['CPF']}")


class CNPJConsultationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Consulta CNPJ")
        self.root.geometry("600x600")
        self.root.minsize(200, 200)
        self.root.resizable(True, True)

        self.authorization_token = "06aef429-a981-3ec5-a1f8-71d38d86481e"
        self.historico_cnpjs = []  # Lista para armazenar o histórico (CNPJ e payload)

        self.create_widgets()

    def create_widgets(self):
        self.frame_consulta = ttk.Frame(self.root)
        self.frame_consulta.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.label_cnpj = ttk.Label(self.frame_consulta, text="Número do CNPJ:")
        self.label_cnpj.grid(row=0, column=0, padx=10, pady=10)

        self.entry_cnpj = ttk.Entry(self.frame_consulta)
        self.entry_cnpj.grid(row=0, column=1, padx=10, pady=10)

        self.btn_consultar = ttk.Button(self.frame_consulta, text="Consultar", command=self.consultar_cnpj)
        self.btn_consultar.grid(row=0, column=2, padx=10, pady=10)

        self.resultado_label = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=50, height=10, state="disabled")
        self.resultado_label.grid(row=1, column=0, columnspan=3, pady=10)

        self.listbox_historico = tk.Listbox(self.root, width=40, height=10)
        self.listbox_historico.grid(row=2, column=0, columnspan=3, pady=10)

        self.label_buscar = ttk.Label(self.root, text="Buscar CNPJ:")
        self.label_buscar.grid(row=3, column=0, padx=10, pady=10)

        self.entry_buscar = ttk.Entry(self.root)
        self.entry_buscar.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self.root, text="Buscar", command=self.buscar_cnpj).grid(row=3, column=2, padx=10, pady=10)

        # Usando o evento <<ListboxSelect>> para chamar a função de exibir detalhes no double-click
        self.listbox_historico.bind("<<ListboxSelect>>", self.on_item_selected)

        ttk.Button(self.root, text="Baixar JSON", command=self.baixar_json).grid(row=4, column=0, columnspan=3, pady=10)

    def consultar_cnpj(self):
        numero_cnpj = self.entry_cnpj.get()
        url = f"https://gateway.apiserpro.serpro.gov.br/consulta-cnpj-df-trial/v2/basica/{numero_cnpj}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.authorization_token}'
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                resultado_json = json.dumps(response.json(), indent=2)
                self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
                self.resultado_label.delete(1.0, tk.END)
                self.resultado_label.insert(tk.INSERT, resultado_json)
                self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

                # Adicionar o CNPJ e o payload ao histórico
                self.historico_cnpjs.append({'CNPJ': numero_cnpj, 'payload': response.json()})

                # Atualizar a Listbox com o histórico
                self.atualizar_listbox_historico()
            else:
                self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
                self.resultado_label.delete(1.0, tk.END)
                self.resultado_label.insert(tk.INSERT, f"Erro na consulta: {response.status_code}")
                self.resultado_label.config(state="disabled")  # Desabilitar edição novamente
        except Exception as e:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, f"Erro na consulta: {str(e)}")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def atualizar_listbox_historico(self):
        self.listbox_historico.delete(0, tk.END)  # Limpar a Listbox
        for item in self.historico_cnpjs:
            self.listbox_historico.insert(tk.END, f"CNPJ: {item['CNPJ']}")

    def on_item_selected(self, event):
        selected_index = self.listbox_historico.curselection()
        if selected_index:
            selected_item = self.historico_cnpjs[selected_index[0]]
            payload = json.dumps(selected_item['payload'], indent=2)
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, f"Detalhes do CNPJ {selected_item['CNPJ']}:\n{payload}")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente
        else:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, "Selecione um item no histórico para ver os detalhes")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente

    def baixar_json(self):
        selected_index = self.listbox_historico.curselection()
        if selected_index:
            selected_item = self.historico_cnpjs[selected_index[0]]
            payload = json.dumps(selected_item['payload'], indent=2)

            # Abrir a janela de salvar arquivo e permitir que o usuário escolha o local
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])

            if file_path:
                with open(file_path, 'w') as file:
                    file.write(payload)
        else:
            self.resultado_label.config(state="normal")  # Habilitar edição temporariamente
            self.resultado_label.delete(1.0, tk.END)
            self.resultado_label.insert(tk.INSERT, "Selecione um item no histórico para baixar o JSON")
            self.resultado_label.config(state="disabled")  # Desabilitar edição novamente


if __name__ == "__main__":
    root = tk.Tk()
    app = HomeApp(root)
    root.mainloop()
