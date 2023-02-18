from collections import OrderedDict
from itertools import product, combinations
from typing import Dict, Callable

from constants import *
from helpers import *


class Proposition:
    # original statement (input)
    statement: str
    # parsed structure (nested list)
    structs: list
    # compiled statement (executable expression)
    source: str
    # all variables
    variables: list
    # all cases
    cases: list
    # constituent sentences
    constituents: list
    # parsed structures of constituents
    constituent_structs: list
    # truth table
    truth_table: Dict[str, list] = {}

    # custom labels for TF
    labels: list[str] | None = None
    # reverse truth values?
    reverse_values: bool

    # truth values of the proposition
    def values(self):
        return self.truth_table[self.source]

    # dict: truth values of the proposition
    def row(self) -> Dict[str, list[str]]:
        return {standardize_notations(self.source, display=True): self.values()}

    def __init__(self, statement: str,
                 labels: str | None = None,
                 reverse: bool = False):
        self.statement = statement
        self.reverse_values = reverse
        if labels:
            if len(labels) != 2:
                print(CUSTOM_LABEL_EXCEED_LENGTH)
                exit()
            if labels[0] == labels[1]:
                print(CUSTOM_LABEL_IDENTICAL)
                exit()
            self.labels = [char for char in labels]

        # parse and get structure (nested list)
        try:
            parsed_struct = parsed(statement)
        except AssertionError as err:
            print(err)
            exit()
        except SyntaxError:
            print('Expression:', f"'{statement}'")
            print(UNMATCHED_PARENTHESES)
            exit()
        except Exception as err:
            print('Expression:', f"'{statement}'")
            print(UNEXPECTED_ERROR, err)
            exit()

        if parsed_struct == []:
            print(NULL_STATEMENT)
            exit()

        self.structs = parsed_struct

        # compile statement
        src_object = compile(parsed_struct)
        (source, variables, atomic_sentences, atomic_structs) = src_object
        self.source = source
        self.variables = variables
        self.constituents = atomic_sentences
        self.constituent_structs = atomic_structs

        # make all cases
        # default order: F (top) -> T (bottom)
        cases = list(product([0, 1], repeat=len(variables)))
        if reverse:
            cases = cases[::-1]
        self.cases = cases
        # make table with variable columns
        self.truth_table = OrderedDict({var: [] for var in variables})
        for index, var in enumerate(variables):
            for case in cases:
                self.truth_table[var].append(case[index])
        # fill in atomic sentences columns
        self.truth_table.update({s: [] for s in atomic_sentences})
        # for each atomic sentences
        for sentence in atomic_sentences:
            # for each case (row)
            for case in cases:
                namespace = {var: case[index]
                             for index, var in enumerate(variables)}
                # evaluate result using eval
                result = eval(sentence, {}, namespace)
                # add to table
                self.truth_table[sentence].append(result)

    # an negated instance of the proposition
    def negated(self):
        return Proposition(f'~({self.statement})',
                           reverse=self.reverse_values)

    # whether the proposition is a tautology
    def is_tautology(self, column: str | int | None = None) -> bool:
        if column:
            if isinstance(column, str):
                return all(self.truth_table[column])
            elif isinstance(column, int):
                return all(self.truth_table[self.constituents[column]])
        return all(self.values())

    # preprocess and output
    def output(self, check_handler: Callable[[list[str]], bool] | None = None,
               no_atoms: bool = False,
               filename: str | None = None):

        table_data = OrderedDict()

        for col, values in self.truth_table.items():
            if col in self.variables:
                table_data[col] = values
            else:
                display_sentence = standardize_notations(col, display=True)
                if no_atoms:
                    # no reference columns, just the statement itself
                    if col == self.source:
                        table_data[display_sentence] = values
                else:
                    if col in self.constituents:
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

        output_table(table_data, labels=self.labels, filename=filename)


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
    truth_table: Dict[str, list]

    # custom labels for TF
    labels: list[str] | None = None
    # reverse truth values?
    reverse_values: bool

    # get all premises (source)
    def all_premises(self) -> list[str]:
        return [p.source for p in self.premises]

    # get all Proposition objects
    def all_propositions(self) -> list[Proposition]:
        return self.premises + ([self.conclusion] if self.conclusion else [])

    # get all sentences: premises + conclusion (source)
    def all_sentences(self, variables: bool = False, conclusion: bool = True) -> list[str]:
        sentences = self.all_premises()
        if variables:
            sentences = self.variables + sentences
        if conclusion and self.conclusion:
            sentences.append(self.conclusion.source)
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
            # check if conclusion is a Proposition object
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
        variables = self.premises[0].variables[:]  # make a copy
        # loop through all Proposition objects
        # and NOT the compiled strings
        for sentence in self.all_propositions():
            for variable in sentence.variables:
                if variable not in variables:
                    variables.append(variable)
        self.variables = variables

        # make all cases
        # default order: F (top) -> T (bottom)
        cases = list(product([0, 1], repeat=len(variables)))
        if reverse:
            cases = cases[::-1]
        self.cases = cases
        # make table with variable columns
        self.truth_table = OrderedDict({var: [] for var in variables})
        for index, var in enumerate(variables):
            for case in cases:
                self.truth_table[var].append(case[index])

        # get all sentences
        sentences = self.all_sentences()
        # fill in sentences columns
        self.truth_table.update({s: [] for s in sentences})
        # for each sentence
        for sentence in sentences:
            # for each case (row)
            for case in cases:
                namespace = {var: case[index]
                             for index, var in enumerate(variables)}
                # evaluate result using eval
                result = eval(sentence, {}, namespace)
                # add to table
                self.truth_table[sentence].append(result)

    # preprocess and output
    def output(self, check_handler: Callable[[list[str]], bool] | None = None,
               filename: str | None = None):
        # all COMPILED sentences
        sentences = self.all_sentences(variables=True)

        table_data = OrderedDict()

        for col, values in self.truth_table.items():
            if col in sentences:
                display_sentence = standardize_notations(col, display=True)
                table_data[display_sentence] = values

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

        output_table(table_data, labels=self.labels, filename=filename)

    # whether the argument is valid

    def is_valid(self) -> bool:
        sentences = self.all_sentences(variables=True)
        premises = self.all_premises()
        # for each premise
        for row in range(len(self.cases)):
            consistent = True
            for sentence in sentences:
                # if it is a premise
                if sentence in premises:
                    # if any premise is false, skip the rest
                    if not self.truth_table[sentence][row]:
                        consistent = False
                        # break  # actually, don't skip just yet
                        # have to keep going until we find the conclusion
                if sentence == self.conclusion.source:
                    conclusion = self.truth_table[sentence][row]
            # look at conclusion only if the premises are consistent
            if consistent and not conclusion:
                # a counterexample is found when conclusion is false
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
            display_expr = [standardize_notations(p.source, display=True)
                            for p in propositions]
            # join with equivalence sign
            display_expr = ' \u2261 '.join(display_expr)

            if verbose:
                # display test cases
                prefix = bold(yellow(f"Test {index + 1}:"))
                print(prefix, display_expr)

            # test if the two are of the same form
            structs = list(map(lambda p: p.structs, propositions))
            if equivalent_form(*structs):
                # no need to use the biconditional
                results[display_expr] = f" {bold(green(CHECK_MARK))} "
                pass_count += 1
                print()
                continue

            if verbose:
                # load test case into an argument object
                arguments = Argument(propositions,
                                     labels=self.labels)

                # print truth table with checkmarks
                arguments.output(check_handler=arguments.CHECK_EQUIVALENT)

                print()

            # test equivalence using biconditional
            sources = list(map(lambda p: p.source, propositions))
            statement = ' iff '.join(sources)

            statement = Proposition(statement,
                                    labels=self.labels)

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
        sentences = self.all_sentences()
        sentence_values = []
        for sentence in sentences:
            # get index of sentence
            sentence_index = headers.index(sentence)
            sentence_values.append(values[sentence_index])
        # it would be of length 1 if all same
        return len(set(sentence_values)) == 1

    # predicate: check counterexamples (x-mark)

    def X_COUNTEREXAMPLE(self, values: list[str]) -> bool:
        # get the headers from the truth table
        # this would correspond to the row values
        headers = list(self.truth_table.keys())
        # get index of conclusion
        # it is NOT safe to assume that
        # the conclusion is always the last column
        conclusion_index = headers.index(self.conclusion.source)
        conclusion = values[conclusion_index]
        # get all premises
        premises = self.all_premises()
        premise_values = []
        for premise in premises:
            # get index of premise
            premise_index = headers.index(premise)
            premise_values.append(values[premise_index])

        consistent_premises = all(premise_values)
        # check only when premises -> conclusion is true
        return not consistent_premises or conclusion
