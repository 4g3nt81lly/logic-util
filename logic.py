#!/opt/homebrew/bin/python3
import argparse
# avoid arrow key values
# reference: https://stackoverflow.com/a/66539061/10446972
import readline

from objects import *

parser = argparse.ArgumentParser(prog='Logic',
                                 description='A propositional logic toolkit.',
                                 epilog='')

subparsers = parser.add_subparsers()
make_table_parser = subparsers.add_parser('make-table',
                                          help='Make a truth table using the given propositional statement.')
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
                               help='The file name to be saved.')

check_equivalence_parser = subparsers.add_parser('check-equivalence',
                                                 help="Check if two statements are logically equivalent.")
check_equivalence_parser.add_argument('equivalent_statements',
                                      nargs='*', type=str, action='store', default=None,
                                      metavar=('STATEMENT'),
                                      help='A set of propositional statements to be checked.')
check_equivalence_parser.add_argument('-l', '--labels',
                                      type=str, action='store', default=None,
                                      metavar=('[FALSE][TRUE]'),
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
                                   nargs='*', type=str, action='store', default=None,
                                   metavar=('PREMISE'),
                                   help='A set of premises.')
check_validity_parser.add_argument('-c', '--conclusion',
                                   type=str, action='store', default=None,
                                   help='The conclusion of the argument.')
