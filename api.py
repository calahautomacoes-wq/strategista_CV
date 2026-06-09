"""
StrategisTA — API para integração com Typebot
Endpoints: /health, /verificar-telefone, /analisar-cv, /analisar-cv-url, /salvar
"""
import re
import httpx
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="StrategisTA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class TelefoneRequest(BaseModel):
    telefone: str


class AnalisarUrlRequest(BaseModel):
    url: str
    telefone: str = ""


class SalvarRequest(BaseModel):
    telefone:    str
    nome:        str = ""
    email:       str = ""
    cidade:      str = ""
    estado:      str = ""
    formacao:    str = ""
    experiencia: str = ""
    habilidades: str = ""
    idiomas:     str = ""
    resumo:      str = ""
    nota:        float = 0.0
    justificativa: str = ""
    sexo:        str = "prefiro não dizer"
    lgpd:        str = "não"
    arquivo:     str = ""


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/verificar-telefone")
def verificar_telefone(body: TelefoneRequest):
    """Verifica se o telefone já está cadastrado no banco."""
    from utils.database import get_cv_by_phone, log_access

    digits = re.sub(r"\D", "", body.telefone)
    if not digits:
        raise HTTPException(status_code=422, detail="Telefone inválido")

    dados = get_cv_by_phone(digits)
    if dados:
        log_access(digits, dados.get("nome", ""), "acessou_sistema_typebot")
        # Retorna estrutura plana para compatibilidade com Typebot bot-engine
        # (bodyPath aninhado como "dados.nome" não é suportado)
        return {
            "existe": True,
            "nome":         dados.get("nome", ""),
            "email":        dados.get("email", ""),
            "cidade_estado": dados.get("cidade_estado", ""),
            "formacao":     dados.get("formacao", ""),
            "experiencia":  dados.get("experiencia", ""),
            "habilidades":  dados.get("habilidades", ""),
            "idiomas":      dados.get("idiomas", ""),
            "resumo":       dados.get("resumo", ""),
            "nota":         str(dados.get("nota", "")),
            "arquivo":      dados.get("arquivo", ""),
        }

    log_access(digits, "", "novo_acesso_typebot")
    return {"existe": False}


@app.post("/analisar-cv")
async def analisar_cv(arquivo: UploadFile = File(...)):
    """Recebe um arquivo PDF ou DOCX, extrai texto e analisa com Claude."""
    from utils.cv_parser import extract_text
    from utils.cv_analyzer import analyze_cv

    extensao = (arquivo.filename or "").lower().split(".")[-1]
    if extensao not in ("pdf", "docx"):
        raise HTTPException(status_code=422, detail="Formato inválido. Use PDF ou DOCX.")

    content = await arquivo.read()
    try:
        texto = extract_text(content, arquivo.filename)
        dados  = analyze_cv(texto, arquivo.filename)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {exc}")

    return dados


@app.post("/analisar-cv-url")
async def analisar_cv_url(body: AnalisarUrlRequest):
    """Recebe URL de arquivo do Typebot, baixa, extrai texto e analisa com Claude."""
    from utils.cv_parser import extract_text
    from utils.cv_analyzer import analyze_cv

    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=422, detail="URL do arquivo não informada.")

    # Detecta extensão pela URL
    filename = url.split("?")[0].split("/")[-1] or "curriculo.pdf"
    extensao = filename.lower().split(".")[-1]
    if extensao not in ("pdf", "docx"):
        # Tenta inferir pelo Content-Type
        extensao = "pdf"
        filename = "curriculo.pdf"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            content = resp.content

        # Detecta pelo Content-Type se necessário
        ct = resp.headers.get("content-type", "")
        if "word" in ct or "docx" in ct:
            filename = "curriculo.docx"
        else:
            filename = "curriculo.pdf"

        texto = extract_text(content, filename)
        dados  = analyze_cv(texto, filename)

        # Garante que o telefone esteja no dado se a IA não encontrou
        if not dados.get("telefone") and body.telefone:
            dados["telefone"] = re.sub(r"\D", "", body.telefone)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {exc}")

    return dados


@app.post("/salvar")
def salvar(body: SalvarRequest):
    """Insere um novo registro de candidato no banco."""
    from utils.database import batch_insert_cvs, log_access

    telefone_digits = re.sub(r"\D", "", body.telefone)
    cidade_estado   = ", ".join(filter(None, [
        body.cidade.strip(),
        body.estado.strip().upper(),
    ]))

    dados = {
        "arquivo":       body.arquivo or f"typebot_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "nome":          body.nome.strip(),
        "email":         body.email.strip(),
        "telefone":      telefone_digits,
        "cidade_estado": cidade_estado,
        "formacao":      body.formacao.strip(),
        "experiencia":   body.experiencia.strip(),
        "habilidades":   body.habilidades.strip(),
        "idiomas":       body.idiomas.strip(),
        "resumo":        body.resumo.strip(),
        "nota":          body.nota,
        "justificativa": body.justificativa.strip(),
        "sexo":          body.sexo,
        "lgpd":          body.lgpd,
    }

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        batch_insert_cvs([(dados, ts)])
        acao = "atualizou_curriculo_typebot" if body.arquivo else "enviou_curriculo_typebot"
        log_access(telefone_digits, body.nome, acao)
        if body.lgpd == "sim":
            log_access(telefone_digits, body.nome, "aceite_lgpd")
        else:
            log_access(telefone_digits, body.nome, "recusou_lgpd")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar: {exc}")

    return {"sucesso": True, "mensagem": "Cadastro salvo com sucesso!"}
