import re
import csv
from typing import Dict

from constants import *


def bold(*msg) -> str:
    _msg = ' '.join(msg)
    return f"\033[1m{_msg}\033[0m"


def green(*msg) -> str:
    _msg = ' '.join(msg)
    return f"\033[32m{_msg}\033[0m"


def yellow(*msg) -> str:
    _msg = ' '.join(msg)
    return f"\033[33m{_msg}\033[0m"


def red(*msg) -> str:
    _msg = ' '.join(msg)
    return f"\033[91m{_msg}\033[0m"


# toggle between compilable and display symbols


def standardize_notations(sentence: str, display: bool = False) -> str:
    new_sentence = re.sub(r'\s+', ' ', sentence)

    # replacement
    # XOR
    xor_operator = XOR_SYMBOL if display else XOR_OP  # ^
    # OR
    or_operator = OR_SYMBOL if display else OR_OP    # |
    # AND
    and_operator = AND_SYMBOL if display else AND_OP  # &
    # NOT
    not_operator = NOT_SYMBOL if display else NOT_OP    # 1&~
    # IMPLICATION: a -> b = ~a OR b
    implies_operator = IMPLIES_SYMBOL if display else IMPLIES_OP  # ^1|
    # BICONDITIONAL
    iff_operator = IFF_SYMBOL if display else IFF_OP  # ^1^

    # substitution: ORDER DOES MATTER!
    # 1st-last: NOT -> AND -> IFF -> IMPLY -> XOR -> OR
    # compiler: 1&~ ->  &  -> ^1^ ->  ^1|  ->  ^  -> |

    # matching NOT before AND
    # so that 1&~ doesn't get matched by &
    new_sentence = re.sub(NOT_PATTERNS, not_operator, new_sentence)
    new_sentence = re.sub(AND_PATTERNS, and_operator, new_sentence)
    # matching IFF before IMPLY and XOR
    # so that <-> doesn't get matched by ->
    # so that ^1^ doesn't get matched by ^
    new_sentence = re.sub(IFF_PATTERNS, iff_operator, new_sentence)
    # matching IMPLY before OR and XOR
    # so that ^1| doesn't get matched by | or ^
    new_sentence = re.sub(IMPLIES_PATTERNS, implies_operator, new_sentence)
    # matching XOR before OR
    # so that XOR doesn't get matched by OR
    new_sentence = re.sub(XOR_PATTERNS, xor_operator, new_sentence)
    new_sentence = re.sub(OR_PATTERNS, or_operator, new_sentence)

    # remove extra whitespaces
    new_sentence = re.sub(r'\s+', ' ', new_sentence)

    # remove extra parentheses for non-expressions
    pattern = r'\((\u00ac?[a-zA-Z_]\w*)\)'
    while True:
        new_sentence, count = re.subn(pattern, r'\1', new_sentence)
        if count == 0:
            break

    return new_sentence


# determine if a variable name conforms to the rules
def good_name(name: str) -> bool:
    pattern = r'^[a-zA-Z_]\w*$'
    return bool(re.match(pattern, name))


# convert a struct back to statement sentence


def flatten_struct(s: list | str) -> str:
    if isinstance(s, str):
        return s
    flattened = ''
    for element in s:
        if isinstance(element, str):
            flattened += element
        elif isinstance(element, list):
            flattened += flatten_struct(element)
        flattened += ' '
    return f"({flattened.rstrip()})"


# check syntax and simplify structure


