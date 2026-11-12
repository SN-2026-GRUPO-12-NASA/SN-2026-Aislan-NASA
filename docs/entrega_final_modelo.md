# Evidências de entrega - NASA CMR

**Repositório:** https://github.com/SN-2026-GRUPO-12-NASA/SN-2026-Aislan-NASA

**Página GitHub Pages:** https://sn-2026-grupo-12-nasa.github.io/SN-2026-Aislan-NASA/

**API REST JSON:** 

**GitHub Actions:**
<img width="1919" height="949" alt="image" src="https://github.com/user-attachments/assets/3762300f-4fd8-4d45-98d9-cd910732f968" />

**Supabase:**
<img width="1909" height="935" alt="image" src="https://github.com/user-attachments/assets/172a0905-ed25-4aae-8cc4-69583e9e0800" />
<img width="1913" height="923" alt="image" src="https://github.com/user-attachments/assets/256efbc0-8162-4b5e-a8af-93b45bda9e3d" />

**Planilha da turma:** [registrar onde links foram enviados, incluindo evidência]

<img width="1919" height="941" alt="image" src="https://github.com/user-attachments/assets/06a5ab78-22d1-492b-a20c-1e1d2e689729" />

**API REST JSON — Supabase**

**Endpoint:** https://impazlmkzwergverqawm.supabase.co/rest/v1/colecoes?select=cmr_id,title&limit=5

A API REST do Supabase permite consultar os registros científicos coletados da NASA CMR e armazenados no banco PostgreSQL.

O endpoint utiliza o método HTTP `GET` e retorna os dados em formato JSON, incluindo o identificador único (`cmr_id`) e o título (`title`) de cada coleção.

Para realizar a requisição, é necessário informar a chave pública do projeto no cabeçalho HTTP `apikey`. O acesso de leitura é autorizado pelas políticas RLS configuradas no Supabase.

O parâmetro `limit=5` restringe a resposta a cinco registros, facilitando a verificação do funcionamento da API.

Essa integração é utilizada pelo painel publicado no GitHub Pages, que consulta os dados armazenados no Supabase sem acessar diretamente a API da NASA.

<img width="544" height="794" alt="image" src="https://github.com/user-attachments/assets/903d66a4-6b88-4dbf-a0fa-61e0b66fdd1a" />
<img width="552" height="793" alt="image" src="https://github.com/user-attachments/assets/9b74ceb1-e113-4c92-9ffc-ed53bf0154a0" />

<img width="1724" height="66" alt="image" src="https://github.com/user-attachments/assets/a7af15c7-22a7-489d-b285-d03e1d8b8a06" />

