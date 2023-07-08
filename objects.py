from itertools import product, combinations
from functools import cached_property

from typing import List, Optional, Literal

from constants import *
from helpers import *
from fol import *

class Config:
    def __init__(self,
                 reverse: bool = False,
                 labels: Optional[str] = None,
                 atoms: bool = True,
                 log_countermodel: bool = False,
                 **kwargs):
        self.reverse = reverse
        self.labels = labels
        self.atoms = atoms
        self.log_countermodel = log_countermodel
        # extra keyword arguments in kwargs are not used temporarily

    def __repr__(self) -> str:
        return str(self.__dict__)


class Proposition:
    def __init__(self, sentence: str | Token,
                 config: Config = Config()):
        self.config = config
        if isinstance(sentence, Token):
            # pre-compiled token
            self.token = sentence
        else:
            assert isinstance(sentence, str) and sentence != '', NULL_SENTENCE
            sentence = standardize_notations(sentence.strip())
            try:
                self.parsed = parse(sentence)
            except SyntaxError:
                print(UNMATCHED_PARENTHESES)
                exit()
            self.compile()

    def __repr__(self) -> str:
        return str(self.token)

    def __eq__(self, __value) -> bool:
        if isinstance(__value, Proposition):
            return self.token == __value.token
        elif isinstance(__value, str):
            return str(self) == __value
        return False

    @cached_property
    def variables(self) -> List[str]:
        return self.token.variables

    @cached_property
    def sentences(self) -> List[Token]:
        return self.token.sentences

    def compile(self):
        def _compile(s: List) -> Token:
            # variables
            if isinstance(s, str):
                assert good_name(s), f"Bad name: '{s}'\n{NAME_HELP}"
                return Variable(s)

            # expressions
            assert isinstance(s, list) and len(s) > 0, NULL_SENTENCE
            # for error

            def expr(s: List) -> str:
                s = [expr(i) if isinstance(i, list) else i for i in s]
                return f"'{' '.join(s)}'"

            if len(s) == 1:
                # ((...)) OR ({variable})
                # get rid of encapsulating parentheses
                arg: str | List = s[0]
                return _compile(arg)
            elif len(s) == 2:
                # (not (...))
                assert s[0] == 'not', MISSING_COMPONENTS + f"{expr(s)}."
                arg: str | List = s[1]
                token: Token = _compile(arg)
                if type(token) is Negation:
                    # apply double negation equivalence rule
                    return token.negated
                return Negation(token)
            elif len(s) > 2:
                # any other forms
                initializers = {'and': Conjunction,
                                'or': Disjunction,
                                'xor': XDisjunction,
                                '->': Implication,
                                'iff': Biconditional}
                for operator in OPS_BY_PRECEDENCE:
                    try:
                        index = s.index(operator)
                        assert index > 0, MISSING_COMPONENTS + f"{expr(s)}."
                    except ValueError:
                        continue

                    lhs: Token = _compile(s[:index])
                    rhs: Token = _compile(s[index + 1:])

                    token: Token = initializers[operator](lhs, rhs)

                    # get rid of unnecessary parentheses
                    if operator in ASSOCIATIVE_OPERATORS:
                        # and, or, xor, iff
                        assert isinstance(token, NaryExpression)
                        if type(lhs) is type(token):
                            token.operands = lhs.operands + token.operands[1:]
                        if type(rhs) is type(token):
                            token.operands = token.operands[:-1] + rhs.operands
                    return token

                # no N-ary operators, then it must be multiple negations
                assert s[0] == 'not', \
                    f"Expected a NOT operator but found non-operator token '{s[0]}'."
                return _compile(['not', s[1:]])
            else:
                # unless in the event of a single-event upset (SEU), it should NEVER get here
                raise Exception(UNEXPECTED_ERROR)
        self.token = _compile(self.parsed)

    @cached_property
    def truth_table(self) -> List[List[str | int]]:
        variables = self.variables
        cases = list(product([0, 1], repeat=len(variables)))
        if self.config.reverse:
            cases = cases[::-1]
        # sentences of interest
        if self.config.atoms:
            # get unique constituent sentences
            sentences = self.sentences
            # o o o o ... o o x
            for i in range(len(sentences) - 1):
                # o [o] o o ... o o o
                # x  x  o o ... o o o
                for j in range(i + 1, len(sentences)):
                    if sentences[i] == sentences[j]:
                        # mark the later for removal
                        sentences[j] = None
            sentences = [s for s in sentences if s is not None]
        else:
            sentences = [self.token]
        # truth table
        table: List[List[str | int]] = [variables + [display(s) for s in sentences]]
        for case in cases:
            # variable columns
            row = list(case)
            # make key-value variable assignments
            assignments = dict(zip(variables, case))
            # evalute for each sentence and at to row correspondingly
            for sentence in sentences:
                truth_value = sentence.evaluate(**assignments)
                row.append(truth_value)
            # add row to table
            table.append(row)
        return table

    def output_truth_table(self, filepath: Optional[str] = None):
        table = self.truth_table
        output_table(table, labels=self.config.labels, filepath=filepath)
    
    def is_tautology(self) -> bool:
        table = self.truth_table
        return all(row[-1] for row in table[1:])
    
    def is_contradiction(self) -> bool:
        table = self.truth_table
        return not any(row[-1] for row in table[1:])


