import model
import sympy


def ode_model():

    t = sympy.Symbol('t')
    r = sympy.Symbol('r')
    c0 = sympy.Symbol('cinit')
    K = sympy.Symbol('K')
    c = sympy.Function('c')(t)
    m = model.Model()
    m.name = 'logistic'
    m.solution_variables = {c}
    m.parameters = {r, K, c0}
    m.bounds = t > 0
    c = sympy.Symbol('c')
    m.eqs = {
        sympy.Eq(sympy.Derivative(c, t), r * c * (1 - c/K)),
        (sympy.Eq(t, 0), sympy.Eq(c, c0)),
    }

    return m


def ode_model_disc(dt, N):
    if dt < 0:
        raise ValueError("dt must be non-negative")

    if N < 1:
        raise ValueError("N must be positive")

    n = sympy.Symbol('n', integer=True)
    r = sympy.Symbol('r')
    K = sympy.Symbol('K')
    c0 = sympy.Symbol('cinit')

    c = sympy.IndexedBase('c')
    m = model.Model()
    m.name = 'logistic discretised'
    m.parameters = {r, K, c0}
    m.solution_variables = {c[n]}
    m.bounds = sympy.And(n >= 0, n <= N)
    m.eqs = {
        sympy.Eq((c[n] - c[n-1])/dt, r * c[n-1] * (1 - c[n-1]/K)),
        (sympy.Eq(n, 0), sympy.Eq(c[n], c0)),
    }

    return m
