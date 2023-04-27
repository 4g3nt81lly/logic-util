# internal operators (for compiler)
BINARY_OPERATORS = {'and': '&',
                    'or': '|',
                    'xor': '^',
                    'not': '1&~',
                    '->': '^1|',
                    'iff': '^1^'}
# display operators
DISPLAY_OPERATORS = {'and': '\u2227',
                     'or': '\u2228', 
                     'xor': '\u22bb',
                     'not': '\u00ac',
                     '->': '\u2192',
                     'iff': '\u2194'}
OPERATORS = list(BINARY_OPERATORS.keys())
OPS_BY_PRECEDENCE = ['iff', '->', 'xor', 'or', 'and']
# logical operators that obey commutativity
COMMUTATIVE_OPERATORS = ['and', 'or', 'xor', 'iff']
# logical operators that obey associativity
ASSOCIATIVE_OPERATORS = COMMUTATIVE_OPERATORS
XOR_OP = ' xor '
OR_OP = ' or '
AND_OP = ' and '
NOT_OP = 'not '
IMPLIES_OP = ' -> '
IFF_OP = ' iff '


# check/cross mark
MARK_COLUMN = 'CHECK/CROSS'
CHECK_MARK = '\u2713'
CROSS_MARK = '\u2717'


# table drawing characters
# corners
BOX_TOP_LEFT = '\u250f'
BOX_TOP_RIGHT = '\u2513'
BOX_BOTTOM_LEFT = '\u2517'
BOX_BOTTOM_RIGHT = '\u251b'
# sides & borders
BOX_OUTER_HLINE = '\u2501'
BOX_OUTER_VLINE = '\u2503'
BOX_INNER_HLINE = '\u2500'
BOX_INNER_VLINE = '\u2502'
# joints & intersections
BOX_JOINT = '\u253c'
BOX_LEFT_T = '\u2520'
BOX_RIGHT_T = '\u2528'
BOX_TOP_T = '\u252f'
BOX_BOTTOM_T = '\u2537'

EQUIV_SYMBOL = ' \u2261 '

# operator regex patterns
AND_PATTERNS = r'[&*\u2227\u22c5]+|\b(AND|and)\b'

OR_PATTERNS = r'[|+\u2228]+|\b(OR|or)\b'

XOR_PATTERNS = r'[\^\u22bb\u2295\u2a01]+|\b(XOR|xor)\b'

NOT_PATTERNS = r'\u223c|\u00ac|~|!|\b(NOT|not)\b'

IMPLIES_PATTERNS = r'-+>|\u27f9|\u27f6|\u2192|\u21d2|\bto\b'

IFF_PATTERNS = r'<-+>|\u21d4|\u27f7|\u2194|\u27fa|\b(IFF|iff)\b'


# error messages
UNEXPECTED_ERROR = 'An unexpected error occurred:'
NULL_STATEMENT = 'Error: Null statement.'
UNMATCHED_PARENTHESES = 'Syntax error: Unmatched parentheses.'
CUSTOM_LABEL_EXCEED_LENGTH = 'Custom label string must be of length 2.'
CUSTOM_LABEL_IDENTICAL = 'Custom labels must be different.'
NAME_HELP = '''Rules:
1. Contains only alpha-numeric characters and underscores.
2. Must not start with a number.
3. Case-sensitive.'''
