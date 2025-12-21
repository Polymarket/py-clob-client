"""
Диагностический скрипт для определения правильного signature_type
Проверяет разные комбинации и помогает найти правильную конфигурацию
"""

import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds

load_dotenv()

def test_signature_type(sig_type, funder=None):
    """Тестирует конкретный signature_type"""
    try:
        print(f"\n{'='*60}")
        print(f"Тестирование signature_type={sig_type}")
        if funder:
            print(f"С funder: {funder[:10]}...{funder[-8:]}")
        else:
            print("Без funder")
        print('='*60)

        host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
        private_key = os.getenv("PK")

        # Создаем клиента
        client = ClobClient(
            host,
            key=private_key,
            chain_id=137,
            signature_type=sig_type,
            funder=funder
        )

        # Пробуем создать новые API ключи
        print(f"Попытка создания API ключей с signature_type={sig_type}...")
        new_creds = client.create_or_derive_api_creds()

        print(f"✅ УСПЕХ! signature_type={sig_type} работает!")
        print(f"\nНовые API ключи (сохраните их!):")
        print(f"CLOB_API_KEY={new_creds.api_key}")
        print(f"CLOB_SECRET={new_creds.api_secret}")
        print(f"CLOB_PASS_PHRASE={new_creds.api_passphrase}")

        # Проверяем баланс для подтверждения
        try:
            balance = client.get_balance_allowance()
            print(f"\n✓ Баланс успешно получен: {balance}")
        except Exception as e:
            print(f"\n⚠️  Предупреждение при получении баланса: {e}")

        return True, new_creds

    except Exception as e:
        print(f"❌ Ошибка с signature_type={sig_type}: {e}")
        return False, None

def main():
    print("="*60)
    print("ДИАГНОСТИКА SIGNATURE TYPE")
    print("="*60)

    private_key = os.getenv("PK")
    existing_funder = os.getenv("FUNDER")

    if not private_key:
        print("❌ Не найден PK в .env файле!")
        return

    print(f"✓ Приватный ключ найден")
    print(f"✓ Funder из .env: {existing_funder[:10] + '...' + existing_funder[-8:] if existing_funder else 'Не указан'}")

    # Вычисляем адрес из приватного ключа
    from eth_account import Account
    if private_key.startswith('0x'):
        account = Account.from_key(private_key)
    else:
        account = Account.from_key('0x' + private_key)

    wallet_address = account.address
    print(f"✓ Адрес кошелька из приватного ключа: {wallet_address}")

    print("\n" + "="*60)
    print("ПРОВЕРКА РАЗНЫХ КОНФИГУРАЦИЙ")
    print("="*60)

    # Список конфигураций для проверки
    configs = [
        # (signature_type, funder, description)
        (0, None, "EOA/MetaMask без funder"),
        (0, wallet_address, "EOA/MetaMask с funder = адрес кошелька"),
        (1, existing_funder, "Proxy wallet с funder из .env"),
        (1, wallet_address, "Proxy wallet с funder = адрес кошелька"),
        (2, existing_funder, "Browser wallet proxy с funder из .env"),
        (2, wallet_address, "Browser wallet proxy с funder = адрес кошелька"),
    ]

    working_config = None

    for sig_type, funder, description in configs:
        print(f"\n🔍 Проверка: {description}")
        success, creds = test_signature_type(sig_type, funder)

        if success:
            working_config = (sig_type, funder, creds)
            print(f"\n{'='*60}")
            print(f"🎉 НАЙДЕНА РАБОЧАЯ КОНФИГУРАЦИЯ!")
            print(f"{'='*60}")
            print(f"signature_type={sig_type}")
            print(f"funder={funder if funder else 'None'}")
            print(f"\nОбновите ваш .env файл:")
            print(f"FUNDER={funder if funder else ''}")
            print(f"\nИ замените старые API ключи на новые:")
            print(f"CLOB_API_KEY={creds.api_key}")
            print(f"CLOB_SECRET={creds.api_secret}")
            print(f"CLOB_PASS_PHRASE={creds.api_passphrase}")

            print(f"\nВ place_limit_order.py измените строку 46 на:")
            print(f"signature_type={sig_type},  # Правильный тип для вашего кошелька")

            break

    if not working_config:
        print("\n❌ Не удалось найти рабочую конфигурацию!")
        print("\nВозможные причины:")
        print("1. Неправильный приватный ключ")
        print("2. Кошелек не зарегистрирован на Polymarket")
        print("3. Проблемы с сетью")
        print("\nПопробуйте:")
        print("- Проверить приватный ключ в .env")
        print("- Зайти на polymarket.com с этим кошельком")
        print("- Убедиться что кошелек активирован")

if __name__ == "__main__":
    main()
