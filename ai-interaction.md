# Histórico de Interação com IA

## Informações gerais

| Campo | Valor |
|---|---|
| **Grupo** | Grupo 12 — NASA CMR |
| **Integrantes** | Aislan Gabriel Franzão de Freitas |
| **API NASA escolhida** | Common Metadata Repository (CMR) — NASA Earthdata |
| **IA utilizada** | ChatGPT — OpenAI |
| **Data de início** | 28-09-2026 |
| **Data de conclusão** | 10-11-2026 |

---

## Interação 1 — Ampliação da quantidade de registros coletados

**Data:** 30-09-2026

**Objetivo:** Identificar como aumentar a quantidade de registros coletados pela API NASA CMR, ultrapassando os 501 registros inicialmente armazenados.

**Prompt enviado à IA:**

```
e depois do pages, acabou?

Tenho outra dúvida, no momento ele puxa 501 exatamente, como eu faço pra ter mais?
```

**Resumo da resposta:**

A IA explicou que o limite de registros estava relacionado à quantidade de páginas consultadas pelo script Python, e não necessariamente a uma limitação da API. Foi apresentada a possibilidade de ampliar o intervalo de páginas coletadas, utilizando o parâmetro `page_size` para definir a quantidade de registros por requisição e `page_num` para controlar a paginação.

Também foi explicado que o registro adicional provavelmente correspondia a um dado inserido anteriormente para testes.

**O que funcionou:**

A explicação permitiu compreender a relação entre número de páginas, tamanho dos lotes e quantidade de registros armazenados.

**O que precisou ajuste:**

A ampliação simples do número de páginas não resolvia a necessidade de continuar a coleta em execuções futuras. Era necessário implementar um mecanismo que armazenasse a última página processada.

---

## Interação 2 — Implementação de coleta incremental

**Data:** 30-09-2026

**Objetivo:** Permitir que cada nova execução do pipeline continue a coleta a partir do ponto anterior, buscando até 2.000 registros adicionais sem duplicar os existentes.

**Prompt enviado à IA:**

```
E esse é o limite? Se eu rodar mais uma vez vai subir pra 4000 ou só tentar de novo os 2000?
```

**Resumo da resposta:**

A IA propôs criar uma tabela adicional no Supabase, chamada `controle_pipeline`, responsável por armazenar a próxima página a ser consultada na API.

A estrutura foi planejada para permitir o avanço da coleta entre diferentes execuções:

- Primeira execução: páginas 1 a 20.
- Segunda execução: páginas 21 a 40.
- Terceira execução: páginas 41 a 60.

A lógica também preservaria a posição anterior caso houvesse uma falha, permitindo repetir a coleta sem gerar registros duplicados.

Um trecho representativo da implementação foi:

```python
db.table("controle_pipeline").update({
    "proxima_pagina": pagina + 1
}).eq("nome", "cmr").execute()
```

A atualização do checkpoint deve ocorrer somente depois da confirmação de que os dados foram armazenados.

**O que funcionou:**

O mecanismo incremental foi posteriormente implementado e testado. Em 3 de novembro, uma execução processou 2.000 registros em 20 lotes, sem erros, e avançou o checkpoint para a página 41.

Após essa execução, o banco possuía 4.011 coleções com identificadores únicos.

**O que precisou ajuste:**

A primeira versão publicada ainda não utilizava o checkpoint, mesmo depois da criação da tabela de controle. O problema foi identificado ao comparar o código do repositório com o estado real do banco.

A implementação precisou ser corrigida para consultar a página inicial armazenada no Supabase e atualizar essa posição depois de cada lote enviado com sucesso.

---

## Interação 3 — Verificação das pendências do projeto

**Data:** 03-11-2026

**Objetivo:** Identificar quais requisitos técnicos e documentais ainda precisavam ser concluídos antes da entrega.

**Prompt enviado à IA:**

```
O que falta agora?
```

**Resumo da resposta:**

A IA realizou uma análise da estrutura disponível no GitHub e comparou o projeto com os requisitos da atividade.

Foram identificados arquivos já existentes, como o coletor Python, o workflow do GitHub Actions, o painel HTML e o arquivo de dependências.

Também foram apontadas pendências relacionadas à documentação, especialmente o preenchimento do arquivo SQL, a elaboração do tutorial, a apresentação, o registro de interações com IA e a organização das evidências de funcionamento.

**O que funcionou:**

A resposta permitiu organizar as tarefas restantes por prioridade e diferenciar os requisitos de implementação dos requisitos de documentação e entrega.

**O que precisou ajuste:**

