import customtkinter as ctk
import json
import os

# Configuração do tema (altera isso se quiser (mudar a aparência do app))
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

ARQUIVO_SAVE = "tarefas.json"

# --- CLASSE CUSTOMIZADA: Checkbox Animado ---
class CheckboxAnimado(ctk.CTkFrame):
    def __init__(self, master, cor_tema, command=None, **kwargs):
        # Cria um quadradinho com borda colorida
        super().__init__(master, width=24, height=24, corner_radius=6, border_width=2, border_color=cor_tema, fg_color="transparent", **kwargs)
        self.pack_propagate(False) # Impede que o frame mude de tamanho
        self.command = command
        self.is_checked = False
        self.cor_tema = cor_tema
        
        # O símbolo de confere (✔)
        self.check_label = ctk.CTkLabel(self, text="✔", text_color=cor_tema, font=ctk.CTkFont(size=14, weight="bold"))
        # Inicia escondido (y=35 fica fora do quadradinho de tamanho 24)
        self.check_label.place(relx=0.5, y=35, anchor="center") 
        
        # Clicar no frame ou no texto aciona a troca
        self.bind("<Button-1>", self.alternar)
        self.check_label.bind("<Button-1>", self.alternar)
        
    def alternar(self, event=None):
        self.is_checked = not self.is_checked
        self.animar()
        if self.command:
            self.command(self.is_checked)
            
    def animar(self):
        # Pega a posição Y atual do ✔
        current_y = float(self.check_label.place_info()['y'])
        
        if self.is_checked and current_y > 12:
            # Sobe
            self.check_label.place(relx=0.5, y=current_y - 3, anchor="center")
            self.after(10, self.animar)
        elif not self.is_checked and current_y < 35:
            # Desce
            self.check_label.place(relx=0.5, y=current_y + 3, anchor="center")
            self.after(10, self.animar)
            
    def set_estado_inicial(self, estado):
        self.is_checked = estado
        if estado:
            self.check_label.place(relx=0.5, y=12, anchor="center")
        else:
            self.check_label.place(relx=0.5, y=35, anchor="center")

