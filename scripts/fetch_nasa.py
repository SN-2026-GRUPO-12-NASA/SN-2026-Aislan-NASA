import os
import sys
import requests

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

CMR_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"

PAGE_SIZE = 100
MAX_REGISTROS = 2000
TAMANHO_LOTE = 100


if not SUPABASE_URL:
    print("Erro: SUPABASE_URL não encontrada.")
    sys.exit(1)

if not SUPABASE_SERVICE_KEY:
    print("Erro: SUPABASE_SERVICE_KEY não encontrada.")
    sys.exit(1)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


def buscar_cmr():
    print("===================================")
    print("Buscando dados da NASA CMR")
    print("===================================")

    todos_registros = []

    max_paginas = MAX_REGISTROS // PAGE_SIZE

    for pagina in range(1, max_paginas + 1):
        params = {
            "page_size": PAGE_SIZE,
            "page_num": pagina
        }

        print(
            f"Buscando página {pagina}/{max_paginas}..."
        )

        resposta = requests.get(
            CMR_URL,
            params=params,
            timeout=30
        )

        resposta.raise_for_status()

        dados = resposta.json()
        registros = dados["feed"].get("entry", [])

        print(
            f"Página {pagina}: "
            f"{len(registros)} registros recebidos."
        )

        if not registros:
            print("Nenhum registro adicional encontrado.")
            break

        todos_registros.extend(registros)

        if len(todos_registros) >= MAX_REGISTROS:
            todos_registros = todos_registros[:MAX_REGISTROS]
            break

        if len(registros) < PAGE_SIZE:
            print("Última página encontrada.")
            break

    print()
    print(
        f"Total recebido da NASA: "
        f"{len(todos_registros)} registros."
    )

    return todos_registros


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
    print()
    print("Normalizando registros...")

    dados_normalizados = [
        normalizar(registro)
        for registro in registros
    ]

    dados_normalizados = deduplicar(
        dados_normalizados
    )

    print(
        f"{len(dados_normalizados)} registros "
        "após deduplicação."
    )

    total_processados = 0
    lotes_processados = 0
    erros = 0

    for inicio in range(
        0,
        len(dados_normalizados),
        TAMANHO_LOTE
    ):
        lote = dados_normalizados[
            inicio:inicio + TAMANHO_LOTE
        ]

        numero_lote = lotes_processados + 1

        print(
            f"Enviando lote {numero_lote} "
            f"com {len(lote)} registros..."
        )

        try:
            supabase.table("colecoes").upsert(
                lote,
                on_conflict="cmr_id"
            ).execute()

            total_processados += len(lote)

            print(
                f"Lote {numero_lote} enviado "
                "com sucesso."
            )

        except Exception as erro_lote:
            erros += 1

            print(
                f"Erro no lote {numero_lote}:"
            )
            print(erro_lote)

        lotes_processados += 1

    return (
        total_processados,
        lotes_processados,
        erros
    )


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

        processados, lotes, erros = salvar_colecoes(
            registros
        )

        if erros == 0:
            status = "concluido"

        elif processados > 0:
            status = "erro_parcial"

        else:
            status = "erro_critico"

        registrar_execucao(
            registros_processados=processados,
            lotes=lotes,
            erros=erros,
            status=status
        )

        print()
        print("===================================")
        print("Resumo da execução")
        print("===================================")
        print(f"Registros processados: {processados}")
        print(f"Lotes processados: {lotes}")
        print(f"Erros: {erros}")
        print(f"Status: {status}")

        if status != "concluido":
            sys.exit(1)

    except Exception as erro:
        print()
        print("Erro crítico durante o pipeline:")
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