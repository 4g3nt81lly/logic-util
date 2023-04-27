from re import sub, subn, match
from itertools import permutations
import csv
from os import path
from typing import Dict

from constants import *


def bold(*msg, sep = ' ') -> str:
    msg = sep.join(msg)
    return f"\033[1m{msg}\033[0m"


def green(*msg, sep = ' ') -> str:
    msg = sep.join(msg)
    return f"\033[32m{msg}\033[0m"


def yellow(*msg, sep = ' ') -> str:
    msg = sep.join(msg)
    return f"\033[33m{msg}\033[0m"


def red(*msg) -> str:
    msg = ' '.join(msg)
    return f"\033[91m{msg}\033[0m"


def separator(length: int):
    print('\u2500' * length)


def confirm(prompt: str) -> bool:
    try:
        response = input(prompt).strip().lower()
    except KeyboardInterrupt:
        print()
        return False
    except EOFError:
        exit()

    return response in ['yes', 'y']

# standardize notations before compilation


def standardize_notations(s: str) -> str:
    s = sub(r'\s+', ' ', s)

    s = sub(AND_PATTERNS, AND_OP, s)
    # matching XOR before OR
    # so that XOR doesn't get matched by OR
    s = sub(XOR_PATTERNS, XOR_OP, s)
    s = sub(OR_PATTERNS, OR_OP, s)
    # matching IFF before IMPLY
    # so that <-> doesn't get matched by ->
    s = sub(IFF_PATTERNS, IFF_OP, s)
    s = sub(IMPLIES_PATTERNS, IMPLIES_OP, s)
    # match NOT last so that spaces are properly added
    s = sub(NOT_PATTERNS, NOT_OP, s)

    s = sub(r'\s+', ' ', s)

    # handle cases: ( not ...
    s = sub(r'\(\s+not', '(not', s)

    # remove extra parentheses for non-expressions
    # examples: (a), (not a), (not not not a)
    pattern = r'\(((?:not )*[a-zA-Z_]\w*)\)'
    while True:
        s, count = subn(pattern, r'\1', s)
        if count == 0:
            break

    # apply the rule for double negation
    pattern = r'(\s|\()(not\s){2}'
    while True:
        s, count = subn(pattern, r'\1', s)
        if count == 0:
            break

    return s


# flatten all associative expressions


def flatten(s: list):
    def _flatten(s: list | str,
              op: str | None = None):
        if isinstance(s, str):
            return s

        # ASSUME a list
        assert isinstance(s, list)

        if len(s) == 1:
            # ((...))
            return _flatten(s[0], op)
        elif len(s) == 2:
            # (not (...))
            arg = _flatten(s[1])
            # unpack ONLY IF it is not a variable
            arg = [*arg] if isinstance(arg, tuple) else [arg]
            return 'not', *arg
        elif len(s) > 2:
            for operator in OPS_BY_PRECEDENCE:
                try:
                    index = s.index(operator)
                except ValueError:
                    continue

                # apply to both sides
                lhs = _flatten(s[:index], operator)
                rhs = _flatten(s[index + 1:], operator)

                # unpack ONLY IF it is not a variable
                lhs = [*lhs] if isinstance(lhs, tuple) else [lhs]
                rhs = [*rhs] if isinstance(rhs, tuple) else [rhs]

                # apply associativity for associative operators
                # and ONLY IF the current operator is same as the outer scope
                if operator in ASSOCIATIVE_OPERATORS and operator == op:
                    return *lhs, operator, *rhs

                return [*lhs, operator, *rhs]

        # NOTE: should NEVER get here
        raise SyntaxError(UNEXPECTED_ERROR)

    flattened = _flatten(s)
    return list(flattened)


# convert a parsed structure into display sentence


def render(s: list, flattened: bool = True) -> str:
    def _render(s: list | str,
                outermost: bool = False) -> str:
        if isinstance(s, str):
            return s
        # ASSUME a list
        if len(s) == 1:
            # ((...))
            return _render(s[0])
        elif len(s) == 2:
            # (not (...))
            return f"{DISPLAY_OPERATORS['not']}{_render(s[1])}"
        elif len(s) > 2:
            results = []
            # whether the current item is the arg of a NOT operator
            not_arg = False
            for i, j in enumerate(s):
                if not_arg:
                    not_arg = False
                    continue
                assert isinstance(j, (str, list)), UNEXPECTED_ERROR
                if isinstance(j, list):
                    # expression
                    results.append(_render(j))
                else:
                    if j in OPS_BY_PRECEDENCE:
                        # binary operators
                        results.append(DISPLAY_OPERATORS[j])
                    elif j == 'not':
                        # unary operator: NOT
                        results.append(_render(s[i:i + 2]))
                        not_arg = True
                    else:
                        # variable
                        results.append(j)
            results = ' '.join(results)
            if outermost:
                return results
            return f"({results})"

        # NOTE: should NEVER get here
        raise SyntaxError(UNEXPECTED_ERROR)

    _s = s
    if flattened:
        _s = flatten(s)
    return _render(_s, outermost=True)


