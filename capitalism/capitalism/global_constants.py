SOCIAL = 'Social'
INDUSTRIAL = 'Industrial'
MONEY = 'Money'
CONSUMPTION = 'Consumption'
PRODUCTION = 'Production'
UNDEFINED = "###"
CAPITALISTS = "Capitalists"
WORKERS = "Workers"
INDUSTRY = "Industry"
SOCIAL_CLASS = "Social Class"
SALES = "Sales"

ORIGIN_CHOICES = [
    (SOCIAL, 'Social'),
    (INDUSTRIAL, 'Industrial'),
    (MONEY, 'Money'),
    (UNDEFINED, '###')
]

USAGE_CHOICES = [
    (PRODUCTION, 'Production'),
    (CONSUMPTION, 'Consumption'),
    (MONEY, 'Money'),
    (SALES, 'Sales'),
    (UNDEFINED, '###')
]

SOCIAL_CLASS_TYPES = [
    (CAPITALISTS, "Capitalists"),
    (WORKERS, "Workers"),
    (UNDEFINED, '###')
]

STOCK_OWNER_TYPES = [
    (INDUSTRY, 'Industry'),
    (SOCIAL_CLASS, 'Social Class'),
    (UNDEFINED, '###')
]

M_C = "M-C (exchange)"
C_P = "C-P-C' (produce)"
C_M = "C'-M' (distribute)"

DEMAND = "demand"
SUPPLY = "supply"
ALLOCATE = "allocate"
TRADE = "trade"
PRODUCE = "produce"
PRICES = "prices"
REPRODUCE = "reproduce"
REVENUE="revenue"
ACCUMULATE="accumulate"

CONTROL_SUB_STATES = [
    (DEMAND, "Demand"),
    (SUPPLY, "Supply"),
    (ALLOCATE, "Allocate"),
    (TRADE, "Trade"),
    (PRODUCE, "Produce"),
    (PRICES, "Prices"),
    (REPRODUCE, "Reproduce"),
    (REVENUE, "Revenue"),
    (ACCUMULATE, "Accumulate"),
    (UNDEFINED, "###")
]

class SubState:
    def __init__(self,name, superstate_name, next_substate_name):
        self.name = name
        self.superstate_name=superstate_name
        self.next_substate_name=next_substate_name


SUBSTATES={
  "demand":SubState(name=DEMAND,superstate_name="M_C", next_substate_name=SUPPLY),
  "supply":SubState(name=SUPPLY,superstate_name="M_C", next_substate_name=ALLOCATE),
  "allocate":SubState(name=ALLOCATE,superstate_name="M_C", next_substate_name=TRADE),
  "trade":SubState(name=TRADE,superstate_name="M_C",next_substate_name=PRODUCE),
  "produce":SubState(name=PRODUCE,superstate_name="C_P", next_substate_name=PRICES),
  "prices":SubState(name=PRICES,superstate_name="C_P", next_substate_name=REPRODUCE),
  "reproduce":SubState(name=REPRODUCE,superstate_name="C_P", next_substate_name=REVENUE),
  "revenue":SubState(name=REVENUE,superstate_name="C_M",next_substate_name=ACCUMULATE),
  "accumulate":SubState(name=ACCUMULATE,superstate_name="C_M", next_substate_name=DEMAND),
  "UNDEFINED":SubState(name=UNDEFINED,superstate_name="C_M", next_substate_name=UNDEFINED)
}

SUPERSTATES={
    "M_C":M_C,
    "C_P":C_P,
    "C_M":C_M
}

SUPERSTATE_NAMES=[ 
    M_C,C_P,C_M
]

