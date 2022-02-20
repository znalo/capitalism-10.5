import logging

logger = logging.getLogger(__name__)

SOCIAL = 'Social'
INDUSTRIAL = 'Industrial'
MONEY = 'Money'
CONSUMPTION = 'Consumption'
PRODUCTION = 'Production'
UNDEFINED = "Undefined"
CAPITALISTS = "Capitalists"
WORKERS = "Workers"
INDUSTRY = "Industry"
SOCIAL_CLASS = "Social Class"
SALES = "Sales"
DEMAND = "demand"
ALLOCATE = "allocate"
TRADE = "trade"
PRODUCE = "produce"
PRICES = "prices"
REPRODUCE = "reproduce"
REVENUE="revenue"
INVEST="invest"
CAPITAL="capital"
REVALUE="revalue"
M_C = "M-C (exchange)"
C_P = "C-P-C' (produce)"
C_M = "C'-M' (distribute)"
INITIAL="Initial"
VALUES='Values',
EQUALIZED='Equal Profit Rate',
DYNAMIC='Dynamic'



ORIGIN_CHOICES = [
    (SOCIAL, 'Social'),
    (INDUSTRIAL, 'Industrial'),
    (MONEY, 'Money'),
    (UNDEFINED, 'UNDEFINED')
]

USAGE_CHOICES = [
    (PRODUCTION, 'Production'),
    (CONSUMPTION, 'Consumption'),
    (MONEY, 'Money'),
    (SALES, 'Sales'),
    (UNDEFINED, 'UNDEFINED')
]

SOCIAL_CLASS_TYPES = [
    (CAPITALISTS, "Capitalists"),
    (WORKERS, "Workers"),
    (UNDEFINED, 'UNDEFINED')
]

STOCK_OWNER_TYPES = [
    (INDUSTRY, 'Industry'),
    (SOCIAL_CLASS, 'Social Class'),
    (UNDEFINED, 'UNDEFINED')
]

PRICE_RESPONSE_TYPES =[
    (VALUES,'Values'),
    (EQUALIZED, 'Equal Profit Rate'),
    (DYNAMIC, 'Dynamic')
]

class Step:
    def __init__(self, name, stage_name, next_step, description):
        self.name = name
        self.stage_name=stage_name
        self.next_step=next_step
        self.description=description


STEPS={
  "demand":Step(name=DEMAND,stage_name="M_C", next_step=ALLOCATE, description="EVALUATE DEMAND AND SUPPLY"),
  "allocate":Step(name=ALLOCATE,stage_name="M_C", next_step=TRADE, description="ALLOCATE SUPPLY"),
  "trade":Step(name=TRADE,stage_name="M_C",next_step=PRODUCE, description="TRADE"),
  "produce":Step(name=PRODUCE,stage_name="C_P", next_step="revalue", description="PRODUCE"),
  "revalue":Step(name=CAPITAL,stage_name="C_P", next_step="reprice", description="CALCULATE COMMODITY VALUES, STOCK VALUES, AND CAPITAL AS THE IMMEDIATE RESULT OF PRODUCTION"),
  "reprice":Step(name=REVALUE,stage_name="C_P", next_step=REPRODUCE, description="PRICE AND VALUE CHANGES ARISING FROM DISTRIBUTION"),
  "reproduce":Step(name=REPRODUCE,stage_name="C_P", next_step=REVENUE, description="SOCIAL REPRODUCTION"),
  "revenue":Step(name=REVENUE,stage_name="C_M",next_step=INVEST, description="REVENUES"),
  "invest":Step(name=INVEST,stage_name="C_M", next_step=DEMAND, description="INVESTMENT"),
  "UNDEFINED":Step(name=UNDEFINED,stage_name="C_M", next_step=UNDEFINED, description=UNDEFINED),
  "Initial":Step(name=INITIAL,stage_name="C_M", next_step=INITIAL, description=UNDEFINED),
}

STAGES={
    "M_C":M_C,
    "C_P":C_P,
    "C_M":C_M
}

