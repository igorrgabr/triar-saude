import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from app.gemini_service import classificar_demanda
from app.schemas import TriagemRequest, TriagemResponse

load_dotenv()

app = FastAPI(
    title="Triar Saúde API",
    description="API de triagem e classificação de demandas de saúde pública e atenção básica (Natal/RN) com FastAPI e Gemini.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "servico": "triar-saude-api",
        "modelo_configurado": os.getenv("GEMINI_MODEL", "gemini-4-hydrogen"),
    }


@app.post("/triagem", response_model=TriagemResponse)
def triar_mensagem(payload: TriagemRequest) -> TriagemResponse:
    try:
        return classificar_demanda(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao processar triagem com o modelo de IA: {exc}",
        ) from exc