""" Implements the function mml2sympy, a parser of Content MathML into a
	string with the internal representation of the input.

	mml2sympy depends on sympy and the lxml library.

	Author: Ezequiel Arceo May
	December 2 
"""

from sympy import *
from sympy import printing
from lxml import etree
import logging

INDENT_STR = '  '

logger = logging.getLogger(__name__)

mml2sympy_dict_not_supported = {
    # Not supporting calculus for now
    # 'diff': r'Derivative',
    # 'int': r'Integral',

    # Never supporting relations
    # 'eq': r'Equality',
    # 'neq': r'Unequality',
    # 'geq': r'GreaterThan',
    # 'leq': r'LessThan',
    # 'gt': r'StrictGreaterThan',
    # 'lt': r'StrictLessThan',
}
mml2sympy_dict_trig = {
    'sin': r'sin',
    'cos': r'cos',
    'tan': r'tan',
    'sec': r'sec',
    'csc': r'csc',
    'cot': r'cot',
    'sinh': r'sinh',
    'cosh': r'cosh',
    'tanh': r'tanh',
    'sech': r'sech',
    'csch': r'csch',
    'coth': r'coth',
}
mml2sympy_dict_trig_inverse = {
    'arcsin': r'asin',
    'arccos': r'acos',
    'arctan': r'atan',
    'arcsec': r'asec',
    'arccsc': r'acsc',
    'arccot': r'acot',
    'arcsinh': r'asinh',
    'arccosh': r'acosh',
    'arctanh': r'atanh',
    'arcsech': r'asech',
    'arccsch': r'acsch',
    'arccoth': r'acoth',
}
mml2sympy_dict = {
    'cn': r'Integer',
    'ci': r'Symbol',
    'divide': r"Pow",
    'max': r'Max',
    'min': r'Min',
    'minus': r'Add',
    'plus': r"Add",
    'power': r'Pow',
    'times': r'Mul',
    'root': r"Pow",
    'abs': r'Abs',
    'floor': r'floor',
    'ceiling': r'ceiling',  # NOT SUPPORTED by Wiris MathType
    'exp': r'exp',
    'exponentiale': r'exp',
    'ln': r'log',
    'log': r'log',  # also handles logbase
    'sum': r'Sum',
    'pi': r'pi',
}
mml2sympy_dict.update(mml2sympy_dict_trig)
mml2sympy_dict.update(mml2sympy_dict_trig_inverse)


def mml2sympy(expression_raw):
    if expression_raw.find('<math') >= 0:
        expression_inner_start = expression_raw.find('>', expression_raw.find('<math')) + 1
    else:
        expression_inner_start = 0
    expression_inner_math_ml = expression_raw[expression_inner_start:].replace('</math>', '')
    logger.info(f'Begin mml2sympy{f", Stripped <math> tag" if expression_inner_start > 0 else ""}, '
                f'expression_inner_math_ml: {expression_inner_math_ml}')
    sympyified = sympify(mml2sympy_worker(etree.XML(expression_inner_math_ml)))
    logger.info(f'Completed mml2sympy, sympyified: {sympyified}')
    return sympyified


