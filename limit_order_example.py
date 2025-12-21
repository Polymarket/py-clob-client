"""
Пример размещения лимитного ордера на Polymarket

Перед запуском:
1. Установите библиотеку: pip install py-clob-client python-dotenv
2. Создайте файл .env и заполните:
   PK=<ваш_приватный_ключ>
   FUNDER=<адрес_который_держит_средства>
   CLOB_API_KEY=<опционально_если_уже_есть>
   CLOB_SECRET=<опционально_если_уже_есть>
   CLOB_PASS_PHRASE=<опционально_если_уже_есть>
"""

import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType, ApiCreds
from py_clob_client.order_builder.constants import BUY, SELL

# Загружаем переменные окружения из .env файла
load_dotenv()

def main():
    # Настройка клиента
    HOST = "https://clob.polymarket.com"
    CHAIN_ID = 137  # Polygon Mainnet

    # Ваши ключи из .env файла
    PRIVATE_KEY = os.getenv("PK")
    FUNDER = os.getenv("FUNDER")  # Адрес, который держит средства

    if not PRIVATE_KEY:
        raise ValueError("Не найден PK в .env файле!")

    print("Инициализация клиента...")

    # Создаем клиента
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1,  # 1 для email/Magic wallet, 0 для MetaMask/EOA
        funder=FUNDER
    )

    # Если у вас уже есть API ключи, загружаем их
    if os.getenv("CLOB_API_KEY"):
        creds = ApiCreds(
            api_key=os.getenv("CLOB_API_KEY"),
            api_secret=os.getenv("CLOB_SECRET"),
            api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
        )
        client.set_api_creds(creds)
    else:
        # Иначе создаем новые
        print("Создание API ключей...")
        creds = client.create_or_derive_api_creds()
        client.set_api_creds(creds)
        print(f"API Key: {creds.api_key}")
        print(f"API Secret: {creds.api_secret}")
        print(f"API Passphrase: {creds.api_passphrase}")
        print("Сохраните эти ключи в .env файл для будущего использования!")

    # ВАЖНО: Получите token_id с помощью Markets API:
    # https://docs.polymarket.com/developers/gamma-markets-api/get-markets
    # Или используйте пример ниже

    # Пример: получаем информацию о рынке
    print("\nПолучение списка рынков...")
    markets = client.get_simplified_markets()
    if markets and "data" in markets and len(markets["data"]) > 0:
        example_market = markets["data"][0]
        print(f"\nПример рынка: {example_market.get('question', 'N/A')}")

        # Получаем token_id из outcomes
        if "tokens" in example_market and len(example_market["tokens"]) > 0:
            token_info = example_market["tokens"][0]
            token_id = token_info.get("token_id")
            print(f"Token ID: {token_id}")

            # Получаем текущую цену
            try:
                midpoint = client.get_midpoint(token_id)
                print(f"Текущая средняя цена: ${midpoint}")
            except Exception as e:
                print(f"Не удалось получить цену: {e}")

    # ====================
    # РАЗМЕЩЕНИЕ ЛИМИТНОГО ОРДЕРА
    # ====================

    # ВАЖНО: Замените token_id на реальный!
    TOKEN_ID = "ваш_token_id_здесь"

    # Параметры ордера
    PRICE = 0.55  # Цена в долларах (от 0.00 до 1.00)
    SIZE = 10.0   # Количество токенов (шаров)
    SIDE = BUY    # BUY или SELL

    print("\n" + "="*50)
    print("РАЗМЕЩЕНИЕ ЛИМИТНОГО ОРДЕРА")
    print("="*50)
    print(f"Token ID: {TOKEN_ID}")
    print(f"Сторона: {'ПОКУПКА' if SIDE == BUY else 'ПРОДАЖА'}")
    print(f"Цена: ${PRICE}")
    print(f"Размер: {SIZE} токенов")
    print(f"Общая сумма: ${PRICE * SIZE}")

    # Раскомментируйте следующие строки, когда будете готовы разместить ордер:
    """
    # Создаем ордер
    order_args = OrderArgs(
        token_id=TOKEN_ID,
        price=PRICE,
        size=SIZE,
        side=SIDE
    )

    # Подписываем ордер
    print("\nПодпись ордера...")
    signed_order = client.create_order(order_args)

    # Размещаем ордер на бирже
    print("Размещение ордера...")
    response = client.post_order(signed_order, OrderType.GTC)

    print("\nОтвет от биржи:")
    print(response)

    # Получаем ID размещенного ордера
    if "orderID" in response:
        order_id = response["orderID"]
        print(f"\nОрдер успешно размещен! ID: {order_id}")

        # Проверяем статус ордера
        order_status = client.get_order(order_id)
        print("\nСтатус ордера:")
        print(order_status)
    """

    print("\n✓ Скрипт готов к использованию!")
    print("Замените TOKEN_ID на реальный и раскомментируйте код размещения ордера.")


if __name__ == "__main__":
    main()
