import model
import sympy


def pde_model():

    x = sympy.Symbol('x')
    r = sympy.Symbol('r')
    cl = sympy.Symbol('cl')
    L = sympy.Symbol('L')

    m = model.Model()
    m.name = 'laplace'
    m.solution_variables = {sympy.Function('c')(x)}
    m.bounds = {x > 0, x < L}
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

    c = sympy.Symbol('c')
    m_lhs = model.Model()
    m_lhs.name = 'laplace disc lhs'
    m_lhs.solution_variables = {c}
    m_lhs.eqs = {sympy.Eq(c, cl)}

    m_rhs = model.Model()
    m_rhs.name = 'laplace disc rhs'
    m_rhs.solution_variables = {c}
    m_rhs.eqs = {sympy.Eq(c, 0)}

    i = sympy.Idx('i')
    c = sympy.IndexedBase('c')
    m = model.Model()
    m.name = 'laplace discretised'
    m.solution_variables = {c[i]}
    m.bounds = {i > 0, i < N}
    m.eqs = {
        sympy.Eq((c[i+1] - 2*c[i] - c[i-1])/(dx**2), 0),
    }
    m.includes = {
        (m_lhs, sympy.Symbol('c'), c[0]),
        (m_rhs, sympy.Symbol('c'), (c[N] - c[N-1])/dx),
    }

    return m
