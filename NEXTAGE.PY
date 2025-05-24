import customtkinter as ctk
from mysql.connector import connect, Error
from decimal import Decimal

# Configurações do banco de dados
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "jogos"
}

# Funções de Conexão e Mensagens
def conectar_banco():
    """Tenta conectar ao banco de dados e retorna a conexão."""
    try:
        return connect(**DB_CONFIG)
    except Error as e:
        mostrar_mensagem(f"Erro ao conectar ao MySQL: {e}", cor="#FF5555")
        return None

def mostrar_mensagem(msg, cor="#FFD700"):
    """Exibe uma mensagem temporária no modify_frame."""
    for widget in modify_frame.winfo_children():
        if getattr(widget, 'is_msg', False):
            widget.destroy()
    label = ctk.CTkLabel(modify_frame, text=msg, text_color=cor, font=("Arial", 12))
    label.is_msg = True
    label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

def limpar_modify_frame():
    """Limpa todos os widgets do modify_frame."""
    for widget in modify_frame.winfo_children():
        widget.destroy()

## Funções de Manipulação do Banco de Dados

def listar_produtos_db():
    """Lista todos os produtos com suas categorias e fornecedores."""
    conn = conectar_banco()
    produtos = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Corrigido: 'c.cat_nome' ao invés de 'c.nome_cat' para corresponder à tabela tb_categoria
            query = """
            SELECT p.pro_id, p.pro_nome, p.prod_desc, p.prod_preco, p.qntd_estoque,
                   c.cat_nome AS categoria, f.forn_nome AS fornecedor
            FROM tb_produtos p
            JOIN tb_categoria c ON p.cat_id = c.cat_id
            JOIN tb_fornecedor f ON p.forn_id = f.forn_id
            ORDER BY p.pro_nome
            """
            cursor.execute(query)
            produtos = cursor.fetchall()
        except Exception as e:
            mostrar_mensagem(f"Erro ao listar produtos: {e}", cor="#FF5555")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return produtos

def adicionar_produto_db(nome, descricao, preco, estoque, cat_id, forn_id):
    """Adiciona um novo produto ao banco de dados."""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO tb_produtos
            (pro_nome, prod_desc, prod_preco, qntd_estoque, cat_id, forn_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nome, descricao, preco, estoque, cat_id, forn_id))
            conn.commit()
            return True
        except Exception as e:
            mostrar_mensagem(f"Erro ao adicionar produto: {e}", cor="#FF5555")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return False

