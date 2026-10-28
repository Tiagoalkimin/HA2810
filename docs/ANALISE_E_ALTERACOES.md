# Análise do código e decisões

## Inspeção antes das alterações

O arquivo recebido contém uma aplicação Streamlit, com 19 telas registradas em app.py. Os modelos estão separados em models e os cálculos em core. Não havia suíte de testes no ZIP.

Funcionalidades encontradas:

* Três computadores com modelos de CPU, GPU, componentes e refrigeração.
* Atividades leves, moderadas e pesadas com faixas de utilização.
* Potência não linear por componente, integração de energia e projeção financeira.
* Modelo térmico de primeira ordem com evolução gradual.
* Simulador com duas trilhas, histórico e cinco decisões de intervenção.
* Injeção de potência extra para representar processos desnecessários.
* Detecção por faixa esperada da tarefa com margem de 15%.
* Recomendações, relatório e comparação entre computadores sob estresse.
* Oito experimentos, tabelas e exportação CSV no laboratório.
* Telas explicativas de eletrônica, refrigeração, impactos e soluções.

## Gargalos observados

O caminho inicial exigia várias telas teóricas e configuração antes de mostrar os números. A tela de simulação combinava métricas de CPU, GPU, potência, temperatura, energia, custo, duração, estresse, desempenho e FPS, além de gráficos e decisões.

O botão de desperdício alterava waste_w sem avançar a simulação. O snapshot, portanto, ainda mostrava o registro anterior até um avanço posterior. A comparação de uma decisão era renderizada logo antes de st.rerun e desaparecia. Isso impedia que o público percebesse a relação entre clique e efeito.

A trilha baseline original não recebia o desperdício injetado na trilha real. Usar diretamente seu percentual histórico como economia do novo cenário seria inadequado. O novo painel calcula a diferença entre potências antes e depois com a mesma duração mensal. Sua trilha contrafactual também mantém a parcela extra após a intervenção.

## Intervenção localizada

A interface rápida foi adicionada como entrada do app existente. Todas as funções antigas e todos os módulos originais de core e models permanecem intactos. O README original está arquivado em docs/README_ORIGINAL.md.

O controlador QuickDemo usa pontos médios das faixas da tarefa, eliminando variação aleatória de utilização. Os cálculos continuam passando pelo motor original. A faixa para detecção continua sendo a faixa completa da tarefa original. A decisão verificar_processos remove apenas a potência extra. Não foi usado o modo economia porque ele alteraria a carga útil e confundiria a comparação.

Callbacks atualizam o estado antes da renderização. O resultado permanece na sessão após qualquer atualização e desaparece apenas ao reiniciar. Os botões são habilitados na ordem apropriada e o controlador ignora repetição de operações.

A temperatura é calculada pelo modelo original em 180 segundos simulados por cenário. Isso permite apresentar o efeito rapidamente sem afirmar que o resfriamento é instantâneo. O consumo extra é aditivo, portanto não há aumento inventado de utilização de CPU/GPU.

## Escopo e limites de validação

Os testes verificam o fluxo rápido e a compatibilidade básica do motor legado. Não constituem certificação física ou validação de eficiência de um computador real. O funcionamento detalhado de todas as telas educativas antigas não foi revalidado de ponta a ponta, pois seus módulos permaneceram inalterados.

A validação visual por captura de navegador não pôde ser concluída neste ambiente, pois o download do navegador retornou um arquivo inválido. A interface foi exercitada com Streamlit AppTest, sem exceções. É necessário conferir o enquadramento no computador e projetor do evento.
