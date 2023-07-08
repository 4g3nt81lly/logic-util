import argparse
from sys import exit
# avoid arrow key values
# reference: https://stackoverflow.com/a/66539061/10446972
import readline

from objects import *

parser = argparse.ArgumentParser(prog='Logic',
                                 description='A propositional logic toolkit.',
                                 epilog='')

subparsers = parser.add_subparsers()
make_table_parser = subparsers.add_parser('make-table',
                                          help='Make a truth table for the given propositional statement.')
make_table_parser.add_argument('table_statement',
                               nargs='?', type=str, action='store', default=None,
                               metavar=('STATEMENT'),
                               help='A propositional statement.')
make_table_parser.add_argument('-l', '--labels',
                               type=str, action='store', default=None,
                               metavar=('[FALSE][TRUE]'),
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
                               help='The file path to be saved.')

check_equivalence_parser = subparsers.add_parser('check-equivalence',
                                                 help="Check if multiple statements are logically equivalent.")
check_equivalence_parser.add_argument('equivalent_statements',
                                      nargs='*', type=str, action='store', default=None,
                                      metavar=('STATEMENT'),
                                      help='A set of propositional statements to be checked.')
check_equivalence_parser.add_argument('-l', '--labels',
                                      type=str, action='store', default=None,
                                      metavar=('[FALSE][TRUE]'),
                                      help='Custom labels for truth values.')
check_equivalence_parser.add_argument('-m', '--mode',
                                      type=str.lower, choices=['default',
                                                               'paired',
                                                               'tree'],
                                      action='store', default='default',
                                      metavar=('MODE'),
                                      help='Mode for testing logical equivalences.')
check_equivalence_parser.add_argument('-r', '--reverse-values',
                                      action='store_true', default=False,
                                      help='Reverse the order of the truth values in the table.')
check_equivalence_parser.add_argument('-o', '--output',
                                      type=str, action='store',
                                      metavar=('FILE-PATH'),
                                      help='The file path to be saved. \
                                        This flag is ignored when mode is set to paired.')

check_validity_parser = subparsers.add_parser('check-validity',
                                              help='Check if an argument is valid.')
check_validity_parser.add_argument('arg_premises',
                                   nargs='*', type=str, action='store', default=None,
                                   metavar=('PREMISE'),
                                   help='A set of premises.')
check_validity_parser.add_argument('-c', '--conclusion',
                                   type=str, action='store', default=None,
                                   help='(Optional) The conclusion of the argument. \
                                    The last premise will be used as the conclusion if one is\'t provided.')
check_validity_parser.add_argument('-l', '--labels',
                                   type=str, action='store', default=None,
                                   metavar=('[FALSE][TRUE]'),
                                   help='Custom labels for truth values.')
check_validity_parser.add_argument('-r', '--reverse-values',
                                   action='store_true', default=False,
                                   help='Reverse the order of the truth values in the table.')
check_validity_parser.add_argument('-o', '--output', type=str, action='store',
                                   metavar=('FILE-PATH'),
                                   help='The file path to be saved.')

# get arguments
args = parser.parse_args()
opts = vars(args)


if 'table_statement' in opts.keys():
    # make truth table
    def make_table(statement: str):
        config = Config(reverse=args.reverse_values,
                        labels=args.labels,
                        atoms=(not args.no_atoms))
        statement = Proposition(statement, config=config)

        # get output file name
        filename = args.output.strip() if args.output else None
        statement.output_truth_table(filepath=filename)

    if args.table_statement:
        statement = args.table_statement.strip()
        if statement != '':
            try:
                make_table(statement)
            except Exception as err:
                print(err)
            exit()

    while True:
        try:
            statement = input('Enter a statement: ').strip()
        except (KeyboardInterrupt, EOFError):
            break  # exit

        if statement == '':
            exit()

        try:
            make_table(statement)
        except Exception as err:
            print(err)
            continue

