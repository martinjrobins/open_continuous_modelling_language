def simultaneous_model():

    a = sympy.Symbol('a')
    b = sympy.Symbol('b')

    m = model.Model()
    m.name = 'simultaneous'
    m.solution_variables = {a, b}
    m.independent_variables = {}
    m.eqs = {
        sympy.Eq(a + b, 1)
        sympy.Eq(2*a + b, 2)
    }

    return m
