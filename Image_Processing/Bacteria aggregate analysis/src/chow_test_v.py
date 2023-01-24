####=== Chow test ====#
# the chow code used from here https://github.com/jtloong/chow_test/blob/master/chow_test/__init__.py
###===================#

import numpy as np
from scipy.stats import f



# Simple test
# N = 40
# tst_x = np.arange(N)
# tst_y = 0.1*(tst_x>30)+np.random.normal(0, 0.01, size = N)
# plt.plot(tst_x, tst_y)

# #for i in range(5, N-5):
# i = 30
# x1 = tst_x[0:i]
# x2 = tst_x[(i+1):]
# y1 = tst_y[0:i]
# y2 = tst_y[(i+1):]
# is_break,p_val= chow_test_v.p_value(y1, x1, y2, x2)
# if is_break == 1:
#     plt.plot(tst_x[i], tst_y[i], 'or')

# print(chow_test_v.p_value(y1, x1, y2, x2))



def f_value(y1, x1, y2, x2):
    """This is the f_value function for the Chow Break test package
    Args:
        y1: Array like y-values for data preceeding the breakpoint
        x1: Array like x-values for data preceeding the breakpoint
        y2: Array like y-values for data occuring after the breakpoint
        x2: Array like x-values for data occuring after the breakpoint
    Returns:
        F-value: Float value of chow break test
    """
    def find_rss (y, x):
        """This is the subfunction to find the residual sum of squares for a given set of data
        Args:
            y: Array like y-values for data subset
            x: Array like x-values for data subset
        Returns:
            rss: Returns residual sum of squares of the linear equation represented by that data
            length: The number of n terms that the data represents
        """
        A = np.vstack([x, np.ones(len(x))]).T
        rss = np.linalg.lstsq(A, y, rcond=None)[1]
        length = len(y)
        return (rss, length)


    rss_total, n_total = find_rss(np.append(y1, y2), np.append(x1, x2))
    rss_1, n_1 = find_rss(y1, x1)
    rss_2, n_2 = find_rss(y2, x2)

    chow_nom = (rss_total - (rss_1 + rss_2)) / 2
    chow_denom = (rss_1 + rss_2) / (n_1 + n_2 - 4)
    
    #print(chow_nom,chow_denom,chow_nom / chow_denom)
    #print(rss_total,rss_1,rss_2)
    #print("n1={} n2={}".format(n_1,n_2))
    
    return chow_nom / chow_denom


def p_value(y1, x1, y2, x2, **kwargs):
    """
    this is p_value calculataion for a chow test
     Args:
        y1: Array like y-values for data preceeding the breakpoint
        x1: Array like x-values for data preceeding the breakpoint
        y2: Array like y-values for data occuring after the breakpoint
        x2: Array like x-values for data occuring after the breakpoint
    Returns:
        p_value: float value of chow break test
        is_break: if the break statistically significant
    
    """
    F = f_value(y1, x1, y2, x2, **kwargs)
    if not F:
        return 1
    df1 = 2
    df2 = len(x1) + len(x2) - 4
    #print("F0={} df1={} df2={}".format(F[0],df1,df2))

    # The survival function (1-cdf) is more precise than using 1-cdf,
    # this helps when p-values are very close to zero.
    # -f.logsf would be another alternative to directly get -log(pval) instead.
    p_val = f.sf(F[0], df1, df2)
    #print("p_val={}".format(p_val))



    #Null (H0): a1 = a2, b1 = b2, and c1 = c2
    #Alternative (HA): At least one of the comparisons in the Null is not equal.
    #If the p-value associated with this test statistic is less than a certain significance 
    #level, we can reject the null hypothesis and conclude that there is a structural break point in the data.
    alpha=1e-6
    if p_val<alpha:
        is_break=1
    else:
        is_break=0  

    return is_break,p_val