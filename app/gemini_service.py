import json
import os
from google import genai
from google.genai import types
from app.schemas import TriagemRequest, TriagemResponse

SYSTEM_INSTRUCTION = """
Você é um assistente de triagem e organização de demandas de saúde pública e atenção básica,
com foco no contexto de Natal (Rio Grande do Norte) e no sistema público de saúde (SUS).

Sua função é analisar mensagens simuladas ou anônimas e retornar APENAS um JSON válido
seguindo exatamente o schema solicitado, sem markdown extra fora do JSON.

Diretrizes de classificação:
- categoria:
  * "duvida": perguntas sobre funcionamento de serviços, vacinação, horários, documentos ou fluxos.
  * "solicitacao_informacao": pedidos específicos de andamento, orientação de canal ou consulta de informação pública.
  * "reclamacao": insatisfações com atendimento, demora, estrutura, falta de insumo ou dificuldade de acesso.
  * "denuncia_sanitaria": relatos de risco sanitário ou ambiental coletivo (ex.: focos de água parada/arboviroses, descarte irregular de risco, condições insalubres). Nunca trate como emergência clínica imediata.
  * "elogio": reconhecimento positivo de equipe, unidade ou serviço.
- prioridade:
  * "alta": relatos com risco sanitário coletivo relevante, situação que exige atenção rápida da equipe/vigilância ou bloqueio crítico de acesso.
  * "media": reclamações de atendimento/demora, solicitações pendentes ou dúvidas que impactam o acompanhamento do usuário.
  * "baixa": dúvidas gerais, pedidos simples de informação ou elogios.
- encaminhamento_sugerido: escolha o destino mais coerente com a necessidade real do relato (evitando repetir cegamente a unidade onde o usuário já relata falha ou falta de retorno):
  * "Acompanhamento de Exames e Fluxos (UBS / Regulação)": quando o relato trata de resultado/retorno de exame, agendamento ou trâmite assistencial.
  * "Ouvidoria SUS / Gestão do Atendimento": quando há reclamação de demora sem resposta, falta de informação ou falha de comunicação recorrente.
  * "Vigilância Ambiental / Saúde Coletiva": quando há risco sanitário ou ambiental coletivo (ex.: focos de arboviroses/água parada).
  * "UBS / Atenção Básica": quando é um fluxo ou dúvida comum da atenção básica sem reclamação de bloqueio/falta de retorno.
  * "Registro e Acompanhamento": para elogios ou registros gerais.
- resumo_curto: escreva em português claro, objetivo, em 1 a 2 frases, sem inventar fatos.
- justificativa: explique de forma concisa o critério usado para categoria, prioridade e encaminhamento.
"""


def _build_user_prompt(payload: TriagemRequest) -> str:
    linhas = [
        "Contexto local: Natal, Rio Grande do Norte (saúde pública / atenção básica / saúde coletiva).",
        f"Canal de origem: {payload.canal_origem or 'nao_informado'}",
        f"Bairro informado: {payload.bairro or 'nao_informado'}",
        f"Mensagem para triagem: {payload.mensagem.strip()}",
    ]
    return "\n".join(linhas)


def classificar_demanda(payload: TriagemRequest) -> TriagemResponse:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Variável GEMINI_API_KEY não configurada no ambiente.")

    model_name = os.getenv("GEMINI_MODEL", "gemini-4-hydrogen")
    client = genai.Client(api_key=api_key)

    # Schema interno sem o campo de metadado modelo_utilizado, que adicionamos após validar
    class ModeloClassificacao(TriagemResponse):
        pass

    response = client.models.generate_content(
        model=model_name,
        contents=_build_user_prompt(payload),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=ModeloClassificacao,
        ),
    )

    if not response.text:
        raise RuntimeError("O modelo Gemini não retornou conteúdo textual.")

    dados = json.loads(response.text)
    dados["modelo_utilizado"] = model_name
    return TriagemResponse.model_validate(dados)