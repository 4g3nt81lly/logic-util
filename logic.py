#!/opt/homebrew/bin/python3
import argparse

from constants import *
from helpers import *
from objects import *

parser = argparse.ArgumentParser(prog='Logic',
                                 description='A propositional logic toolkit.',
                                 epilog='')

subparsers = parser.add_subparsers()
make_table_parser = subparsers.add_parser('make-table',
                                          help='Make a truth table using the given propositional statement.')
make_table_parser.add_argument('table_statement',
                               type=str, action='store',
                               metavar=('STATEMENT'),
                               help='A propositional statement.')
make_table_parser.add_argument('-l', '--labels',
                               type=str, action='store', default=None,
                               metavar=('[TRUE][FALSE]'),
                               help='Custom labels for truth values.')
make_table_parser.add_argument('-n', '--no-atoms',
                               action='store_true', default=False,
                               help='Do not include atomic sentences in the table.')
make_table_parser.add_argument('-r', '--reverse-values',
                               action='store_true', default=False,
                               help='Reverse the order of the truth values in the table.')
make_table_parser.add_argument('-o', '--output',
                               type=str, action='store',
                               metavar=('FILE-PATH'),
                               help='The file name to be saved.')

check_equivalence_parser = subparsers.add_parser('check-equivalence',
                                                 help="Check if two statements are logically equivalent.")
check_equivalence_parser.add_argument('equivalent_statements',
                                      nargs='+', type=str, action='store',
                                      metavar=('STATEMENT'),
                                      help='A set of propositional statements to be checked.')
check_equivalence_parser.add_argument('-l', '--labels',
                                      type=str, action='store', default=None,
                                      metavar=('[TRUE][FALSE]'),
                                      help='Custom labels for truth values.')
check_equivalence_parser.add_argument('-v', '--verbose',
                                      action='store_true', default=False,
                                      help='Verbose Mode: Print the truth table and a detailed conclusion.')
check_equivalence_parser.add_argument('-o', '--output',
                                      type=str, action='store',
                                      metavar=('FILE-PATH'),
                                      help='The file name to be saved. \
                                        This flag is ignored when verbose mode is on.')

check_validity_parser = subparsers.add_parser('check-validity',
                                              help='Check if an argument is valid.')
check_validity_parser.add_argument('arg_premises',
                                   nargs='+', type=str, action='store',
                                   metavar=('PREMISE'),
                                   help='A set of premises.')
check_validity_parser.add_argument('-c', '--conclusion',
                                   type=str, action='store', required=True,
                                   help='The conclusion of the argument.')
check_validity_parser.add_argument('-l', '--labels',
                                   type=str, action='store', default=None,
                                   metavar=('[TRUE][FALSE]'),
                                   help='Custom labels for truth values.')
check_validity_parser.add_argument('-r', '--reverse-values',
                                   action='store_true', default=False,
                                   help='Reverse the order of the truth values in the table.')
check_validity_parser.add_argument('-o', '--output', type=str, action='store',
                                   metavar=('FILE-PATH'),
                                   help='The file name to be saved.')

# get arguments
args = parser.parse_args()
opts = vars(args)


if 'table_statement' in opts.keys():
    # make truth table
    statement = args.table_statement.strip()

    statement = Proposition(statement,
                            labels=args.labels,
                            reverse=args.reverse_values)

    # get output file name
    filename = args.output.strip() if args.output else None
    statement.output(filename=filename, no_atoms=args.no_atoms)

elif 'equivalent_statements' in opts.keys():
    # check equivalence
    # strip all statements
    statements = [s.strip() for s in args.equivalent_statements]
    # standardize notations for all statements
    # statements = [standardize_notations(f"({s})") for s in statements]

    # parse and compile all statements
    statements = Argument(statements,
                          labels=args.labels)

    # get output file name
    filename = args.output.strip() if args.output else None

    if not args.verbose:
        # normal: print a combined table with checkmarks
        statements.output(check_handler=statements.CHECK_EQUIVALENT,
                          filename=filename)

    # print conclusion
    if statements.all_equivalent(verbose=args.verbose):
        # equivalent
        print(
            bold(green(CHECK_MARK,
                       'The statements are logically equivalent!'))
        )
    else:
        # not equivalent
        print(
            bold(red(CROSS_MARK,
                     'The statements are not logically equivalent!'))
        )

elif 'arg_premises' in opts.keys():
    # check validity
    # strip all statements
    statements = [s.strip() for s in args.arg_premises]
    # standardize notations for all statements
    statements = [standardize_notations(f"({s})") for s in statements]

    # parse and compile all statements
    statements = Argument(statements, conclusion=args.conclusion,
                          labels=args.labels,
                          reverse=args.reverse_values)

    # get output file name
    filename = args.output.strip() if args.output else None

    statements.output(check_handler=statements.X_COUNTEREXAMPLE,
                      filename=filename)

    # print conclusion
    if statements.is_valid():
        # valid
        print(bold(green(CHECK_MARK, 'The argument is valid!')))
    else:
        # invalid
        print(bold(red(CROSS_MARK, 'The argument is invalid!')))

else:
    parser.print_help()
