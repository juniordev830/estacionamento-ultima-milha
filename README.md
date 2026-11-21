# Estacionamento e última milha

Compare pontos de estacionamento, com links para dirigir até lá e caminhar ao destino.

## Rodar

Python 3.10 ou mais recente. Cada execução lê um JSON local e imprime outro JSON no terminal.

```bash
python app.py exemplo.json
python -m unittest -v
```

## Uso

Preencha os minutos de carro e de caminhada e o preço total consultado. Indique teto de gasto e de caminhada. As opções que atendem aos limites aparecem pela menor duração combinada.

## Google Maps

Os links seguem a documentação de [Maps URLs](https://developers.google.com/maps/documentation/urls/get-started) e abrem o app ou site sem chave. Confira no Maps a rota oferecida, a cobertura de transporte e as condições do momento. Os valores numéricos no arquivo de exemplo são demonstrações.

## Estado do projeto

Versão inicial funcional por linha de comando, sem interface web. Usa apenas a biblioteca padrão do Python. Os testes executam os exemplos e verificam as regras do projeto.

## Exportação para planilha

Use `python app.py exemplo.json --csv > relatorio.csv` para exportar as opções de estacionamento e seus percursos. O CSV usa ponto e vírgula, conserva a ordem do relatório e inclui o cabeçalho mesmo quando a seleção está vazia. O JSON continua sendo a saída padrão.

Também é possível encadear a ferramenta com outro comando usando `-` como entrada. Exemplo em um terminal Bash:

```bash
cat exemplo.json | python app.py -
```

O comparador aceita até 100 pontos de estacionamento por execução. Para valores iguais de tempo total e preço, o desempate é feito alfabeticamente pelo nome do ponto, tornando os resultados reproduzíveis.

Arquivos e entrada padrão JSON são limitados a 1 MB (1.000.000 bytes). Entradas maiores não são processadas.
