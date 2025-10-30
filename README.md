**Bot de Scalping (Day Trading) em Python para Binance Spot**

Este é um bot de trading automatizado, escrito em Python, projetado para executar uma estratégia de scalping de alta frequência no mercado Spot da Binance.
O bot utiliza análise técnica (RSI) para identificar pontos de entrada em "sobrevenda" e combina lógicas avançadas de Trailing Stop-Loss e Stop-Loss com Confirmação para operar de forma autônoma e gerenciar os riscos.

**Demonstração (Log de Execução)**

Abaixo, alguns exemplos do log do terminal mostrando o bot em operação.

**Detecção e Compra (RSI < 35)**

O bot monitora o mercado e, ao detectar que o RSI caiu abaixo do gatilho (35), identifica uma oportunidade de compra, executa a ordem e salva seu estado.

<img width="555" height="135" alt="parte2" src="https://github.com/user-attachments/assets/b3c4e5e5-c092-4108-b1cc-290e64464ffd" />



**Cenário de Lucro (Trailing Stop-Loss)**

Para maximizar os ganhos, o bot não vende em um alvo fixo. Ao atingir um lucro inicial (2.5%), ele ativa um "stop móvel" que segue o preço para cima, vendendo apenas quando o preço recua 0.5% a partir do seu último pico, garantindo o lucro máximo da tendência.

<img width="677" height="154" alt="parte3" src="https://github.com/user-attachments/assets/67f49a8e-77bd-482f-9a52-4b72fffa799c" />


**Cenário de Risco (Stop-Loss com Confirmação)**

Para evitar perdas em quedas bruscas ("violinadas"), o bot não vende em pânico. Se o stop-loss inicial (-2%) é atingido, ele inicia uma pausa de 10 minutos para confirmar se a queda é persistente.
Após 10 minutos, se o preço ainda estiver baixo, ele confirma a venda para proteger o capital e entra em um "cooldown" de 30 minutos para evitar operar em um mercado instável.

<img width="648" height="133" alt="parte5" src="https://github.com/user-attachments/assets/2569c882-5b32-4333-ab98-728b68c5c6fc" />


**Principais Funcionalidades**

* **Estratégia de Entrada (RSI):** O bot monitora o Índice de Força Relativa (RSI) e só compra quando o ativo entra em território de "sobrevenda" (RSI < 35), buscando uma reversão de preço.
* **Trailing Stop-Loss Avançado:** Para maximizar os lucros, o bot não usa um alvo fixo. Ao atingir um lucro inicial (ex: 2.5%), ele ativa um "stop móvel" que segue o preço, vendendo apenas quando o preço recua uma pequena porcentagem (ex: 0.5%) a partir do seu pico.
* **Gerenciamento de Risco (Stop-Loss com Confirmação):** Se uma operação vai contra, o bot não vende em pânico. Ele aciona um gatilho de stop-loss (ex: -2%) e entra em um "período de confirmação" de 10 minutos para filtrar quedas falsas.
* **Persistência de Estado (Memória):** O bot salva seu estado atual (se está em uma posição, preço de compra, etc.) em um arquivo `bot_state.json`. Ele pode ser parado e reiniciado a qualquer momento e continuará de onde parou.
* **Cooldown Pós-Venda:** Após uma venda com prejuízo (stop-loss), o bot entra em um período de "resfriamento" (ex: 30 minutos) para evitar operar em um mercado instável.
* **Gerenciamento de Capital:** Utiliza uma porcentagem configurável do capital (ex: 99%) para cada operação, permitindo o efeito de juros compostos.

**Tecnologias Utilizadas**

* **Python 3**
* **CCXT:** Para integração unificada com a API da Binance.
* **Pandas:** Para manipulação e organização de dados de séries temporais (OHLCV).
* **TA-Lib (Technical Analysis Library):** Para o cálculo preciso do indicador RSI.
* **JSON:** Para persistência de estado (memória do bot).
