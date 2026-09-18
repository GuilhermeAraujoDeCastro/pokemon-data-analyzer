# Extrator e Analisador de Dados Pokémon

Script em Python que junta dados de Pokémon (da PokéAPI ao vivo ou de um CSV já salvo), organiza tudo numa tabela e responde perguntas estatísticas de verdade: qual combinação de tipos é mais rara, qual tipo tem a maior velocidade média, se existe correlação entre peso e defesa. Gera os gráficos dessas respostas e, se quiser, exporta o dataset pra um banco SQL. É o terceiro e último projeto da minha trilogia Pokémon: o primeiro foi o Simulador de Batalha em Python, o segundo foi o Team Builder em C#/ASP.NET Core, e esse aqui troca jogo e site por análise de dados.

## Como configurar

```bash
cd extrator-dados-pokemon
pip install -r requirements.txt
```

## Como rodar

Sem nenhum argumento, roda em cima do CSV de exemplo que já vem no projeto (20 Pokémon, sem precisar de internet):

```bash
python3 run_extractor.py
```

Isso imprime o relatório no terminal e salva 4 gráficos em `charts/`. Pra buscar dados de verdade, direto da PokéAPI (a API pública oficial, com mais de mil Pokémon):

```bash
python3 run_extractor.py --source api --limit 151
```

`--limit` controla quantos Pokémon buscar (151 pega a Pokédex inteira de Kanto; pode subir esse número). Isso salva o dataset baixado em `data/pokemon_data.csv`, pra não precisar buscar de novo toda vez, e depois é só rodar `python3 run_extractor.py --source csv --input data/pokemon_data.csv` pra reanalisar sem tocar a rede.

Outras opções: `--charts-dir` muda a pasta dos gráficos, `--no-charts` pula a geração deles, e `--sqlite-db caminho.db` exporta o dataset pra um banco SQLite (passo opcional, útil se quiser conectar um Power BI ou outra ferramenta de dashboard nesse banco depois).

## Sobre o CSV de exemplo (leia antes de tirar conclusões dele)

Os 20 Pokémon em `data/sample_pokemon.csv` são reais, escolhidos por serem bem conhecidos (os iniciais, lendários e alguns clássicos como Snorlax, Ditto e Magikarp), e eu digitei os stats base, altura e peso de cada um de memória, conferindo contra o que lembro de cada um com mais confiança. Ainda assim é digitação manual, não veio de uma fonte automatizada, então pode ter algum valor errado num Pokémon ou outro. Esse CSV existe só pra o script funcionar direto da caixa e pros testes automatizados rodarem sem depender de internet: pra qualquer conclusão que você queira levar a sério, rode com `--source api` e pegue os números direto da fonte oficial.

Também não consegui testar a chamada de rede de verdade contra a PokéAPI a partir daqui, pelo mesmo motivo dos outros projetos: o ambiente onde eu rodo código não tem saída de rede liberada pra sites externos. O que testei foi a lógica de processamento inteira (limpeza dos dados, análise, gráficos) usando exemplos de resposta da API que montei no formato real e documentado dela, incluindo o detalhe de que ela manda altura em decímetros e peso em hectogramas, não em metros e quilos direto. Roda `--source api` uma vez pra confirmar que a chamada de verdade funciona; se der algum erro, me manda a mensagem que eu ajusto.

## O que o script responde

Rodando com o CSV de exemplo, hoje ele responde isto:

```
Combinacao de tipos mais rara: Dragon / Flying (1 Pokemon)
Tipo primario com maior velocidade media: psychic (125.0)
Correlacao entre peso e defesa: 0.465
```

Ou seja: nesses 20, só o Dragonite tem a combinação Dragão/Voador; os psíquicos (Mewtwo e Alakazam) são em média os mais rápidos; e existe uma correlação positiva moderada entre peso e defesa (nem toda a variação de defesa vem do peso, mas pesar mais ajuda, na média, com uma exceção clara: o Onix é leve pros padrões dele e tem a maior defesa da lista). Com o dataset completo da API (todos os Pokémon, não só 20 escolhidos a dedo) essas respostas tendem a ficar mais confiáveis estatisticamente, porque saem de uma amostra bem maior.

## Rodando os testes

```bash
python3 -m pytest -v
```

São 28 testes, nenhum deles precisa de internet: limpeza dos dados vindos da API (incluindo a conversão de unidades e Pokémon de um tipo só), montagem e leitura/gravação do dataset em CSV, as 5 perguntas de análise (com exemplos pequenos que dá pra conferir de cabeça, tipo um time de 2 elétricos e 1 pedra pra confirmar a média de velocidade), geração dos 4 gráficos (só confere que o arquivo PNG foi criado), exportação pro SQLite, e a lógica de busca na PokéAPI com a rede simulada (`requests.get` trocado por uma versão fake nos testes).

## Arquitetura

```
run_extractor.py            # linha de comando: junta tudo, imprime o relatorio, gera graficos
pokedata/
  fetch_api.py               # busca lista + detalhes de Pokemon na PokeAPI de verdade
  clean.py                   # JSON bruto da API -> dict plano (tipos, stats, altura em m, peso em kg)
  dataset.py                 # monta o DataFrame e le/grava o CSV
  analysis.py                # as perguntas estatisticas: tipo mais raro, tipo mais rapido, correlacao, rankings
  charts.py                  # gera os 4 graficos em PNG a partir do DataFrame
  sql_export.py              # exportacao opcional pra SQLite
data/
  sample_pokemon.csv          # dataset de exemplo com 20 Pokemon (veja o aviso acima)
tests/
  fixtures/                   # exemplos de resposta da PokeAPI, no formato real dela
  test_clean.py
  test_dataset.py
  test_analysis.py
  test_charts.py
  test_sql_export.py
  test_fetch_api.py
```

Cada etapa (buscar, limpar, guardar, analisar, desenhar) é um módulo separado que só depende do anterior através de dados simples (dicts, DataFrame), nunca do jeito como os dados chegaram. Por isso dá pra testar a análise inteira sem tocar rede nem arquivo: só monta um DataFrame pequeno na mão e confere o resultado.

## O que eu treinei com esse projeto

pandas pra limpar, organizar e agregar dados tabulares (groupby, correlação, rankings com nlargest), matplotlib pra transformar essas agregações em gráfico salvo em arquivo, consumo de uma API REST pública de verdade (paginação simples de lista + detalhe por item), e exportação de dados pra SQL como ponte pra ferramentas de dashboard. É o projeto mais parecido com o trabalho de análise de dados do certificado de Power BI que já tenho, só que em Python em vez de point-and-click.

## Próximos passos possíveis

Rodar com o dataset completo (todos os Pokémon, não só os 20 de exemplo) e comparar se a correlação entre peso e defesa se mantém; adicionar mais perguntas (correlação entre altura e HP, tipo mais comum por geração); e usar exatamente esse mesmo pipeline de coleta e limpeza como base pro Monitor de Hardware com Power BI, que é o próximo projeto da lista e reaproveita a ideia de guardar histórico num banco SQL pra alimentar um dashboard.
