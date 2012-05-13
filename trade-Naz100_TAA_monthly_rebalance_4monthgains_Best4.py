import numpy as np
from matplotlib.pylab import *

import datetime
from scipy import random
from scipy.stats import rankdata
#import scipy as sp

import nose
import bottleneck as bn
import la

from la.external.matplotlib import quotes_historical_yahoo

## local imports
from functions.quotes_for_list import *

#---------------------------------------------

##
##  Import list of symbols to process.
##

# read list of symbols from disk.
filename = "C:\users\don\python\Naz100_symbols.txt"

##
## Get quotes for each symbol in list
## process dates.
## Clean up quotes.
## Make a plot showing all symbols in list
##

firstdate = (1985,1,1)
firstdate = (2011,1,1)
lastdate=(2012,3,30)
adjClose, symbols, datearray = arrayFromQuotesForList(filename, firstdate, lastdate)

plt.figure(1)
plt.grid()
plt.title('fund closing prices')
for ii in range(adjClose.shape[0]):
    plt.plot(datearray,adjClose[ii])

print " security values check: ",adjClose[isnan(adjClose)].shape

gainloss = np.ones((adjClose.shape[0],adjClose.shape[1]),dtype=float)
gainloss[:,1:] = adjClose[:,1:] / adjClose[:,:-1]
gainloss[isnan(gainloss)]=1.
value = 10000. * np.cumprod(gainloss,axis=1)
BuyHoldFinalValue = np.average(value,axis=0)[-1]

print " gainloss check: ",gainloss[isnan(gainloss)].shape
print " value check: ",value[isnan(value)].shape

plt.figure(29)
plt.grid()
plt.title('fund monthly gains & losses')

LongPeriod =21*5
LongPeriod =50
LongPeriod =75
LongPeriod =125
monthgainloss = np.ones((adjClose.shape[0],adjClose.shape[1]),dtype=float)
monthgainloss[:,LongPeriod:] = adjClose[:,LongPeriod:] / adjClose[:,:-LongPeriod]
monthgainloss[isnan(monthgainloss)]=1.
for ii in np.arange(1,monthgainloss.shape[1]):
    if datearray[ii].month == datearray[ii-1].month:
        monthgainloss[:,ii] = monthgainloss[:,ii-1]
for ii in range(monthgainloss.shape[0]):
    plt.plot(datearray,monthgainloss[ii,:])

print " monthgainloss check: ",monthgainloss[isnan(monthgainloss)].shape

monthgainlossrange = np.ones(adjClose.shape[0],dtype=float)
monthgainlossweight = np.zeros((adjClose.shape[0],adjClose.shape[1]),dtype=float)

rankthreshold = 9     # select this many funds with best recent performance
rankthreshold = 4     # select this many funds with best recent performance
rankthreshold = 4     # select this many funds with best recent performance
rankweight = 1./rankthreshold
monthgainlossrank = bn.rankdata(monthgainloss,axis=0)
rankmin = np.min(monthgainlossrank,axis=0)
rankmax = np.max(monthgainlossrank,axis=0)
rankcutoff = float(adjClose.shape[0]-rankthreshold)/(adjClose.shape[0]-1)*(rankmax-rankmin)*rankmin
ranktest = monthgainlossrank > rankcutoff
monthgainlossweight[ranktest == True]  = rankweight
rankweightsum = np.sum(monthgainlossweight,axis=0)

print " 2a - rankweightsum check isnan: ",rankweightsum[isnan(rankweightsum)].shape[0]
print " 2b - rankweightsum check isinf: ",rankweightsum[isinf(rankweightsum)].shape[0]
print " 2c - rankweightsum check: zero  ",rankweightsum[where(rankweightsum==0)].shape[0]
print " 2d - shape of rankweightsum :   ",rankweightsum.shape[0]
plt.figure(22)
plt.grid()
plt.title('rankweightsum')
plt.plot(datearray,rankweightsum)

