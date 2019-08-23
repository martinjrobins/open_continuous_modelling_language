import model
import model_library
import xml.etree.ElementTree as ET
from lxml import etree

smodel = model_library.electrochemistry_model()
print('sympy model is:')
print(smodel)
mmodel = model.model_to_mathml(smodel)
print('mathml model is: ')
print(etree.tostring(etree.fromstring(ET.tostring(mmodel)),
    pretty_print=True).decode('utf-8'))
