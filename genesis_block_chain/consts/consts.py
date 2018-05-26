from .foreign_consts import (
    TxTypeFirstBlock,
    TxTypeStopNetwork,
    TxTypeParserFirstBlock,
    TxTypeParserStopNetwork,
)

tx_types = {
    TxTypeFirstBlock:  TxTypeParserFirstBlock,
    TxTypeStopNetwork: TxTypeParserStopNetwork,
}
