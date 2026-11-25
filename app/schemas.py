from typing import Literal, Optional
from pydantic import BaseModel, Field


class TriagemRequest(BaseModel):
    mensagem: str = Field(
        ...,
        min_length=5,
        max_length=3000,
        description="Relato ou mensagem simulada/anônima sobre saúde pública em Natal/RN.",
        examples=["Estou há três semanas aguardando retorno de exame na minha UBS e não consigo informação."],
    )
    bairro: Optional[str] = Field(
        default=None,
        max_length=120,
        description="Bairro de Natal/RN mencionado ou associado ao relato (opcional).",
        examples=["Alecrim"],
    )
    canal_origem: Optional[str] = Field(
        default="webhook",
        max_length=60,
        description="Canal de origem da mensagem (ex.: formulario_web, whatsapp_simulado, webhook).",
        examples=["formulario_web"],
    )


class TriagemResponse(BaseModel):
    categoria: Literal[
        "duvida",
        "reclamacao",
        "denuncia_sanitaria",
        "solicitacao_informacao",
        "elogio",
    ] = Field(..., description="Categoria principal da demanda.")
    prioridade: Literal["baixa", "media", "alta"] = Field(
        ..., description="Nível de prioridade sugerido para triagem."
    )
    encaminhamento_sugerido: str = Field(
        ...,
        description="Área ou fluxo sugerido no contexto de saúde pública/atenção básica de Natal/RN.",
    )
    resumo_curto: str = Field(
        ...,
        description="Resumo objetivo da mensagem em 1 ou 2 frases.",
    )
    justificativa: str = Field(
        ...,
        description="Breve explicação do porquê dessa classificação e prioridade.",
    )
    modelo_utilizado: str = Field(
        ...,
        description="Identificador do modelo Gemini usado na classificação.",
    )