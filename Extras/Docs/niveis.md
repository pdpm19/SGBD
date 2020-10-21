# Níveis de isolamento

## Read Uncommited
- Nível mais baixo de isolamento.
- Permite dirty reads pelo facto de que uma transação pode ser valores que não foram
ainda committed por outra transação
- As transações não são isoladas umas das outras

## Read Committed
- Cada leitura feita tem a certeza que os dados que estão a ser lidos foram committed 
no momento da leitura, não permitindo assim dirty reads.
- A transação tem um lock de leitura ou escrita na coluna atual para prevenir que 
outra transação leia, atualize ou apague-a.

## Repeatable Read
- Nível mais restrito de isolamento
- A transação tem locks de leitura em todas as colunas que façam referência e locks
de escrita em todas as colunas em que insere, atualiza ou apaga-a.
- Como as restantes transações não podem ler, atualizar ou apagar as colunas, 
evitando assim leituras não repetíveis.

## Serializable
- Nível mais alto de isolamento
- A execução é garantida pela execução em série
- As operações concorrentes são executadas em série

## Leituras nos níveis de isolamento

![Níveis de isolamento] (isolamento.png "Níveis de isolamento/leituras")

