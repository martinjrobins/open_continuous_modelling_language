import sympy
import xml.etree.ElementTree as ET
import numbers


class Model:
    def __init__(self):
        self.name = ''
        self.solution_variables = {}
        self.independent_variables = {}
        self.eqs = {}

    def __str__(self):
        out = ''

        out = out + 'Model "{}":\n'.format(self.name)
        out = out + 'solution_variables:\n'
        for symbol in self.solution_variables:
            out = out + sympy.pretty(symbol) + '\n'

        out = out + 'independent_variables:\n'
        for relation in self.independent_variables:
            out = out + sympy.pretty(relation) + '\n'

        out = out + 'equations:\n'
        for eq in self.eqs:
            out = out + sympy.pretty(eq) + '\n'
        return out


class Models:
    def __init__(self):
        self.models = {}
        self.connections = {}

    def __str__(self):
        out = 'Collection of Models:\n'
        out = out + '---------------------\n'
        for m in self.models:
            out = out + str(m) + '\n'
            out = out + '---------------------\n'

        out = out + 'connections:\n'
        for c in self.connections:
            out = out + str(c) + '\n'

        return out


class Connection:
    def __init__(self, origin, to):
        self.origin = origin
        self.to = to

    def __str__(self):
        out = ''

        for m in (self.origin, self.to):
            out = out + 'model "{}":\n{}'.format(m[0].name, sympy.pretty(m[1])) + '\n'

        return out


def create_sympy_model():

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
    E = Es + t + dE * sympy.sin(w * t)

    c = sympy.Symbol('c')
    lhs_boundary = Model()
    lhs_boundary.name = 'lhs'
    lhs_boundary.solution_variables = {c}
    lhs_boundary.independent_variables = {}
    lhs_boundary.eqs = {sympy.Eq(c, 1)}
    clhs = c

    c = sympy.Function('c')(x, t)
    i = sympy.Function('i')(t)
    rhs_boundary = Model()
    rhs_boundary.name = 'rhs'
    rhs_boundary.independent_variables = {sympy.Eq(x, L), t > 0}
    rhs_boundary.solution_variables = {c, i}
    rhs_boundary.eqs = {
        sympy.Eq(c.diff(x), k0 * ((1-c)*sympy.exp((1-alpha)*(E-E0)) -
                                  c*sympy.exp(-alpha*(E-E0)))),
        sympy.Eq(i, Cdl * E.diff(t))
    }
    crhs = c

    c = sympy.Function('c')(x, t)
    domain = Model()
    domain.name = 'domain'
    domain.independent_variables = {sympy.And(0 < x, x < L), t > 0}
    domain.solution_variables = {c}
    domain.eqs = {sympy.Eq(c.diff(t), c.diff(x).diff(x))}
    cd = c

    models = Models()
    models.models = {lhs_boundary, rhs_boundary, domain}
    models.connections = {
        Connection(
            (lhs_boundary, sympy.Symbol('c')),
            (domain, sympy.Function('c')(0, t))
        ),
        Connection(
            (rhs_boundary, sympy.Function('c')(L, t)),
            (domain, sympy.Function('c')(L, t))
        ),
        Connection(
            (domain, sympy.Function('c')(L, t)),
            (rhs_boundary, sympy.Function('c')(L, t))
        ),
        Connection(
            (domain, sympy.Function('c')(x, t).diff(x)),
            (rhs_boundary, sympy.Function('c')(x, t).diff(x))
        )
    }

    return models


def sympy_to_mathml(s):
    mathml_str = sympy.printing.mathml(s)
    return ET.fromstring(mathml_str)


def number_or_equation(s):
    if isinstance(s, numbers.Number):
        return ET.Element('cn', text=s)
    elif isinstance(s, sympy.Basic):
        return sympy_to_mathml(s)


def independent_variable_to_mathml(relation):
    root = ET.Element("independent_variable")
    root.append(sympy_to_mathml(relation))
    return root


def solution_variable_to_mathml(symbol):
    root = ET.Element("solution_variable")
    root.append(sympy_to_mathml(symbol))
    return root


def model_to_mathml(d):
    root = ET.Element("model", name=d.name)

    for symbol in d.solution_variables:
        root.append(solution_variable_to_mathml(symbol))

    for relation in d.independent_variables:
        root.append(independent_variable_to_mathml(relation))

    for eq in d.eqs:
        root.append(sympy_to_mathml(eq))

    return root


def connection_to_mathml(m):
    root = ET.Element("connection")
    for i in (m.origin, m.to):
        model = ET.Element("model", name=i[0].name)
        model.append(sympy_to_mathml(i[1]))
        root.append(model)

    return root


def models_to_mathml(model):
    root = ET.Element("models")

    for i in model.models:
        root.append(model_to_mathml(i))

    for i in model.connections:
        root.append(connection_to_mathml(i))

    return root
