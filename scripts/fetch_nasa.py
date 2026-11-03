"""Pipeline incremental NASA CMR -> Supabase.

Processa ate 20 paginas de 100 colecoes por execucao; persiste um checkpoint
apos cada lote confirmado. Reexecutar apos erro nao duplica cmr_id.
"""
import os
import sys
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
URL = os.getenv('SUPABASE_URL')
KEY = os.getenv('SUPABASE_SERVICE_KEY')
CMR_URL = 'https://cmr.earthdata.nasa.gov/search/collections.json'
PAGE_SIZE = 100
PAGES_PER_RUN = 20


def normalizar(item):
    return {
        'cmr_id': item['id'],
        'title': item.get('title'),
        'short_name': item.get('short_name'),
        'version_id': item.get('version_id'),
        'data_center': item.get('data_center'),
        'processing_level': item.get('processing_level_id'),
        'collection_type': item.get('collection_data_type'),
        'time_start': item.get('time_start'),
        'updated_at': item.get('updated'),
        'platforms': item.get('platforms'),
        'organizations': item.get('organizations'),
        'summary': item.get('summary'),
        'online_access': item.get('online_access_flag'),
        'raw_data': item,
    }


def main():
    if not URL or not KEY:
        print('Configure SUPABASE_URL e SUPABASE_SERVICE_KEY.', file=sys.stderr)
        return 1

    db = create_client(URL, KEY)
    processados, lotes, erros, status = 0, 0, 0, 'concluido'
    try:
        controle = (db.table('controle_pipeline')
                    .select('proxima_pagina').eq('nome', 'cmr').single().execute())
        pagina_inicial = int(controle.data['proxima_pagina'])
        print(f'Iniciando na pagina {pagina_inicial}; ate {PAGES_PER_RUN} lotes.')

        with requests.Session() as session:
            for pagina in range(pagina_inicial, pagina_inicial + PAGES_PER_RUN):
                response = session.get(CMR_URL,
                    params={'page_size': PAGE_SIZE, 'page_num': pagina}, timeout=40)
                response.raise_for_status()
                entradas = response.json().get('feed', {}).get('entry', [])
                if not entradas:
                    print('Sem mais colecoes retornadas. Checkpoint preservado.')
                    break

                # Evita duplicacoes na mesma resposta e ignora itens sem ID.
                registros = {item['id']: normalizar(item)
                             for item in entradas if item.get('id')}
                if not registros:
                    raise ValueError(f'Pagina {pagina} nao contem IDs validos.')

                db.table('colecoes').upsert(
                    list(registros.values()), on_conflict='cmr_id').execute()
                processados += len(registros)
                lotes += 1

                # Só avança depois do UPSERT confirmado.
                db.table('controle_pipeline').update({
                    'proxima_pagina': pagina + 1,
                }).eq('nome', 'cmr').eq('proxima_pagina', pagina).execute()
                # Verifica que o checkpoint realmente avançou.
                checkpoint = (db.table('controle_pipeline')
                              .select('proxima_pagina').eq('nome', 'cmr')
                              .single().execute())
                if int(checkpoint.data['proxima_pagina']) != pagina + 1:
                    raise RuntimeError(f'Falha em confirmar checkpoint da pagina {pagina}.')

                print(f'Pagina {pagina}: {len(registros)} colecoes; '
                      f'total desta execucao: {processados}.')
                if len(entradas) < PAGE_SIZE:
                    print('Pagina parcial: fim do conjunto atual.')
                    break
    except Exception as exc:
        erros += 1
        status = 'erro_parcial' if processados > 0 else 'erro_critico'
        print(f'Erro na coleta: {exc}', file=sys.stderr)

    try:
        db.table('execucoes').insert({
            'registros_processados': processados,
            'lotes': lotes,
            'erros': erros,
            'status': status,
        }).execute()
    except Exception as exc:
        print(f'Erro ao registrar execucao: {exc}', file=sys.stderr)
        return 1

    print(f'Status: {status}; registros: {processados}; lotes: {lotes}; erros: {erros}')
    return 0 if status == 'concluido' else 1


if __name__ == '__main__':
    sys.exit(main())