Alguns arquivos existiam, mas estavam incompletos ou não estavam organizados nos diretórios esperados. Foi necessário revisar a estrutura do repositório e preparar os documentos obrigatórios.

---

## Interação 4 — Auditoria técnica do GitHub e Supabase

**Data:** 03-11-2026

**Objetivo:** Realizar uma auditoria das implementações existentes, verificando o banco de dados, a segurança, os registros armazenados e o código publicado no GitHub.

**Prompt enviado à IA:**

```
[$supabase](app://asdk_app_69d3e5ee6a708191baa733f7b8931995) [$github](app://connector_76869538009648d5b282a4bb21c3d157) Te dei acesso ao Supabase e o Github, checa se tá tudo certo
```

**Resumo da resposta:**

Utilizando as integrações com GitHub e Supabase, a IA examinou o estado do projeto.

No banco de dados, foram confirmadas as três tabelas principais:

- `colecoes`: armazenamento dos metadados científicos.
- `execucoes`: histórico das execuções do pipeline.
- `controle_pipeline`: acompanhamento da paginação incremental.

Na primeira auditoria, foram encontrados 2.065 registros com identificadores únicos e 44 execuções concluídas.

A análise identificou problemas importantes:

- O script Python ainda consultava repetidamente as primeiras páginas.
- O painel não estava preparado para receber mais de 1.000 registros em uma consulta REST.
- O arquivo `sql/setup.sql` estava vazio.
- Havia permissões SQL públicas mais amplas do que o necessário.
- A documentação do repositório estava incompleta.

**O que funcionou:**

A auditoria permitiu identificar diferenças entre o funcionamento esperado e a implementação real, utilizando consultas ao banco e inspeção dos arquivos publicados.

Também foi possível verificar a existência das políticas RLS e das permissões necessárias para que o painel realizasse consultas públicas.

**O que precisou ajuste:**

Foram necessárias correções na coleta incremental, na paginação REST do painel e nas permissões do banco.

Durante a publicação das correções, uma versão do HTML substituiu a chave pública válida do Supabase por um texto de exemplo, provocando falhas de consulta no painel. O problema foi identificado e corrigido.

Após as correções, o GitHub Pages voltou a consultar o banco normalmente.

---

## Interação 5 — Síntese e planejamento da entrega final

**Data:** 10-11-2026

**Objetivo:** Organizar um resumo do desenvolvimento realizado e identificar as tarefas restantes para concluir a entrega.

**Prompt enviado à IA:**

```
Faça um resumo de tudo que foi feito.
```

**Resumo da resposta:**

A IA apresentou uma síntese da arquitetura do projeto, das tecnologias utilizadas, das funcionalidades implementadas e dos resultados verificados.

Também organizou as pendências documentais, incluindo a conclusão do README.

**O que funcionou:**

O resumo consolidou as diferentes etapas do desenvolvimento em um único registro, facilitando a organização da documentação.

**O que precisou ajuste:**

Foi necessário separar os requisitos já concluídos daqueles que ainda dependiam de revisão, especialmente os arquivos de documentação e as evidências exigidas pelo professor.

---

## Resumo final

**Total de interações centrais documentadas:** 6

### Principais contribuições da IA

- Explicação e organização da arquitetura NASA CMR → Python → Supabase → GitHub Pages.
- Desenvolvimento e aperfeiçoamento da coleta de dados em lotes.
- Implementação da lógica de paginação incremental.
- Orientações para evitar registros duplicados.
- Auxílio na integração com o banco de dados Supabase.
- Identificação de problemas na paginação REST do painel.
- Organização das atividades pendentes.

### Principais limitações encontradas

- Algumas soluções inicialmente propostas não funcionaram corretamente na implementação real.
- O primeiro coletor de 2.000 registros não avançava automaticamente entre execuções.
- O painel precisava de paginação adicional para consultar todos os registros do banco.
- As respostas da IA nem sempre representavam o estado real do projeto, tornando necessária a validação com logs, arquivos e consultas ao banco.

### Avaliação geral do uso da IA

A inteligência artificial contribuiu significativamente para o desenvolvimento do projeto, principalmente na compreensão das APIs e na integração com o Supabase. Também auxiliou na identificação de erros, na organização dos arquivos e na preparação da documentação. Entretanto, algumas soluções apresentadas exigiram modificações após os testes. Isso demonstrou que a geração de código não garante seu funcionamento correto. A utilização de logs, consultas SQL, testes no GitHub Actions e verificações no navegador foi fundamental para validar as implementações. Dessa forma, a IA atuou como ferramenta de apoio técnico e educacional, enquanto a avaliação dos resultados e a responsabilidade pela execução permaneceram sob supervisão humana.
