OPS_BY_PRECEDENCE = ['iff', '->', 'xor', 'or', 'and']
# logical operators that obey commutativity
COMMUTATIVE_OPERATORS = ['and', 'or', 'xor']
# logical operators that obey associativity
ASSOCIATIVE_OPERATORS = COMMUTATIVE_OPERATORS
XOR_OP = ' xor '
OR_OP = ' or '
AND_OP = ' and '
NOT_OP = 'not '
IMPLIES_OP = ' -> '
IFF_OP = ' iff '


# check/cross mark
MARK_COLUMN = ' '
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
AND_PATTERNS = r'[&\*\u2227\u22c5]+|\b(AND|and)\b'

OR_PATTERNS = r'[|+\u2228]+|\b(OR|or)\b'

XOR_PATTERNS = r'[\^\u22bb\u2295\u2a01]+|\b(XOR|xor)\b'

NOT_PATTERNS = r'\u223c|\u00ac|~|!|\b(NOT|not)\b'

IMPLIES_PATTERNS = r'-+>|\u27f9|\u27f6|\u2192|\u21d2|\bto\b'

IFF_PATTERNS = r'<-+>|\u21d4|\u27f7|\u2194|\u27fa|\b(IFF|iff)\b'


# error messages
UNEXPECTED_ERROR = 'An unexpected error occurred:'
NULL_SENTENCE = '[Syntax Error] Null sentence.'
UNMATCHED_PARENTHESES = '[Syntax Error] Unmatched parentheses.'
MISSING_COMPONENTS = '[Syntax error] Missing an operand/operator in expression '
CUSTOM_LABEL_LENGTH_ERROR = 'Custom label string must be of length 2.'
CUSTOM_LABEL_IDENTICAL_ERROR = 'Custom labels must be different.'
NAME_HELP = '''Rules:
1. Contains only alpha-numeric characters and underscores.
2. Must not start with a number.
3. Case-sensitive.'''
