import numpy as np
"""
Various Useful Penalty Functions for Hazan's Algorithm.

@author: Bharath Ramsundar
@email: bharath.ramsundar@gmail.com
"""

def compute_scale(m,n, eps):
    """
    Compute the scaling factor required for m inequality and
    n equality constraints in the log_sum_exp penalty.

    Parameters
    __________
    m: int
        Number of inequality constraints
    n: int
        Number of equality constraints
    """
    if m + n > 0:
        M = 0.
        if m > 0:
            M += np.max((np.log(m), 1.))/eps
        if n > 0:
            M += np.max((np.log(n), 1.))/eps
    else:
        M = 1.
    return M


def neg_sum_squares(x):
    """
    Computes f(x) = -\sum_k x_kk^2. Useful for debugging.

    Parameters
    __________
    x: numpy.ndarray
    """
    (N, _) = np.shape(x)
    retval = 0.
    for i in range(N):
        retval += -x[i,i]**2
    return retval

def grad_neg_sum_squares(x):
    """
    Computes grad(-\sum_k x_kk^2). Useful for debugging.

    Parameters
    __________
    x: numpy.ndarray
    """
    (N, _) = np.shape(x)
    G = np.zeros((N,N))
    for i in range(N):
        G[i,i] += -2.*x[i,i]
    return G

#def f(X):
#    """
#    TODO: Delete this once okay
#    X: np.ndarray
#        Computes function
#        f(X) = -(1/M) log(sum_{i=1}^m exp(M*(Tr(Ai,X) - bi)))
#    """
#    s = 0.
#    for i in range(m):
#        Ai = As[i]
#        bi = bs[i]
#        s += np.exp(M*(np.trace(np.dot(Ai,X)) - bi))
#    return -(1.0/M) * np.log(s)
#
#def gradf(X):
#    """
#    TODO: Delete this once okay
#    X: np.ndarray
#        Computes grad f(X) = -(1/M) * f' / f where
#          f' = sum_{i=1}^m exp(M*(Tr(Ai, X) - bi)) * (M * Ai.T)
#          f  = sum_{i=1}^m exp(M*(Tr(Ai,X) - bi))
#    """
#    num = 0.
#    denom = 0.
#    for i in range(m):
#        Ai = As[i]
#        bi = bs[i]
#        if dim >= 2:
#            num += np.exp(M*(np.trace(np.dot(Ai,X)) - bi))*(M*Ai.T)
#            denom += np.exp(M*(np.trace(np.dot(Ai,X)) - bi))
#        else:
#            num += np.exp(M*(Ai*X - bi))*(M*Ai.T)
#            denom += np.exp(M*(Ai*X - bi))
#    return (-1.0/M) * num/denom

def log_sum_exp_penalty(X, m, n, M, As, bs, Cs, ds, dim):
    """
    TODO: Make this more numerically stable
    Computes
    f(X) = -(1/M) log(sum_{i=1}^m exp(M*(Tr(Ai,X) - bi))
                    + sum_{j=1}^n exp(M*(Tr(Cj,X) - dj)^2))

    where m is the number of linear constraints and M = log m / eps,
    with eps an error tolerance parameter

    Parameters
    __________

    m: int
        Number of inequaltity constraints
    n: int
        Number of equality constraints
    M: float
        Rescaling Factor
    """
    s = None
    r = None
    penalties_m = np.zeros(m)
    penalties_n = np.zeros(n)
    for i in range(m):
        Ai = As[i]
        bi = bs[i]
        if dim >= 2:
            penalties_m[i] = M*(np.trace(np.dot(Ai,X)) - bi)
        else:
            penalties_m[i] = M*(Ai*X - bi)
    for j in range(n):
        Cj = Cs[j]
        dj = ds[j]
        if dim >= 2:
            penalties_n[j] = M*np.abs(np.trace(np.dot(Cj,X)) - dj)
        else:
            penalties_n[j] = M*np.abs(Cj*X - dj)
    if m + n > 0:
        if m > 0:
            retval += scipy.misc.logsumexp(np.array(penalties_m), axis=0)
        if n > =:
            retval += scipy.misc.logsumexp(np.array(penalties_n), axis=0)
        retval = -(1.0/M) * np.exp(retval)
    return retval

