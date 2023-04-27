from collections import OrderedDict
from itertools import product, combinations
from typing import Dict, Callable

from constants import *
from helpers import *


class Token:
    # parsed structure
    struct: list
    # source binary
    binary: str
    # all variables
    variables: list | None
    # constituent sentences
    constituents: list | None
    # parsed structures of constituents
    constituent_structs: list | None

    def display_text(self) -> str:
        return render(self.struct)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Token):
            return self.binary == other.binary
        elif isinstance(other, str):
            return self.binary == other
        return False
    
    def __str__(self) -> str:
        return self.binary

    def __hash__(self):
        return hash(str(self))

    def __init__(self, struct: list, binary: str,
                 variables: list[str] | None = None,
                 constituents: list | None = None,
                 constituent_structs: list | None = None):
        self.struct = struct
        self.binary = binary
        self.variables = variables
        self.constituents = constituents
        self.constituent_structs = constituent_structs


class Proposition:
    # original statement (input)
    statement: str
    # compiled
    source: Token
    # all cases
    cases: list
    # truth table (ordered)
    truth_table: Dict[str | Token, list]

    # custom labels for TF
    labels: list[str] | None = None
    # reverse truth values?
    reverse_values: bool

    # display style statement
    def display(self) -> str:
        return self.source.display_text()

    # truth values of the proposition
    def values(self) -> list[int]:
        return self.truth_table[self.source]

    # dict: truth values of the proposition
    def row(self) -> Dict[str, list[str]]:
        return {render(self.token.struct): self.values()}
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Proposition):
            return self.source == other.source
        elif isinstance(other, str):
            return self.source == other
        return False
    
    def __repr__(self) -> str:
        return self.statement

    def __init__(self, statement: str,
                 labels: str | None = None,
                 reverse: bool = False,
                 handle_error: bool = True):
        statement = standardize_notations(f"({statement})")
        self.statement = statement
        self.reverse_values = reverse
        if isinstance(labels, (str, list)):
            if len(labels) != 2:
                print(CUSTOM_LABEL_EXCEED_LENGTH)
                exit()
            if labels[0] == labels[1]:
                print(CUSTOM_LABEL_IDENTICAL)
                exit()
            self.labels = [char for char in labels]

        # parse and get structure (to nested list)
        
        if handle_error:
            try:
                parsed_struct = parsed(statement)
            except AssertionError as err:
                print(err)
                exit()
            except SyntaxError as err:
                print('Expression:', f"'{statement}'")
                print(UNMATCHED_PARENTHESES)
                exit()
            except Exception as err:
                print('Expression:', f"'{statement}'")
                print(UNEXPECTED_ERROR, err)
                exit()
        else:
            # NOTE: can raise exceptions
            parsed_struct = parsed(statement)

        if parsed_struct == []:
            print(NULL_STATEMENT)
            raise Exception(NULL_STATEMENT)
        
        # compile statement
        token = compile(parsed_struct)
        token = Token(*token)
        self.source = token

        # make all cases
        # default order: F (top) -> T (bottom)
        cases = list(product([0, 1], repeat=len(token.variables)))
        if reverse:
            cases = cases[::-1]
        self.cases = cases
        # make table with variable columns

        self.truth_table = OrderedDict()

        for index, var in enumerate(token.variables):
            for case in cases:
                value = case[index]
                if var in self.truth_table.keys():
                    # key already exists, add to table
                    self.truth_table[var].append(value)
                else:
                    # add new key to table
                    self.truth_table[var] = [value]
        # for each atomic sentences
        for sentence, struct in zip(token.constituents, token.constituent_structs):
            # for each case (row)
            for case in cases:
                namespace = {var: case[index]
                             for index, var in enumerate(token.variables)}
                # evaluate result using eval
                result = eval(sentence, {}, namespace)
                # token object
                t = Token(struct, sentence)
                if t in self.truth_table.keys():
                    # key already exists, add to table
                    self.truth_table[t].append(result)
                else:
                    # add new key to table
                    self.truth_table[t] = [result]

    # an negated instance of the proposition
    def negated(self):
        return Proposition(f'~({self.statement})',
                           reverse=self.reverse_values, labels=self.labels)

    # whether the proposition is a tautology
    def is_tautology(self) -> bool:
        return all(self.values())

    # preprocess and output
    def output(self, check_handler: Callable[[list[str]], bool] | None = None,
               no_atoms: bool = False,
               filename: str | None = None):

        table_data = OrderedDict()

        for col, values in self.truth_table.items():
            if col in self.source.variables:
                table_data[col] = values
            else:
                display_sentence = col.display_text()
                if no_atoms:
                    # no reference columns, just the statement itself
                    if col == self.source:
                        table_data[display_sentence] = values
                else:
                    if col.binary in self.source.constituents:
                        table_data[display_sentence] = values

        if check_handler:
            # go through each row and add a column of check/cross mark
            headers = list(table_data.keys())
            # create a mark column
            table_data[MARK_COLUMN] = []
            for row in range(len(self.cases)):
                values = [table_data[col][row] for col in headers]
                # add check/cross mark using the given predicate
                mark = red(CROSS_MARK)
                if check_handler(values):
                    mark = green(CHECK_MARK)
                mark = f" {bold(mark)} "
                table_data[MARK_COLUMN].append(mark)

        output_table(table_data, labels=self.labels, filepath=filename)