check_validity_parser.add_argument('-l', '--labels',
                                   type=str, action='store', default=None,
                                   metavar=('[FALSE][TRUE]'),
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
    def make_table(statement: str):
        statement = Proposition(statement,
                                labels=args.labels,
                                reverse=args.reverse_values)

        # get output file name
        filename = args.output.strip() if args.output else None
        statement.output(filename=filename, no_atoms=args.no_atoms)

    if args.table_statement:
        statement = args.table_statement.strip()
        if statement != '':
            make_table(statement)
            exit()

    while True:
        try:
            statement = input('Enter a statement: ').strip()
        except (KeyboardInterrupt, EOFError):
            break  # exit

        if statement == '':
            exit()

        make_table(statement)

elif 'equivalent_statements' in opts.keys():
    # check equivalence
    def check_equivalence(statements: list[Proposition] | list[str]):
        # parse and compile all statements
        statements = Argument(statements,
                              labels=args.labels)

        # get output file name
        filename = args.output.strip() if args.output else None

        if not args.verbose:
            # normal: print a combined table with checkmarks
            statements.output(check_handler=statements.CHECK_EQUIVALENT,
                              filename=filename)

        equivalent = statements.all_equivalent(verbose=args.verbose)

        print()

        # print conclusion
        if equivalent:
            # equivalent
            print(
                '\n',
                bold(green(CHECK_MARK,
                           'The statements are logically equivalent!'))
            )
        else:
            # not equivalent
            print(
                bold(red(CROSS_MARK,
                         'The statements are not logically equivalent!'))
            )
        
        print()

    if args.equivalent_statements:
        # strip all statements
        statements = [s.strip() for s in args.equivalent_statements]
        # filter empty statements
        statements = list(filter(lambda s: s != '', statements))

        if len(statements) < 2:
            print('At least 2 statements are required.')
            exit()

        # create proposition objects
        statements = [Proposition(s) for s in statements]

        # display statements
        print()
        for index, statement in enumerate(statements):
            print(f"{index + 1}.", statement.display())
        print()

        # filter statements with equivalent forms
        equivalent_statements = OrderedDict()
        for i, p1 in enumerate(statements):
            # skip the ones pending removal
            if not p1:
                continue
            # check rest of the list
            for j, p2 in enumerate(statements[i + 1:]):
                if equivalent_form(p1.source.struct, p2.source.struct):
                    # remove the later (p2, keeping the p1)
                    # NOTE: to preserve normal indexing, don't remove right away
                    index = i + j + 1
                    statements[index] = None
                    # keep track of the these statements
                    key, val = p1.display(), p2.display()
                    if key not in equivalent_statements.keys():
                        equivalent_statements[key] = []
                    equivalent_statements[key].append((index, val))
        # remove the None values
        statements = list(filter(lambda s: s is not None, statements))

        if len(equivalent_statements) > 0:
            print('The following are commutative/associative-equivalent:')
            for i, (p1, p2s) in enumerate(equivalent_statements.items()):
                for (j, p2) in p2s:
                    print(f"({i + 1})",
                          p1 + EQUIV_SYMBOL + f"({j + 1})",
                          p2)
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
        statements: list[Proposition] = []
        while True:
            try:
                statement = input(f"({len(statements) + 1}) ").strip()
            except (KeyboardInterrupt, EOFError):
                exit()

            if statement == '':
                break

            try:
                statement = Proposition(statement,
                                        handle_error=False)
            except (Exception, AssertionError, SyntaxError):
                continue

            # get commutative/associative-equivalent statements
            equivalences = []
            for s in statements:
                if equivalent_form(statement.source.struct, s.source.struct):
                    equivalences.append(s.display())
            if len(equivalences) > 0:
                print('The statement is commutative/associative-equivalent to:')
                statement = statement.display()
                for s in equivalences:
                    print('>', s)
            else:
                statements.append(statement)

        if statements == []:
            exit()
        elif len(statements) == 1:
            print('At least 2 statements are required.')
        else:
            print()
            check_equivalence(statements)

elif 'arg_premises' in opts.keys():
    # check validity
    def check_validity(premises, conclusion):
        # parse and compile all statements
        argument = Argument(premises, conclusion=conclusion,
                            labels=args.labels,
                            reverse=args.reverse_values)

        # get output file name
        filename = args.output.strip() if args.output else None

        argument.output(check_handler=argument.X_COUNTERMODEL,
                        filename=filename)

        valid = argument.is_valid(print_countermodel=True)

        # print conclusion
        if valid:
            # valid
            print(bold(green(CHECK_MARK, 'The argument is valid!')))
        else:
            # invalid
            print()
            print(bold(red(CROSS_MARK, 'The argument is invalid!')))

        print()

    if args.arg_premises:
        # strip all premises
        premises = [p.strip() for p in args.arg_premises]
        # filter empty premises
        premises = list(filter(lambda p: p != '', premises))

        # take last premise as conclusion if none provided
        conclusion = premises[-1]
        if args.conclusion:
            # conclusion is given
            conclusion = args.conclusion.strip()
        else:
            conclusion = premises[-1]
            # exclude the last premise since it was used as conclusion
            premises = premises[:-1]

        premises = [Proposition(p) for p in premises]
        conclusion = Proposition(conclusion)

        # display argument, confirm
        print()
        max_length = 0
        for index, premise in enumerate(premises):
            display = premise.display()
            # update max length
            if len(display) > max_length:
                max_length = len(display)
            print(f"{index + 1}.", premise.display())
        # separate w/ max length of display premises + 5
        separator(max_length + 5)
        print('\u2234', conclusion.display(), end='\n\n')

        check_validity(premises, conclusion)
        exit()

    # interactive mode
    while True:
        premises: list[Proposition] = []
        while True:
            try:
                premise = input(f"Premise {len(premises) + 1}: ").strip()
            except (KeyboardInterrupt, EOFError):
                exit()

            if premise == '':
                break

            try:
                premise = Proposition(premise,
                                      handle_error=False)
            except (Exception, AssertionError, SyntaxError):
                continue

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
                except (Exception, AssertionError, SyntaxError):
                    continue

                break

        # display argument, confirm
        print()
        max_length = 0
        for index, premise in enumerate(premises):
            display = premise.display()
            # update max length
            if len(display) > max_length:
                max_length = len(display)
            print(f"{index + 1}.", premise.display())
        # separate w/ max length of display premises + 5
        separator(max_length + 5)
        print('\u2234', conclusion.display(), end='\n\n')
        if confirm('Check? (Y/n)'):
            print()
            check_validity(premises, conclusion)

else:
    parser.print_help()