def mml2sympy_worker(mmltree, log_indent='', nested_value=''):
    sympyres = r""
    # #######################
    # ## Non-atomic elements

    if mmltree.tag == "apply":
        logger.info(f'{log_indent}Begin an apply block'
                    f'{f", nested_value: {nested_value}" if nested_value else ""}')
        # Handle 'minus' tag
        if mmltree[0].tag == 'minus':
            if len(mmltree) == 2:
                logger.info(f'{log_indent}In the apply minus block - applying a sign')
                sympyres += r"Mul(Integer(-1),"
                sympyres += mml2sympy_worker(mmltree[1], log_indent + INDENT_STR)
            else:
                logger.info(f'{log_indent}In the apply minus block - subtracting')
                sympyres += r"Add("
                sympyres += mml2sympy_worker(mmltree[1], log_indent + INDENT_STR)
                sympyres += r",Mul(Integer(-1),"
                sympyres += mml2sympy_worker(mmltree[2], log_indent + INDENT_STR)
                sympyres += r")"
        # Handle 'divide' tag
        elif mmltree[0].tag == 'divide':
            logger.info(f'{log_indent}In the apply divide block')
            sympyres += r"Mul("
            sympyres += mml2sympy_worker(mmltree[1], log_indent + INDENT_STR)
            sympyres += r",Pow("
            sympyres += mml2sympy_worker(mmltree[2], log_indent + INDENT_STR)
            sympyres += r",Integer(-1)"
            sympyres += r")"
        # Handle 'root' tag
        elif mmltree[0].tag == 'root':
            logger.info(f'{log_indent}In the apply root block')
            sympyres += r"Pow("
            if mmltree[1].tag == 'degree':
                sympyres += mml2sympy_worker(mmltree[2], log_indent + INDENT_STR)
                sympyres += r",Pow("
                sympyres += mml2sympy_worker(mmltree[1][0], log_indent + INDENT_STR)
                sympyres += r",Integer(-1))"
            else:
                sympyres += mml2sympy_worker(mmltree[1], log_indent + INDENT_STR)
                sympyres += r",Rational(1,2)"
        # End: handle 'root' tag
        elif mmltree[0].tag == 'log' and mmltree[1].tag == 'logbase':
            logger.info(f'{log_indent}In the apply for log with logbase block')
            sympyres += r"log("
            sympyres += mml2sympy_worker(mmltree[2], log_indent + INDENT_STR)
            sympyres += r","
            sympyres += mml2sympy_worker(mmltree[1][0], log_indent + INDENT_STR)
        # End: handle 'log' w/ 'logbase' tag
        elif mmltree[0].tag == 'power' and mmltree[1].tag in ('exponentiale', 'exp'):
            logger.info(f'{log_indent}In the apply for exponentiale inside a power block')
            sympyres += r"exp("
            sympyres += mml2sympy_worker(mmltree[2], log_indent + INDENT_STR)
        # End: handle exponentiale inside power tag
        elif mmltree[0].tag == 'inverse' and mmltree[1].tag in mml2sympy_dict_trig:
            logger.info(f'{log_indent}In the apply for an inverse {mmltree[1].tag} block')
            sympyres += r"a"
            sympyres += mml2sympy_dict_trig[mmltree[1].tag]
            sympyres += r"("
        # End: handle inverse trig tag
        elif mmltree[0].tag == 'apply':
            logger.info(f'{log_indent}In the apply for an immediate apply block. next branch: {mmltree[0][0]}')
            sympyres += mml2sympy_worker(mmltree[0], log_indent + INDENT_STR,
                                         nested_value=mml2sympy_worker(mmltree[1], log_indent + INDENT_STR))
        # End: handle immediately nested apply tag
        else:
            logger.info(f'{log_indent}In the apply else block with tag: {mmltree[0].tag}')
            if mmltree[0].tag in mml2sympy_dict:
                sympyres += mml2sympy_dict[mmltree[0].tag]
                sympyres += r"("
                for branch in list(mmltree)[1:]:
                    sympyres += mml2sympy_worker(branch, log_indent + INDENT_STR)
                    if branch != list(mmltree)[-1]:
                        sympyres += r","
            else:
                raise NotImplementedError(f'{mmltree[0].tag} is not currently supported')
        sympyres += nested_value
        if mmltree[0].tag != 'apply':
            sympyres += r")"
    # ###################
    # ## Atomic elements
    else:
        logger.info(f'{log_indent}Begin a non-apply block: {mmltree.tag}')
        content = mmltree.text
        content_type = type(sympify(content))
        # Handle integer content (.text method) in 'cn' tags
        if (content_type == Integer) or (str(content_type) == "<class 'sympy.core.numbers.One'>"):
            sympyres += r"Integer(" + (content or '') + r")"
        # Handle float content (.text method) in 'cn' tags
        elif content_type == Float:
            sympyres += r"Float('" + (content or '') + r"', dps = 15)"
        # Handle symbol
        else:
            sympyres += r"Symbol('" + (content or '') + r"')"

    logger.info(f'{log_indent}Completed block worker of tag {mmltree.tag}, sympyres: {sympyres}')
    return (sympyres)


def main():
    # A dictionary to translate tags into sympy objects's names
    x, y, z = symbols('x y z')
    print("Hello World!")
    e = x - y - z - y * z / (x + z * tan(x ** 2)) + sin(z) + exp(-3 / x) * acos(5 * x) - 1 + sqrt(x / (y ** 2 + z ** 2))
    print(f'---Example---------- {e}')
    print(f'---String Repr------ {srepr(e)}')
    mml = printing.mathml(e)
    print(f'---Content MathML--- {mml}')
    back = mml2sympy(mml)
    print(f'---Back to SymPy---- {back}')
    print(f'---Python Code------ {printing.pycode(back)}')
    print(f'---Julia Code------- {printing.julia_code(back)}')
    print(f'---Sympify---------- {sympify(back)}')
    print(f'---Example again---- {e}')


if __name__ == '__main__':
    main()