class Argument:
    # premises (Proposition)
    premises: list[Proposition]
    # conclusion (optional)
    conclusion: Proposition | None = None
    # all variables
    variables: list[str]
    # all possible cases
    cases: list
    # truth table
    truth_table: Dict[str | Token, list]

    # custom labels for TF
    labels: list[str] | None = None
    # reverse truth values?
    reverse_values: bool

    # get all Proposition objects
    def all_propositions(self) -> list[Proposition]:
        return self.premises + ([self.conclusion] if self.conclusion else [])

    # get all sentences: premises + conclusion
    def all_sentences(self, variables: bool = False, conclusion: bool = True) -> list[str | Proposition]:
        sentences = self.premises
        if variables:
            sentences = self.variables + sentences
        if conclusion and self.conclusion:
            sentences.append(self.conclusion)
        return sentences

    def __init__(self, premises: list[str] | list[Proposition],
                 conclusion: str | Proposition | None = None,
                 labels: str | None = None,
                 reverse: bool = False):
        # check if premises is a list of Proposition objects
        if isinstance(premises[0], Proposition):
            # convert to list (if tuple)
            self.premises = list(premises)
        else:
            self.premises = [Proposition(premise) for premise in premises]
        if conclusion:
            if isinstance(conclusion, Proposition):
                self.conclusion = conclusion
            else:
                self.conclusion = Proposition(conclusion)

        self.reverse_values = reverse
        if labels:
            if len(labels) != 2:
                print(CUSTOM_LABEL_EXCEED_LENGTH)
                exit()
            if labels[0] == labels[1]:
                print(CUSTOM_LABEL_IDENTICAL)
                exit()
            self.labels = [char for char in labels]

        # collect all variables
        variables = []
        # loop through all Proposition objects to get vars
        for sentence in self.all_propositions():
            for variable in sentence.source.variables:
                if variable not in variables:
                    variables.append(variable)
        variables = sorted(variables)
        self.variables = variables

        # make all cases
        # default order: F (top) -> T (bottom)
        cases = list(product([0, 1], repeat=len(variables)))
        if reverse:
            cases = cases[::-1]
        self.cases = cases

        # make table with variable columns
        self.truth_table = OrderedDict()

        for index, var in enumerate(variables):
            for case in cases:
                value = case[index]
                if var in self.truth_table.keys():
                    # key already exists, add variable to table
                    self.truth_table[var].append(value)
                else:
                    # add new key to table
                    self.truth_table[var] = [value]

        # get all propositions
        sentences = self.all_propositions()
        # for each sentence
        for sentence in sentences:
            # for each case (row)
            s = sentence
            if isinstance(s, Proposition):
                s = s.source
            if s not in self.truth_table.keys():
                # add ONLY IF it's not already added to the truth table
                for case in cases:
                    namespace = {var: case[index]
                                for index, var in enumerate(variables)}
                    # evaluate result using eval
                    result = eval(sentence.source.binary, {}, namespace)
                    if sentence.source in self.truth_table.keys():
                        # key already exists, add variable to table
                        self.truth_table[sentence.source].append(result)
                    else:
                        # add new key to table
                        self.truth_table[sentence.source] = [result]


    # preprocess and output
    def output(self, check_handler: Callable[[list[str]], bool] | None = None,
               filename: str | None = None):
        # all COMPILED sentences
        sentences = self.all_sentences(variables=True)

        table_data = OrderedDict()

        for sentence in sentences:
            if isinstance(sentence, str):
                table_data[sentence] = self.truth_table[sentence]
            else:
                display_sentence = sentence.source.display_text()
                table_data[display_sentence] = self.truth_table[sentence.source]

        if check_handler:
            # go through each row and add a column of check/cross mark
            # get headers
            headers = list(table_data.keys())
            # add a check/cross column
            table_data[MARK_COLUMN] = []
            # for each row
            for row in range(len(self.cases)):
                # get values of each column in the row
                values = [table_data[col][row] for col in headers]
                # add check/cross mark using the given predicate
                mark = red(CROSS_MARK)
                if check_handler(values):
                    mark = green(CHECK_MARK)
                mark = f" {bold(mark)} "
                table_data[MARK_COLUMN].append(mark)

        output_table(table_data, labels=self.labels, filepath=filename)

    # whether the argument is valid

    def is_valid(self, print_countermodel: bool = False) -> bool:
        propositions = self.all_sentences(variables=True)
        for row in range(len(self.cases)):
            consistent = True
            for p in propositions:
                # if it is a premise
                if consistent and p in self.premises:
                    # if any premise is false, skip the rest
                    p = p.source if isinstance(p, Proposition) else p
                    
                    if not self.truth_table[p][row]:
                        consistent = False
                        # break  # actually, don't skip just yet
                        # have to keep going until we get the conclusion
                
                if p == self.conclusion:
                    p = p.source if isinstance(p, Proposition) else p
                    conclusion = self.truth_table[p][row]

            # look at conclusion only if the premises are consistent
            if consistent and not conclusion:
                if print_countermodel:
                    # a counterexample is found when conclusion is false
                    countermodel = []
                    for variable, value in zip(self.variables, self.cases[row]):
                        if self.labels:
                            # custom labels
                            value = self.labels[value]
                        countermodel.append(f"{variable} = {value}")
                    countermodel = ', '.join(countermodel)
                    print(bold(yellow("Countermodel:", countermodel)))

                return False

        return True

    # whether the set of propositions are all equivalent

    def all_equivalent(self, verbose: bool = False) -> bool:
        # test cases:
        # (1 iff 2)
        # (1 iff 3)
        # (1 iff 4)
        # ...
        statements = self.all_propositions()
        tests = list(combinations(statements, 2))

        all_equivalent = True

        results = OrderedDict()
        # row: key, value
        # 2 columns
        # add a header row for display
        results['Tests'] = ''
        pass_count = 0

        # test all cases using biconditional
        for index, propositions in enumerate(tests):
            display_expr = [p.source.display_text() for p in propositions]
            # join with equivalence sign
            display_expr = EQUIV_SYMBOL.join(display_expr)

            if verbose:
                # display test cases
                prefix = bold(yellow(f"Test {index + 1}:"))
                print(prefix, display_expr)

            # test if the two are of the same form
            # NOTE: no longer needed, assumption: no commutative/associative-equivalent statement
            # structs = list(map(lambda p: p.source.struct, propositions))
            # if equivalent_form(*structs):
            #     # no need to use the biconditional
            #     results[display_expr] = f" {bold(green(CHECK_MARK))} "
            #     pass_count += 1
            #     print()
            #     continue

            if verbose:
                # load test case into an argument object
                arguments = Argument(propositions,
                                     labels=self.labels)

                # print truth table with checkmarks
                arguments.output(check_handler=arguments.CHECK_EQUIVALENT)

                print()

            # test equivalence using biconditional
            statement = list(map(lambda p: p.statement, propositions))
            statement = ' iff '.join(statement)

            statement = Proposition(statement)

            # add test results regardless
            if statement.is_tautology():
                results[display_expr] = f" {bold(green(CHECK_MARK))} "
                pass_count += 1
            else:
                results[display_expr] = f" {bold(red(CROSS_MARK))} "
                all_equivalent = False

        # print a conclusion under verbose mode
        if verbose:
            # get max size
            size = len(max(results.keys(), key=lambda r: len(r)))

            top_border = [BOX_OUTER_HLINE * size, BOX_OUTER_HLINE * 3]
            top_border = BOX_TOP_T.join(top_border)
            top_border = BOX_TOP_LEFT + top_border + BOX_TOP_RIGHT

            row_template = ['{:^' + str(size) + '}', '{:^3}']
            row_template = BOX_INNER_VLINE.join(row_template)
            row_template = BOX_OUTER_VLINE + row_template + BOX_OUTER_VLINE

            row_separator = [BOX_INNER_HLINE * size, BOX_INNER_HLINE * 3]
            row_separator = BOX_JOINT.join(row_separator)
            row_separator = BOX_LEFT_T + row_separator + BOX_RIGHT_T
            row_separator = '\n' + row_separator + '\n'

            bottom_border = [BOX_OUTER_HLINE * size, BOX_OUTER_HLINE * 3]
            bottom_border = BOX_BOTTOM_T.join(bottom_border)
            bottom_border = BOX_BOTTOM_LEFT + bottom_border + BOX_BOTTOM_RIGHT

            rows: list[str] = []
            for key, value in results.items():
                rows.append(row_template.format(key, value))

            # summary table
            count_msg = "All" if all_equivalent else f"{pass_count}/{len(tests)}"
            print(bold(yellow('Summary:')), f"{count_msg} tests passed.")
            print(top_border)
            print(row_separator.join(rows))
            print(bottom_border)

        return all_equivalent

    # predicate: check if all sentences are equivalent

    def CHECK_EQUIVALENT(self, values: list[str]) -> bool:
        # get the headers from the truth table
        # this would correspond to the row values
        headers = list(self.truth_table.keys())
        # get all sentences (of concern)
        propositions = self.all_propositions()
        sentence_values = []
        for p in propositions:
            # get index of sentence
            sentence_index = headers.index(p.source)
            sentence_values.append(values[sentence_index])
        # it would be of length 1 if all same
        return len(set(sentence_values)) == 1

    # predicate: check counterexamples (x-mark)

    def X_COUNTERMODEL(self, values: list[str]) -> bool:
        # get the headers from the truth table
        # this would correspond to the row values
        headers = list(self.truth_table.keys())
        # get index of conclusion
        # it is NOT safe to assume that
        # the conclusion is always the last column
        conclusion_index = headers.index(self.conclusion.source)
        conclusion = values[conclusion_index]

        premise_values = []
        for premise in self.premises:
            # get index of premise
            premise_index = headers.index(premise.source)
            premise_values.append(values[premise_index])

        consistent_premises = all(premise_values)
        # check only when premises -> conclusion is true
        return not consistent_premises or conclusion
