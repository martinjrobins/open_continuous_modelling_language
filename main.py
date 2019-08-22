import model
import xml.etree.ElementTree as ET
from lxml import etree

smodel = model.create_sympy_model()
print('sympy model is:')
print(smodel)
mmodel = model.models_to_mathml(smodel)
print('mathml model is: ')
print(etree.tostring(etree.fromstring(ET.tostring(mmodel)),
    pretty_print=True).decode('utf-8'))
