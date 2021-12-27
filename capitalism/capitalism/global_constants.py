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

CONTROL_SUPER_STATES = [
    (M_C, "M-C (exchange)"),
    (C_P, "C-P-C' (produce)"),
    (C_M, "C'-M' (distribute)"),
    (UNDEFINED, "###")
]


DEMAND = "Demand"
SUPPLY = "Supply"
ALLOCATE = "Allocate"
TRADE = "Trade"
PRODUCE = "Produce"
PRICES = "Prices"
REPRODUCE = "Reproduce"
REVENUE="Revenue"
ACCUMULATE="Accumulate"

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