elif 'equivalent_statements' in opts.keys():
    # check equivalence
    def check_equivalence(statements: List[Proposition] | List[str]):
        config = Config(reverse=args.reverse_values,
                        labels=args.labels)
        # parse and compile all statements
        statements: Argument = Argument(statements, config=config)

        # get output file name
        filename = args.output.strip() if args.output else None

        if args.mode == 'default':
            statements.output_truth_table(annotate='equivalence', filepath=filename)

        equivalent = statements.test_equivalence(mode=args.mode)

        print(end=('' if filename else '\n'))

        # print conclusion
        if equivalent:
            # equivalent
            print(
                bold(green(CHECK_MARK,
                           'The sentences are logically equivalent!'))
            )
        else:
            # not equivalent
            print(
                bold(red(CROSS_MARK,
                         'The sentences are not logically equivalent!'))
            )
        
        print()

    if args.equivalent_statements:
        # strip all statements
        statements = [s.strip() for s in args.equivalent_statements]
        # filter empty statements
        statements = [s for s in statements if s != '']

        if len(statements) < 2:
            print('At least 2 sentences are required.')
            exit()

        # create proposition objects
        statements: List[Proposition] = [Proposition(s) for s in statements]

        # display statements
        print()
        for index, statement in enumerate(statements):
            print(f"{index + 1}.", display(statement))
        print()

        # filter statements with equivalent forms
        equivalent_statements: List[Tuple[int, Proposition,
                                          List[Tuple[int, Proposition]]]] = []
        for i, s1 in enumerate(statements[:-1]):
            # skip the ones pending removal
            if not s1:
                continue
            # equivalent pairs
            equivalents: List[Proposition] = []
            for j, s2 in enumerate(statements[i + 1:]):
                if s1 == s2:
                    # get index to s2
                    index = i + j + 1
                    equivalents.append((index + 1, s2))
                    # mark the later for removal
                    statements[index] = None
            # add to list only if there are equivalents
            if len(equivalents) > 0:
                equivalent_statements.append((i + 1, s1, equivalents))
        statements = [s for s in statements if s is not None]

        if len(equivalent_statements) > 0:
            print('The following are commutative/associative-equivalent:')
            for (i, p1, p2s) in equivalent_statements:
                for (j, p2) in p2s:
                    print(f"({i})",
                          display(p1) + EQUIV_SYMBOL + f"({j})",
                          display(p2))
            print()
            # check the other statements
            if len(statements) > 1:
                print(BOX_INNER_HLINE * 50, end='\n\n')
                check_equivalence(statements)
        else:
            check_equivalence(statements)
        exit()

    # interactive mode
    while True:
        statements: List[Proposition] = []
        while True:
            try:
                statement = input(f"({len(statements) + 1}) ").strip()
            except (KeyboardInterrupt, EOFError):
                exit()

            if statement == '':
                break

            try:
                statement = Proposition(statement)
            except Exception as err:
                print(err)
                continue

            # get prior commutative/associative-equivalent statements
            equivalences = []
            for s in statements:
                if statement == s:
                    equivalences.append(s)
            if len(equivalences) > 0:
                print('The sentence is commutative/associative-equivalent to:')
                for s in equivalences:
                    print('>', display(s))
            else:
                print(display(statement))
                statements.append(statement)

        if statements == []:
            exit()
        elif len(statements) == 1:
            print('At least 2 sentences are required.')
        else:
            print()
            check_equivalence(statements)

elif 'arg_premises' in opts.keys():
    # check validity
    def check_validity(premises: List[Proposition],
                       conclusion: Proposition):
        config = Config(reverse=args.reverse_values,
                        labels=args.labels,
                        log_countermodel=True)
        # parse and compile all statements
        argument = Argument(premises, conclusion, config=config)

        # get output file name
        filename = args.output.strip() if args.output else None
        
        argument.output_truth_table(annotate='validity', filepath=filename)

        valid = argument.is_valid()

        print(end=('' if filename else '\n'))

        # print conclusion
        if valid:
            # valid
            print(bold(green(CHECK_MARK, 'The argument is valid!')))
        else:
            # invalid
            print(bold(red(CROSS_MARK, 'The argument is invalid!')))

        print()
    
    def display_argument(premises: List[Proposition],
                         conclusion: Proposition):
        # display argument, confirm
        print()
        max_length = 0
        for index, premise in enumerate(premises):
            display_text_length = len(str(premise))
            # update max length
            if display_text_length > max_length:
                max_length = display_text_length
            print(f"{index + 1}.", display(premise))
        # separate w/ max length of display premises + 5
        separator(max_length + 5)
        print(u'\u2234', display(conclusion), end='\n\n')

    if args.arg_premises:
        # strip all premises
        premises = [p.strip() for p in args.arg_premises]
        # filter empty premises
        premises = [p for p in premises if p != '']

        # take last premise as conclusion if none provided
        conclusion = premises[-1]
        if args.conclusion:
            # conclusion is given
            conclusion = args.conclusion.strip()
        else:
            # exclude the last premise since it was used as conclusion
            premises = premises[:-1]

        premises = [Proposition(p) for p in premises]
        conclusion = Proposition(conclusion)

        display_argument(premises, conclusion)

        check_validity(premises, conclusion)
        exit()

    # interactive mode
    while True:
        premises: List[Proposition] = []
        while True:
            try:
                premise = input(f"Premise {len(premises) + 1}: ").strip()
            except (KeyboardInterrupt, EOFError):
                exit()

            if premise == '':
                break

            try:
                premise = Proposition(premise)
            except Exception as err:
                print(err)
                continue

            print(display(premise))
            premises.append(premise)

        if premises == []:
            exit()

        while True:
            try:
                conclusion = input('Conclusion: ').strip()
            except (KeyboardInterrupt, EOFError):
                exit()

            if conclusion == '':
                # conclusion is not given
                if len(premises) > 1:
                    # take last premise as conclusion
                    conclusion = premises[-1]
                    premises = premises[:-1]
                    break
                else:
                    print('No conclusion is provided or not enough premises.')
                    print('NOTE: An argument needs at least 1 premise and 1 conclusion.')
                    continue
            else:
                try:
                    conclusion = Proposition(conclusion)
                except Exception as err:
                    print(err)
                    continue

                print(display(conclusion))
                break

        display_argument(premises, conclusion)

        if confirm('Check? (Y/n)'):
            print()
            check_validity(premises, conclusion)

else:
    parser.print_help()