def log_sum_exp_grad_penalty(X, m, n, M, As, bs, Cs, ds, dim, eps):
    """
    TODO: Make this more numerically stable
    Computes grad f(X) = -(1/M) * c' / c where
      c' = (sum_{i=1}^m exp(M*(Tr(Ai, X) - bi)) * (M * Ai.T)
            + sum_{j=1}^n exp(M(Tr(Cj,X) - dj)**2)
                            * (2M(Tr(Cj,X) - dj)) * Cj.T)
      c  = (sum_{i=1}^m exp(M*(Tr(Ai,X) - bi))
            + sum_{i=1}^n exp(M(Tr(Cj,X) - dj)**2))

    Need Ai and Cj to be symmetric real matrices
    """
    retval = 0.
    nums_m = np.zeros(m)
    denoms_m = np.zeros(m)
    for i in range(m):
        Ai = As[i]
        bi = bs[i]
        if dim >= 2:
            nums_m[i] = M*(np.trace(np.dot(Ai,X)) - bi) + np.log(M*Ai.T)
            denoms_m[i] = M*(np.trace(np.dot(Ai,X)) - bi)
        else:
            nums_m[i] = M*(Ai*X - bi) + (M*Ai.T)
            denoms_m[i] = M*(Ai*X - bi)
    nums_n = np.zeros(n)
    denoms_n = np.zeros(n)
    for j in range(n):
        Cj = Cs[j]
        dj = ds[j]
        if dim >= 2:
            # fix derivative
            nums_n[j] += (np.abs(M*(np.trace(np.dot(Cj,X)) - dj))+
                            np.log(2*M*(np.trace(np.dot(Cj,X)) - dj))+
                            np.log(Cj.T))
            denoms_n[j] += M*(np.trace(np.dot(Cj,X)) - dj)
        else:
            nums_n[j] += (np.abs(M*(Cj*x - dj))+np.log(2*M*(Cj*x -
                            dj))+np.log(Cj.T))
            denoms_n[j] += M*(Cj*x - dj)
    if m + n > 0:
        retval += -(1.0/M) * num/denom
    #import pdb
    #pdb.set_trace()
    return retval


def neg_max_penalty(X, m, n, M, As, bs, Cs, ds, dim):
    """
    Computes penalty

     -max(max_i {Tr(Ai,X) - bi}, max_j{|Tr(Cj,X) - dj|})

    This function computes and returns this quantity.
    """
    penalties = np.zeros(n+m)
    for i in range(m):
        Ai = As[i]
        bi = bs[i]
        if dim >= 2:
            penalties[i] = np.trace(np.dot(Ai,X)) - bi
        else:
            penalties[i] = Ai*X - bi
    for j in range(n):
        Cj = Cs[j]
        dj = ds[j]
        if dim >= 2:
            penalties[j+m] += np.abs(np.trace(np.dot(Cj,X)) - dj)
        else:
            penalties[j+m] += np.abs(Cj*x - dj)
    return -np.amax(penalties)

def neg_max_grad_penalty(X, m, n, M, As, bs, Cs, ds, dim, eps):
    """
    Note that neg_max_penalty(X) roughly equals

    -max(max_i {Tr(Ai,X) - bi}, max_j{|Tr(Cj,X) - dj|})

    Since neg_max_penalty is concave, we need to return a supergradient
    of this function. The supergradient of this function equals the
    subgradient of -neg_max_penalty(X):

    max(max_i {Tr(Ai,X) - bi}, max_j{|Tr(Cj,X) - dj|})

    which equals

    Conv{{A_i | -neg_max_penalty(X) = Tr(Ai,X) - bi} union
         { sign(Tr(Cj,X) - dj) Cj  | penalty(X) = |Tr(Cj,X) - dj| }}

    We use a weak subdifferential calculus that averages the gradients
    of all violated constraints.
    """
    penalties = np.zeros(n+m)
    count = 0
    for i in range(m):
        Ai = As[i]
        bi = bs[i]
        if dim >= 2:
            penalties[i] = np.trace(np.dot(Ai,X)) - bi
        else:
            penalties[i] = Ai*X - bi
    for j in range(n):
        Cj = Cs[j]
        dj = ds[j]
        if dim >= 2:
            penalties[j+m] = np.abs(np.trace(np.dot(Cj,X)) - dj)
        else:
            penalties[j+m] = np.abs(Cj*X - dj)
    #ind = np.argmax(penalties)
    inds = [ind for ind in range(n+m) if penalties[ind] > eps]

    grad = np.zeros(np.shape(X))
    for ind in inds:
        if ind < m:
            Ai = As[ind]
            grad += Ai
        else:
            Cj = Cs[ind - m]
            dj = ds[ind - m]
            val = np.trace(np.dot(Cj,X)) - dj
            #print "val: ", val
            if val < 0:
                grad += -Cj
            elif val > 0:
                grad += Cj
    # Average by num entries
    grad = grad / max(len(inds), 1.)
    # Take the negative since our function is -max{..}
    grad = -grad
    #import pdb
    #pdb.set_trace()
    return grad

