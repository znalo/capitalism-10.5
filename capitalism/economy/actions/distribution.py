from ..models.states import State, Log
from ..models.owners import Industry, SocialClass
from ..models.commodity import Commodity
from ..actions.exchange import calculate_demand, calculate_supply, set_initial_capital
from capitalism.global_constants import *

#! In the revenue stage, profit is transferred to the owners of the industries
#! In a more complex setup (for example with bankers or government) we will need
#! specific rules to say what these various agents receive
#! Once the owners (and other agencies) have received their profit, they decide what to do with it
#! The complication is that they cannot always be paid in money, because we would need to reach 
#! the M-C stage before they actually get the money.
#! Strictly, what they should do at this point is register a claim on the money.
#! For simplicity, we simply give them enough money to be sure they can pay it over
#? Interesting question: do industry owners have by definition a credit relation with their industries?
#? Certainly, if the company issues shares, then they do, because the shareholders have pieces of paper that are exchangeable,
#? that is, they function as credit instruments
#? but if there is a family owner, it's more moot. Basically, they have credit (it's called "capital" by the accountants) but it is not monetised

def revenue():
    Log.enter(0,"Calculate capitalist revenue and other property-based entitlements")
    for industry in Industry.time_stamped_queryset():
        Log.enter(2,f"Industry {Log.sim_object(industry.name)} has made a profit of {Log.sim_quantity(industry.profit)} which will be transferred to the capitalists")
        donor_money_stock=industry.money_stock
        recipient=SocialClass.capitalists()
        Log.enter(2,f"This will go to {Log.sim_object(recipient.name)}")
        recipient_money_stock=recipient.money_stock
        donor_money_stock.size-=industry.profit
        recipient_money_stock.size+=industry.profit
        donor_money_stock.save()
        recipient_money_stock.save()



#! Here, the capitalists decide what to do with their money
#! There is no special reason for them to invest in any particular industry just because it is there
#! This takes place if either 
# * they were simply capitalist planners, or
# * barriers to entry force the capitalists to re-invest in the same industries
#! but in general, they will pursue the greatest return on capital
#! In a price-driven model, the money will therefore go to the industry that is making the greatest profit
#! but if profit rates are equal, it will be distributed among the various industries proportinately
#! In general of course there will be a distribution of a 'Marginal Efficiency of Capital' type

#! Curiously, this is may be the simplest to implement, certainly in a price-driven model.
#! However, it would not guarantee the proportions of the industries so this has to be built in as an option, especially in the non-price-driven case

#* The money should be doled out in some manner that reflects the relative size of the industries
#* perhaps in proportion to the demand for their products? This would be the most obvious provision against some kind of catastrophic simulation-induced failure

#! so
#* calculate demand and supply again
#* Allocate money in proportion to the demand for the various outputs
#* Note that if supply is short in one branch, this method will gradually restore the supply
#* and vice versa

#! If the above reasoning is correct, then this allocation method is, in effect, the 'Schumpeterian self-restoration' assumption
#! Of course, there is no reason to suppose the market would behave like this
#! but that comes later, when we get to the price-driven scenario

def invest():
    #TODO complete this
    calculate_demand()
    total_monetarily_effective_demand=0
    for commodity in Commodity.time_stamped_queryset():
        commodity.monetarily_effective_demand=commodity.demand*commodity.unit_price
        Log.enter(1,f"Evaluating money demand from {commodity.name} of origin {commodity.origin}; demand ={commodity.monetarily_effective_demand}")
        if commodity.origin=="INDUSTRIAL": #! filter didn't work, TODO we found out why, change the code
            total_monetarily_effective_demand+=commodity.monetarily_effective_demand
            commodity.save()
    Log.enter(1,f"Total money demand is {Log.sim_object(total_monetarily_effective_demand)}")
    for commodity in Commodity.time_stamped_queryset():
        if commodity.origin=="INDUSTRIAL": #! filter didn't work, TODO we found out why, change the code
            commodity.investment_proportion=commodity.monetarily_effective_demand/total_monetarily_effective_demand
            Log.enter(2,f"Investment proportion for {Log.sim_object(commodity.name)} is {Log.sim_quantity(commodity.investment_proportion)}")
            commodity.save()

    #! TODO TODO TODO

    set_initial_capital() #! as soon as we are ready for the next circuit, we should reset the initial capital
     
