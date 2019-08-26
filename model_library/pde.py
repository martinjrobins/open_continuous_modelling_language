import model
import sympy


def pde_model():

    x = sympy.Symbol('x')
    r = sympy.Symbol('r')
    cl = sympy.Symbol('cl')
    L = sympy.Symbol('L')

    m = model.Model()
    m.name = 'laplace'
    m.parameters
    m.solution_variables = {sympy.Function('c')(x)}
    m.parameters = {cl, L}
    m.bounds = sympy.And(x > 0, x < L)
    c = sympy.Symbol('c')
    m.eqs = {
        sympy.Eq(sympy.Derivative(c, x, x), 0),
        (sympy.Eq(x, 0), sympy.Eq(c, cl)),
        (sympy.Eq(x, L), sympy.Eq(sympy.Derivative(c, x), 0)),
    }

    return m


def pde_model_disc(N, dx):
    if dx < 0:
        raise ValueError("dx must be non-negative")

    if N < 1:
        raise ValueError("N must be positive")

    x = sympy.Symbol('x')
    r = sympy.Symbol('r')
    cl = sympy.Symbol('cl')
    L = sympy.Symbol('L')

    i = sympy.Idx('i')
    c = sympy.IndexedBase('c')
    m = model.Model()
    m.name = 'laplace discretised'
    m.parameters = {cl, L}
    m.solution_variables = {c[i]}
    m.bounds = sympy.And(i >= 0, i <= N)
    m.eqs = {
        (sympy.And(i > 0, i < N), sympy.Eq((c[i+1] - 2*c[i] - c[i-1])/(dx**2), 0)),
        (sympy.Eq(i, 0), sympy.Eq(c[i], cl)),
        (sympy.Eq(i, N), sympy.Eq((c[i] - c[i-1])/dx, 0))
    }

    return m
