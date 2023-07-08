from re import sub, match
import csv
from os import path

from typing import List, Tuple
from typing import Any

from constants import *


# ===== stdout =====


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


# ===== Preprocessing =====


def standardize_notations(s: str) -> str:
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

    return s


def parse(s: str) -> list:
    # for each component: add quotes and separate by ,
    s = sub(r'([^\s()]+\b|[^\w\s()]+\B)',
            r'"\1",',
            s)
    # convert () to python list notation [[...],]
    s = s.replace('(', '[')
    s = sub(r'\)(?!$)', '],', s)
    s = s.replace(')', ']')  # last ) should not end in ,

    struct = list(eval(s))
    return struct


# ===== Miscellaneous =====


# NOTE: temporary solution to removing parentheses
def display(token) -> str:
    # '(a V b)' -> 'a V b'
    return sub(r'^\(([\s\S]*)\)$', r'\1', str(token))


# https://stackoverflow.com/questions/1653970/does-python-have-an-ordered-set
def unique(seq: List | Tuple) -> List:
    return list(dict.fromkeys(seq))


# determine if a variable name conforms to the rules


def good_name(name: str) -> bool:
    # 1. begins with a-z, A-Z or _ (underscore)
    # 2. contains only a-z, A-Z, 0-9 or _
    # 3. does not contain any spaces
    pattern = r'^[a-zA-Z_]\w*$'
    return bool(match(pattern, name))


# process new file name


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


def output_table(table: List[List[Any]],
                 labels: str | None = None,
                 filepath: str | None = None):
    if isinstance(labels, str):
        # prepare custom labels
        assert len(labels) == 2, CUSTOM_LABEL_LENGTH_ERROR
        assert labels[0] != labels[1], CUSTOM_LABEL_IDENTICAL_ERROR
        table = [
            [labels[cell] if cell in [0, 1] else cell for cell in row]
            for row in table
        ]
    
    header = table[0]

    if filepath:
        # write to csv file
        filepath = preprocess_filename(filepath)

        if MARK_COLUMN in header:
            # remove mark column
            table = [row[:-1] for row in table]

        with open(filepath, 'w') as csv_file:
            writer = csv.writer(csv_file)
            # write body
            for row in table:
                writer.writerow(row)
    else:
        col_widths: List[int] = []
        # get lengthiest string per column as its width
        for i in range(len(header)):
            if header[i] == MARK_COLUMN:
                col_widths.append(3)
            else:
                col_lengths = [len(str(row[i])) for row in table]
                col_widths.append(max(col_lengths) + 2)

        # create row templates
        row_template, row_separator, border = [], [], []
        for width in col_widths:
            border.append(BOX_OUTER_HLINE * width)
            row_template.append('{:^' + str(width) + '}')
            row_separator.append(BOX_INNER_HLINE * width)

        # create top/bottom borders
        top_border = f"{BOX_TOP_LEFT}{BOX_TOP_T.join(border)}{BOX_TOP_RIGHT}"
        bottom_border = f"{BOX_BOTTOM_LEFT}{BOX_BOTTOM_T.join(border)}{BOX_BOTTOM_RIGHT}"

        # create row separator and separator
        row_separator = f"\n{BOX_LEFT_T}{BOX_JOINT.join(row_separator)}{BOX_RIGHT_T}\n"
        row_template = f"{BOX_OUTER_VLINE}{BOX_INNER_VLINE.join(row_template)}{BOX_OUTER_VLINE}"

        rows = []
        for row in table:
            rows.append(row_template.format(*row))

        print(top_border)
        print(row_separator.join(rows))
        print(bottom_border)
