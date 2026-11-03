# Registro de interações com IA

**Nota de transparência:** síntese temática do processo, reconstruída a partir das decisões discutidas durante o desenvolvimento. **Não é transcrição literal de todos os prompts e respostas.** O histórico de conversa original deve ser anexado/consultado se o professor exigir reprodução fiel.

## 1. Organização da arquitetura
- **Objetivo:** transformar o enunciado em um pipeline NASA CMR → Python → Supabase → GitHub Pages.
- **Uso de IA:** explicar os componentes, os arquivos e os segredos do GitHub Actions.
- **Validação humana:** criar projeto e tabelas, testar workflow e corrigir configurações.

## 2. Erros de integração
- **Problemas encontrados:** URL com parâmetros de consulta inválidos na CMR; falhas de DNS; função de log inexistente; erros de configuração de `.env` e do YAML.
- **Ajustes:** usar `collections.json`, `page_size` e `page_num`; implementar `registrar_execucao`; configurar Secrets no Actions.
- **Resultado:** execuções concluídas com logs gravados na tabela `execucoes`.

## 3. Paginação, duplicatas e persistência
- **Objetivo:** coletar mais de 100 registros, em blocos de 100, sem duplicar os anteriores.
- **Uso de IA:** incrementar páginas, recomendar `upsert(on_conflict='cmr_id')`, criar `controle_pipeline` para continuar depois da última página.
- **Revisão crítica:** a primeira versão do código buscava sempre as páginas 1–20, mesmo com a tabela de checkpoint criada. Posteriormente, foi preparada correção para avançar somente depois de lotes persistidos.

## 4. Interface web
- **Objetivo:** filtrar, pesquisar e exibir dados armazenados no Supabase.
- **Uso de IA:** revisar o front-end, diferenciar consulta à API NASA de consulta à API REST do Supabase e verificar sanitização de texto externo.
- **Revisão crítica:** uma requisição REST sem paginação podia exibir somente os primeiros 1.000 resultados; foi preparado carregamento em lotes.

## 5. Auditoria final
- **Ferramentas consultadas:** GitHub e Supabase por integrações conectadas.
- **Constatações em 03/11/2026:** 2.065 `cmr_id` distintos; 44 execuções registradas como concluídas; permissões de escrita anon inadequadas eram possíveis em SQL, embora bloqueadas por RLS.
- **Ação corretiva:** revogação de privilégios de escrita para `anon` e `authenticated`, preservando SELECT nas tabelas públicas; criação/validação do check de status.

## Declaração
A IA auxiliou com código, explicações e revisão. As decisões técnicas, a execução das tarefas e a responsabilidade pela validação final são humanas. Completar com capturas e trechos reais do histórico antes da entrega caso exigido.
