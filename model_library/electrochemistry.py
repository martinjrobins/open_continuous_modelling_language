import model
import sympy

def electrochemistry_model():

    x = sympy.Symbol('x')
    t = sympy.Symbol('t')
    L = sympy.Symbol('L')
    alpha = sympy.Symbol('a')
    E0 = sympy.Symbol('Emid')
    k0 = sympy.Symbol('krate')
    Cdl = sympy.Symbol('Cdl')
    Es = sympy.Symbol('Es')
    dE = sympy.Symbol('dE')
    w = sympy.Symbol('w')
    E = sympy.Function('E')(t)

    c = sympy.Symbol('c')
    lhs_boundary = model.Model()
    lhs_boundary.name = 'lhs'
    lhs_boundary.solution_variables = {c}
    lhs_boundary.bounds = {}
    lhs_boundary.eqs = {sympy.Eq(c, 1)}

    c = sympy.Function('c')(t)
    i = sympy.Function('i')(t)
    rhs_boundary = model.Model()
    rhs_boundary.name = 'rhs'
    rhs_boundary.bounds = {sympy.Eq(x, L), t > 0}
    rhs_boundary.solution_variables = {c, i}
    rhs_boundary.parameters = [sympy.Eq(E,Es + t + dE * sympy.sin(w * t)), k0,
            sympy.Eq(alpha,0.5), E0, Cdl]
    rhs_boundary.eqs = {
        sympy.Eq(c.diff(t), k0 * ((1-c)*sympy.exp((1-alpha)*(E-E0)) -
                                  c*sympy.exp(-alpha*(E-E0)))),
        sympy.Eq(i, Cdl * E.diff(t))
    }

    c = sympy.Function('c')(x, t)
    domain = model.Model()
    domain.name = 'domain'
    domain.bounds = {0 < x, x < L, t > 0}
    domain.solution_variables = {c}
    domain.eqs = {sympy.Eq(c.diff(t), c.diff(x).diff(x))}
    domain.includes = {
            (lhs_boundary, sympy.Symbol('c'), sympy.Function('c')(0, t)),
            (lhs_boundary, sympy.Symbol('c'), sympy.Function('c')(x, 0)),
            (rhs_boundary, sympy.Function('c')(t).diff(t), sympy.Function('c')(x,
                L).diff(x)),
    }

    return domain


