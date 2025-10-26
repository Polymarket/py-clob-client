# Инструкция по размещению лимитного ордера

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install py-clob-client python-dotenv
```

### 2. Настройка ключей

Скопируйте файл `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

Откройте `.env` и заполните:
- **PK** - ваш приватный ключ
- **FUNDER** - адрес, который держит средства (для proxy wallet)

### 3. Запуск примера

```bash
python limit_order_example.py
```

## Что делает скрипт

1. Подключается к Polymarket CLOB API
2. Создает/загружает API ключи
3. Показывает пример доступных рынков
4. Готовит код для размещения лимитного ордера

## Размещение реального ордера

### Шаг 1: Найдите token_id

Используйте Gamma Markets API для поиска рынков:
https://docs.polymarket.com/developers/gamma-markets-api/get-markets

Или запустите скрипт - он покажет примеры доступных рынков.

### Шаг 2: Настройте параметры ордера

В файле `limit_order_example.py` найдите и измените:

```python
TOKEN_ID = "ваш_token_id_здесь"  # ID токена с рынка
PRICE = 0.55      # Цена от 0.00 до 1.00 (в долларах)
SIZE = 10.0       # Количество токенов
SIDE = BUY        # BUY (купить) или SELL (продать)
```

### Шаг 3: Раскомментируйте код размещения

Найдите блок кода в тройных кавычках `"""` и раскомментируйте его.

### Шаг 4: Запустите

```bash
python limit_order_example.py
```

## Типы signature_type

В коде клиента указывается `signature_type`:

```python
client = ClobClient(
    HOST,
    key=PRIVATE_KEY,
    chain_id=CHAIN_ID,
    signature_type=1,  # ← ВАЖНО!
    funder=FUNDER
)
```

- **signature_type=0** - для MetaMask, hardware wallets, обычные EOA кошельки
- **signature_type=1** - для email/Magic wallet (proxy)
- **signature_type=2** - для browser wallet proxy

## Важно для MetaMask/EOA

Если вы используете MetaMask или hardware wallet (signature_type=0), **перед торговлей** нужно установить token allowances!

См. подробности в README.md раздел "Important: Token Allowances for MetaMask/EOA Users"

## Типы ордеров (OrderType)

- **OrderType.GTC** - Good 'Til Cancelled (действует пока не отменят)
- **OrderType.FOK** - Fill Or Kill (исполнить полностью или отменить)
- **OrderType.GTD** - Good 'Til Date (действует до определенной даты)

## Полезные команды

### Получить открытые ордера

```python
from py_clob_client.clob_types import OpenOrderParams

open_orders = client.get_orders(OpenOrderParams())
print(open_orders)
```

### Отменить ордер

```python
order_id = "ваш_order_id"
client.cancel(order_id)
```

### Отменить все ордера

```python
client.cancel_all()
```

### Получить баланс

```python
balance = client.get_balance_allowance()
print(balance)
```

## Примеры

В папке `examples/` есть много готовых примеров:
- `order.py` - простой лимитный ордер
- `orders.py` - множественные ордера
- `market_buy_order.py` - рыночный ордер на покупку
- `cancel_all.py` - отмена всех ордеров
- и многие другие...

## Полезные ссылки

- Документация Polymarket: https://docs.polymarket.com/
- Markets API: https://docs.polymarket.com/developers/gamma-markets-api/get-markets
- GitHub: https://github.com/Polymarket/py-clob-client

## Поддержка

При возникновении проблем проверьте:
1. Правильность приватного ключа
2. Достаточность средств на балансе
3. Корректность token_id
4. Для MetaMask - установлены ли allowances

Удачной торговли! 🚀
