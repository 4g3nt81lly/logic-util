import re
import csv
from typing import Dict

from constants import *


def bold(msg: str) -> str:
    return f"\033[1m{msg}\033[0m"


def green(msg: str) -> str:
    return f"\033[32m{msg}\033[0m"


def yellow(msg: str) -> str:
    return f"\033[33m{msg}\033[0m"


def red(msg: str) -> str:
    return f"\033[91m{msg}\033[0m"


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


# check syntax


def check_syntax(s: list | str) -> list:
    if isinstance(s, str):
        assert good_name(s), \
            f"Syntax error: Bad name '{s}'.\n{NAME_HELP}"
        return s

    expr = f"Expression: ({flatten_struct(s)})\nSyntax error:"

    assert len(s) in range(1, 6), \
        f"{expr} Too many arguments ({len(s)})."
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


def equivalent_structs(s1: list | str, s2: list | str) -> bool:
    if isinstance(s1, str) and isinstance(s2, str):
        # both strings
        return s1 == s2
    elif isinstance(s1, list) and isinstance(s2, list):
        # both lists

        if len(s1) == len(s2):
            if len(s1) == 1:
                # ((...))
                # ((...))
                return equivalent_structs(s1[0], s2[0])
            if len(s1) == 2:
                # (not (...))
                # (not (...))
                return equivalent_structs(s1[1], s2[1])
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
                        return ((equivalent_structs(lhs1, lhs2) and
                                 equivalent_structs(rhs1, rhs2)) or
                                (equivalent_structs(lhs1, rhs2) and
                                 equivalent_structs(rhs1, lhs2)))
                    else:
                        # both not commutative
                        return (equivalent_structs(lhs1, lhs2) and
                                equivalent_structs(rhs1, rhs2))

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
                    return (equivalent_structs(s1[1], s2[1]) and
                            equivalent_structs(s1[3], s2[3]))
                elif s1[2] == 'not' and s2[2] == 'not':
                    # case 4
                    return (equivalent_structs(s1[0], s2[0]) and
                            equivalent_structs(s1[3], s2[3]))
                elif s1[0] == 'not' and s2[2] == 'not':
                    # case 2
                    return all([s1[2] in COMMUTATIVE_OPERATORS,
                                s2[1] in COMMUTATIVE_OPERATORS,
                                s1[2] == s2[1],
                                equivalent_structs(s1[1], s2[3]),
                                equivalent_structs(s1[3], s2[0])])
                elif s2[0] == 'not' and s1[2] == 'not':
                    # case 3
                    return all([s1[1] in COMMUTATIVE_OPERATORS,
                                s2[2] in COMMUTATIVE_OPERATORS,
                                s1[1] == s2[2],
                                equivalent_structs(s1[0], s2[3]),
                                equivalent_structs(s1[3], s2[1])])

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
                        return ((equivalent_structs(lhs1, lhs2) and
                                 equivalent_structs(rhs1, rhs2)) or
                                (equivalent_structs(lhs1, rhs2) and
                                 equivalent_structs(rhs1, lhs2)))
                    else:
                        # both not commutative
                        return (equivalent_structs(lhs1, lhs2) and
                                equivalent_structs(rhs1, rhs2))
        else:
            if len(s1) == 1:
                # ((...))
                # arbitrary length
                return equivalent_structs(s1[0], s2)
            elif len(s2) == 1:
                # arbitrary length
                # ((...))
                return equivalent_structs(s1, s2[0])

    return False


# compile a parsed statement


def compile(s: list):
    variables: set[str] = set()
    atoms: list[str] = []
    structs: list = []

    # check if same form already exists
    def should_add(s: list) -> bool:
        for struct in structs:
            if equivalent_structs(s, struct):
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


def output_table(data: Dict[str, list], filename: str | None = None):
    headers = list(data.keys())
    # ASSERT: same number of rows in data
    row_no = len(data[headers[0]])

    if filename:
        # write to csv file
        with open(filename, 'w') as csv_file:
            writer = csv.writer(csv_file)
            # write header (variables + sentences, display style)
            writer.writerow(headers)
            # write body
            for row in range(row_no):
                # truth_table: COMPILED sentences as keys
                values = [data[col][row] for col in headers]
                writer.writerow(values)
    else:
        # print table
        # make header
        top_border = '\u252f'.join(
            ['\u2501' * (len(col) + 2) for col in headers]
        )
        top_border = f"\u250f{top_border}\u2513"

        # make rows
        row_template = '\u2502'.join(
            ['{:^' + str(len(col) + 2) + '}' for col in headers]
        )
        row_template = f"\u2503{row_template}\u2503"

        # initialize rows with header
        rows = [row_template.format(*headers)]
        for row in range(row_no):
            values = [data[col][row] for col in headers]
            rows.append(row_template.format(*values))
        
        # make row separator
        row_separator = '\u253c'.join(
            ['\u2500' * (len(col) + 2) for col in headers]
        )
        row_separator = f"\n\u2520{row_separator}\u2528\n"

        # make footer
        bottom_border = '\u2537'.join(
            ['\u2501' * (len(col) + 2) for col in headers]
        )
        bottom_border = f"\u2517{bottom_border}\u251b"

        # print table
        print(top_border)
        print(row_separator.join(rows))
        print(bottom_border)

        # for row in range(row_no):
        #     values = [data[col][row] for col in headers]
        #     if MARK_COLUMN in headers:
        #         if data[MARK_COLUMN][row] == CHECK_MARK:
        #             print('\033[0m\033[32m', end='')
        #         else:
        #             print('\033[0m\033[91m', end='')
        #     print(row_template.format(*values) + '\033[0m')


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