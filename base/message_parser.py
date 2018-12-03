"""
Extracts data from messages and returns the appropriate class(es)

"""

from base.messages import Messages
from classes.contracts.contract import Contract
from classes.contracts.contract_details import ContractDetails
from classes.contracts.contract_description import ContractDescription
from classes.bar import Bar

import logging
import time

logger = logging.getLogger(__name__)


class MessageParser(object):
    def __init__(self):
        self.server_version = 147


    def contract_data(self, message):
        contract = Contract()
        fields = message['fields']
        
        version = fields[0]
        request_id = int(fields[1])
        contract.symbol = bytearray(fields[2]).decode() 
        contract.security_type = bytearray(fields[3]).decode()
        #self.readLastTradeDate(fields, contract, False) ???
        contract.strike = float(fields[4])
        contract.right = bytearray(fields[5]).decode()
        contract.exchange = bytearray(fields[6]).decode()
        contract.currency = bytearray(fields[7]).decode()
        contract.local_symbol = bytearray(fields[8]).decode()
        contract.market_name = bytearray(fields[9]).decode()          # New to contract
        contract.trading_class = bytearray(fields[10]).decode()
        contract.id = int(fields[11])
        contract.min_tick = float(fields[12])                     # New to contract
        contract.md_size_multiplier = int(fields[13])
        contract.multiplier  = bytearray(fields[14]).decode()
        contract.order_types = bytearray(fields[15]).decode()
        contract.valid_exchanges = bytearray(fields[16]).decode()
        contract.price_magnifier = int(fields[17])
        contract.under_contract_id = int(fields[18])
        contract.long_name = bytearray(fields[19]).decode()
        contract.primary_exchange = bytearray(fields[20]).decode()
        contract.contract_month = bytearray(fields[21]).decode()
        contract.industry = bytearray(fields[22]).decode()
        contract.category = bytearray(fields[23]).decode()
        contract.sub_category = bytearray(fields[24]).decode()
        contract.time_zone_id = bytearray(fields[25]).decode()
        contract.trading_hours = bytearray(fields[26]).decode()
        contract.liquid_hours =  bytearray(fields[27]).decode()
        contract.ev_rule = bytearray(fields[28]).decode()
        contract.ev_multiplier = int(fields[29])

        """
        Not yet ported
        secIdListCount = decode(int, fields)
        if secIdListCount > 0:
            contract.secIdList = []
            for _ in range(secIdListCount):
                tagValue = TagValue()
                tagValue.tag = decode(str, fields)
                tagValue.value = decode(str, fields)
                contract.secIdList.append(tagValue)

        if self.server_version >= MIN_SERVER_VER_AGG_GROUP:
            contract.aggGroup = decode(int, fields)

        if self.server_version >= MIN_SERVER_VER_UNDERLYING_INFO:
            contract.underSymbol = decode(str, fields)
            contract.underSecType = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_MARKET_RULES:
            contract.marketRuleIds = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_REAL_EXPIRATION_DATE:
            contract.realExpirationDate = decode(str, fields)
        """        
    def processBondContractDataMsg(self, fields):

        next(fields)
        version = decode(int, fields)

        reqId = -1
        if version >= 3:
            reqId = decode(int, fields)

        contract = ContractDetails()
        contract.contract.symbol = decode(str, fields)
        contract.contract.security_type = decode(str, fields)
        contract.cusip = decode(str, fields)
        contract.coupon = decode(int, fields)
        self.readLastTradeDate(fields, contract, True)
        contract.issueDate = decode(str, fields)
        contract.ratings = decode(str, fields)
        contract.bondType = decode(str, fields)
        contract.couponType = decode(str, fields)
        contract.convertible = decode(bool, fields)
        contract.callable = decode(bool, fields)
        contract.putable = decode(bool, fields)
        contract.descAppend = decode(str, fields)
        contract.contract.exchange = decode(str, fields)
        contract.contract.currency = decode(str, fields)
        contract.marketName = decode(str, fields)
        contract.contract.tradingClass = decode(str, fields)
        contract.contract.id = decode(int, fields)
        contract.minTick = decode(float, fields)
        if self.server_version >= MIN_SERVER_VER_MD_SIZE_MULTIPLIER:
            contract.mdSizeMultiplier = decode(int, fields)
        contract.orderTypes = decode(str, fields)
        contract.validExchanges = decode(str, fields)
        contract.nextOptionDate = decode(str, fields)  # ver 2 field
        contract.nextOptionType = decode(str, fields)  # ver 2 field
        contract.nextOptionPartial = decode(bool, fields)  # ver 2 field
        contract.notes = decode(str, fields)  # ver 2 field
        if version >= 4:
            contract.longName = decode(str, fields)
        if version >= 6:
            contract.evRule = decode(str, fields)
            contract.evMultiplier = decode(int, fields)
        if version >= 5:
            secIdListCount = decode(int, fields)
            if secIdListCount > 0:
                contract.secIdList = []
                for _ in range(secIdListCount):
                    tagValue = TagValue()
                    tagValue.tag = decode(str, fields)
                    tagValue.value = decode(str, fields)
                    contract.secIdList.append(tagValue)

        if self.server_version >= MIN_SERVER_VER_AGG_GROUP:
            contract.aggGroup = decode(int, fields)

        if self.server_version >= MIN_SERVER_VER_MARKET_RULES:
            contract.marketRuleIds = decode(str, fields)

        # self.response_handler.bondContractDetails(reqId, contract)


    @staticmethod
    def current_time(message):
        """
        Parse data from the current_time response message

        Message Fields
        0 - Message ID
        1 - Request ID
        2 - Current Time (seconds since epoch)

        :param message: API Response message
        :returns: (request_id:int, timestamp)
        """
        request_id = int(message['fields'][1])
        timestamp = time.ctime(int(message['fields'][2]))
        return request_id, timestamp

    @staticmethod
    def family_codes(message):
        fields = message['fields']

        num_family_codes = int(fields[0])
        family_codes = []
        field_index = 1
        for i in range(num_family_codes):
            data = {}
            data['account_id'] = bytearray(fields[field_index]).decode()
            data['family_code'] = bytearray(fields[field_index+1]).decode()
            field_index += 2
            family_codes.append(data)
        return family_codes

    @staticmethod
    def historical_data(message):
        """

        :param message:
        :return: Message ID, Request ID, Bar Data
        """
        bars = []
        fields = message['fields']
        message_id = int(fields[0])
        request_id = int(fields[1])
        start_date = fields[2]
        end_date   = fields[3]
        bar_count = int(fields[4])
        current_bar = 1
        bar_index = 5

        while current_bar <= bar_count:
            bar = Bar()
            bar.date = str(fields[bar_index]) # TODO: Make a proper date
            bar.open = float(fields[bar_index+1])
            bar.high = float(fields[bar_index+2])
            bar.low = float(fields[bar_index+3])
            bar.close = float(fields[bar_index+4])
            bar.volume = fields[bar_index+5]
            bar.average = fields[bar_index+6]
            bar.bar_count = fields[bar_index+7]
            bar_index += 8
            current_bar += 1
            bars.append(bar)

        return message_id, request_id, bars
    
    @staticmethod
    def info_message(message):
        """
        Message Fields
        0 - Message ID
        1 - Request ID
        2 - Ticker ID (~Contract ID , -1 No Ticker associated)
        3 - Info Code
        4 - Info
        :param message:
        :return:
        """
        fields = message['fields']
        ticker_id = int(fields[2])
        info_code = int(fields[3])
        text      = bytearray(fields[4]).decode()
        return ticker_id, info_code, text

    def managed_accounts(self, fields):
        accounts = []  # List of Accounts to Return
        print(fields)
        return accounts


    @staticmethod
    def market_depth_l2(message):
        fields = message['fields']
        data = {
            'message_id':int(fields[0]),
            'request_id':int(fields[1]),
            'position':int(fields[2]),
            'market_maker':bytearray(fields[3]).decode(),
            'operation':int(fields[4]),
            'side':int(fields[5]),
            'price':float(fields[6]),
            'size':int(fields[7]),
            'is_smart_depth':bool(fields[8])
            }
        
        return data

    @staticmethod
    def reroute_market_data_request(message):
        fields = message['fields']
        data = {
            'request_id':int(fields[0]),
            'contract_id':int(fields[1]),
            'exchange':bytearray(fields[2]).decode()
        }
        return data
    
    @staticmethod
    def reroute_market_depth_request(message):
        fields = message['fields']
        data = {
            'request_id':int(fields[0]),
            'contract_id':int(fields[1]),
            'exchange':bytearray(fields[2]).decode()
        }
        return data

    @staticmethod
    def scanner_data(message):
        fields = message['fields']

        message_id = int(fields[0])
        request_id = int(fields[1])
        number_of_elements = int(fields[2])
        index = 1
        field_index = 0
        results = []
        while index <= number_of_elements:
            data = {}
            contract = Contract()
            data['rank'] = int(fields[field_index])
            contract.id = int(fields[field_index+1])
            contract.symbol = bytearray(fields[field_index+2]).decode()
            contract.security_type = bytearray(fields[field_index+3]).decode()
            contract.last_trade_date_or_contract_month= bytearray(fields[field_index+4]).decode()
            contract.strike= int(fields[field_index+5])
            contract.right= bytearray(fields[field_index+6]).decode()
            contract.exchange= bytearray(fields[field_index+7]).decode()
            contract.currency= bytearray(fields[field_index+8]).decode()
            contract.local_symbol= bytearray(fields[field_index+9]).decode()
            contract.market_name= bytearray(fields[field_index+10]).decode()
            contract.trading_class= bytearray(fields[field_index+11]).decode()

            data['contract'] = contract
            data['distance'] = fields[field_index+12]
            data['benchmark'] = fields[field_index+13]
            data['projection'] = fields[field_index+14]
            data['legs_str'] = fields[field_index+15]
            field_index += 16
            results.append(data)
            index += 1
        return message_id,request_id,results

    @staticmethod
    def symbol_samples(message):
        fields = message['fields']

        request_id = int(fields[1])
        num_samples = int(fields[2])
        field_index = 3
        contracts = []
        for index in range(num_samples):
            contract = Contract()
            contract.id = int(fields[field_index])
            contract.symbol = bytearray(fields[field_index+1]).decode()
            contract.security_type = bytearray(fields[field_index+2]).decode()
            contract.primary_exchange = bytearray(fields[field_index+3]).decode()
            contract.currency = bytearray(fields[field_index+4]).decode()

            num_security_types = int(fields[field_index+5])
            field_index += 6
            for j in range(num_security_types):
                derivative_security_type = str(fields[field_index])
                contract.derivative_security_types.append(derivative_security_type)
                field_index += 1

            contracts.append(contract)

        return request_id, contracts

    def processTickPriceMsg(self, fields):
        next(fields)
        decode(int, fields)

        reqId = decode(int, fields)
        tickType = decode(int, fields)
        price = decode(float, fields)
        size = decode(int, fields)  # ver 2 field
        attrMask = decode(int, fields)  # ver 3 field

        attrib = TickAttrib()

        attrib.canAutoExecute = attrMask == 1

        if self.server_version >= MIN_SERVER_VER_PAST_LIMIT:
            attrib.canAutoExecute = attrMask & 1 != 0
            attrib.pastLimit = attrMask & 2 != 0
            if self.server_version >= MIN_SERVER_VER_PRE_OPEN_BID_ASK:
                attrib.preOpen = attrMask & 4 != 0

        # self.response_handler.tickPrice(reqId, tickType, price, attrib)

        # process ver 2 fields
        sizeTickType = TickTypeEnum.NOT_SET
        if TickTypeEnum.BID == tickType:
            sizeTickType = TickTypeEnum.BID_SIZE
        elif TickTypeEnum.ASK == tickType:
            sizeTickType = TickTypeEnum.ASK_SIZE
        elif TickTypeEnum.LAST == tickType:
            sizeTickType = TickTypeEnum.LAST_SIZE
        elif TickTypeEnum.DELAYED_BID == tickType:
            sizeTickType = TickTypeEnum.DELAYED_BID_SIZE
        elif TickTypeEnum.DELAYED_ASK == tickType:
            sizeTickType = TickTypeEnum.DELAYED_ASK_SIZE
        elif TickTypeEnum.DELAYED_LAST == tickType:
            sizeTickType = TickTypeEnum.DELAYED_LAST_SIZE

        if sizeTickType != TickTypeEnum.NOT_SET:
            pass
            # self.response_handler.tickSize(reqId, sizeTickType, size)

    def processOrderStatusMsg(self, fields):

        next(fields)
        if self.server_version < MIN_SERVER_VER_MARKET_CAP_PRICE:
            decode(int, fields)
        orderId = decode(int, fields)
        status = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            filled = decode(float, fields)
        else:
            filled = decode(int, fields)

        if self.server_version >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            remaining = decode(float, fields)
        else:
            remaining = decode(int, fields)

        avgFillPrice = decode(float, fields)

        permId = decode(int, fields)  # ver 2 field
        parentId = decode(int, fields)  # ver 3 field
        lastFillPrice = decode(float, fields)  # ver 4 field
        clientId = decode(int, fields)  # ver 5 field
        whyHeld = decode(str, fields)  # ver 6 field

        if self.server_version >= MIN_SERVER_VER_MARKET_CAP_PRICE:
            mktCapPrice = decode(float, fields)
        else:
            mktCapPrice = None

        # self.response_handler.orderStatus(orderId, status, filled, remaining,
        #    avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)

    def processOpenOrder(self, fields):

        next(fields)

        if self.server_version < MIN_SERVER_VER_ORDER_CONTAINER:
            version = decode(int, fields)
        else:
            version = self.server_version

        order = Order()
        order.orderId = decode(int, fields)

        contract = Contract()

        contract.id = decode(int, fields)  # ver 17 field
        contract.symbol = decode(str, fields)
        contract.security_type = decode(str, fields)
        contract.last_trade_date_or_contract_month = decode(str, fields)
        contract.strike = decode(float, fields)
        contract.right = decode(str, fields)
        if version >= 32:
            contract.multiplier = decode(str, fields)
        contract.exchange = decode(str, fields)
        contract.currency = decode(str, fields)
        contract.localSymbol = decode(str, fields)  # ver 2 field
        if version >= 32:
            contract.tradingClass = decode(str, fields)

        # read order fields
        order.action = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            order.totalQuantity = decode(float, fields)
        else:
            order.totalQuantity = decode(int, fields)

        order.orderType = decode(str, fields)
        if version < 29:
            order.lmtPrice = decode(float, fields)
        else:
            order.lmtPrice = decode(float, fields, SHOW_UNSET)
        if version < 30:
            order.auxPrice = decode(float, fields)
        else:
            order.auxPrice = decode(float, fields, SHOW_UNSET)
        order.tif = decode(str, fields)
        order.ocaGroup = decode(str, fields)
        order.account = decode(str, fields)
        order.openClose = decode(str, fields)

        order.origin = decode(int, fields)

        order.orderRef = decode(str, fields)
        order.clientId = decode(int, fields)  # ver 3 field
        order.permId = decode(int, fields)  # ver 4 field

        order.outsideRth = decode(bool, fields)  # ver 18 field
        order.hidden = decode(bool, fields)  # ver 4 field
        order.discretionaryAmt = decode(float, fields)  # ver 4 field
        order.goodAfterTime = decode(str, fields)  # ver 5 field

        _sharesAllocation = decode(str, fields)  # deprecated ver 6 field

        order.faGroup = decode(str, fields)  # ver 7 field
        order.faMethod = decode(str, fields)  # ver 7 field
        order.faPercentage = decode(str, fields)  # ver 7 field
        order.faProfile = decode(str, fields)  # ver 7 field

        if self.server_version >= MIN_SERVER_VER_MODELS_SUPPORT:
            order.modelCode = decode(str, fields)

        order.goodTillDate = decode(str, fields)  # ver 8 field

        order.rule80A = decode(str, fields)  # ver 9 field
        order.percentOffset = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.settlingFirm = decode(str, fields)  # ver 9 field
        order.shortSaleSlot = decode(int, fields)  # ver 9 field
        order.designatedLocation = decode(str, fields)  # ver 9 field
        if self.server_version == MIN_SERVER_VER_SSHORTX_OLD:
            decode(int, fields)
        elif version >= 23:
            order.exemptCode = decode(int, fields)
        order.auctionStrategy = decode(int, fields)  # ver 9 field
        order.startingPrice = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.stockRefPrice = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.delta = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.stockRangeLower = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.stockRangeUpper = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.displaySize = decode(int, fields)  # ver 9 field

        # if( version < 18) {
        #		# will never happen
        #		/* order.rthOnly = */ readBoolFromInt()
        # }

        order.blockOrder = decode(bool, fields)  # ver 9 field
        order.sweepToFill = decode(bool, fields)  # ver 9 field
        order.allOrNone = decode(bool, fields)  # ver 9 field
        order.minQty = decode(int, fields, SHOW_UNSET)  # ver 9 field
        order.ocaType = decode(int, fields)  # ver 9 field
        order.eTradeOnly = decode(bool, fields)  # ver 9 field
        order.firmQuoteOnly = decode(bool, fields)  # ver 9 field
        order.nbboPriceCap = decode(float, fields, SHOW_UNSET)  # ver 9 field

        order.parentId = decode(int, fields)  # ver 10 field
        order.triggerMethod = decode(int, fields)  # ver 10 field

        order.volatility = decode(float, fields, SHOW_UNSET)  # ver 11 field
        order.volatilityType = decode(int, fields)  # ver 11 field
        order.deltaNeutralOrderType = decode(str, fields)  # ver 11 field (had a hack for ver 11)
        order.deltaNeutralAuxPrice = decode(float, fields, SHOW_UNSET)  # ver 12 field

        if version >= 27 and order.deltaNeutralOrderType:
            order.deltaNeutralConId = decode(int, fields)
            order.deltaNeutralSettlingFirm = decode(str, fields)
            order.deltaNeutralClearingAccount = decode(str, fields)
            order.deltaNeutralClearingIntent = decode(str, fields)

        if version >= 31 and order.deltaNeutralOrderType:
            order.deltaNeutralOpenClose = decode(str, fields)
            order.deltaNeutralShortSale = decode(bool, fields)
            order.deltaNeutralShortSaleSlot = decode(int, fields)
            order.deltaNeutralDesignatedLocation = decode(str, fields)

        order.continuousUpdate = decode(bool, fields)  # ver 11 field

        # will never happen
        # if( self.server_version == 26) {
        #	order.stockRangeLower = readDouble()
        #	order.stockRangeUpper = readDouble()
        # }

        order.referencePriceType = decode(int, fields)  # ver 11 field

        order.trailStopPrice = decode(float, fields, SHOW_UNSET)  # ver 13 field

        if version >= 30:
            order.trailingPercent = decode(float, fields, SHOW_UNSET)

        order.basisPoints = decode(float, fields, SHOW_UNSET)  # ver 14 field
        order.basisPointsType = decode(int, fields, SHOW_UNSET)  # ver 14 field
        contract.comboLegsDescrip = decode(str, fields)  # ver 14 field

        if version >= 29:
            comboLegsCount = decode(int, fields)

            if comboLegsCount > 0:
                contract.comboLegs = []
                for _ in range(comboLegsCount):
                    comboLeg = ComboLeg()
                    comboLeg.conId = decode(int, fields)
                    comboLeg.ratio = decode(int, fields)
                    comboLeg.action = decode(str, fields)
                    comboLeg.exchange = decode(str, fields)
                    comboLeg.openClose = decode(int, fields)
                    comboLeg.shortSaleSlot = decode(int, fields)
                    comboLeg.designatedLocation = decode(str, fields)
                    comboLeg.exemptCode = decode(int, fields)
                    contract.comboLegs.append(comboLeg)

            orderComboLegsCount = decode(int, fields)
            if orderComboLegsCount > 0:
                order.orderComboLegs = []
                for _ in range(orderComboLegsCount):
                    orderComboLeg = OrderComboLeg()
                    orderComboLeg.price = decode(float, fields, SHOW_UNSET)
                    order.orderComboLegs.append(orderComboLeg)

        if version >= 26:
            smartComboRoutingParamsCount = decode(int, fields)
            if smartComboRoutingParamsCount > 0:
                order.smartComboRoutingParams = []
                for _ in range(smartComboRoutingParamsCount):
                    tagValue = TagValue()
                    tagValue.tag = decode(str, fields)
                    tagValue.value = decode(str, fields)
                    order.smartComboRoutingParams.append(tagValue)

        if version >= 20:
            order.scaleInitLevelSize = decode(int, fields, SHOW_UNSET)
            order.scaleSubsLevelSize = decode(int, fields, SHOW_UNSET)
        else:
            # ver 15 fields
            order.notSuppScaleNumComponents = decode(int, fields, SHOW_UNSET)
            order.scaleInitLevelSize = decode(int, fields, SHOW_UNSET)  # scaleComponectSize

        order.scalePriceIncrement = decode(float, fields, SHOW_UNSET)  # ver 15 field

        if version >= 28 and order.scalePriceIncrement != UNSET_DOUBLE \
                and order.scalePriceIncrement > 0.0:
            order.scalePriceAdjustValue = decode(float, fields, SHOW_UNSET)
            order.scalePriceAdjustInterval = decode(int, fields, SHOW_UNSET)
            order.scaleProfitOffset = decode(float, fields, SHOW_UNSET)
            order.scaleAutoReset = decode(bool, fields)
            order.scaleInitPosition = decode(int, fields, SHOW_UNSET)
            order.scaleInitFillQty = decode(int, fields, SHOW_UNSET)
            order.scaleRandomPercent = decode(bool, fields)

        if version >= 24:
            order.hedgeType = decode(str, fields)
            if order.hedgeType:
                order.hedgeParam = decode(str, fields)

        if version >= 25:
            order.optOutSmartRouting = decode(bool, fields)

        order.clearingAccount = decode(str, fields)  # ver 19 field
        order.clearingIntent = decode(str, fields)  # ver 19 field

        if version >= 22:
            order.notHeld = decode(bool, fields)

        if version >= 20:
            deltaNeutralContractPresent = decode(bool, fields)
            if deltaNeutralContractPresent:
                contract.deltaNeutralContract = DeltaNeutralContract()
                contract.deltaNeutralContract.conId = decode(int, fields)
                contract.deltaNeutralContract.delta = decode(float, fields)
                contract.deltaNeutralContract.price = decode(float, fields)

        if version >= 21:
            order.algoStrategy = decode(str, fields)
            if order.algoStrategy:
                algoParamsCount = decode(int, fields)
                if algoParamsCount > 0:
                    order.algoParams = []
                    for _ in range(algoParamsCount):
                        tagValue = TagValue()
                        tagValue.tag = decode(str, fields)
                        tagValue.value = decode(str, fields)
                        order.algoParams.append(tagValue)

        if version >= 33:
            order.solicited = decode(bool, fields)

        orderState = OrderState()

        order.whatIf = decode(bool, fields)  # ver 16 field

        orderState.status = decode(str, fields)  # ver 16 field
        if self.server_version >= MIN_SERVER_VER_WHAT_IF_EXT_FIELDS:
            orderState.initMarginBefore = decode(str, fields)
            orderState.maintMarginBefore = decode(str, fields)
            orderState.equityWithLoanBefore = decode(str, fields)
            orderState.initMarginChange = decode(str, fields)
            orderState.maintMarginChange = decode(str, fields)
            orderState.equityWithLoanChange = decode(str, fields)

        orderState.initMarginAfter = decode(str, fields)  # ver 16 field
        orderState.maintMarginAfter = decode(str, fields)  # ver 16 field
        orderState.equityWithLoanAfter = decode(str, fields)  # ver 16 field

        orderState.commission = decode(float, fields, SHOW_UNSET)  # ver 16 field
        orderState.minCommission = decode(float, fields, SHOW_UNSET)  # ver 16 field
        orderState.maxCommission = decode(float, fields, SHOW_UNSET)  # ver 16 field
        orderState.commissionCurrency = decode(str, fields)  # ver 16 field
        orderState.warningText = decode(str, fields)  # ver 16 field

        if version >= 34:
            order.randomizeSize = decode(bool, fields)
            order.randomizePrice = decode(bool, fields)

        if self.server_version >= MIN_SERVER_VER_PEGGED_TO_BENCHMARK:
            if order.orderType == "PEG BENCH":
                order.referenceContractId = decode(int, fields)
                order.isPeggedChangeAmountDecrease = decode(bool, fields)
                order.peggedChangeAmount = decode(float, fields)
                order.referenceChangeAmount = decode(float, fields)
                order.referenceExchangeId = decode(str, fields)

            conditionsSize = decode(int, fields)
            if conditionsSize > 0:
                order.conditions = []
                for _ in range(conditionsSize):
                    conditionType = decode(int, fields)
                    condition = order_condition.Create(conditionType)
                    condition.decode(fields)
                    order.conditions.append(condition)

                order.conditionsIgnoreRth = decode(bool, fields)
                order.conditionsCancelOrder = decode(bool, fields)

            order.adjustedOrderType = decode(str, fields)
            order.triggerPrice = decode(float, fields)
            order.trailStopPrice = decode(float, fields)
            order.lmtPriceOffset = decode(float, fields)
            order.adjustedStopPrice = decode(float, fields)
            order.adjustedStopLimitPrice = decode(float, fields)
            order.adjustedTrailingAmount = decode(float, fields)
            order.adjustableTrailingUnit = decode(int, fields)

        if self.server_version >= MIN_SERVER_VER_SOFT_DOLLAR_TIER:
            name = decode(str, fields)
            value = decode(str, fields)
            displayName = decode(str, fields)
            order.softDollarTier = SoftDollarTier(name, value, displayName)

        if self.server_version >= MIN_SERVER_VER_CASH_QTY:
            order.cashQty = decode(float, fields)

        if self.server_version >= MIN_SERVER_VER_AUTO_PRICE_FOR_HEDGE:
            order.dontUseAutoPriceForHedge = decode(bool, fields)

        if self.server_version >= MIN_SERVER_VER_ORDER_CONTAINER:
            order.isOmsContainer = decode(bool, fields)

        # self.response_handler.openOrder(order.orderId, contract, order, orderState)

    def processPortfolioValueMsg(self, fields):

        next(fields)
        version = decode(int, fields)

        # read contract fields
        contract = Contract()
        contract.id = decode(int, fields)  # ver 6 field
        contract.symbol = decode(str, fields)
        contract.security_type = decode(str, fields)
        contract.last_trade_date_or_contract_month = decode(str, fields)
        contract.strike = decode(float, fields)
        contract.right = decode(str, fields)

        if version >= 7:
            contract.multiplier = decode(str, fields)
            contract.primaryExchange = decode(str, fields)

        contract.currency = decode(str, fields)
        contract.localSymbol = decode(str, fields)  # ver 2 field
        if version >= 8:
            contract.tradingClass = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            position = decode(float, fields)
        else:
            position = decode(int, fields)

        marketPrice = decode(float, fields)
        marketValue = decode(float, fields)
        averageCost = decode(float, fields)  # ver 3 field
        unrealizedPNL = decode(float, fields)  # ver 3 field
        realizedPNL = decode(float, fields)  # ver 3 field

        accountName = decode(str, fields)  # ver 4 field

        if version == 6 and self.server_version == 39:
            contract.primaryExchange = decode(str, fields)

        # self.response_handler.updatePortfolio( contract,
        #    position, marketPrice, marketValue, averageCost,
        #    unrealizedPNL, realizedPNL, accountName)

    def processExecutionDataMsg(self, fields):
        next(fields)
        version = self.server_version

        if (self.server_version < MIN_SERVER_VER_LAST_LIQUIDITY):
            version = decode(int, fields)

        reqId = -1
        if version >= 7:
            reqId = decode(int, fields)

        orderId = decode(int, fields)

        # decode contract fields
        contract = Contract()
        contract.id = decode(int, fields)  # ver 5 field
        contract.symbol = decode(str, fields)
        contract.security_type = decode(str, fields)
        contract.last_trade_date_or_contract_month = decode(str, fields)
        contract.strike = decode(float, fields)
        contract.right = decode(str, fields)
        if version >= 9:
            contract.multiplier = decode(str, fields)
        contract.exchange = decode(str, fields)
        contract.currency = decode(str, fields)
        contract.localSymbol = decode(str, fields)
        if version >= 10:
            contract.tradingClass = decode(str, fields)

        # decode execution fields
        execution = Execution()
        execution.orderId = orderId
        execution.execId = decode(str, fields)
        execution.time = decode(str, fields)
        execution.acctNumber = decode(str, fields)
        execution.exchange = decode(str, fields)
        execution.side = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            execution.shares = decode(float, fields)
        else:
            execution.shares = decode(int, fields)

        execution.price = decode(float, fields)
        execution.permId = decode(int, fields)  # ver 2 field
        execution.clientId = decode(int, fields)  # ver 3 field
        execution.liquidation = decode(int, fields)  # ver 4 field

        if version >= 6:
            execution.cumQty = decode(float, fields)
            execution.avgPrice = decode(float, fields)

        if version >= 8:
            execution.orderRef = decode(str, fields)

        if version >= 9:
            execution.evRule = decode(str, fields)
            execution.evMultiplier = decode(float, fields)
        if self.server_version >= MIN_SERVER_VER_MODELS_SUPPORT:
            execution.modelCode = decode(str, fields)
        if self.server_version >= MIN_SERVER_VER_LAST_LIQUIDITY:
            execution.lastLiquidity = decode(int, fields)

        # self.response_handler.execDetails(reqId, contract, execution)


    def processHistoricalDataUpdateMsg(self, fields):
        next(fields)
        reqId = decode(int, fields)
        bar = BarData()
        bar.barCount = decode(int, fields)
        bar.date = decode(str, fields)
        bar.open = decode(float, fields)
        bar.close = decode(float, fields)
        bar.high = decode(float, fields)
        bar.low = decode(float, fields)
        bar.average = decode(float, fields)
        bar.volume = decode(int, fields)
        # self.response_handler.historicalDataUpdate(reqId, bar)

    def processRealTimeBarMsg(self, fields):
        next(fields)
        decode(int, fields)
        reqId = decode(int, fields)

        bar = RealTimeBar()
        bar.time = decode(int, fields)
        bar.open = decode(float, fields)
        bar.high = decode(float, fields)
        bar.low = decode(float, fields)
        bar.close = decode(float, fields)
        bar.volume = decode(int, fields)
        bar.wap = decode(float, fields)
        bar.count = decode(int, fields)

        # self.response_handler.realtimeBar(reqId, bar.time, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.wap, bar.count)

    def processTickOptionComputationMsg(self, fields):
        optPrice = None
        pvDividend = None
        gamma = None
        vega = None
        theta = None
        undPrice = None

        next(fields)
        version = decode(int, fields)
        reqId = decode(int, fields)
        tickTypeInt = decode(int, fields)

        impliedVol = decode(float, fields)
        delta = decode(float, fields)

        if impliedVol < 0:  # -1 is the "not computed" indicator
            impliedVol = None
        if delta == -2:  # -2 is the "not computed" indicator
            delta = None

        if version >= 6 or \
                tickTypeInt == TickTypeEnum.MODEL_OPTION or \
                tickTypeInt == TickTypeEnum.DELAYED_MODEL_OPTION:

            optPrice = decode(float, fields)
            pvDividend = decode(float, fields)

            if optPrice == -1:  # -1 is the "not computed" indicator
                optPrice = None
            if pvDividend == -1:  # -1 is the "not computed" indicator
                pvDividend = None

        if version >= 6:
            gamma = decode(float, fields)
            vega = decode(float, fields)
            theta = decode(float, fields)
            undPrice = decode(float, fields)

            if gamma == -2:  # -2 is the "not yet computed" indicator
                gamma = None
            if vega == -2:  # -2 is the "not yet computed" indicator
                vega = None
            if theta == -2:  # -2 is the "not yet computed" indicator
                theta = None
            if undPrice == -1:  # -1 is the "not computed" indicator
                undPrice = None

        # self.response_handler.tickOptionComputation(reqId, tickTypeInt, impliedVol,
        #    delta, optPrice, pvDividend, gamma, vega, theta, undPrice)

    def processDeltaNeutralValidationMsg(self, fields):
        next(fields)
        decode(int, fields)
        reqId = decode(int, fields)

        deltaNeutralContract = DeltaNeutralContract()

        deltaNeutralContract.conId = decode(int, fields)
        deltaNeutralContract.delta = decode(float, fields)
        deltaNeutralContract.price = decode(float, fields)

        # self.response_handler.deltaNeutralValidation(reqId, deltaNeutralContract)

    def processMarketDataTypeMsg(self, fields):
        next(fields)
        decode(int, fields)
        reqId = decode(int, fields)
        marketDataType = decode(int, fields)

        # self.response_handler.marketDataType(reqId, marketDataType)

    def processCommissionReportMsg(self, fields):
        next(fields)
        decode(int, fields)

        commissionReport = CommissionReport()
        commissionReport.execId = decode(str, fields)
        commissionReport.commission = decode(float, fields)
        commissionReport.currency = decode(str, fields)
        commissionReport.realizedPNL = decode(float, fields)
        commissionReport.yield_ = decode(float, fields)
        commissionReport.yieldRedemptionDate = decode(int, fields)

        # self.response_handler.commissionReport(commissionReport)

    def processPositionDataMsg(self, fields):
        next(fields)
        version = decode(int, fields)

        account = decode(str, fields)

        # decode contract fields
        contract = Contract()
        contract.id = decode(int, fields)
        contract.symbol = decode(str, fields)
        contract.security_type = decode(str, fields)
        contract.last_trade_date_or_contract_month = decode(str, fields)
        contract.strike = decode(float, fields)
        contract.right = decode(str, fields)
        contract.multiplier = decode(str, fields)
        contract.exchange = decode(str, fields)
        contract.currency = decode(str, fields)
        contract.localSymbol = decode(str, fields)
        if version >= 2:
            contract.tradingClass = decode(str, fields)

        if self.server_version >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            position = decode(float, fields)
        else:
            position = decode(int, fields)

        avgCost = 0.
        if version >= 3:
            avgCost = decode(float, fields)

        # self.response_handler.position(account, contract, position, avgCost)

    def processPositionMultiMsg(self, fields):
        next(fields)
        decode(int, fields)
        reqId = decode(int, fields)
        account = decode(str, fields)

        # decode contract fields
        contract = Contract()
        contract.id = decode(int, fields)
        contract.symbol = decode(str, fields)
        contract.security_type = decode(str, fields)
        contract.last_trade_date_or_contract_month = decode(str, fields)
        contract.strike = decode(float, fields)
        contract.right = decode(str, fields)
        contract.multiplier = decode(str, fields)
        contract.exchange = decode(str, fields)
        contract.currency = decode(str, fields)
        contract.localSymbol = decode(str, fields)
        contract.tradingClass = decode(str, fields)
        position = decode(float, fields)
        avgCost = decode(float, fields)
        modelCode = decode(str, fields)

        # self.response_handler.positionMulti(reqId, account, modelCode, contract, position, avgCost)

    def processSecurityDefinitionOptionParameterMsg(self, fields):
        next(fields)

        reqId = decode(int, fields)
        exchange = decode(str, fields)
        underlyingConId = decode(int, fields)
        tradingClass = decode(str, fields)
        multiplier = decode(str, fields)

        expCount = decode(int, fields)
        expirations = set()
        for _ in range(expCount):
            expiration = decode(str, fields)
            expirations.add(expiration)

        strikeCount = decode(int, fields)
        strikes = set()
        for _ in range(strikeCount):
            strike = decode(float, fields)
            strikes.add(strike)

        # self.response_handler.securityDefinitionOptionParameter(reqId, exchange,
        #    underlyingConId, tradingClass, multiplier, expirations, strikes)

    def processSecurityDefinitionOptionParameterEndMsg(self, fields):
        next(fields)

        reqId = decode(int, fields)
        # self.response_handler.securityDefinitionOptionParameterEnd(reqId)

    def processSoftDollarTiersMsg(self, fields):
        next(fields)

        reqId = decode(int, fields)
        nTiers = decode(int, fields)

        tiers = []
        for _ in range(nTiers):
            tier = SoftDollarTier()
            tier.name = decode(str, fields)
            tier.val = decode(str, fields)
            tier.displayName = decode(str, fields)
            tiers.append(tier)

    def processSmartComponents(self, fields):
        next(fields)
        reqId = decode(int, fields)
        n = decode(int, fields)

        smartComponentMap = []
        for _ in range(n):
            smartComponent = SmartComponent()
            smartComponent.bitNumber = decode(int, fields)
            smartComponent.exchange = decode(str, fields)
            smartComponent.exchangeLetter = decode(str, fields)
            smartComponentMap.append(smartComponent)

    def processTickReqParams(self, fields):
        next(fields)
        tickerId = decode(int, fields)
        minTick = decode(float, fields)
        bboExchange = decode(str, fields)
        snapshotPermissions = decode(int, fields)

    def processMktDepthExchanges(self, fields):
        next(fields)
        depthMktDataDescriptions = []
        nDepthMktDataDescriptions = decode(int, fields)

        if nDepthMktDataDescriptions > 0:
            for _ in range(nDepthMktDataDescriptions):
                desc = DepthMktDataDescription()
                desc.exchange = decode(str, fields)
                desc.security_type = decode(str, fields)
                if self.server_version >= MIN_SERVER_VER_SERVICE_DATA_TYPE:
                    desc.listingExch = decode(str, fields)
                    desc.serviceDataType = decode(str, fields)
                    desc.aggGroup = decode(int, fields)
                else:
                    decode(int, fields)  # boolean notSuppIsL2
                depthMktDataDescriptions.append(desc)

    def processTickNews(self, fields):
        next(fields)
        tickerId = decode(int, fields)
        timeStamp = decode(int, fields)
        providerCode = decode(str, fields)
        articleId = decode(str, fields)
        headline = decode(str, fields)
        extraData = decode(str, fields)

    def processNewsProviders(self, fields):
        next(fields)
        newsProviders = []
        nNewsProviders = decode(int, fields)
        if nNewsProviders > 0:
            for _ in range(nNewsProviders):
                provider = NewsProvider()
                provider.code = decode(str, fields)
                provider.name = decode(str, fields)
                newsProviders.append(provider)


    def processNewsArticle(self, fields):
        next(fields)
        reqId = decode(int, fields)
        articleType = decode(int, fields)
        articleText = decode(str, fields)

    def processHistoricalNews(self, fields):
        next(fields)
        requestId = decode(int, fields)
        time = decode(str, fields)
        providerCode = decode(str, fields)
        articleId = decode(str, fields)
        headline = decode(str, fields)

    def processHistoricalNewsEnd(self, fields):
        next(fields)
        reqId = decode(int, fields)
        hasMore = decode(bool, fields)

    def processHistogramData(self, fields):
        next(fields)
        reqId = decode(int, fields)
        numPoints = decode(int, fields)

        histogram = []
        for _ in range(numPoints):
            dataPoint = HistogramData()
            dataPoint.price = decode(float, fields)
            dataPoint.count = decode(int, fields)
            histogram.append(dataPoint)


    def processMarketRuleMsg(self, fields):
        next(fields)
        marketRuleId = decode(int, fields)

        nPriceIncrements = decode(int, fields)
        priceIncrements = []

        if nPriceIncrements > 0:
            for _ in range(nPriceIncrements):
                prcInc = PriceIncrement()
                prcInc.lowEdge = decode(float, fields)
                prcInc.increment = decode(float, fields)
                priceIncrements.append(prcInc)


    def processPnLMsg(self, fields):
        next(fields)
        reqId = decode(int, fields)
        dailyPnL = decode(float, fields)
        unrealizedPnL = None
        realizedPnL = None

        if self.server_version >= MIN_SERVER_VER_UNREALIZED_PNL:
            unrealizedPnL = decode(float, fields)

        if self.server_version >= MIN_SERVER_VER_REALIZED_PNL:
            realizedPnL = decode(float, fields)

        # self.response_handler.pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)

    def processPnLSingleMsg(self, fields):
        next(fields)
        reqId = decode(int, fields)
        pos = decode(int, fields)
        dailyPnL = decode(float, fields)
        unrealizedPnL = None
        realizedPnL = None

        if self.server_version >= MIN_SERVER_VER_UNREALIZED_PNL:
            unrealizedPnL = decode(float, fields)

        if self.server_version >= MIN_SERVER_VER_REALIZED_PNL:
            realizedPnL = decode(float, fields)

        value = decode(float, fields)

        # self.response_handler.pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)

    def processHistoricalTicks(self, fields):
        next(fields)
        reqId = decode(int, fields)
        tickCount = decode(int, fields)

        ticks = []

        for _ in range(tickCount):
            historicalTick = HistoricalTick()
            historicalTick.time = decode(int, fields)
            next(fields)  # for consistency
            historicalTick.price = decode(float, fields)
            historicalTick.size = decode(int, fields)
            ticks.append(historicalTick)

        done = decode(bool, fields)

        # self.response_handler.historicalTicks(reqId, ticks, done)

    def processHistoricalTicksBidAsk(self, fields):
        next(fields)
        reqId = decode(int, fields)
        tickCount = decode(int, fields)

        ticks = []

        for _ in range(tickCount):
            historicalTickBidAsk = HistoricalTickBidAsk()
            historicalTickBidAsk.time = decode(int, fields)
            mask = decode(int, fields)
            tickAttribBidAsk = TickAttribBidAsk()
            tickAttribBidAsk.askPastHigh = mask & 1 != 0
            tickAttribBidAsk.bidPastLow = mask & 2 != 0
            historicalTickBidAsk.tickAttribBidAsk = tickAttribBidAsk
            historicalTickBidAsk.priceBid = decode(float, fields)
            historicalTickBidAsk.priceAsk = decode(float, fields)
            historicalTickBidAsk.sizeBid = decode(int, fields)
            historicalTickBidAsk.sizeAsk = decode(int, fields)
            ticks.append(historicalTickBidAsk)

        done = decode(bool, fields)

        # self.response_handler.historicalTicksBidAsk(reqId, ticks, done)

    def processHistoricalTicksLast(self, fields):
        next(fields)
        reqId = decode(int, fields)
        tickCount = decode(int, fields)

        ticks = []

        for _ in range(tickCount):
            historicalTickLast = HistoricalTickLast()
            historicalTickLast.time = decode(int, fields)
            mask = decode(int, fields)
            tickAttribLast = TickAttribLast()
            tickAttribLast.pastLimit = mask & 1 != 0
            tickAttribLast.unreported = mask & 2 != 0
            historicalTickLast.tickAttribLast = tickAttribLast
            historicalTickLast.price = decode(float, fields)
            historicalTickLast.size = decode(int, fields)
            historicalTickLast.exchange = decode(str, fields)
            historicalTickLast.specialConditions = decode(str, fields)
            ticks.append(historicalTickLast)

        done = decode(bool, fields)

        # self.response_handler.historicalTicksLast(reqId, ticks, done)

    def processTickByTickMsg(self, fields):
        next(fields)
        reqId = decode(int, fields)
        tickType = decode(int, fields)
        time = decode(int, fields)

        if tickType == 0:
            # None
            pass
        elif tickType == 1 or tickType == 2:
            # Last or AllLast
            price = decode(float, fields)
            size = decode(int, fields)
            mask = decode(int, fields)

            tickAttribLast = TickAttribLast()
            tickAttribLast.pastLimit = mask & 1 != 0
            tickAttribLast.unreported = mask & 2 != 0
            exchange = decode(str, fields)
            specialConditions = decode(str, fields)

            # self.response_handler.tickByTickAllLast(reqId, tickType, time, price, size, tickAttribLast,
            #                               exchange, specialConditions)
        elif tickType == 3:
            # BidAsk
            bidPrice = decode(float, fields)
            askPrice = decode(float, fields)
            bidSize = decode(int, fields)
            askSize = decode(int, fields)
            mask = decode(int, fields)
            tickAttribBidAsk = TickAttribBidAsk()
            tickAttribBidAsk.bidPastLow = mask & 1 != 0
            tickAttribBidAsk.askPastHigh = mask & 2 != 0

            # self.response_handler.tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize,
            #                              askSize, tickAttribBidAsk)
        elif tickType == 4:
            # MidPoint
            midPoint = decode(float, fields)

            # self.response_handler.tickByTickMidPoint(reqId, time, midPoint)

    def processOrderBoundMsg(self, fields):
        next(fields)
        reqId = decode(int, fields)
        apiClientId = decode(int, fields)
        apiOrderId = decode(int, fields)

        # self.response_handler.orderBound(reqId, apiClientId, apiOrderId)


    ######################################################################

    def readLastTradeDate(self, fields, contract: ContractDetails, isBond: bool):
        last_trade_date_or_contract_month = decode(str, fields)
        if last_trade_date_or_contract_month is not None:
            splitted = last_trade_date_or_contract_month.split()
            if len(splitted) > 0:
                if isBond:
                    contract.maturity = splitted[0]
                else:
                    contract.contract.last_trade_date_or_contract_month = splitted[0]

            if len(splitted) > 1:
                contract.lastTradeTime = splitted[1]

            if isBond and len(splitted) > 2:
                contract.timeZoneId = splitted[2]

    ######################################################################

