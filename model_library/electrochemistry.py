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
    E = sympy.Symbol('E')

    c = sympy.Symbol('c')
    lhs_boundary = model.Model()
    lhs_boundary.name = 'lhs'
    lhs_boundary.solution_variables = {c}
    lhs_boundary.bounds = {}
    lhs_boundary.eqs = {sympy.Eq(c, 1)}

    c = sympy.Symbol('c')
    i = sympy.Symbol('i')
    rhs_boundary = model.Model()
    rhs_boundary.name = 'rhs'
    rhs_boundary.bounds = t > 0
    rhs_boundary.solution_variables = {sympy.Function('c')(t), sympy.Function('i')(t)}
    rhs_boundary.parameters = [sympy.Eq(E, Es + t + dE * sympy.sin(w * t)), k0,
                               sympy.Eq(alpha, 0.5), E0, Cdl]
    rhs_boundary.eqs = {
        sympy.Eq(sympy.Derivative(c, t), k0 * ((1-c)*sympy.exp((1-alpha)*(E-E0)) -
                                               c*sympy.exp(-alpha*(E-E0)))),
        sympy.Eq(i, Cdl * sympy.Derivative(E, t))
    }

    domain = model.Model()
    domain.name = 'domain'
    domain.bounds = sympy.And(0 < x, x < L, t > 0)
    domain.solution_variables = {sympy.Function('c')(x, t)}
    domain.eqs = {
        sympy.Eq(sympy.Derivative(c, t), sympy.Derivative(c, x, x)),
        (sympy.Eq(x, 0), sympy.Eq(c, 1)),
        (sympy.Eq(t, 0), sympy.Eq(c, 1)),
    }
    domain.includes = {
        model.Include(rhs_boundary,
                      sympy.Eq(x, L),
                      {
                          sympy.Eq(sympy.Derivative(c, t), sympy.Derivative(c, x))
                      },
                      {'c': 'c'}
                      )
    }

    return domain
