from cvxopt import matrix, solvers
import numpy as np

def l1(mat_A, vec_b, C, solver='glpk'):
    """
    Compute the perturbations needed to ensure arbitrage-free surface using
    the l1-norm objective.
    Minimise    ||epsilon||_l1
    s.t.        mat_A * (C + epsilon) >= vec_b
    Parameters
    ----------
    mat_A: 2D numpy.array, shape = (n_constraint, n_quote)
        The arbitrage-free constraint coefficient matrix.
    vec_b: 1D numpy.array, shape = (n_constraint,)
        The arbitrage-free constraint constant bound vector.
    C: 1D numpy.array, shape = (n_quote,)
        The call price vector.
    Returns
    -------
    epsilon: 1D numpy.array, shape = (n_quote, )
        The optimal perturbation vector, if the optimisation problem is
        solved successfully. Otherwise an empty list will be returned.
    """

    n_quote = mat_A.shape[1]
    MAX_ATTEMPTS = 8  # max number of attempts to solve the optimisation
    sol = []

    # Construct required quantities for the LP
    A = -np.hstack((mat_A, -mat_A))
    b = -(vec_b - mat_A.dot(C))
    coeff = np.ones(2 * n_quote)

    A1 = np.vstack((A, -np.diag(np.ones(2 * n_quote))))
    b1 = np.hstack((b, np.zeros(2 * n_quote)))
    G = matrix(A1)
    h = matrix(b1.astype(np.double))
    c = matrix(coeff)

    '''
    Scale the constraint for numerical stability
    A * (scale * epsilon) >= scale * b
    '''
    G *= 2.0
    h *= 2.0

    i_attempt = 1
    scale = .1
    status = 'initial'
    while status != 'optimal':
        scale *= 10
        c *= scale
        h *= scale

        # solve the LP
        sol = solvers.lp(c, G, h, solver=solver)
        status = sol['status']

        i_attempt += 1
        if i_attempt > MAX_ATTEMPTS:
            break

    if status == 'optimal':
        x = np.array(sol['x'])
        epsilon = x[:n_quote] - x[n_quote:]
        epsilon = epsilon.flatten()
        epsilon /= scale
    else:
        epsilon = []
        print('Optimal perturbation is not found after {} attempts!'.
              format(MAX_ATTEMPTS))

    return epsilon

def l1ba(mat_A, vec_b, C, spread=None, solver='glpk'):
    """
    Compute the perturbations needed to ensure arbitrage-free surface.
    Minimise    f(epsilon; spreads)
    s.t.        mat_A * (C + epsilon) >= vec_b
    Parameters
    ----------
    mat_A: 2D numpy.array, shape = (n_constraint, n_quote)
        The arbitrage-free constraint coefficient matrix.
    vec_b: 1D numpy.array, shape = (n_constraint,)
        The arbitrage-free constraint constant bound vector.
    C: 1D numpy.array, shape = (n_quote,)
        The call price vector.
    spread: 1d numpy.array, shape = (n_quote,)
        The bid-ask spread vector.
    Returns
    -------
    epsilon: 1d numpy.array, shape = (n_quote, )
        The optimal perturbation vector, if the optimisation problem is
        solved successfully. Otherwise an empty list will be returned.
    """

    n_quote = mat_A.shape[1]
    MAX_ATTEMPTS = 2  # max number of attempts to solve the optimisation
    sol = []

    if spread is None:
        print('No spread data have been provided, so the l1-norm objecitve is '
              'used automatically.')
        return l1(mat_A, vec_b, C)
    else:
        try:
            delta_ask = spread[0]
            delta_bid = spread[1]
            delta0 = np.min([np.min(delta_ask), np.min(delta_bid)])
            delta0 = 1./len(delta_ask) if delta0 > 1./len(delta_ask) else delta0
            delta0 = 1e-8 if delta0 < 1e-8 else delta0
        except ValueError:
            raise  ValueError('Please ensure that the spread input has legal '
                              'format! It should contain two arrays/lists, one '
                              'for bid-reference spread, one for ask-reference '
                              'spread.')

        # Construct required quantities for the LP
        I = np.eye(n_quote)
        B2_bid = np.diag(delta_bid) / delta0
        B2_ask = np.diag(delta_ask) / delta0
        O = np.zeros([mat_A.shape[0], n_quote])
        B = np.block([
            [-I, -I],
            [I, -I],
            [-I, -B2_bid],
            [I, -B2_ask],
            [-mat_A, O]
        ])
        d = np.hstack([delta_bid - delta0,
                        delta_ask - delta0,
                        np.zeros(2 * n_quote),
                        -vec_b + mat_A.dot(C)])
        coeff = np.hstack([np.zeros(n_quote), np.ones(n_quote)])

        G = matrix(B)
        h = matrix(d.astype(np.double))
        c = matrix(coeff)

        '''
        Scale the constraint for numerical stability
        A * (scale * epsilon) >= scale * b
        '''
        i_attempt = 1
        scale = .1
        status = 'initial'
        while status != 'optimal':
            scale *= 10
            c *= scale
            h *= scale

            # Solve the LP
            sol = solvers.lp(c, G, h, solver=solver)
            status = sol['status']

            i_attempt += 1
            if i_attempt > MAX_ATTEMPTS:
                break

        if status == 'optimal':
            epsilon = np.array(sol['x'])[:n_quote]
            epsilon = epsilon.flatten()
            epsilon /= scale
        else:
            epsilon = []
            print('Optimal perturbation is not found after {} attempts!'.
                  format(MAX_ATTEMPTS))

    return epsilon