"""
Проверка существующих API ключей с разными signature_type
Помогает найти правильную конфигурацию для ваших ключей
"""

import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from py_clob_client.order_builder.constants import BUY

load_dotenv()

def test_config(sig_type, funder=None):
    """Тестирует конфигурацию с существующими API ключами"""
    try:
        print(f"\n{'='*60}")
        print(f"Тест: signature_type={sig_type}, funder={'Да' if funder else 'Нет'}")
        print('='*60)

        api_key = os.getenv("CLOB_API_KEY")
        api_secret = os.getenv("CLOB_SECRET")
        api_passphrase = os.getenv("CLOB_PASS_PHRASE")
        host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
        private_key = os.getenv("PK")

        creds = ApiCreds(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
        )

        client = ClobClient(
            host,
            key=private_key,
            chain_id=137,
            signature_type=sig_type,
            funder=funder,
            creds=creds
        )

        print(f"✓ Клиент создан")

        # Пробуем получить открытые ордера
        print(f"Проверка: получение открытых ордеров...")
        from py_clob_client.clob_types import OpenOrderParams
        orders = client.get_orders(OpenOrderParams())
        print(f"✓ Открытые ордера получены: {len(orders)} шт.")

        # Пробуем создать и подписать тестовый ордер (но НЕ размещать!)
        print(f"Проверка: создание тестового ордера...")
        test_order = OrderArgs(
            token_id="89452825777123819275479300852822806637100581036043674494348493206941034444680",
            price=0.01,  # Очень низкая цена для теста
            size=1.0,
            side=BUY
        )
        signed_order = client.create_order(test_order)
        print(f"✓ Ордер подписан успешно")

        print(f"\n🎉 УСПЕХ! Эта конфигурация работает!")
        print(f"{'='*60}")
        print(f"signature_type={sig_type}")
        if funder:
            print(f"funder={funder}")
        print(f"\nИспользуйте эти настройки в place_limit_order.py:")
        print(f"  signature_type={sig_type},")
        if funder:
            print(f"  funder='{funder}',")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("="*60)
    print("ПРОВЕРКА СУЩЕСТВУЮЩИХ API КЛЮЧЕЙ")
    print("="*60)

    private_key = os.getenv("PK")
    existing_funder = os.getenv("FUNDER")
    api_key = os.getenv("CLOB_API_KEY")

    if not all([private_key, api_key]):
        print("❌ Не найдены необходимые ключи в .env!")
        return

    print(f"✓ Все ключи найдены в .env")

    # Вычисляем адрес из приватного ключа
    from eth_account import Account
    if private_key.startswith('0x'):
        account = Account.from_key(private_key)
    else:
        account = Account.from_key('0x' + private_key)

    wallet_address = account.address
    print(f"✓ Адрес кошелька: {wallet_address}")
    if existing_funder:
        print(f"✓ Funder из .env: {existing_funder}")

    print("\nПроверяем разные конфигурации...\n")

    # Тестируем разные варианты
    configs = [
        (0, None, "EOA/MetaMask без funder"),
        (0, wallet_address, "EOA/MetaMask с wallet адресом"),
        (0, existing_funder, "EOA/MetaMask с funder из .env") if existing_funder else None,
        (1, None, "Proxy wallet без funder"),
        (1, existing_funder, "Proxy wallet с funder из .env") if existing_funder else None,
        (1, wallet_address, "Proxy wallet с wallet адресом"),
        (2, existing_funder, "Browser proxy с funder из .env") if existing_funder else None,
        (2, wallet_address, "Browser proxy с wallet адресом"),
    ]

    configs = [c for c in configs if c is not None]

    found = False
    for sig_type, funder, description in configs:
        print(f"\n🔍 {description}")
        if test_config(sig_type, funder):
            found = True
            break

    if not found:
        print("\n" + "="*60)
        print("❌ НЕ НАЙДЕНА РАБОЧАЯ КОНФИГУРАЦИЯ")
        print("="*60)
        print("\nВозможные причины:")
        print("1. API ключи были созданы с другим приватным ключом")
        print("2. API ключи устарели или были удалены")
        print("\nРешение:")
        print("Запустите скрипт check_signature_type.py для создания новых API ключей:")
        print("  python check_signature_type.py")

if __name__ == "__main__":
    main()
