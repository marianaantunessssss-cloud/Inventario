import streamlit as st
import pandas as pd
import json
import os


# Configuração da Página
st.set_page_config(page_title="Minha Despensa", page_icon="🍞")

FICHEIRO_DADOS = 'despensa_st.json'

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if os.path.exists(FICHEIRO_DADOS):
        with open(FICHEIRO_DADOS, 'r', encoding='utf-8') as f:
            return pd.DataFrame(json.load(f))
    # Dados Iniciais se não existir ficheiro
    df_inicial = pd.DataFrame([
        {"Artigo": "Milho", "Categoria": "enlatados", "Unidade": "Lata", "Stock_Atual": 3, "Nivel_Minimo": 3},
        {"Artigo": "Atum", "Categoria": "enlatados", "Unidade": "Lata", "Stock_Atual": 7, "Nivel_Minimo": 5},
        {"Artigo": "Leite", "Categoria": "laticinios", "Unidade": "Litro", "Stock_Atual": 1, "Nivel_Minimo": 2},
    ])
    return df_inicial

def guardar_dados(df):
    df.to_json(FICHEIRO_DADOS, orient='records', indent=4)

# Inicializar dados na sessão
if 'df' not in st.session_state:
    st.session_state.df = carregar_dados()

df = st.session_state.df

# --- INTERFACE STREAMLIT ---
st.title("🏠 Gestão de Despensa")

aba1, aba2, aba3, aba4 = st.tabs([
    "📦 Stock Atual", 
    "📉 Registar Consumo", 
    "🛒 Lista de Compras", 
    "➕ Novo Artigo"
])

# --- ABA A: LISTA DE STOCK ---
with aba1:
    st.subheader("Estado da Despensa")
    
    # Criar uma coluna de estado visual
    def destacar_baixo_stock(row):
        return ['background-color: #ffcccc' if row.Stock_Atual < row.Nivel_Minimo else '' for _ in row]

    st.dataframe(df.style.apply(destacar_baixo_stock, axis=1), use_container_width=True)

# --- ABA B: REGISTAR CONSUMO ---
with aba2:
    st.subheader("O que gastou hoje?")
    artigo_sel = st.selectbox("Selecione o artigo:", df['Artigo'].unique())
    quantidade = st.number_input("Quantidade consumida:", min_value=1, step=1)
    
    if st.button("Confirmar Consumo"):
        idx = df[df['Artigo'] == artigo_sel].index[0]
        if df.at[idx, 'Stock_Atual'] >= quantidade:
            df.at[idx, 'Stock_Atual'] -= quantidade
            guardar_dados(df)
            st.success(f"Consumo de {quantidade} {df.at[idx, 'Unidade']} de {artigo_sel} registado!")
            st.rerun()
        else:
            st.error("Erro: Stock insuficiente!")

# --- ABA C: LISTA DE COMPRAS ---
with aba3:
    st.subheader("Artigos a Comprar")
    compras = df[df['Stock_Atual'] < df['Nivel_Minimo']].copy()
    
    if not compras.empty:
        compras['A_Comprar'] = compras['Nivel_Minimo'] - compras['Stock_Atual']
        st.warning("Estes itens estão abaixo do nível mínimo:")
        
        for _, row in compras.iterrows():
            st.write(f"⚠️ **{row['Artigo']}**: Comprar {int(row['A_Comprar'])} {row['Unidade']} (Faltam para atingir o mínimo)")
        
        st.table(compras[['Artigo', 'Stock_Atual', 'Nivel_Minimo', 'A_Comprar']])
    else:
        st.success("A despensa está cheia! Não é preciso comprar nada.")

# --- ABA D: ADICIONAR NOVO ---
with aba4:
    st.subheader("Adicionar novo item")
    with st.form("novo_artigo"):
        nome = st.text_input("Nome do Artigo")
        cat = st.text_input("Categoria")
        uni = st.text_input("Unidade de Medida (Ex: Lata, Litro)")
        s_atual = st.number_input("Stock Inicial", min_value=0)
        s_min = st.number_input("Nível Mínimo", min_value=0)
        
        if st.form_submit_button("Guardar Artigo"):
            novo_dado = {
                "Artigo": nome, "Categoria": cat, "Unidade": uni, 
                "Stock_Atual": s_atual, "Nivel_Minimo": s_min
            }
            st.session_state.df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
            guardar_dados(st.session_state.df)
            st.success(f"{nome} adicionado!")
            st.rerun()
