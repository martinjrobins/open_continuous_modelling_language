import sympy
import xml.etree.ElementTree as ET
import numbers
import collections


class Model:
    def __init__(self):
        self.name = ''
        self.solution_variables = {}
        self.bounds = None
        self.parameters = {}
        self.eqs = {}
        self.includes = {}

    def __str__(self):
        out = ''

        out = out + '---------------------\n'
        out = out + 'Model "{}":\n'.format(self.name)

        out = out + 'parameters:\n'
        for param in self.parameters:
            out = out + sympy.pretty(param) + '\n'

        out = out + 'solution_variables:\n'
        for symbol in self.solution_variables:
            out = out + sympy.pretty(symbol) + '\n'

        out = out + 'bounds:\n'
        out = out + sympy.pretty(self.bounds) + '\n'

        out = out + 'equations:\n'
        for eq in self.eqs:
            out = out + sympy.pretty(eq) + '\n'

        out = out + 'includes:\n'
        for i in self.includes:
            out = out + str(i) + '\n'
        out = out + '---------------------\n'
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


class Include:
    def __init__(self, submodel, bounds, eqs, mapping):
        self.submodel = submodel
        self.bounds = bounds
        self.eqs = eqs
        self.mapping = mapping

    def __str__(self):
        out = 'bounds:\n'
        out = out + sympy.pretty(self.bounds) + '\n'
        out = out + 'with additional equations:\n'
        for eq in self.eqs:
            out = out + sympy.pretty(eq) + '\n'

        out = out + 'mapping:\n'
        for f,t in self.mapping.items():
            out = out + '{} = {}\n'.format(f,t)


        out = out + str(self.submodel)


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


def symbol_to_mathml(s):
    if s.is_integer:
        t = 'integer'
    else:
        t = 'real'
    root = ET.Element("ci", type=t)
    root.text = s.name
    return root


def sympy_to_mathml(s):
    mathml_str = sympy.printing.mathml(s)
    return ET.fromstring(mathml_str)


def number_or_equation(s):
    if isinstance(s, numbers.Number):
        return ET.Element('cn', text=s)
    elif isinstance(s, sympy.Basic):
        return sympy_to_mathml(s)


def bounds_to_mathml(b):
    root = ET.Element("domainofapplication")
    root.append(sympy_to_mathml(b))
    return root


def solution_variables_to_mathml(symbols):
    root = ET.Element("solution_variables")
    for s in symbols:
        root.append(sympy_to_mathml(s))
    return root

def mapping_to_mathml(maps):
    root = ET.Element("mapping")
    for k, v in maps.items():
        m = ET.Element('map')
        f = ET.Element('cs')
        f.text = k
        m.append(f)
        t = ET.Element('cs')
        t.text = v
        m.append(t)
    root.append(m)
    return root


def include_to_mathml(include):
    submodel = include.submodel
    eqs = include.eqs
    root = ET.Element("model", name=submodel.name)
    for i in submodel.includes:
        root.append(include_to_mathml(i))

    root.append(mapping_to_mathml(include.mapping))
    root.append(bounds_to_mathml(include.bounds))
    root.append(equations_to_mathml(include.eqs))

    return root


def equations_to_mathml(eqs):
    root = ET.Element("equations")
    for eq in eqs:
        if isinstance(eq, tuple):
            node = ET.Element('apply')
            node.append(ET.Element('eq'))
            domain = ET.Element('domainofapplication')
            domain.append(sympy_to_mathml(eq[0]))
            node.append(domain)
            lhs = sympy_to_mathml(eq[1].args[0])
            rhs = sympy_to_mathml(eq[1].args[1])
            node.append(lhs)
            node.append(rhs)
            root.append(node)
        else:
            root.append(sympy_to_mathml(eq))
    return root


def includes_to_mathml(includes):
    root = ET.Element("includes")
    for i in includes:
        root.append(include_to_mathml(i))
    return root


def submodel_to_mathml(m):
    root = ET.Element("model", name=m.name)


    root.append(solution_variables_to_mathml(m.solution_variables))

    root.append(bounds_to_mathml(m.bounds))

    root.append(parameters_to_mathml(m.parameters))

    root.append(equations_to_mathml(m.eqs))

    root.append(includes_to_mathml(m.includes))

    return root


def parameters_to_mathml(params):
    root = ET.Element("parameters")
    for p in params:
        root.append(sympy_to_mathml(p))
    return root


def collect_models(m, models, parameters):
    for (m, _, _) in m.includes:
        collect_models(m, models, parameters)

    # collect all the models
    models[m] = None

    # collect all the parameters
    for peq in m.parameters:
        if isinstance(peq, sympy.Eq):
            # get dependent parameters
            subjects = peq.args[0].free_symbols
            free_p = peq.free_symbols
            for s in subjects:
                free_p.remove(s)
            for p in free_p:
                parameters[p] = None

        parameters[peq] = None


def model_to_mathml(d):
    root = ET.Element("collection")
    # collect internal models
    models = collections.OrderedDict()
    parameters = collections.OrderedDict()
    for i in d.includes:
        collect_models(i.submodel, models, parameters)

    # serialise internal models
    for m in models.keys():
        root.append(submodel_to_mathml(m))

    # serialise this models
    root.append(submodel_to_mathml(d))

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
