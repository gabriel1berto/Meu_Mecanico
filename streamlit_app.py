import streamlit as st
import google.generativeai as genai
import os
import pandas as pd

# Defina a chave da API diretamente no código
api_key = "AIzaSyDS60UHapVgSZteCD0-A7UTcsHGFpojRhs"  # Substitua pelo seu valor real da chave da API

# Verifique se a chave da API foi configurada corretamente
if not api_key:
    st.error("Erro: A chave da API não foi encontrada.")
    st.stop()  # Para a execução do código

# Configura a API com a chave
try:
    genai.configure(api_key=api_key)  # Passa a chave da API para a configuração
except Exception as e:
    st.error(f"Erro ao configurar a API: {e}")
    st.stop()

# Cria o modelo
generation_config = {
    "temperature": 0.5,
    "top_p": 0.5,
    "top_k": 50,
    "max_output_tokens": 700,
    "response_mime_type": "text/plain",
}

safety_settings = [
    {"category": "harm_category_harassment", "threshold": "block_none"},
    {"category": "harm_category_hate_speech", "threshold": "block_medium_and_above"},
    {"category": "harm_category_sexually_explicit", "threshold": "block_medium_and_above"},
    {"category": "harm_category_dangerous_content", "threshold": "block_medium_and_above"},
]

try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction="Pablo é um mecânico com anos de experiência, especialista em manuais de veículos e diagnóstico de problemas comuns. Combinando profundo conhecimento técnico com uma comunicação direta, simples e acessível, explicando de forma sucinta e clara qualquer questão mecânica. Além disso, ele sugere soluções práticas. Ppablo gosta de orientar os donos de carros sobre boas práticas de manutenção preventiva, reforçando a importância de cuidar do veículo para evitar problemas futuros.",
    )
except Exception as e:
    st.error(f"Erro ao criar o modelo: {e}")
    st.stop()

# inicializa a sessão de chat e o histórico
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'round' not in st.session_state:  # Adicione o controle de rodada
    st.session_state.round = 1
  
# função para salvar dados em um arquivo csv
def save_to_csv(round_number, user_message, bot_response, voto1, voto2):
    file_path = "chatbot_data.csv"  # caminho direto, mudar conforme necessário
    # cria um dataframe a partir dos dados
    data = {
        "round": [round_number],
        "user message": [user_message],
        "bot response": [bot_response],
        "vote 1": [voto1],
        "vote 2": [voto2]
    }

    df = pd.DataFrame(data)  # Corrigido de pd.dataframe para pd.DataFrame

    try:
        # salva o dataframe no csv (adicionando aos dados existentes)
        df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)  # Corrigido index=false para index=False
    except Exception as e:  # Corrigido de 'exception' para 'Exception'
        st.error(f"erro ao salvar os dados no arquivo csv: {e}")
# Layout da página
st.title("🚗💨 Carros são o meu negócio!")

# Criar duas colunas: uma para interação do usuário e outra para a votação
col1, col2 = st.columns([7,3])  # 1 parte para col1 e 2 partes para col2

# Coluna à esquerda para o chatbot e interações
with col1:
    # Instruções para o usuário
    st.markdown(
        "Pode comecar falando seu nome, modelo e ano do seu veículo ⚡ <br><br>"
        "",
        unsafe_allow_html=True
    )

    # Criar uma lista para armazenar as mensagens se não existir
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Exibindo mensagens anteriores em um expander
    with st.expander("histórico de mensagens", expanded=True):
        for msg in st.session_state.messages:
            st.text(msg)

    # Caixa de entrada para o usuário
    user_input = st.text_input("Como posso te ajudar??: ", "")

    # Quando o usuário envia a mensagem
    if st.button("Enviar"):
        if user_input:
            # Adiciona a mensagem do usuário à sessão
            st.session_state.messages.append(f"Você: {user_input}")

            # Envia a mensagem do usuário para o chatbot e obtém a resposta
            try:
                response = st.session_state.chat_session.send_message(user_input)
                model_response = response.text

                # Adiciona a resposta do chatbot à sessão
                st.session_state.messages.append(f"Pablo, mecânico: {model_response}")

                # Salva as mensagens e os votos no CSV
                if 'voto' in st.session_state and 'voto2' in st.session_state:
                    save_to_csv(user_input, model_response, st.session_state.voto, st.session_state.voto2)

            except Exception as e:
                error_message = str(e)
                st.error(f"Erro ao obter a resposta do chatbot: {error_message}")
                if "500" in error_message:
                    st.warning("Não entendi bem sua pergunta, pode ser um pouco mais específico?")
                elif "429" in error_message:
                    st.error("Não entendi bem sua pergunta, pode ser um pouco mais específico?")
                else:
                    st.error(f"Erro desconhecido: {error_message}")



# coluna à direita para a avaliação (30%)
with col2:
    with st.expander("Podemos fazer seu carro não quebrar?", expanded=True):  # 'expanded=True' para mostrar a caixa já aberta

        # Subtítulo
        st.markdown("<small> Não é só botar gasolina e sair rodando, queremos te ajudar a ter o melhor do seu carro!</small>", unsafe_allow_html=True)
        # criando duas colunas para o slider e o botão
        vote_col1, vote_col2 = st.columns([3, 2])  # o slider ocupa 3 partes e o botão ocupa 1 parte

        with vote_col1:
            # slider para votar
            voto1 = st.slider("De 0 a 10:", min_value=0, max_value=10, value=5, key="voto_slider")

        with vote_col2:
            # botão para enviar o voto
            if st.button("go"):
                st.session_state.voto1 = voto1  # armazenando o voto na sessão
                st.success(f"👍")

        # adicionando uma linha com texto menor
        st.markdown("", unsafe_allow_html=True)

        # fechando o bloco
        st.markdown("</div>", unsafe_allow_html=True)    # Todo o conteúdo da col2 deve estar dentro do bloco estilizado

    # Criando duas colunas para o slider e o botão
    vote_col1, vote_col2 = st.columns([3, 1])  # O slider ocupa 3 partes e o botão ocupa 1 parte

    with st.expander("Podemos fazer não levar mais multas?", expanded=True):

        # Subtítulo
        st.markdown("<small>Não é só botar gasolina e sair rodando, queremos te ajudar a ter o melhor do seu carro!</small>", unsafe_allow_html=True)

        # Criando duas colunas para o slider e o botão
        vote_col1, vote_col2 = st.columns([3, 2])  # o slider ocupa 3 partes e o botão ocupa 1 parte

        with vote_col1:  
            # Slider para votar
            voto2 = st.slider("De 0 a 10:", min_value=0, max_value=10, value=5, key="voto_slider_usuario_2")  # chave única para o slider

        with vote_col2:
            # Botão para enviar o voto
            if st.button("Go", key="botao_enviar_voto_2"):  # chave única para o botão
                st.session_state.voto2 = voto2  # Armazenando o voto na sessão
                st.success("👍")