# --- CLASSE PRINCIPAL DO APLICATIVO ---
class AplicativoTarefas(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Pessoal (Feito por Geld0x)")
        self.geometry("500x600")
        self.resizable(True, True)

        # Dicionário de cores para as categorias
        self.cores_categorias = {
            "Casa": "#3498db",     # Azul
            "Escola": "#2ecc71",   # Verde
            "Trabalho": "#e67e22"  # Laranja
        }
        self.tarefas_widgets = [] # Lista para guardar os cartões em memória

        # 1. Título e Subtítulo
        self.titulo = ctk.CTkLabel(self, text="Minhas Tarefas", font=ctk.CTkFont(size=24, weight="bold"))
        self.titulo.pack(pady=(20, 0))

        self.subtitulo = ctk.CTkLabel(self, text="Feito Por Geld0x", font=ctk.CTkFont(size=12, weight="normal"), text_color="gray")
        self.subtitulo.pack(pady=(0, 15))

        # 2. Área de Entrada (Entrada, Categoria e Botão)
        self.frame_entrada = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_entrada.pack(pady=5, padx=20, fill="x")

        # Categoria (Menu Suspenso)
        self.categoria_var = ctk.StringVar(value="Casa")
        self.menu_categoria = ctk.CTkOptionMenu(
            self.frame_entrada, 
            values=["Casa", "Escola", "Trabalho"], 
            variable=self.categoria_var, 
            width=100
        )
        self.menu_categoria.pack(side="left", padx=(0, 10))

        # Campo de texto
        self.entrada_tarefa = ctk.CTkEntry(self.frame_entrada, placeholder_text="O que precisa ser feito?")
        self.entrada_tarefa.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.entrada_tarefa.bind("<Return>", lambda event: self.adicionar_tarefa())

        # Botão de adicionar
        self.botao_adicionar = ctk.CTkButton(self.frame_entrada, text="Adicionar", width=80, command=self.adicionar_tarefa)
        self.botao_adicionar.pack(side="right")

        # 3. Lista de Tarefas (Cartões)
        self.lista_scroll = ctk.CTkScrollableFrame(self, label_text="Tarefas Pendentes")
        self.lista_scroll.pack(pady=15, padx=20, expand=True, fill="both")

        # Configura o evento de fechar a janela para salvar os dados
        self.protocol("WM_DELETE_WINDOW", self.salvar_e_fechar)
        
        # Carrega as tarefas salvas anteriormente
        self.carregar_tarefas()

    def adicionar_tarefa(self, texto=None, categoria=None, concluida=False, animar=True):
        if texto is None:
            texto = self.entrada_tarefa.get()
            categoria = self.categoria_var.get()
        
        if not texto.strip():
            return

        cor = self.cores_categorias.get(categoria, "#ffffff")

        # Cria o cartão com altura 0 se for animar, ou altura 50 se for carregado direto do save
        cartao_tarefa = ctk.CTkFrame(self.lista_scroll, height=0 if animar else 50, border_color=cor, border_width=2)
        cartao_tarefa.pack_propagate(False if animar else True)
        cartao_tarefa.pack(pady=5, padx=5, fill="x")

        # Salvando atributos no próprio cartão para facilitar na hora de salvar em JSON
        cartao_tarefa.texto_tarefa = texto
        cartao_tarefa.categoria = categoria
        cartao_tarefa.concluida = concluida

        lbl_texto = ctk.CTkLabel(cartao_tarefa, text=texto, font=ctk.CTkFont(size=14))

        # Função que reage quando a caixinha é clicada
        def ao_marcar(estado):
            cartao_tarefa.concluida = estado
            if estado:
                lbl_texto.configure(text_color="gray")
            else:
                cor_padrao = "white" if ctk.get_appearance_mode() == "Dark" else "black"
                lbl_texto.configure(text_color=cor_padrao)

        # Usando nosso Checkbox Animado
        chk = CheckboxAnimado(cartao_tarefa, cor_tema=cor, command=ao_marcar)
        chk.pack(side="left", padx=15, pady=13)
        lbl_texto.pack(side="left", padx=(0, 15), pady=13)

        # Botão Excluir
        btn_excluir = ctk.CTkButton(
            cartao_tarefa, text="X", width=30, 
            fg_color="#d9534f", hover_color="#c9302c", 
            command=lambda: self.remover_tarefa(cartao_tarefa)
        )
        btn_excluir.pack(side="right", padx=15, pady=13)

        # Define estados iniciais
        chk.set_estado_inicial(concluida)
        ao_marcar(concluida)

        self.tarefas_widgets.append(cartao_tarefa)
        self.entrada_tarefa.delete(0, 'end')

        # Inicia a animação de deslizamento para baixo
        if animar:
            self.animar_entrada(cartao_tarefa, 0)

    # --- Funções de Animação ---
    def animar_entrada(self, cartao, altura):
        if altura <= 50:
            cartao.configure(height=altura)
            self.after(10, lambda: self.animar_entrada(cartao, altura + 4))
        else:
            cartao.pack_propagate(True) # Libera o frame para se ajustar ao conteúdo após crescer

    def remover_tarefa(self, cartao):
        cartao.pack_propagate(False) # Trava o tamanho para podermos encolher
        altura_atual = cartao.winfo_height()
        self.animar_saida(cartao, altura_atual)
        
    def animar_saida(self, cartao, altura):
        if altura > 0:
            cartao.configure(height=altura)
            self.after(10, lambda: self.animar_saida(cartao, altura - 5))
        else:
            self.tarefas_widgets.remove(cartao)
            cartao.destroy()

    # --- Funções de Salvar / Carregar ---
    def carregar_tarefas(self):
        if os.path.exists(ARQUIVO_SAVE):
            try:
                with open(ARQUIVO_SAVE, "r", encoding="utf-8") as f:
                    tarefas = json.load(f)
                
                # Recria cada tarefa do arquivo
                for t in tarefas:
                    self.adicionar_tarefa(texto=t["texto"], categoria=t["categoria"], concluida=t["concluida"], animar=False)
                
                # Excluir o arquivo de save logo após abrir (entrou 1 vez)
                os.remove(ARQUIVO_SAVE)
            except Exception as e:
                print("Erro ao carregar o save:", e)

    def salvar_e_fechar(self):
        tarefas_para_salvar = []
        for cartao in self.tarefas_widgets:
            tarefas_para_salvar.append({
                "texto": cartao.texto_tarefa,
                "categoria": cartao.categoria,
                "concluida": cartao.concluida
            })
            
        with open(ARQUIVO_SAVE, "w", encoding="utf-8") as f:
            json.dump(tarefas_para_salvar, f, ensure_ascii=False, indent=4)
            
        self.destroy() # Fecha a janela definitivamente

if __name__ == "__main__":
    app = AplicativoTarefas()
    app.mainloop()