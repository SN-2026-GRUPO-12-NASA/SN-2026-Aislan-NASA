import os
import sys
import requests

from dotenv import load_dotenv
from supabase import create_client


# Carrega as variáveis do arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

CMR_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"


# Verifica se as variáveis do Supabase existem
if not SUPABASE_URL:
    print("Erro: SUPABASE_URL não encontrada no arquivo .env")
    sys.exit(1)

if not SUPABASE_SERVICE_KEY:
    print("Erro: SUPABASE_SERVICE_KEY não encontrada no arquivo .env")
    sys.exit(1)


# Cria conexão com o Supabase
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


def buscar_cmr():
    print("Buscando dados da NASA CMR...")

    params = {
        "page_size": 10
    }

    resposta = requests.get(
        CMR_URL,
        params=params,
        timeout=30
    )

    resposta.raise_for_status()

    dados = resposta.json()

    registros = dados["feed"]["entry"]

    print(f"{len(registros)} registros recebidos da NASA.")

    return registros


def normalizar(registro):
    return {
        "cmr_id": registro.get("id"),
        "title": registro.get("title"),
        "short_name": registro.get("short_name"),
        "version_id": registro.get("version_id"),
        "data_center": registro.get("data_center"),
        "processing_level": registro.get("processing_level_id"),
        "collection_type": registro.get("collection_data_type"),
        "time_start": registro.get("time_start"),
        "updated_at": registro.get("updated"),
        "platforms": registro.get("platforms"),
        "organizations": registro.get("organizations"),
        "summary": registro.get("summary"),
        "online_access": registro.get("online_access_flag"),
        "raw_data": registro
    }


def deduplicar(registros):
    registros_unicos = {}

    for registro in registros:
        cmr_id = registro.get("cmr_id")

        if cmr_id:
            registros_unicos[cmr_id] = registro

    return list(registros_unicos.values())


def salvar_colecoes(registros):
    print("Normalizando registros...")

    dados_normalizados = []

    for registro in registros:
        dados_normalizados.append(
            normalizar(registro)
        )

    dados_normalizados = deduplicar(
        dados_normalizados
    )

    print(
        f"{len(dados_normalizados)} registros "
        "após deduplicação."
    )

    print("Enviando dados ao Supabase...")

    supabase.table("colecoes").upsert(
        dados_normalizados,
        on_conflict="cmr_id"
    ).execute()

    print("Dados enviados ao Supabase.")

    return len(dados_normalizados)


def registrar_execucao(
    registros_processados,
    lotes,
    erros,
    status
):
    supabase.table("execucoes").insert({
        "registros_processados": registros_processados,
        "lotes": lotes,
        "erros": erros,
        "status": status
    }).execute()


def main():
    print("===================================")
    print("Pipeline NASA CMR iniciado")
    print("===================================")

    try:
        registros = buscar_cmr()

        quantidade = salvar_colecoes(
            registros
        )

        registrar_execucao(
            registros_processados=quantidade,
            lotes=1,
            erros=0,
            status="concluido"
        )

        print()
        print("Pipeline concluído com sucesso.")
        print(
            f"{quantidade} registros processados."
        )

    except Exception as erro:
        print()
        print("Erro durante o pipeline:")
        print(erro)

        try:
            registrar_execucao(
                registros_processados=0,
                lotes=0,
                erros=1,
                status="erro_critico"
            )

        except Exception as erro_log:
            print(
                "Não foi possível registrar "
                "o erro no Supabase:"
            )
            print(erro_log)

        sys.exit(1)


if __name__ == "__main__":
    main()