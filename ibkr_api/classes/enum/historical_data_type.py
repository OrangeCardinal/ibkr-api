from enum import Enum
class HistoricalDataType(Enum):
    TRADES                    = 'TRADES'
    MIDPOINT                  = 'MIDPOINT'
    BID                       = 'BID'
    ASK                       = 'ASK'
    BID_ASK                   = 'BID_ASK'
    HISTORICAL_VOLATILITY     = 'HISTORICAL_VOLATILITY'
    OPTION_IMPLIED_VOLATILITY = 'OPTION_IMPLIED_VOLATILITY'
    FEE_RATE                  = 'FEE_RATE'
    REBATE_RATE               = 'REBATE_RATE'
