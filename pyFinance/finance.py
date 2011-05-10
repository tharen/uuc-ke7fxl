'''
Created on Nov 14, 2010

@author: Tod

Objects and functions for various financial calculations
'''

import random
import math
import datetime

def compound(value, rate, periods):
    """
    Return the future value and annuity table of a series of compounded interest payments
    
    value - Present value
    rate - Percentage change in value per period
    periods - Integer number of periods to compound  
    """
    annuity = [[0.0, 0.0]] * periods
    factor = 1 + rate
    for p, a in enumerate(annuity):
        a[0] = value * factor
        print a[0]
        a[1] = factor
        factor += rate


    return value * (factor - rate), annuity

def pvPayments(rate, periods, pmt, fv=0.0, annuityDue=False):
    """
    """
    pv = fv
    if not annuityDue:
        pv += pmt

    for p in xrange(periods):
        pv /= 1 + rate
        pv += pmt

    if not annuityDue:
        pv -= pmt

    return pv

def fvPayments(intRate, pmtAmount, pmtPeriods, initBalance=0, annuityDue=False):
    balance = initBalance
    runningBalance = []
    runningInterest = []

    for i in xrange(pmtPeriods):
        if annuityDue:
            #1 - payment is due at the beginning of the period prior to interest accrual
            balance += pmtAmount

            #2 - interest accrues and is applied to the balance
            interest = balance * intRate
            balance += interest

        else:
            #1 - Payment is due at the end of the period after interest accrual
            interest = balance * intRate
            balance += pmtAmount + interest

        runningBalance.append(balance)
        runningInterest.append(interest)

    return balance, runningBalance, runningInterest

def xfvPayments(rate, periods, pmt, pv=0.0, annuityDue=False):
    """
    Compute the future value of a series of payments
    
    pmt - Amount of the periodic payment
    rate - The interest rate earn on accumulated payments
    periods - number of periods payments are to be made
    pv - Current balance payments are applied to
    annuityDue - If True, payment is applied at the beginning of the period 
                    prior to interest accrual, (Annuity Due)
                If False, payment is applied after interest accrual (Ordinary Annuity)
    """

    fv = pv
    if annuityDue:
        fv += pmt

    for p in xrange(periods):
        fv *= 1 + rate
        fv += pmt

    if annuityDue:
        fv -= pmt

    return fv

class Account:
    def __init__(self, name, balance=0
                 , date=datetime.date.today()
                 , interestRate=0.0,):
        self.name = name
        self.initBalance = balance
        self.initDate = date
        self.interestRate = interestRate

        self._transacts = []

class AccountSim:
    def __init__(self, initYear, initAge,):
        self.initYear = initYear
        self.initAge = initAge

def normalRate(rate, stddev
               , minRate= -999.9, maxRate=999.9):
    """
    Calculate a random rate assuming a normal distribution with mean of rate and stddev
    """
    rate = random.normalvariate(rate, stddev)
    rate = min(rate, maxRate)
    rate = max(rate, minRate)
    return rate

def simulation(periods=10
               , balance=0.0
               , rate=0.0
               , varRate=lambda x: x
               ):
    periodicBalance = [None] * periods
    periodicRate = [None] * periods

    for p in xrange(periods):
        rate = varRate(rate)
        interest = balance * rate
        balance += interest
        periodicBalance[p] = balance
        periodicRate[p] = rate
#        print rate, interest, balance

    return periodicBalance, periodicRate

def test():
    pmt = 500
    rate = 0.003
    rateSD = .005
    periods = 12 # * 70
    pv = 1000

    tests = 1000
    varRate = lambda x: normalRate(x, rateSD, -0.1, 0.1)

    runs = []
    for i in xrange(tests):
        runs.append(simulation(periods, pv, rate, varRate)[0][-1])

    print simulation(periods, pv, rate, varRate)

    print '%g' % (sum(runs) / len(runs),)

#    v, a = compound(pv, rate, periods)
#    print v,
#    print pv * (1 + rate) ** periods
#    print a

#    print 'Annuity Due=False',
#    annuityDue = False
#    print pmt * (((1 + rate) ** periods - 1) / rate) + pv * (1 + rate) ** periods,
#    v, b, i = fvPayments(rate, pmt, periods, pv, annuityDue)
#    print v, b, i
#
#    print 'Annuity Due=True',
#    annuityDue = True
#    print pmt * (((1 + rate) ** periods - 1) / rate) * (1 + rate) + pv * (1 + rate) ** periods,
#    v, b, i = fvPayments(rate, pmt, periods, pv, annuityDue)
#    print v, b, i
#
#    print pvPayments(rate, periods, pmt, pv, annuityDue),
#    print 1000 * (1 - (1 + rate) ** (-periods)) / rate * (1 + rate)

if __name__ == '__main__':
    test()
