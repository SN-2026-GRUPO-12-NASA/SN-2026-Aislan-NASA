# Reflexão crítica sobre uso de IA

O apoio da inteligência artificial acelerou a compreensão da arquitetura do projeto, especialmente a integração entre API REST, Python, banco de dados e GitHub Actions. A ferramenta ajudou a estruturar funções, interpretar mensagens de erro e explicar políticas RLS.

A maior limitação observada foi a diferença entre **um código que parece correto** e **um código realmente verificado**. A implementação inicial buscava repetidamente as primeiras páginas da NASA. Mesmo após a criação da tabela `controle_pipeline`, o coletor publicado não utilizava seu checkpoint. O problema só ficou claro ao comparar o código com o estado real do banco.

Também foi necessário distinguir permissões SQL de políticas de segurança: ter RLS ativo não significa que os `GRANT` estejam restritos. A revisão removeu privilégios de escrita dos papéis públicos, mantendo o acesso somente de leitura usado pelo painel.

Outra aprendizagem foi a paginação em dois níveis. A NASA fornece páginas de coleções, mas o Supabase também limita resultados por resposta REST. Resolver um dos lados não basta para mostrar todos os registros na interface.

Assim, o uso mais confiável da IA ocorreu quando cada sugestão foi confrontada com registros reais, logs e consultas ao banco. A IA contribui para formular soluções, mas não substitui testes, rastreabilidade das mudanças, documentação e avaliação crítica do desenvolvedor.