# print out list of symbols with valuation from today and LongPeriod ago
for ii in range(adjClose.shape[0]):
    if monthgainlossrank[ii,-28] > 96 or monthgainlossrank[ii,-1] > 96:
        #print '{} {:<5} {:5.3f} {:5.3f} {:6.2f} '.format('symbol, value today, value LongPeriod ago, gain over LongPeriod:  ',symbols[ii], x[ii,2,-LongPeriod], x[ii,2,-1],x[ii,2,-1]/x[ii,2,-LongPeriod])
        print '{} {:<5} {:5.3f} {:5.3f} {:6.2f} '.format('symbol, value today, value LongPeriod ago, gain over LongPeriod:  ',symbols[ii], adjClose[ii,-LongPeriod], adjClose[ii,-1],adjClose[ii,-1]/adjClose[ii,-LongPeriod])
# print out list of symbols with last month's and this month's gain
for ii in range(len(symbols)):
    if monthgainlossrank[ii,-28] > 96 or monthgainlossrank[ii,-1] > 96:
        #print '{} {:<5} {:5.3f} {:5.3f} {:6.2f} {:6.2f}'.format('symbol, previous month gain, current month gain:  ',symbols[ii], monthgainloss[ii,-28], monthgainloss[ii,-1], monthgainlossrank[ii,-28], monthgainlossrank[ii,-1])
        print '{} {:<5} {:5.3f} {:5.3f} {:6.2f} {:6.2f}'.format('symbol, previous month gain, current month gain:  ',symbols[ii], monthgainloss[ii,-28], monthgainloss[ii,-1], monthgainlossrank[ii,-28], monthgainlossrank[ii,-1])


monthgainlossweight = monthgainlossweight / rankweightsum
monthgainlossweight[isnan(monthgainlossweight)] = 1. / adjClose.shape[0]

print " 3 - monthgainlossweight check: ",monthgainloss[isnan(monthgainlossweight)].shape


monthvalue = value.copy()
print " 1 - monthvalue check: ",monthvalue[isnan(monthvalue)].shape
for ii in np.arange(1,monthgainloss.shape[1]):
    if datearray[ii].month <> datearray[ii-1].month:
        valuesum=np.sum(monthvalue[:,ii-1])
        print " re-balancing ",datearray[ii],valuesum
        for jj in range(value.shape[0]):
            monthvalue[jj,ii] = monthgainlossweight[jj,ii]*valuesum*gainloss[jj,ii]   # re-balance using weights (that sum to 1.0)
            if ii>0 and ii<30:print "      ",jj,ii," previous value, new value:  ",monthvalue[jj,ii-1],monthvalue[jj,ii],valuesum,monthgainlossweight[jj,ii],valuesum,gainloss[jj,ii],monthgainlossweight[jj,ii]
    else:
        for jj in range(value.shape[0]):
            monthvalue[jj,ii] = monthvalue[jj,ii-1]*gainloss[jj,ii]   # re-balance using weights (that sum to 1.0)

plt.figure(2)
plt.grid()
plt.title('fund gains & losses')
for ii in range(gainloss.shape[0]):
    plt.plot(datearray,gainloss[ii,:])

plt.figure(3)

plt.grid()
plt.yscale('log')


BuyHoldPortfolioValue = np.mean(value,axis=0)
plt.plot(datearray,BuyHoldPortfolioValue,lw=5)
plt.plot(datearray,np.average(monthvalue,axis=0),lw=5,c='k')
plt.show()

plt.figure(16)
plt.clf()
plt.grid()
plt.title('Best Signals')
for ii in range(value.shape[0]):
    plt.plot(datearray,monthgainlossweight[ii,:])
plt.show()

plt.figure(20)
plt.clf()
plt.yscale('log')
plt.grid()
plt.title('Monthly re-balanced Traded Values')
for ii in range(value.shape[0]):
    plt.plot(datearray,monthvalue[ii,:]/monthvalue.shape[0])
