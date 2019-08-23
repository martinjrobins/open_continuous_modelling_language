import sympy
import xml.etree.ElementTree as ET
import numbers
import collections


class Model:
    def __init__(self):
        self.name = ''
        self.solution_variables = {}
        self.independent_variables = {}
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

        out = out + 'independent_variables:\n'
        for relation in self.independent_variables:
            out = out + sympy.pretty(relation) + '\n'

        out = out + 'equations:\n'
        for eq in self.eqs:
            out = out + sympy.pretty(eq) + '\n'

        out = out + 'includes:\n'
        for (submodel, to_replace, replacement) in self.includes:
            out = out + 'replace:' + '\n'
            out = out + sympy.pretty(to_replace) + '\n'
            out = out + 'with:' + '\n'
            out = out + sympy.pretty(replacement) + '\n'
            out = out + 'in:' + '\n'
            out = out + str(submodel) + '\n'
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


class Connection:
    def __init__(self, origin, to):
        self.origin = origin
        self.to = to

    def __str__(self):
        out = ''

        for m in (self.origin, self.to):
            out = out + 'model "{}":\n{}'.format(m[0].name, sympy.pretty(m[1])) + '\n'

        return out


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


def include_to_mathml(include):
    (submodel, to_replace, replacement) = include
    root = ET.Element("include")
    root.append(include_model_to_mathml(submodel))
    root.append(sympy_to_mathml(to_replace))
    root.append(sympy_to_mathml(replacement))
    return root


def include_model_to_mathml(m):
    root = ET.Element("model", name=m.name)
    for i in m.includes:
        root.append(include_to_mathml(i))
    return root


def submodel_to_mathml(m):
    root = ET.Element("model", name=m.name)

    for p in m.parameters:
        root.append(parameter_to_mathml(p))

    for symbol in m.solution_variables:
        root.append(solution_variable_to_mathml(symbol))

    for relation in m.independent_variables:
        root.append(independent_variable_to_mathml(relation))

    for eq in m.eqs:
        root.append(sympy_to_mathml(eq))

    for i in m.includes:
        root.append(include_to_mathml(i))

    return root


def parameter_to_mathml(p):
    root = ET.Element("parameter")
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
    for (m, _, _) in d.includes:
        collect_models(m, models, parameters)

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
