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