plt.show()

print " "
print "The B&H portfolio final value is: ",BuyHoldFinalValue
print " "
print "Monthly re-balance based on ",LongPeriod, "days of recent performance."
print "The portfolio final value is: ",np.average(monthvalue,axis=0)[-1]
print " "
'''print "Cross-check symbol names: "
for ii in range(len(symbols)):
    print ii,symbols[ii],quote.getlabel(0)[ii]
'''

print " "
print "Today's top ranking choices are: "
for ii in range(len(symbols)):
    if ranktest[ii,-1]: print symbols[ii]
    #if ranktest[ii,-1]: print quote.getlabel(0)[ii]
from scipy.stats import gmean

PortfolioDailyGains = np.average(monthvalue,axis=0)[1:] / np.average(monthvalue,axis=0)[:-1]
PortfolioSharpe = ( gmean(PortfolioDailyGains)**252 -1. ) / ( np.std(PortfolioDailyGains)*sqrt(252) )
print "portfolio annualized gains : ", ( gmean(PortfolioDailyGains)**252 )
print "portfolio annualized StdDev : ", ( np.std(PortfolioDailyGains)*sqrt(252) )
print "portfolio sharpe ratio : ",PortfolioSharpe

BandHDailyGains = BuyHoldPortfolioValue[1:] / BuyHoldPortfolioValue[:-1]
BandHSharpe = ( gmean(BandHDailyGains)**252 -1.) / ( np.std(BandHDailyGains)*sqrt(252) )
print "Buy and Hold annualized gains : ", ( gmean(BandHDailyGains)**252 )
print "portfolio annualized StdDev : ", ( np.std(BandHDailyGains)*sqrt(252) )
print "Buy and Hold sharpe ratio : ",BandHSharpe

print ""
print "Rankings list for today ",datearray[-1]," :"
print "symbol, past price, today's price, gain or loss over period of ", LongPeriod," days, # days,  Rank (high=1)"
gainForLongPeriod = np.zeros( adjClose.shape[0], dtype=float )
gainForLongPeriodRank = np.zeros( adjClose.shape[0], dtype=int )
for ii in range(len(symbols)):
    gainForLongPeriod[ii] = (adjClose[ii,-1]/adjClose[ii,-LongPeriod]-1)
# calculate ranking of gains (low to high)
gainForLongPeriodRank = bn.rankdata(gainForLongPeriod,axis=0)
# reverse the ranks
maxrank = np.max(gainForLongPeriodRank)
gainForLongPeriodRank -= maxrank-1
gainForLongPeriodRank *= -1
gainForLongPeriodRank += 2

for ii in range(len(symbols)):
    gainForLongPeriodFormatted = format(gainForLongPeriod[ii],'8.2%')
    if gainForLongPeriodRank[ii] < 5:
        print "%7s %6.2f %6.2f %2s %4d %3d **" % (symbols[ii], adjClose[ii,-LongPeriod],adjClose[ii,-1],gainForLongPeriodFormatted,LongPeriod, int(gainForLongPeriodRank[ii]))
    else:
        print "%7s %6.2f %6.2f %2s %4d %3d" % (symbols[ii], adjClose[ii,-LongPeriod],adjClose[ii,-1],gainForLongPeriodFormatted,LongPeriod, int(gainForLongPeriodRank[ii]))

print ""
print " top 4 performers for preceding ",LongPeriod," days, as of ",datearray[-1]
for ii in range(len(symbols)):
    gainForLongPeriodFormatted = format(gainForLongPeriod[ii],'8.2%')
    if int(gainForLongPeriodRank[ii]) < 5:
        print "%7s %6.2f %6.2f %2s %4d %3d" % (symbols[ii], adjClose[ii,-LongPeriod],adjClose[ii,-1],gainForLongPeriodFormatted,LongPeriod, int(gainForLongPeriodRank[ii]))
