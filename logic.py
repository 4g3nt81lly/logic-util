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
                               type=str, action='store', metavar=('STATEMENT'),
                               help='A propositional statement.')
make_table_parser.add_argument('-n', '--no-atoms', action='store_true', default=False,
                               help='Do not include atomic sentences in the table.')
make_table_parser.add_argument('-r', '--reverse-values', action='store_true', default=False,
                               help='Reverse the order of the truth values in the table.')
make_table_parser.add_argument('-o', '--output', type=str, action='store', metavar=('FILE-PATH'),
                               help='The file name to be saved.')

check_equivalence_parser = subparsers.add_parser('check-equivalence',
                                                 help="Check if two statements are logically equivalent.")
check_equivalence_parser.add_argument('equivalent_statements',
                                      nargs='+', type=str, action='store', metavar=('STATEMENT'),
                                      help='A set of propositional statements to be checked.')
check_equivalence_parser.add_argument('-v', '--verbose', action='store_true', default=False,
                                      help='Verbose Mode: Print the truth table and a detailed conclusion.')
check_equivalence_parser.add_argument('-o', '--output', type=str, action='store', metavar=('FILE-PATH'),
                                      help='The file name to be saved. This flag is ignored when verbose mode is off.')

check_validity_parser = subparsers.add_parser('check-validity',
                                              help='Check if an argument is valid.')
check_validity_parser.add_argument('arg_premises', nargs='+', type=str, action='store', metavar=('PREMISE'),
                                   help='A set of premises.')
check_validity_parser.add_argument('-c', '--conclusion', type=str, action='store',
                                   help='The conclusion of the argument.')

# get arguments
args = parser.parse_args()
opts = vars(args)


if 'table_statement' in opts.keys():
    # make truth table
    statement = args.table_statement.strip()

    statement = Proposition(statement, reverse=args.reverse_values)

    if args.output:
        # output specified
        filename = args.output.strip()
        statement.output(filename, no_atoms=args.no_atoms)
    else:
        # print table
        statement.output(no_atoms=args.no_atoms)

elif 'equivalent_statements' in opts.keys():
    # check equivalence
    statements = [s.strip() for s in args.equivalent_statements]
    statements = [standardize_notations(f"({s})") for s in statements]

    statements = Argument(statements)

    # get output file name
    filename = None
    if args.output:
        filename = args.output.strip()

    if not args.verbose:
        # normal: print a combined table with checkmarks
        def check(s: list[str]) -> bool:
            # avoid checking variable columns
            variables_count = len(statements.variables)
            sentences = s[variables_count:]
            # it would be of length 1 if all same
            return len(set(sentences)) == 1

        statements.output(check_handler=check, filename=filename)
    # print conclusion
    if statements.all_equivalent(verbose=args.verbose):
        # equivalent
        print(CHECK_MARK,
              bold(green('The statements are logically equivalent!')))
    else:
        # not equivalent
        print(CROSS_MARK,
              bold(red('The statements are not logically equivalent!')))

elif 'arg_premises' in opts.keys():
    print('check validity')
else:
    parser.print_help()
