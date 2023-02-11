# internal operators (for compiler)
OPERATOR_TOKENS = {'and': '&',
                   'or': '|',
                   'xor': '^',
                   'not': '1&~',
                   '->': '^1|',
                   'iff': '^1^'}
OPERATORS = list(OPERATOR_TOKENS.keys())
# logical operators that obey commutativity
COMMUTATIVE_OPERATORS = ['and', 'or', 'xor', 'iff']
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


# operator regex patterns
XOR_PATTERNS = r'[\^\u22bb\u2295\u2a01]+|\b(XOR|xor)\b'

OR_PATTERNS = r'[|+\u2228]+|\b(OR|or)\b'

AND_PATTERNS = r'[&*\u2227\u22c5]+|\b(AND|and)\b'

NOT_PATTERNS = r'(1&~|\u00ac|~)|\b(NOT|not)\b'

IMPLIES_PATTERNS = r'\^1\||\u27f9|\u27f6|\u2192|\u21d2|->'

IFF_PATTERNS = r'<-+>|\^1\^|\u21d4|\u27f7|\u2194|\u27fa|\b(IFF|iff)\b'


# display operators
XOR_SYMBOL = ' \u22bb '
OR_SYMBOL = ' \u2228 '
AND_SYMBOL = ' \u2227 '
NOT_SYMBOL = '\u00ac'
IMPLIES_SYMBOL = ' \u2192 '
IFF_SYMBOL = ' \u2194 '


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
