"""
Размещение лимитного ордера на Polymarket
Готовый скрипт для работы с существующими API ключами
"""

import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType, ApiCreds
from py_clob_client.order_builder.constants import BUY, SELL

# Загружаем переменные окружения
load_dotenv()

def main():
    # Загружаем API ключи из .env
    api_key = os.getenv("CLOB_API_KEY")
    api_secret = os.getenv("CLOB_SECRET")
    api_passphrase = os.getenv("CLOB_PASS_PHRASE")
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    private_key = os.getenv("PK")
    funder = os.getenv("FUNDER")  # Опционально для EOA, обязательно для proxy wallet

    # Проверка наличия ключей
    if not all([api_key, api_secret, api_passphrase, private_key]):
        raise ValueError("Не все ключи найдены в .env файле! Проверьте PK, CLOB_API_KEY, CLOB_SECRET, CLOB_PASS_PHRASE")

    print("✓ Все ключи загружены из .env")
    print(f"✓ Используется API: {host}")

    # Настройка клиента
    CHAIN_ID = 137  # Polygon Mainnet

    # Создаем API credentials
    creds = ApiCreds(
        api_key=api_key,
        api_secret=api_secret,
        api_passphrase=api_passphrase,
    )

    # Инициализация клиента
    client = ClobClient(
        host,
        key=private_key,
        chain_id=CHAIN_ID,
        signature_type=1,  # Измените на 0 если используете MetaMask/EOA
        funder=funder,
        creds=creds
    )

    print("✓ Клиент инициализирован\n")

    # ====================
    # ПАРАМЕТРЫ ОРДЕРА
    # ====================

    TOKEN_ID = "89452825777123819275479300852822806637100581036043674494348493206941034444680"

    # НАСТРОЙТЕ ЭТИ ПАРАМЕТРЫ:
    PRICE = 0.50      # Цена в долларах (от 0.00 до 1.00)
    SIZE = 10.0       # Количество токенов
    SIDE = BUY        # BUY (покупка) или SELL (продажа)

    # Получаем информацию о рынке
    try:
        print(f"Token ID: {TOKEN_ID}")

        # Пробуем получить текущую цену
        try:
            midpoint = client.get_midpoint(TOKEN_ID)
            print(f"Текущая средняя цена: ${midpoint}")
        except Exception as e:
            print(f"Не удалось получить цену: {e}")

        # Пробуем получить orderbook
        try:
            orderbook = client.get_order_book(TOKEN_ID)
            if orderbook:
                print(f"Рынок: {orderbook.market}")
                if orderbook.bids:
                    print(f"Лучший bid: ${orderbook.bids[0].price}")
                if orderbook.asks:
                    print(f"Лучший ask: ${orderbook.asks[0].price}")
        except Exception as e:
            print(f"Не удалось получить orderbook: {e}")

    except Exception as e:
        print(f"Ошибка при получении данных о рынке: {e}")

    print("\n" + "="*60)
    print("ПАРАМЕТРЫ ЛИМИТНОГО ОРДЕРА")
    print("="*60)
    print(f"Token ID: {TOKEN_ID}")
    print(f"Сторона: {'ПОКУПКА (BUY)' if SIDE == BUY else 'ПРОДАЖА (SELL)'}")
    print(f"Цена: ${PRICE}")
    print(f"Размер: {SIZE} токенов")
    print(f"Общая сумма: ${PRICE * SIZE}")
    print(f"Тип ордера: GTC (Good 'Til Cancelled)")
    print("="*60)

    # Запрос подтверждения
    confirm = input("\n⚠️  Разместить этот ордер? (yes/no): ").strip().lower()

    if confirm != 'yes':
        print("Отменено пользователем.")
        return

    try:
        # Создаем ордер
        print("\n📝 Создание ордера...")
        order_args = OrderArgs(
            token_id=TOKEN_ID,
            price=PRICE,
            size=SIZE,
            side=SIDE
        )

        # Подписываем ордер
        print("✍️  Подпись ордера...")
        signed_order = client.create_order(order_args)

        # Размещаем ордер на бирже
        print("🚀 Размещение ордера на бирже...")
        response = client.post_order(signed_order, OrderType.GTC)

        print("\n" + "="*60)
        print("✅ ОТВЕТ ОТ БИРЖИ:")
        print("="*60)
        print(response)

        # Получаем ID размещенного ордера
        if "orderID" in response:
            order_id = response["orderID"]
            print(f"\n🎉 Ордер успешно размещен!")
            print(f"Order ID: {order_id}")

            # Проверяем статус ордера
            print("\n📊 Получение статуса ордера...")
            order_status = client.get_order(order_id)
            print("\nСтатус ордера:")
            print(f"  Status: {order_status.get('status', 'N/A')}")
            print(f"  Price: ${order_status.get('price', 'N/A')}")
            print(f"  Size: {order_status.get('original_size', 'N/A')}")
            print(f"  Filled: {order_status.get('size_matched', '0')}")

        elif "error" in response:
            print(f"\n❌ Ошибка при размещении ордера:")
            print(f"  {response['error']}")

    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