def atualizar_produto_db(produto_id, nome, descricao, preco, estoque, cat_id, forn_id):
    """Atualiza um produto existente no banco de dados."""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE tb_produtos
            SET pro_nome = %s, prod_desc = %s, prod_preco = %s, qntd_estoque = %s, cat_id = %s, forn_id = %s
            WHERE pro_id = %s
            """
            cursor.execute(query, (nome, descricao, preco, estoque, cat_id, forn_id, produto_id))
            conn.commit()
            return True
        except Exception as e:
            mostrar_mensagem(f"Erro ao atualizar produto: {e}", cor="#FF5555")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return False

def remover_produto_db(produto_id):
    """Remove um produto do banco de dados."""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tb_produtos WHERE pro_id = %s", (produto_id,))
            conn.commit()
            return True
        except Exception as e:
            mostrar_mensagem(f"Erro ao remover produto: {e}", cor="#FF5555")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return False

def listar_categorias_db():
    """Lista todas as categorias do banco de dados."""
    conn = conectar_banco()
    categorias = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Corrigido: 'cat_nome' ao invés de 'nome_cat' para corresponder à sua query de produtos
            query = "SELECT cat_id, cat_nome FROM tb_categoria ORDER BY cat_nome"
            cursor.execute(query)
            categorias = cursor.fetchall()
        except Exception as e:
            mostrar_mensagem(f"Erro ao listar categorias: {e}", cor="#FF5555")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return categorias

def listar_fornecedores_db():
    """Lista todos os fornecedores do banco de dados."""
    conn = conectar_banco()
    fornecedores = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT forn_id, forn_nome FROM tb_fornecedor ORDER BY forn_nome"
            cursor.execute(query)
            fornecedores = cursor.fetchall()
        except Exception as e:
            mostrar_mensagem(f"Erro ao listar fornecedores: {e}", cor="#FF5555")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return fornecedores

def atualizar_lista_jogos(frame):
    """Atualiza a lista de produtos exibida no scrollable_frame."""
    for widget in frame.winfo_children():
        widget.destroy()
    produtos = listar_produtos_db()
    root = frame.winfo_toplevel()
    
    for prod in produtos:
        item_frame = ctk.CTkFrame(frame, fg_color="transparent")
        item_frame.pack(fill="x", pady=2, padx=2)
        
        # Adicionado categoria e fornecedor na exibição
        texto = (f"{prod['pro_nome']} | R${prod['prod_preco']:.2f} | Estoque: {prod['qntd_estoque']}\n"
                 f"Categoria: {prod['categoria']} | Fornecedor: {prod['fornecedor']}\n"
                 f"Descrição: {prod['prod_desc']}")
        
        label = ctk.CTkLabel(
            item_frame, 
            text=texto, 
            anchor="w", 
            justify="left", 
            font=("Arial", 12), 
            text_color="#fff"
        )
        label.pack(fill="x", pady=2, padx=2)
        
        def make_click_handler(pid, label_widget):
            def click_handler(e):
                for widget in frame.winfo_children():
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            child.configure(fg_color="transparent", text_color="#fff")
                
                label_widget.configure(fg_color="#3a4149", text_color="#FFD700")
                root.selected_id = pid
                print(f"Selecionado: ID {pid}")
            return click_handler
        
        label.bind("<Button-1>", make_click_handler(prod['pro_id'], label))
        item_frame.bind("<Button-1>", make_click_handler(prod['pro_id'], label))

def exibir_lista_categorias():
    """Exibe a lista de categorias no modify_frame."""
    limpar_modify_frame()
    categorias = listar_categorias_db()
    if not categorias:
        ctk.CTkLabel(modify_frame, text="Nenhuma categoria encontrada.", text_color="#ccc").pack(pady=5)
        return

    ctk.CTkLabel(modify_frame, text="Lista de Categorias", font=("Arial Black", 14), text_color="#FFD700").pack(pady=(10, 5))
    for cat in categorias:
        ctk.CTkLabel(modify_frame, text=f"ID: {cat['cat_id']} - {cat['cat_nome']}", anchor="w", justify="left", font=("Arial", 12), text_color="#fff").pack(fill="x", pady=1, padx=5)
    ctk.CTkButton(modify_frame, text="Fechar", command=limpar_modify_frame, width=120).pack(pady=10)

def exibir_lista_fornecedores():
    """Exibe a lista de fornecedores no modify_frame."""
    limpar_modify_frame()
    fornecedores = listar_fornecedores_db()
    if not fornecedores:
        ctk.CTkLabel(modify_frame, text="Nenhum fornecedor encontrado.", text_color="#ccc").pack(pady=5)
        return

    ctk.CTkLabel(modify_frame, text="Lista de Fornecedores", font=("Arial Black", 14), text_color="#FFD700").pack(pady=(10, 5))
    for forn in fornecedores:
        ctk.CTkLabel(modify_frame, text=f"ID: {forn['forn_id']} - {forn['forn_nome']}", anchor="w", justify="left", font=("Arial", 12), text_color="#fff").pack(fill="x", pady=1, padx=5)
    ctk.CTkButton(modify_frame, text="Fechar", command=limpar_modify_frame, width=120).pack(pady=10)


def exibir_form_adicionar():
    """Exibe o formulário para adicionar um novo jogo."""
    limpar_modify_frame()
    ctk.CTkLabel(modify_frame, text="Adicionar Jogo", font=("Arial Black", 16), text_color="#FFD700").pack(pady=(10,5))

    nome_entry = ctk.CTkEntry(modify_frame, placeholder_text="Nome do Jogo")
    nome_entry.pack(pady=5, fill="x", padx=20)
    desc_entry = ctk.CTkEntry(modify_frame, placeholder_text="Descrição")
    desc_entry.pack(pady=5, fill="x", padx=20)
    preco_entry = ctk.CTkEntry(modify_frame, placeholder_text="Preço (R$)")
    preco_entry.pack(pady=5, fill="x", padx=20)
    estoque_entry = ctk.CTkEntry(modify_frame, placeholder_text="Estoque")
    estoque_entry.pack(pady=5, fill="x", padx=20)

    categorias_disponiveis = listar_categorias_db()
    # Usando 'cat_nome' que é o nome correto da coluna
    nomes_categorias = [cat['cat_nome'] for cat in categorias_disponiveis]
    map_cat_nome_to_id = {cat['cat_nome']: cat['cat_id'] for cat in categorias_disponiveis}

    if nomes_categorias:
        ctk.CTkLabel(modify_frame, text="Categoria:", text_color="#fff").pack(pady=(5,0), padx=20, anchor="w")
        categoria_combobox = ctk.CTkComboBox(modify_frame, values=nomes_categorias, state="readonly")
        categoria_combobox.set(nomes_categorias[0])
        categoria_combobox.pack(pady=5, fill="x", padx=20)
    else:
        ctk.CTkLabel(modify_frame, text="Nenhuma categoria disponível.", text_color="#FF5555").pack(pady=5)
        categoria_combobox = None

    fornecedores_disponiveis = listar_fornecedores_db()
    nomes_fornecedores = [forn['forn_nome'] for forn in fornecedores_disponiveis]
    map_forn_nome_to_id = {forn['forn_nome']: forn['forn_id'] for forn in fornecedores_disponiveis}

    if nomes_fornecedores:
        ctk.CTkLabel(modify_frame, text="Fornecedor:", text_color="#fff").pack(pady=(5,0), padx=20, anchor="w")
        fornecedor_combobox = ctk.CTkComboBox(modify_frame, values=nomes_fornecedores, state="readonly")
        fornecedor_combobox.set(nomes_fornecedores[0])
        fornecedor_combobox.pack(pady=5, fill="x", padx=20)
    else:
        ctk.CTkLabel(modify_frame, text="Nenhum fornecedor disponível.", text_color="#FF5555").pack(pady=5)
        fornecedor_combobox = None

    def salvar():
        nome = nome_entry.get().strip()
        desc = desc_entry.get().strip()
        try:
            preco = Decimal(preco_entry.get().replace(",", "."))
            estoque = int(estoque_entry.get())
        except Exception:
            mostrar_mensagem("Preço e Estoque inválidos.", cor="#FF5555")
            return

        cat_id = None
        forn_id = None
        if categoria_combobox and categoria_combobox.get():
            cat_id = map_cat_nome_to_id.get(categoria_combobox.get())
        if fornecedor_combobox and fornecedor_combobox.get():
            forn_id = map_forn_nome_to_id.get(fornecedor_combobox.get())

        if cat_id is None:
            mostrar_mensagem("Selecione uma categoria válida.", cor="#FF5555")
            return
        if forn_id is None:
            mostrar_mensagem("Selecione um fornecedor válido.", cor="#FF5555")
            return

        if nome:
            if adicionar_produto_db(nome, desc, preco, estoque, cat_id, forn_id):
                atualizar_lista_jogos(scrollable_frame)
                mostrar_mensagem("Jogo adicionado com sucesso!", cor="#44FF44")
                limpar_modify_frame()
            else:
                mostrar_mensagem("Erro ao adicionar.", cor="#FF5555")
        else:
            mostrar_mensagem("Nome obrigatório.", cor="#FF5555")

    botoes_frame = ctk.CTkFrame(modify_frame, fg_color="transparent")
    botoes_frame.pack(pady=10)
    ctk.CTkButton(botoes_frame, text="Salvar", command=salvar, width=120).pack(side="left", padx=(0, 10))
    ctk.CTkButton(botoes_frame, text="Cancelar", command=limpar_modify_frame, width=120).pack(side="left")

def exibir_form_editar():
    """Exibe o formulário para editar um jogo existente."""
    root = scrollable_frame.winfo_toplevel()
    if not hasattr(root, 'selected_id') or not root.selected_id:
        mostrar_mensagem("Selecione um jogo na lista.", cor="#FF5555")
        return

    produto_id = root.selected_id
    conn = conectar_banco()
    prod = None
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Corrigido: 'c.cat_nome' ao invés de 'c.nome_cat' para corresponder à tabela tb_categoria
            cursor.execute("""
                SELECT p.*, c.cat_nome, f.forn_nome
                FROM tb_produtos p
                JOIN tb_categoria c ON p.cat_id = c.cat_id
                JOIN tb_fornecedor f ON p.forn_id = f.forn_id
                WHERE p.pro_id = %s
            """, (produto_id,))
            prod = cursor.fetchone()
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()

    if not prod:
        mostrar_mensagem("Produto não encontrado.", cor="#FF5555")
        return

    limpar_modify_frame()
    ctk.CTkLabel(modify_frame, text=f"Editar Jogo (ID {produto_id})", font=("Arial Black", 16), text_color="#FFD700").pack(pady=(10,5))

    nome_entry = ctk.CTkEntry(modify_frame)
    nome_entry.insert(0, prod['pro_nome'])
    nome_entry.pack(pady=5, fill="x", padx=20)

    desc_entry = ctk.CTkEntry(modify_frame)
    desc_entry.insert(0, prod['prod_desc'])
    desc_entry.pack(pady=5, fill="x", padx=20)

    preco_entry = ctk.CTkEntry(modify_frame)
    preco_entry.insert(0, f"{prod['prod_preco']:.2f}")
    preco_entry.pack(pady=5, fill="x", padx=20)

    estoque_entry = ctk.CTkEntry(modify_frame)
    estoque_entry.insert(0, str(prod['qntd_estoque']))
    estoque_entry.pack(pady=5, fill="x", padx=20)

    categorias_disponiveis = listar_categorias_db()
    nomes_categorias = [cat['cat_nome'] for cat in categorias_disponiveis]
    map_cat_nome_to_id = {cat['cat_nome']: cat['cat_id'] for cat in categorias_disponiveis}

    if nomes_categorias:
        ctk.CTkLabel(modify_frame, text="Categoria:", text_color="#fff").pack(pady=(5,0), padx=20, anchor="w")
        categoria_combobox = ctk.CTkComboBox(modify_frame, values=nomes_categorias, state="readonly")
        if prod['cat_nome'] in nomes_categorias: # Corrigido: 'cat_nome'
            categoria_combobox.set(prod['cat_nome'])
        else:
            categoria_combobox.set(nomes_categorias[0])
        categoria_combobox.pack(pady=5, fill="x", padx=20)
    else:
        ctk.CTkLabel(modify_frame, text="Nenhuma categoria disponível.", text_color="#FF5555").pack(pady=5)
        categoria_combobox = None

    fornecedores_disponiveis = listar_fornecedores_db()
    nomes_fornecedores = [forn['forn_nome'] for forn in fornecedores_disponiveis]
    map_forn_nome_to_id = {forn['forn_nome']: forn['forn_id'] for forn in fornecedores_disponiveis}

    if nomes_fornecedores:
        ctk.CTkLabel(modify_frame, text="Fornecedor:", text_color="#fff").pack(pady=(5,0), padx=20, anchor="w")
        fornecedor_combobox = ctk.CTkComboBox(modify_frame, values=nomes_fornecedores, state="readonly")
        if prod['forn_nome'] in nomes_fornecedores:
            fornecedor_combobox.set(prod['forn_nome'])
        else:
            fornecedor_combobox.set(nomes_fornecedores[0])
        fornecedor_combobox.pack(pady=5, fill="x", padx=20)
    else:
        ctk.CTkLabel(modify_frame, text="Nenhum fornecedor disponível.", text_color="#FF5555").pack(pady=5)
        fornecedor_combobox = None

    def salvar():
        nome = nome_entry.get().strip()
        desc = desc_entry.get().strip()
        try:
            preco = Decimal(preco_entry.get().replace(",", "."))
            estoque = int(estoque_entry.get())
        except Exception:
            mostrar_mensagem("Preço e Estoque inválidos.", cor="#FF5555")
            return

        cat_id = None
        forn_id = None
        if categoria_combobox and categoria_combobox.get():
            cat_id = map_cat_nome_to_id.get(categoria_combobox.get())
        if fornecedor_combobox and fornecedor_combobox.get():
            forn_id = map_forn_nome_to_id.get(fornecedor_combobox.get())

        if cat_id is None:
            mostrar_mensagem("Selecione uma categoria válida.", cor="#FF5555")
            return
        if forn_id is None:
            mostrar_mensagem("Selecione um fornecedor válido.", cor="#FF5555")
            return

        if nome:
            if atualizar_produto_db(produto_id, nome, desc, preco, estoque, cat_id, forn_id):
                atualizar_lista_jogos(scrollable_frame)
                mostrar_mensagem("Jogo atualizado!", cor="#44FF44")
                limpar_modify_frame()
            else:
                mostrar_mensagem("Erro ao atualizar.", cor="#FF5555")
        else:
            mostrar_mensagem("Nome obrigatório.", cor="#FF5555")

    botoes_frame = ctk.CTkFrame(modify_frame, fg_color="transparent")
    botoes_frame.pack(pady=10)
    ctk.CTkButton(botoes_frame, text="Salvar", command=salvar, width=120).pack(side="left", padx=(0, 10))
    ctk.CTkButton(botoes_frame, text="Cancelar", command=limpar_modify_frame, width=120).pack(side="left")


def main():
    """Função principal que inicializa a interface do usuário."""
    global scrollable_frame, modify_frame
    root = ctk.CTk()
    root.geometry("800x900")
    root.title("Loja de Jogos")
    root.resizable(False, False)
    root.configure(fg_color="#23272F")
    root.selected_id = None

    def set_selected_id(pid):
        root.selected_id = pid
        print(f"Jogo selecionado: ID {pid}")
    root.set_selected_id = set_selected_id

    title_frame = ctk.CTkFrame(root, fg_color="#1a1d23", corner_radius=15, width=750, height=70)
    title_frame.place(relx=0.5, y=15, anchor="n")
    title_frame.pack_propagate(False)
    
    title_label = ctk.CTkLabel(
        title_frame,
        text="🎮 NEXTAGE SHOP",
        font=("Arial Black", 24, "bold"),
        text_color="#FFD700"
    )
    title_label.place(relx=0.5, rely=0.5, anchor="center")
    
    button_frame = ctk.CTkFrame(root, fg_color="transparent", width=200, height=300)
    button_frame.place(x=30, y=100)

    add_button = ctk.CTkButton(
        button_frame, 
        text="ADICIONAR JOGO", 
        command=exibir_form_adicionar, 
        width=180, 
        height=50,
        font=("Arial Bold", 14)
    )
    add_button.pack(pady=10)

    edit_button = ctk.CTkButton(
        button_frame, 
        text="EDITAR JOGO", 
        command=exibir_form_editar, 
        width=180, 
        height=50,
        font=("Arial Bold", 14)
    )
    edit_button.pack(pady=10)

    remove_button = ctk.CTkButton(
        button_frame, 
        text="REMOVER JOGO", 
        command=remover_produto_db, 
        width=180, 
        height=50,
        font=("Arial Bold", 14)
    )
    remove_button.pack(pady=10)

    # Botões para listar categorias e fornecedores (mantidos da sugestão anterior)
    list_cat_button = ctk.CTkButton(
        button_frame,
        text="VER CATEGORIAS",
        command=exibir_lista_categorias,
        width=180,
        height=50,
        font=("Arial Bold", 14)
    )
    list_cat_button.pack(pady=10)

    list_forn_button = ctk.CTkButton(
        button_frame,
        text="VER FORNECEDORES",
        command=exibir_lista_fornecedores,
        width=180,
        height=50,
        font=("Arial Bold", 14)
    )
    list_forn_button.pack(pady=10)

    scrollable_frame = ctk.CTkScrollableFrame(
        root, 
        width=520, 
        height=300,
        fg_color="#1a1d23",
        corner_radius=10
    )
    scrollable_frame.place(x=230, y=100)
    atualizar_lista_jogos(scrollable_frame)

    modify_frame = ctk.CTkFrame(
        root, 
        fg_color="#1a1d23", 
        corner_radius=15, 
        width=740, 
        height=400
    )
    modify_frame.place(relx=0.5, y=470, anchor="n")
    modify_frame.pack_propagate(False)

    root.mainloop()

if __name__ == "__main__":
    main()