def check_syntax(s: list | str) -> list:
    if isinstance(s, str):
        assert good_name(s), \
            f"Syntax error: Bad name '{s}'.\n{NAME_HELP}"
        return s

    expr = f"Expression: {flatten_struct(s)}\nSyntax error:"

    assert len(s) in range(1, 6), \
        f"{expr} Too few/many arguments ({len(s)})."
    if len(s) == 1:
        # ((...))
        body = s[0]
        if isinstance(body, str):
            assert body not in OPERATORS, \
                f"{expr} Expected an expression, but found an operator."
            return body
        return check_syntax(s[0])
    elif len(s) == 2:
        # (not (...))
        assert (s[0] == 'not' and
                s[1] not in OPERATORS), \
            f"{expr} Invalid or missing arguments."
        return ['not', check_syntax(s[1])]
    elif len(s) == 3:
        # ((...) [operator] (...))
        assert s[1] in OPERATORS, \
            f"{expr} Invalid operator '{s[1]}'."
        assert s[0] not in OPERATORS, \
            f"{expr} Expected an expression at position 1, but found an operator '{s[0]}'."
        assert s[2] not in OPERATORS, \
            f"{expr} Expected an expression at position 3, but found an operator '{s[2]}'."
        return [check_syntax(s[0]), s[1], check_syntax(s[2])]
    elif len(s) == 4:
        # (not (...) [operator] (...))
        # ((...) [operator] not (...))
        case1 = [s[0] == 'not',
                 s[2] in OPERATORS,
                 s[1] not in OPERATORS,
                 s[3] not in OPERATORS]
        case2 = [s[2] == 'not',
                 s[1] in OPERATORS,
                 s[0] not in OPERATORS,
                 s[3] not in OPERATORS]
        assert all(case1) or all(case2), \
            f"{expr} Invalid operand format."
        if all(case1):
            return ['not', check_syntax(s[1]), s[2], check_syntax(s[3])]
        else:
            return [check_syntax(s[0]), s[1], 'not', check_syntax(s[3])]
    elif len(s) == 5:
        # (not (...) [operator] not (...))
        assert s[0] == 'not' and s[3] == 'not', \
            f"{expr} Unexpected token in expression."
        assert s[2] in OPERATORS, \
            f"{expr} Expected an operator, but found '{s[2]}'."
        assert s[1] not in OPERATORS, \
            f"{expr} Expected an expression, but found an operator '{s[1]}'."
        assert s[4] not in OPERATORS, \
            f"{expr} Expected an expression, but found an operator '{s[4]}'."
        return ['not', check_syntax(s[1]), s[2], 'not', check_syntax(s[4])]


# parse a propositional statement (nested list)


def parsed(s: str) -> list:
    _s = standardize_notations(f"({s})", display=False)
    # for each component: add quotes and separate by ,
    _s = re.sub(r'([^\s()]+\b|[^\w\s()]+\B)',
                r'"\1",',
                _s)
    # convert () to python list notation [[...],]
    _s = _s.replace('(', '[')
    _s = re.sub(r'\)(?!$)', '],', _s)
    _s = _s.replace(')', ']')  # last ) should not end in ,

    parsed = eval(_s)
    return check_syntax(parsed)


# check if two statements are equivalent in form


def equivalent_form(s1: list | str, s2: list | str) -> bool:
    if isinstance(s1, str) and isinstance(s2, str):
        # both strings
        return s1 == s2
    elif isinstance(s1, list) and isinstance(s2, list):
        # both lists

        if len(s1) == len(s2):
            if len(s1) == 1:
                # ((...))
                # ((...))
                return equivalent_form(s1[0], s2[0])
            if len(s1) == 2:
                # (not (...))
                # (not (...))
                return equivalent_form(s1[1], s2[1])
            elif len(s1) == 3:
                # ((...) [operator1] (...))
                # ((...) [operator2] (...))
                lhs1, op1, rhs1 = s1
                lhs2, op2, rhs2 = s2

                if op1 == op2:
                    # same operator
                    if (op1 in COMMUTATIVE_OPERATORS and
                            op2 in COMMUTATIVE_OPERATORS):
                        # both commutative
                        return ((equivalent_form(lhs1, lhs2) and
                                 equivalent_form(rhs1, rhs2)) or
                                (equivalent_form(lhs1, rhs2) and
                                 equivalent_form(rhs1, lhs2)))
                    else:
                        # both not commutative
                        return (equivalent_form(lhs1, lhs2) and
                                equivalent_form(rhs1, rhs2))

            elif len(s1) == 4:
                # 1: (not (...) [operator1] (...))
                #    (not (...) [operator2] (...))
                #
                # 2: (not (...) [and/or/xor/iff] (...))
                #    ((...) [and/or/xor/iff] not (...))
                #
                # 3: ((...) [and/or/xor/iff] not (...))
                #    (not (...) [and/or/xor/iff] (...))
                #
                # 4: ((...) [operator1] not (...))
                #    ((...) [operator2] not (...))

                if s1[0] == 'not' and s2[0] == 'not':
                    # case 1
                    return (equivalent_form(s1[1], s2[1]) and
                            equivalent_form(s1[3], s2[3]))
                elif s1[2] == 'not' and s2[2] == 'not':
                    # case 4
                    return (equivalent_form(s1[0], s2[0]) and
                            equivalent_form(s1[3], s2[3]))
                elif s1[0] == 'not' and s2[2] == 'not':
                    # case 2
                    return all([s1[2] in COMMUTATIVE_OPERATORS,
                                s2[1] in COMMUTATIVE_OPERATORS,
                                s1[2] == s2[1],
                                equivalent_form(s1[1], s2[3]),
                                equivalent_form(s1[3], s2[0])])
                elif s2[0] == 'not' and s1[2] == 'not':
                    # case 3
                    return all([s1[1] in COMMUTATIVE_OPERATORS,
                                s2[2] in COMMUTATIVE_OPERATORS,
                                s1[1] == s2[2],
                                equivalent_form(s1[0], s2[3]),
                                equivalent_form(s1[3], s2[1])])

            elif len(s1) == 5:
                # (not (...) [operator1] not (...))
                # (not (...) [operator2] not (...))

                lhs1, op1, rhs1 = s1[1], s1[2], s1[4]
                lhs2, op2, rhs2 = s2[1], s2[2], s2[4]

                if op1 == op2:
                    # same operator
                    if (op1 in COMMUTATIVE_OPERATORS and
                            op2 in COMMUTATIVE_OPERATORS):
                        # both commutative
                        return ((equivalent_form(lhs1, lhs2) and
                                 equivalent_form(rhs1, rhs2)) or
                                (equivalent_form(lhs1, rhs2) and
                                 equivalent_form(rhs1, lhs2)))
                    else:
                        # both not commutative
                        return (equivalent_form(lhs1, lhs2) and
                                equivalent_form(rhs1, rhs2))
        else:
            if len(s1) == 1:
                # ((...))
                # arbitrary length
                return equivalent_form(s1[0], s2)
            elif len(s2) == 1:
                # arbitrary length
                # ((...))
                return equivalent_form(s1, s2[0])

    return False


