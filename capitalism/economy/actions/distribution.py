from economy.models.report import Trace
from economy.models.owners import Industry, SocialClass
from economy.models.commodity import Commodity
from economy.actions.exchange import calculate_demand
from economy.actions.helpers import set_initial_capital
from ..global_constants import *

"""
 In the revenue stage, profit is transferred to the owners of the industries
 In a more complex setup (for example with bankers or government) we will need specific rules to say what these various agents receive
 Once the owners (and other agencies) have received their profit, they decide what to do with it.
 The complication is that they cannot always be paid in money, because we would need to reach the M-C stage before they actually get the money.
 Strictly, what they should do at this point is register a claim on the money.
 For simplicity, we simply give them enough money to be sure they can pay it over
 Interesting question: do industry owners have by definition a credit relation with their industries?
 Certainly, if the company issues shares, then they do, because the shareholders have pieces of paper that are exchangeable, that is, they function as credit instruments but if there is a family owner, it's more moot. Basically, they have credit (it's called "capital" by the accountants) but it is not monetised
"""

def calculate_revenue(simulation):
    current_time_stamp=simulation.current_time_stamp
    Trace.enter(simulation,0,"Calculate capitalist revenue and other property-based entitlements")
    for industry in Industry.objects.filter(time_stamp=current_time_stamp):
        donor_money_stock=industry.money_stock
        recipient=SocialClass.objects.get(time_stamp=current_time_stamp, name="Capitalists")
        Trace.enter(simulation,2,f"Industry {Trace.o(industry.name)} has made a profit of {Trace.q(industry.profit)} which will be transferred to {Trace.o(recipient.name)}")
        recipient_money_stock=recipient.money_stock
        donor_money_stock.change_size(-industry.profit)
        recipient_money_stock.change_size(industry.profit)
        donor_money_stock.save()
        recipient_money_stock.save()

"""
In the 'invest' step, the capitalists decide what to do with their money.

There are two fundamentally different simulation scenarios which go to the heart of the divisions in economics that have been around since Say and Proudhon. Proudhon, Say, and all equilibrium theory simply assumes that the economy reproduces itself. In this scenario, we simply take the given scales of production and consumption and perpetuate them.
It's not clear what happens if this is not possible, and this is (not unsurprisingly) the problem that bedevils all attempts to explore this scenario

In the other scenario explored by Marx, Kalecki, etc, there is no assumption of self-reproduction. Then there must be some mechanism or other that adjusts supply to demand, but over time
This too may break down, but assuming the simulation is good, the breakdown (if it occurs) will reflect what happens in the real world.

This second scenario, however, has two sub-categories. Generally, price-adjustment is supposed. 

The question is then whether there is some other possible adjustment process.If so, this is what should be pursued by rational government insofar as this is confined to the satisfaction of need. In this simulation, we  allow for all three variants. We therefore start by supposing that money is allocated to maintain the existing levels of production.

We should not be overly concerned with a shortage of money, because we know that credit steps in and because monetary shortage is a relatively complex issue, to be addressed when we have a government and a banking sector. Therefore, the 'disparity' question is this: when production is maintained at existing levels, does this result in a disparity between supply and demand?

The original simulation supposed that this will manifest itself in a disparity between *stocks* and *requirements*.
Is this algorithmically the same as a disparity between supply and demand? We'll treat it that way and see what happens (it's an interesting exercise)

Note that our current crude allocation mechanism does provide some sort of provision for dealing with demand/supply mismatches, in that final demand will be reduced as a result, leaving space for production to increase. But we don't know how the simulation will actually proceed without, basically, doing it.So let's try that to start with. 

A more sophisticated approach would be monetary, basically to cut wages, which corresponds more closely to what actually happens. But reluctant to introduce monetary constraints as the primary mechanism, essentially because credit intervenes. We therefore start from simple 'replenishment', get that working for the principal use cases Then explore the effect of supply shortages using the simulation itself.
"""
def calculate_investment(simulation):
    current_time_stamp=simulation.current_time_stamp
    calculate_demand(simulation=simulation) #! this is required if we are to estimate correctly the replenishment cost
    capitalists=SocialClass.objects.get(time_stamp=current_time_stamp, name="Capitalists")    
    industries=Industry.objects.filter(time_stamp=current_time_stamp)
    Trace.enter(simulation,1, f"Calculate input costs to continue producing at current scales")
    for industry in industries:
        cost=industry.replenishment_cost
        Trace.enter(simulation,1, f"{Trace.o(industry.name)} needs {Trace.q(cost)} to produce at its current scale of {Trace.q(industry.output_scale)}")
        #! just give them the money
        capitalists_money=capitalists.money_stock
        industry_money=industry.money_stock
        transferred_amount=cost-industry_money.size
        Trace.enter(simulation,1, f"{Trace.o(industry.name)} already has {Trace.q(industry_money.size)} and will receive {Trace.q(transferred_amount)}")
        capitalists_money.change_size(-transferred_amount)
        industry_money.change_size(transferred_amount)
        industry_money.save()
        capitalists_money.save()
    return

def effective_demand(simulation):
#! Not in current use, preserved here because we may want it.
    current_time_stamp=simulation.current_time_stamp
    total_monetarily_effective_demand=0
    for commodity in Commodity.objects.filter(time_stamp=current_time_stamp):
        commodity.monetarily_effective_demand=commodity.demand*commodity.unit_price
        Trace.enter(simulation,1,f"Evaluating money demand from {commodity.name} of origin {commodity.origin}; demand ={commodity.monetarily_effective_demand}")
        if commodity.origin=="INDUSTRIAL": #! filter didn't work, TODO we found out why, change the code
            total_monetarily_effective_demand+=commodity.monetarily_effective_demand
            commodity.save()
    Trace.enter(simulation,1,f"Total money demand is {Trace.o(total_monetarily_effective_demand)}")
    for commodity in Commodity.current_queryset():
        if commodity.origin=="INDUSTRIAL": #! filter didn't work, TODO we found out why, change the code
            commodity.investment_proportion=commodity.monetarily_effective_demand/total_monetarily_effective_demand
            Trace.enter(simulation,2,f"Investment proportion for {Trace.o(commodity.name)} is {Trace.q(commodity.investment_proportion)}")
            commodity.save()

