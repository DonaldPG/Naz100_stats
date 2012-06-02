import numpy as np
from numpy import isnan

def interpolate(self, method='linear'):
    """
    Interpolate missing values (after the first valid value)
    Parameters
    ----------
    method : {'linear'}
    Interpolation method.
    Time interpolation works on daily and higher resolution
    data to interpolate given length of interval
    Returns
    -------
    interpolated : Series
    from-- https://github.com/wesm/pandas/blob/master/pandas/core/series.py
    edited to keep only 'linear' method
    Usage: infill NaN values with linear interpolated values
    """
    #import numpy as np
    inds = np.arange(len(self))
    values = self.copy()
    invalid = isnan(values)
    valid = -invalid
    firstIndex = valid.argmax()
    valid = valid[firstIndex:]
    invalid = invalid[firstIndex:]
    inds = inds[firstIndex:]
    result = values.copy()
    result[firstIndex:][invalid] = np.interp(inds[invalid], inds[valid],values[firstIndex:][valid])
    return result
#----------------------------------------------
def cleantobeginning(self):
    """
    Copy missing values (to all dates prior the first valid value)

    Usage: infill NaN values at beginning with copy of first valid value
    """
    #import numpy as np
    inds = np.arange(len(self))
    values = self.copy()
    invalid = isnan(values)
    valid = -invalid
    firstIndex = valid.argmax()
    for i in range(firstIndex):
        values[i]=values[firstIndex]
    return values
#----------------------------------------------
def dpgchannel(x,minperiod,maxperiod,incperiod):
    #import numpy as np
    periods = np.arange(minperiod,maxperiod,incperiod)
    minchannel = np.zeros(len(x),dtype=float)
    maxchannel = np.zeros(len(x),dtype=float)
    for i in range(len(x)):
        divisor = 0
        for j in range(len(periods)):
            minx = max(1,i-periods[j])
            #print "i,j,periods[j],minx,x[minx:i]   :",i,j,periods[j],minx,x[i],x[minx:i]
            if len(x[minx:i]) < 1:
                #print "short   ",i,j,x[i]
                minchannel[i] = minchannel[i] + x[i]
                maxchannel[i] = maxchannel[i] + x[i]
                divisor += 1
            else:
                minchannel[i] = minchannel[i] + min(x[minx:i+1])
                maxchannel[i] = maxchannel[i] + max(x[minx:i+1])
                divisor += 1
        minchannel[i] /= divisor
        maxchannel[i] /= divisor
    return minchannel,maxchannel
#----------------------------------------------
def dpgchannel_2D(x,minperiod,maxperiod,incperiod):
    #import numpy as np
    periods = np.arange(minperiod,maxperiod,incperiod)
    minchannel = np.zeros( (x.shape[0],x.shape[1]), dtype=float)
    maxchannel = np.zeros( (x.shape[0],x.shape[1]), dtype=float)
    for i in range( x.shape[1] ):
        divisor = 0
        for j in range(len(periods)):
            minx = max(1,i-periods[j])
            #print "i,j,periods[j],minx,x[minx:i]   :",i,j,periods[j],minx,x[i],x[minx:i]
            if len(x[0,minx:i]) < 1:
                #print "short   ",i,j,x[i]
                minchannel[:,i] = minchannel[:,i] + x[:,i]
                maxchannel[:,i] = maxchannel[:,i] + x[:,i]
                divisor += 1
            else:
                minchannel[:,i] = minchannel[:,i] + np.min(x[:,minx:i+1],axis=-1)
                maxchannel[:,i] = maxchannel[:,i] + np.max(x[:,minx:i+1],axis=-1)
                divisor += 1
        minchannel[:,i] /= divisor
        maxchannel[:,i] /= divisor
    return minchannel,maxchannel
#----------------------------------------------
def move_sharpe_2D(adjClose,dailygainloss,period):
    """
    Compute the moving sharpe ratio
      sharpe_ratio = ( gmean(PortfolioDailyGains[-lag:])**252 -1. )
                   / ( np.std(PortfolioDailyGains[-lag:])*sqrt(252) )
      formula assume 252 trading days per year

    Geometric mean is simplified as follows:
    where the geometric mean is being used to determine the average
    growth rate of some quantity, and the initial and final values
    of that quantity are known, the product of the measured growth
    rate at every step need not be taken. Instead, the geometric mean
    is simply ( a(n)/a(0) )**(1/n), where n is the number of steps
    """
    from scipy.stats import gmean
    from math import sqrt
    from numpy import std
    #
    print "period,adjClose.shape  :",period,adjClose.shape
    #
    gmeans = np.ones( (adjClose.shape[0],adjClose.shape[1]), dtype=float)
    stds   = np.ones( (adjClose.shape[0],adjClose.shape[1]), dtype=float)
    sharpe = np.zeros( (adjClose.shape[0],adjClose.shape[1]), dtype=float)
    for i in range( dailygainloss.shape[1] ):
        minindex = max( i-period, 0 )
        #if i < period*1.2:
            #print "i,minindex,period,adjClose.shape  :",i,minindex,period,adjClose.shape
        if i > minindex :
            #gmeans[:,i] = (adjClose[:,i]/adjClose[:,minindex])**(1./(i-minindex))
            #stds[:,i] = np.std(dailygainloss[:,minindex:i+1],axis=-1)
            sharpe[:,i] = ( gmean(dailygainloss[:,minindex:i+1],axis=-1)**252 -1. )     \
                   / ( np.std(dailygainloss[:,minindex:i+1],axis=-1)*sqrt(252) )
        else :
            #gmeans[:,i] = 1.
            #stds[:,i] = 10.
            sharpe[:,i] = 0.
    #gmeans = gmeans**252 -1.
    #stds  *= sqrt(252)
    #return gmeans/stds
    #print 'sharpe[:,-50] inside move_sharpe_2D  ',sharpe[:,-50]   #### diagnostic
    #print '# zero values inside move_sharpe_2D  ',sharpe[sharpe==0.].shape[0]   #### diagnostic
    sharpe[sharpe==0]=.05
    sharpe[isnan(sharpe)] =.05
    #print '# zero values inside move_sharpe_2D  ',sharpe[sharpe==0.].shape[0]   #### diagnostic
    return sharpe