# compile a parsed statement


def compile(s: list):
    variables: set[str] = set()
    atoms: list[str] = []
    structs: list = []

    # check if same form already exists
    def should_add(s: list) -> bool:
        for struct in structs:
            if equivalent_form(s, struct):
                return False
        return True

    def _compile(s: list | str,
                 variables: set[str],
                 atoms: list[str],
                 structs: list) -> str:
        # variables/operators
        if isinstance(s, str):
            variables.add(s)
            return s

        # encapsulated expression
        assert isinstance(s, list) and len(s) in range(1, 6)

        # do not include those with redundant parentheses or equivalent forms

        if len(s) == 1:
            # ((...))
            # get rid of encapsulating parentheses
            expr = _compile(s[0], variables, atoms, structs)
            if should_add(s[0]):
                atoms.append(expr)
                structs.append(s[0])
            return expr
        elif len(s) == 2:
            # (not (...))
            assert s[0] == 'not'
            expr = _compile(s[1], variables, atoms, structs)
            if should_add(s[1]):
                atoms.append(expr)
                structs.append(s[1])
            return f"({OPERATOR_TOKENS['not']}{expr})"
        elif len(s) == 3:
            # ((...) [operator] (...))
            lhs = _compile(s[0], variables, atoms, structs)
            rhs = _compile(s[2], variables, atoms, structs)
            if should_add(s[0]):
                atoms.append(lhs)
                structs.append(s[0])
            if should_add(s[2]):
                atoms.append(rhs)
                structs.append(s[2])
            return f"({lhs}{OPERATOR_TOKENS[s[1]]}{rhs})"
        elif len(s) == 4:
            # 1: (not (...) [operator] (...))
            # 2: ((...) [operator] not (...))
            assert s[0] == 'not' or s[2] == 'not'
            if s[0] == 'not':
                # case 1
                lhs = _compile(s[1], variables, atoms, structs)
                rhs = _compile(s[3], variables, atoms, structs)
                if should_add(s[1]):
                    atoms.append(lhs)
                    structs.append(s[1])
                if should_add(s[3]):
                    atoms.append(rhs)
                    structs.append(s[3])
                return f"(({OPERATOR_TOKENS['not']}{lhs}){OPERATOR_TOKENS[s[2]]}{rhs})"
            elif s[2] == 'not':
                # case 2
                lhs = _compile(s[0], variables, atoms, structs)
                rhs = _compile(s[3], variables, atoms, structs)
                if should_add(s[0]):
                    atoms.append(lhs)
                    structs.append(s[0])
                if should_add(s[3]):
                    atoms.append(rhs)
                    structs.append(s[3])
                return f"({lhs}{OPERATOR_TOKENS[s[1]]}({OPERATOR_TOKENS['not']}{rhs}))"
        elif len(s) == 5:
            # (not (...) [operator] not (...))
            assert s[0] == 'not' and s[3] == 'not'
            lhs = _compile(s[1], variables, atoms, structs)
            rhs = _compile(s[4], variables, atoms, structs)
            if should_add(s[1]):
                atoms.append(lhs)
                structs.append(s[1])
            if should_add(s[4]):
                atoms.append(rhs)
                structs.append(s[4])
            return f"(({OPERATOR_TOKENS['not']}{lhs}){OPERATOR_TOKENS[s[2]]}({OPERATOR_TOKENS['not']}{rhs}))"

    result = _compile(s, variables, atoms, structs)
    if should_add(s):
        atoms.append(result)
        structs.append(s)
    # remove variables from atomic sentences
    atoms = list(filter(lambda atom: atom not in variables, atoms))
    return (result, sorted(variables), atoms, structs)