# determine if a variable name conforms to the rules:
# 1. begins with a-z, A-Z or _ (underscore)
# 2. contains only a-z, A-Z, 0-9 or _
# 3. does not contain any spaces
def good_name(name: str) -> bool:
    pattern = r'^[a-zA-Z_]\w*$'
    return bool(match(pattern, name))


# check syntax and preprocess


def check_syntax(s: list | str) -> list:
    expr = 'Syntax error:'

    if isinstance(s, str):
        assert good_name(s), \
            f"{expr} Bad name '{s}'.\n{NAME_HELP}"
        return s

    assert len(s) > 0, f"{expr} Too few arguments."

    if len(s) == 1:
        # ((...))
        body = s[0]
        if isinstance(body, str):
            assert body not in OPERATORS, \
                f"{expr} Expected a name, but found an operator."
        return check_syntax(body)
    elif len(s) == 2:
        # (not (...))
        assert (s[0] == 'not' and
                s[1] not in OPERATORS), \
            f"{expr} Invalid or missing arguments."
        return ['not', check_syntax(s[1])]
    elif len(s) > 2:
        for operator in OPS_BY_PRECEDENCE:
            try:
                index = s.index(operator)
            except ValueError:
                continue
            else:
                return [check_syntax(s[:index]), operator, check_syntax(s[index + 1:])]
        errmsg = f"{expr} Expected an operator in expression but found none."
        raise AssertionError(errmsg)


# parse a propositional statement (to nested list)


def parsed(s: str) -> list:
    # for each component: add quotes and separate by ,
    s = sub(r'([^\s()]+\b|[^\w\s()]+\B)',
               r'"\1",',
               s)
    # convert () to python list notation [[...],]
    s = s.replace('(', '[')
    s = sub(r'\)(?!$)', '],', s)
    s = s.replace(')', ']')  # last ) should not end in ,

    struct = eval(s)
    _ = check_syntax(struct)
    return list(struct)


# check if two statements are equivalent in form
# NOTE: this function can only check structures that have already been flattened:
#       E.g. (a or b or c), (a and b and c), (a xor b xor c), (a iff b iff c)
#       expressions of the form '(a or (b or c))' or '(a and (b and c))' should not exist


