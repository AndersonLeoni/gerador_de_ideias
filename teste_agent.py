import os
import json
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# 1. OBRIGATÓRIO: Esta tem que ser a primeira instrução do Streamlit!
st.set_page_config(page_title="Gerador de Ideias", page_icon="🚴‍♂️", layout= "wide")

ARQUIVO_HISTORICO = "historico_ganchos.json"

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            return json.load(f)
    return[]

def salvar_historico(dados):
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()


st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Aumenta o título principal */
        h1 {
            font-size: 50px !important;
        }


        div.stButton > button {
            background-color: #2e86c1;
            color: white;
            border-radius: 8px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

load_dotenv() 

def gerar_ganchos(topico_usuario):
    os.environ["OPENAI_API_KEY"] = os.environ.get("GEMINI_API_KEY") 
    os.environ["OPENAI_API_BASE"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
    os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-3.5-flash"

    agent_test = Agent (
        role="Escritor de legendas para post viral Instagram",
        goal="Especialista em ganchos virais para o instagram, o foco principal é tecnologia e triathlon",
        backstory="Você é um grande sabio com mais de 20 anos nessas 2 areas"
    )

    tarefa_ideias = Task (
        description=f"Crie 3 ideias de legendas virais para instagram focadas no tópico digitado: '{topico_usuario}'. Conecte triathlon ao uso de inteligência artificial ou wearables.",
        expected_output="Uma lista (bullet list), com 3 legendas prontas para viralizar no instagram",
        agent=agent_test
    )

    equipe = Crew (
        agents=[agent_test],
        tasks=[tarefa_ideias],
        process=Process.sequential
    )

    return equipe.kickoff()

with st.sidebar:
    st.title("Menu")
    pagina_atual = st.radio("Ir para:", ["Nova Geração", "Ver historico"])
    
col_esq, col_centro, col_dir = st.columns([1, 2, 1])
# --- PÁGINA 1: O GERADOR ---
with col_centro:
    st.title("Gerador de Ideias")
    st.markdown("Digite um tema para criar as ideias!")
    topico = st.text_input("Tópico para o post")
    
    if st.button("Gerar Ideias"):
        if topico.strip() == "": 
            st.warning("Digite um tópico")
        else:
            with st.spinner("Trabalhando nas ideias..."):
                try:
                    resultado = gerar_ganchos(topico)

                    st.session_state.historico.append({
                        "tema": topico,
                        "ideias": str(resultado)
                    })

                    salvar_historico(st.session_state.historico)

                    st.success("Pronto!")
                    st.markdown("Sugestões:")
                    st.write(str(resultado))
                except Exception as e:
                    st.error(f"Ocorreu um erro ao conectar a IA: {e}")

# --- PÁGINA 2: O HISTÓRICO ---
    elif pagina_atual == "Ver historico":
        st.title("Historico de ganchos")

        if len(st.session_state.historico) == 0:
            st.info("Historico vazio, gere as primeiras ideias")

        else:
            for i, item in enumerate(reversed(st.session_state.historico)):
                with st.expander(f"Tema: {item['tema']}", expanded=False):
                    st.write(item["ideias"])

            if st.button("Limpar Historico"):
                st.session_state.historico = []
                st.rerun()
        