import ccxt
import time
import pandas as pd
import talib
from datetime import datetime, timedelta
import json
import os

api_key = 'SUA CHAVE API'
secret = 'SUA SECRET KEY'

exchange_name = 'binance'
symbol = 'SOL/USDT'
state_file = 'bot_state.json'

# Parâmetros da Estratégia 
percentual_capital_por_trade = 99.0
stop_loss_percentage = 2.0
rsi_period = 14
rsi_oversold_threshold = 35
profit_percentage = 4.0
cooldown_period_minutes = 30 # Pausa APÓS uma venda com stop-loss

# Parâmetros do Stop-Loss Atrasado
stop_loss_confirmation_minutes = 10 # Tempo de espera para confirmar um stop-loss

# Variáveis de Estado
in_position = False
custo_ultima_compra = 0
preco_de_compra = 0
stop_loss_price = 0
last_stop_loss_time = None

# Variáveis de Estado para a Confirmação
confirmation_pending = False
confirmation_start_time = None

def save_state(state):
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=4)
    print("--- Estado do bot salvo! ---")

def load_state():
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            print("--- Carregando estado salvo... ---")
            return json.load(f)
    print("--- Nenhum estado salvo encontrado. Começando do zero. ---")
    return None

exchange = getattr(ccxt, exchange_name)({
    'apiKey': api_key,
    'secret': secret,
    'options': {
        'defaultType': 'spot',
    },
})

def get_rsi(symbol, timeframe='5m', period=14):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
        if not bars or len(bars) < period:
            return None
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        rsi = talib.RSI(df['close'], timeperiod=period)
        return rsi.iloc[-1]
    except Exception as e:
        print(f"Erro ao calcular RSI: {e}")
        return None

saved_state = load_state()
if saved_state:
    in_position = saved_state.get('in_position', False)
    custo_ultima_compra = saved_state.get('custo_ultima_compra', 0)
    preco_de_compra = saved_state.get('preco_de_compra', 0)
    
print("Bot v7 (Com Memória) iniciado. Pressione Ctrl+C para parar.")
print(f"Estado inicial: Em posição = {in_position}, Custo da compra = ${custo_ultima_compra:.2f}")
print("-" * 50)

while True:
    try:
        if in_position:
            stop_loss_price = preco_de_compra * (1 - stop_loss_percentage / 100.0)

        base_currency = symbol.split('/')[0]
        balance = exchange.fetch_balance()
        usdt_balance = balance['total'].get('USDT', 0)
        crypto_balance = balance['total'].get(base_currency, 0)
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        current_investment_value = crypto_balance * current_price
        
        if not in_position:
            if last_stop_loss_time and (datetime.now() - last_stop_loss_time < timedelta(minutes=cooldown_period_minutes)):
                minutes_left = cooldown_period_minutes - (datetime.now() - last_stop_loss_time).total_seconds() / 60
                print(f"Em modo COOLDOWN após stop-loss. Aguardando {minutes_left:.1f} minutos.")
                time.sleep(10)
                continue
            else:
                last_stop_loss_time = None
            
            print(f"Buscando oportunidade de compra... | Preço {base_currency}: ${current_price:.4f} | Saldo: ${usdt_balance:.2f}")

            if usdt_balance > 15:
                rsi_atual = get_rsi(symbol, period=rsi_period)
                if rsi_atual is not None:
                    print(f"RSI atual: {rsi_atual:.2f}")
                    if rsi_atual < rsi_oversold_threshold:
                        print(f"*** OPORTUNIDADE DE COMPRA DETECTADA! (RSI={rsi_atual:.2f}) ***")
                        order = exchange.create_market_buy_order(symbol, (usdt_balance * (percentual_capital_por_trade / 100.0)) / current_price)
                        
                        in_position = True
                        custo_ultima_compra = float(order['cost'])
                        preco_de_compra = float(order['price'])
                        stop_loss_price = preco_de_compra * (1 - stop_loss_percentage / 100.0)
                        
                        current_state = {
                            'in_position': in_position,
                            'custo_ultima_compra': custo_ultima_compra,
                            'preco_de_compra': preco_de_compra
                        }
                        save_state(current_state)
                        
                        print("-" * 50)
                        print(f"COMPRA REALIZADA a ${preco_de_compra:.4f}. Stop definido em ${stop_loss_price:.4f}")
                        print("-" * 50)
        else: 
            profit_target_value = custo_ultima_compra * (1 + profit_percentage / 100.0)
            print(f"Em posição. Monitorando... | Preço {base_currency}: ${current_price:.4f} | Alvo: ${profit_target_value:.2f} | Stop: ${stop_loss_price:.4f}")

            if confirmation_pending:
                if (datetime.now() - confirmation_start_time) >= timedelta(minutes=stop_loss_confirmation_minutes):
                    print("Tempo de confirmação esgotado. Verificando preço final...")
                    if current_price <= stop_loss_price:
                        print(f"Queda confirmada. EXECUTANDO STOP-LOSS.")
                        order = exchange.create_market_sell_order(symbol, crypto_balance)
                        in_position = False
                        last_stop_loss_time = datetime.now()
                        current_state = {'in_position': False, 'custo_ultima_compra': 0, 'preco_de_compra': 0}
                        save_state(current_state)
                    else:
                        print(f"Recuperação confirmada. VENDA CANCELADA.")
                    confirmation_pending = False
                    confirmation_start_time = None
                else:
                    minutes_left = stop_loss_confirmation_minutes - (datetime.now() - confirmation_start_time).total_seconds() / 60
                    print(f"CONFIRMAÇÃO DE STOP-LOSS PENDENTE. Verificação final em {minutes_left:.1f} min.")
            else:
                if current_investment_value >= profit_target_value:
                    print(f"$$$ ALVO DE LUCRO DE {profit_percentage}% ATINGIDO! $$$")
                    order = exchange.create_market_sell_order(symbol, crypto_balance)
                    in_position = False
                    current_state = {'in_position': False, 'custo_ultima_compra': 0, 'preco_de_compra': 0}
                    save_state(current_state)
                elif current_price <= stop_loss_price:
                    print(f"!!! GATILHO DE STOP-LOSS ATINGIDO a ${current_price:.4f} !!!")
                    confirmation_pending = True
                    confirmation_start_time = datetime.now()

    except Exception as e:
        print(f"\nOcorreu um erro crítico: {e}\n")
        
    time.sleep(10)