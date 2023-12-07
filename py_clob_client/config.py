from .clob_types import ContractConfig


def get_contract_config(chainID: int, neg_risk: bool = False) -> ContractConfig:
    """
    Get the contract configuration for the chain
    """

    CONFIG = {
        137: ContractConfig(
            exchange="0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
            collateral="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
            conditional_tokens="0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
        ),
        80001: ContractConfig(
            exchange="0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E",
            collateral="0x2E8DCfE708D44ae2e406a1c02DFE2Fa13012f961",
            conditional_tokens="0x7D8610E9567d2a6C9FBf66a5A13E9Ba8bb120d43",
        ),
    }

    NEG_RISK_CONFIG = {
        137: ContractConfig(
            exchange="0xC5d563A36AE78145C45a50134d48A1215220f80a",
            collateral="0x2791bca1f2de4661ed88a30c99a7a9449aa84174",
            conditional_tokens="0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
        ),
        80001: ContractConfig(
            exchange="0x87d1A0DdB4C63a6301916F02090A51a7241571e4",
            collateral="0x2e8dcfe708d44ae2e406a1c02dfe2fa13012f961",
            conditional_tokens="0x7D8610E9567d2a6C9FBf66a5A13E9Ba8bb120d43",
        ),
    }

    if neg_risk:
        config = NEG_RISK_CONFIG.get(chainID)
    else:
        config = CONFIG.get(chainID)
    if config is None:
        raise Exception("Invalid chainID: ${}".format(chainID))

    return config
