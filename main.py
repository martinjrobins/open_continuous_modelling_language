import model
import model_library
import xml.etree.ElementTree as ET
from lxml import etree

def print_model(smodel):
    print('sympy model is:')
    print(smodel)
    mmodel = model.model_to_mathml(smodel)
    print('mathml model is: ')
    print(etree.tostring(etree.fromstring(ET.tostring(mmodel)),
        pretty_print=True).decode('utf-8'))

print_model(model_library.ode_model())
print_model(model_library.ode_model_disc(0.1, 100))
print_model(model_library.pde_model())
print_model(model_library.pde_model_disc(100, 0.1))
print_model(model_library.electrochemistry_model())



