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
M_C = "M-C (exchange)"
C_P = "C-P-C' (produce)"
C_M = "C'-M' (distribute)"


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

class Step:
    def __init__(self, name, stage_name, next_step_name):
        self.name = name
        self.stage_name=stage_name
        self.next_step_name=next_step_name


STEPS={
  "demand":Step(name=DEMAND,stage_name="M_C", next_step_name=ALLOCATE),
  "allocate":Step(name=ALLOCATE,stage_name="M_C", next_step_name=TRADE),
  "trade":Step(name=TRADE,stage_name="M_C",next_step_name=PRODUCE),
  "produce":Step(name=PRODUCE,stage_name="C_P", next_step_name=PRICES),
  "prices":Step(name=PRICES,stage_name="C_P", next_step_name=REPRODUCE),
  "reproduce":Step(name=REPRODUCE,stage_name="C_P", next_step_name=REVENUE),
  "revenue":Step(name=REVENUE,stage_name="C_M",next_step_name=INVEST),
  "invest":Step(name=INVEST,stage_name="C_M", next_step_name=DEMAND),
  "UNDEFINED":Step(name=UNDEFINED,stage_name="C_M", next_step_name=UNDEFINED)
}

STAGES={
    "M_C":M_C,
    "C_P":C_P,
    "C_M":C_M
}