# naive function that output a table via either stdout or csv


def output_table(data: Dict[str, list],
                 labels: list[str] | None = None,
                 filename: str | None = None):
    headers = list(data.keys())
    # ASSERT: same number of rows in data
    row_no = len(data[headers[0]])

    if filename:
        # write to csv file
        with open(filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            # write header without check/cross column
            headers = list(filter(lambda h: h != MARK_COLUMN, headers))
            writer.writerow(headers)
            # write body
            for row in range(row_no):
                # truth_table: COMPILED sentences as keys
                values = [data[col][row] for col in headers]
                if labels:
                    # use custom labels
                    true, false = labels
                    values = list(
                        map(lambda v: true if v == 1 else false, values))
                writer.writerow(values)
    else:
        # print table
        # make header and template for rows
        top_border = []
        row_template = []
        row_separator = []
        bottom_border = []

        for column in headers:
            size = len(column) + 2
            if column == MARK_COLUMN:
                size = 3
            # make top border
            top_border.append(BOX_OUTER_HLINE * size)
            # make row template
            row_template.append('{:^' + str(size) + '}')
            # make row separator
            row_separator.append(BOX_INNER_HLINE * size)
            # make footer
            bottom_border.append(BOX_OUTER_HLINE * size)

        top_border = BOX_TOP_T.join(top_border)
        row_template = BOX_INNER_VLINE.join(row_template)
        row_separator = BOX_JOINT.join(row_separator)
        bottom_border = BOX_BOTTOM_T.join(bottom_border)

        top_border = BOX_TOP_LEFT + top_border + BOX_TOP_RIGHT
        row_template = BOX_OUTER_VLINE + row_template + BOX_OUTER_VLINE
        row_separator = BOX_LEFT_T + row_separator + BOX_RIGHT_T
        row_separator = '\n' + row_separator + '\n'
        bottom_border = BOX_BOTTOM_LEFT + bottom_border + BOX_BOTTOM_RIGHT

        # initialize rows with header
        # hide CHECK/CROSS key
        display_headers = []
        for header in headers:
            if header == MARK_COLUMN:
                display_headers.append(' ')
            else:
                display_headers.append(header)

        rows: list[str] = [row_template.format(*display_headers)]
        for row in range(row_no):
            values = [data[col][row] for col in headers]
            if labels:
                # use custom labels
                true, false = labels

                # substitution handler
                def substitute(value: str) -> str:
                    return true if value == 1 else (false if value == 0 else value)

                values = list(map(substitute, values))
            rows.append(row_template.format(*values))

        # print table
        print(top_border)
        print(row_separator.join(rows))
        print(bottom_border)


# -----* DEPRECATED *-----
#
#
#     def get_atomic_sentences(sentence: str) -> list[str]:
#         # https://stackoverflow.com/a/12280660/10446972
#         sentence_pattern = '''(?<atm> # capturing group atm
# (?:\( # open parenthesis
#  (?: # non-capturing group
#   [^()]++ # anything but parentheses >=1 times w/o backtracking
#   | # or
#   (?&atm) # recursive substitute of group 'atm'
#  )*
#  \) # close parenthesis
# ))
#         '''
#         results = regex.search(sentence_pattern, sentence,
#                                flags=regex.VERBOSE)
#         return results.captures('atm')
#
#    def get_variables(display_sentence: str) -> list[str]:
#        # this pattern will not work for non-display-style symbols
#        # e.g. NOT, and, iff, XOR, etc.
#        var_pattern = '\\w+'
#        results = regex.findall(var_pattern, display_sentence)
#        return sorted(set(results))