class Argument:
    def __init__(self, premises: List[Proposition | str],
                 conclusion: Optional[Proposition | str] = None,
                 config: Config = Config()):
        assert len(premises) > 0
        self.premises: List[Proposition] = []
        for premise in premises:
            if isinstance(premise, Proposition):
                p = premise
            elif isinstance(premise, str):
                p = Proposition(premise)
            else:
                raise Exception(UNEXPECTED_ERROR)
            self.premises.append(p)
        # avoid having no such attribute
        self.conclusion = None
        if conclusion:
            if isinstance(conclusion, Proposition):
                c = conclusion
            elif isinstance(conclusion, str):
                c = Proposition(conclusion)
            else:
                raise Exception(UNEXPECTED_ERROR)
            self.conclusion = c
        self.config = config
    
    @cached_property
    def variables(self) -> List[str]:
        variables: List[str] = []
        sentences = self.sentences
        for sentence in sentences:
            variables += sentence.variables
        return unique(variables)

    @property
    def sentences(self) -> List[Proposition]:
        return self.premises + ([self.conclusion] if self.conclusion else [])

    def truth_table(self, annotate: Optional[Literal['validity', 'equivalence']] = None) -> List[List[str | int]]:
        variables = self.variables
        cases = list(product([0, 1], repeat=len(variables)))
        if self.config.reverse:
            cases = cases[::-1]
        # sentences of interest
        sentences = self.sentences
        # remove sentences that are variables to account for the case
        # in which the conclusion of an argument is a single variable
        sentences = [s for s in sentences if all(s != var for var in variables)]

        # truth table
        table: List[List[str | int]] = [variables + [display(s) for s in sentences]]
        # get premises and conclusion columns
        header: List[str] = table[0]
        prem_col_indices: List[int] = [header.index(display(s)) for s in self.premises]
        if self.conclusion:
            concl_col_index: int = header.index(display(self.conclusion))

        if annotate and MARK_COLUMN not in table[0]:
            table[0].append(MARK_COLUMN)
        
        for case in cases:
            # variable columns
            row = list(case)
            # make key-value variable assignments
            assignments = dict(zip(variables, case))
            # evalute for each sentence and at to row correspondingly
            for sentence in sentences:
                truth_value = sentence.token.evaluate(**assignments)
                row.append(truth_value)
            
            # get premises and conclusion values
            premises = [row[i] for i in prem_col_indices]

            # add annotation marks
            if annotate == 'validity':
                conclusion = row[concl_col_index]
                mark = green(CHECK_MARK)
                # mark cross for countermodels
                if all(premises) and not conclusion:
                    mark = red(CROSS_MARK)
                mark = f" {bold(mark)} "
                row.append(mark)
            elif annotate == 'equivalence':
                mark = red(CROSS_MARK)
                # mark check for all equivalent rows (all 1/0s)
                if all(premises) or not any(premises):
                    mark = green(CHECK_MARK)
                mark = f" {bold(mark)} "
                row.append(mark)
            # add row to table
            table.append(row)
        return table
    
    def output_truth_table(self, annotate: Optional[Literal['validity', 'equivalence']] = None,
                           filepath: Optional[str] = None):
        table = self.truth_table(annotate=annotate)
        output_table(table, labels=self.config.labels, filepath=filepath)

    def is_valid(self) -> bool:
        table = self.truth_table(annotate='validity')
        # for each row, excluding the header
        for row in table[1:]:
            if CROSS_MARK in row[-1]:
                # countermodel marked
                if self.config.log_countermodel:
                    # get first N columns as variables
                    var_cols = row[:len(self.variables)]
                    # build countermodel
                    countermodel = [f"{var} = {val}"
                                    for var, val in zip(self.variables, var_cols)]
                    countermodel = ', '.join(countermodel)
                    print(bold(yellow("Countermodel:", countermodel)))
                return False
        # premises -> conclusion is tautology
        return True
    
    def test_equivalence(self, mode: Literal['default', 'paired'] = 'default') -> bool:
        sentences: List[Proposition] = self.premises

        if mode == 'default':
            # direct test: if all sentences are equivalent
            tests: List[Biconditional] = []
            for sentence in sentences[1:]:
                biconditional = Biconditional(sentences[0].token, sentence.token)
                tests.append(Proposition(biconditional))
            # test if all test cases are tautologies
            return all(test.is_tautology() for test in tests)
        elif mode == 'paired':
            # paired (combinations) test
            tests = list(combinations(sentences, 2))
            all_equivalent = True
            summary_table: List[List[str]] = [['Tests', MARK_COLUMN]]
            pass_count = 0
            for index, test in enumerate(tests):
                # test if the two sentences are equivalent using biconditional
                p1, p2 = test
                display_expr = EQUIV_SYMBOL.join([display(p1), display(p2)])
                # log test case
                print(
                    bold(yellow(f"Test {index + 1}:")), display_expr
                )
                # print truth table with markings
                # the truth table will inherit configs from current object
                Argument(test, config=self.config).output_truth_table(annotate='equivalence')
                print()

                biconditional = Proposition(Biconditional(p1.token, p2.token))
                is_equivalent = biconditional.is_tautology()
                if is_equivalent:
                    summary_table.append(
                        [display_expr, f" {bold(green(CHECK_MARK))} "]
                    )
                    pass_count += 1
                else:
                    summary_table.append(
                        [display_expr, f" {bold(red(CROSS_MARK))} "]
                    )
                    all_equivalent = False

            # summary table
            count_msg = 'All' if all_equivalent else f"{pass_count}/{len(tests)}"
            print(bold(yellow('Summary:')), f"{count_msg} tests passed.")
            output_table(summary_table)

            return all_equivalent
        else:
            # unknown mode: should NEVER get here
            raise Exception(UNEXPECTED_ERROR)