def equivalent_form(s1: list, s2: list) -> bool:
    def equivalent(s1: list | str, s2: list | str) -> bool:
        if isinstance(s1, str) and isinstance(s2, str):
            # both strings
            return s1 == s2
        elif isinstance(s1, list) and isinstance(s2, list):
            # both lists
            if len(s1) == len(s2):
                if len(s1) == 1:
                    # ((...))
                    # ((...))
                    return equivalent(s1[0], s2[0])
                if len(s1) == 2:
                    # (not (...))
                    # (not (...))
                    return equivalent(s1[1], s2[1])
                elif len(s1) > 2:
                    def separate(struct, operator):
                        result = []
                        sublist = []
                        for item in struct:
                            if item == operator:
                                result.append(sublist)
                                sublist = []
                            else:
                                sublist.append(item)
                        result.append(sublist)
                        return result

                    for operator in COMMUTATIVE_OPERATORS:
                        # find the same commutative operators in both expressions
                        components1 = separate(s1, operator)
                        components2 = separate(s2, operator)
                        # only the same number of components separated by
                        # a commutative operator can potentially be equivalent
                        if len(components1) == len(components2) and len(components1) > 1:
                            # get all permutations
                            perms = permutations(components1, len(components1))
                            # for each arrangement, check one-to-one equivalence
                            # a1 = a2, b1 = b2, c1 = c2, ...

                            for perm in perms:
                                all_equivalent = True
                                # one-to-one correspondence
                                for case1, component2 in zip(perm, components2):
                                    # if any not equivalent in the arrangement
                                    # skip to next arrangement

                                    if not equivalent(case1, component2):
                                        all_equivalent = False
                                        break
                                if all_equivalent:
                                    return True
            else:
                if len(s1) == 1:
                    # ((...))
                    # arbitrary length
                    return equivalent(s1[0], s2)
                elif len(s2) == 1:
                    # arbitrary length
                    # ((...))
                    return equivalent(s1, s2[0])
        else:
            # one string, one list
            if isinstance(s1, list) and len(s1) == 1:
                # ((...))
                # variable (str)
                return equivalent(s1[0], s2)
            elif isinstance(s2, list) and len(s2) == 1:
                # variable (str)
                # ((...))
                return equivalent(s1, s2[0])

        return False

    # _s1 = preprocess(s1)
    # _s2 = preprocess(s2)
    return equivalent(s1, s2)


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
                 structs: list,
                 outermost: bool = False) -> str:
        # variables/operators
        if isinstance(s, str):
            variables.add(s)
            # print(s, variables)
            return s

        # encapsulated expression
        assert isinstance(s, list) and len(s) > 0

        # do not include those with redundant parentheses or equivalent forms

        if len(s) == 1:
            # ((...))
            # get rid of encapsulating parentheses
            body = s[0]
            expr = _compile(body, variables, atoms, structs)
            # check for equivalent form and
            # whether the expr is a variable
            if should_add(body) and expr not in variables:
                atoms.append(expr)
                structs.append(body)
            return expr
        elif len(s) == 2:
            # (not (...))
            if s[0] == 'not':
                body = s[1]
                expr = _compile(body, variables, atoms, structs)
                # check for equivalent form and
                # whether the expr is a variable
                if should_add(body) and expr not in variables:
                    atoms.append(expr)
                    structs.append(body)
                expr = f"{BINARY_OPERATORS['not']}{expr}"
                if outermost:
                    return expr
                return f"({expr})"
        elif len(s) > 2:
            expr = []
            not_arg = False
            for i, j in enumerate(s):
                if not_arg:
                    not_arg = False
                    continue
                assert isinstance(j, (str, list)), UNEXPECTED_ERROR
                if isinstance(j, list):
                    # expression
                    expr.append(_compile(j, variables, atoms, structs))
                else:
                    if j in OPS_BY_PRECEDENCE:
                        # binary operators
                        expr.append(BINARY_OPERATORS[j])
                    elif j == 'not':
                        # unary operator
                        body = s[i:i + 2]
                        arg = _compile(body, variables, atoms, structs)
                        if should_add(body) and arg not in variables:
                            atoms.append(arg)
                            structs.append(body)
                        expr.append(arg)
                        not_arg = True
                    else:
                        # variable
                        expr.append(_compile(j, variables, atoms, structs))

            expr = ''.join(expr)
            if should_add(s) and expr not in variables:
                atoms.append(expr)
                structs.append(s)
            if outermost:
                return expr
            return f"({expr})"

        # NOTE: should NEVER get here
        raise SyntaxError(UNEXPECTED_ERROR)

    _s = flatten(s)
    source = _compile(_s, variables, atoms, structs, outermost=True)
    if should_add(_s) and source not in variables:
        atoms.append(source)
        structs.append(_s)
    return (_s, source, sorted(variables), atoms, structs)


# validate new filename
def preprocess_filename(filepath: str) -> str:
    filepath = filepath.strip()

    if path.isdir(filepath):
        filepath = path.join(filepath, 'output.csv')

    # add extension if no extension is provided
    if not filepath.endswith('.csv'):
        filepath += '.csv'

    # convert to absolute path, resolving ./../~/symlinks
    # also expanding environment variable e.g. $HOME
    filepath = path.realpath(path.expanduser(path.expandvars(filepath)))

    # change file name if file path exists
    counter = 1
    while path.exists(filepath):
        filepath = f"{filepath[:-4]}-{counter}.csv"
        counter += 1
    
    return filepath


# output a table via either stdout or csv


def output_table(data: Dict[str, list],
                 labels: list[str] | None = None,
                 filepath: str | None = None):
    headers = list(data.keys())
    # ASSERT: same number of rows in data
    row_no = len(data[headers[0]])

    if filepath:
        # write to csv file
        filepath = preprocess_filename(filepath)

        with open(filepath, 'w') as csv_file:
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
                values = [labels[v] if isinstance(v, int) else v for v in values]
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
