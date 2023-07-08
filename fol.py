from itertools import permutations

from typing import List

from helpers import unique

class Token:
    pass


class Token:
    @property
    def display_text(self) -> str: pass

    @property
    def source(self) -> str: pass

    @property
    def variables(self) -> List[str]: pass

    @property
    def sentences(self) -> List[Token]:
        return []

    def __repr__(self) -> str:
        return self.display_text

    def evaluate(self, **kwargs) -> int:
        return eval(self.source, {}, kwargs)


class Variable(Token):
    def __init__(self, name: str):
        self.name = name

    @property
    def display_text(self) -> str:
        return self.name

    @property
    def source(self) -> str:
        return self.name

    @property
    def variables(self) -> List[str]:
        return [self.name]

    def __eq__(self, __value) -> bool:
        if isinstance(__value, Variable):
            return self.name == __value.name
        return False


class Negation(Token):
    def __init__(self, negated: Token):
        self.negated = negated

    @property
    def display_text(self) -> str:
        return f"¬{self.negated.display_text}"

    @property
    def source(self) -> str:
        return f"(1&~{self.negated.source})"

    @property
    def variables(self) -> List[str]:
        return unique(self.negated.variables)

    @property
    def sentences(self) -> List[Token]:
        return self.negated.sentences + [self]

    def __eq__(self, __value) -> bool:
        if isinstance(__value, Negation):
            return self.negated == __value.negated
        return False


class BinaryExpression(Token):
    def __init__(self, operator: str, left: Token, right: Token):
        self.operator = operator
        self.left = left
        self.right = right

    @property
    def display_text(self) -> str:
        return f"({self.left.display_text} {self.operator} {self.right.display_text})"

    @property
    def variables(self) -> List[str]:
        return unique(self.left.variables + self.right.variables)

    @property
    def sentences(self) -> List[Token]:
        return self.left.sentences + self.right.sentences + [self]


class Implication(BinaryExpression):
    symbol = u'\u2192'

    def __init__(self, left: Token, right: Token):
        super().__init__(Implication.symbol, left, right)

    @property
    def source(self) -> str:
        return f"({self.left.source}^1|{self.right.source})"

    def __eq__(self, __value) -> bool:
        if isinstance(__value, Implication):
            return self.left == __value.left and self.right == __value.right
        return False


class Biconditional(BinaryExpression):
    symbol = u'\u2194'

    def __init__(self, left: Token, right: Token):
        super().__init__(Biconditional.symbol, left, right)

    @property
    def source(self) -> str:
        return f"({self.left.source}^1^{self.right.source})"

    def __eq__(self, __value) -> bool:
        if isinstance(__value, Biconditional):
            return (self.left == __value.left and self.right == __value.right) or \
                (self.right == __value.left and self.left == __value.right)
        return False


class NaryExpression(Token):
    def __init__(self, operator: str, symbol: str, *args: List[Token]):
        self.operator = operator
        self.symbol = symbol
        self.operands = args

    def __eq__(self, __value) -> bool:
        if type(self) is type(__value):
            # NOTE: need a better solution, it grows exponentially for more operands
            arrangments = permutations(
                range(len(self.operands)), len(self.operands))
            for arrangment in arrangments:
                for index1, index2 in enumerate(arrangment):
                    if self.operands[index1] != __value.operands[index2]:
                        break
                else:
                    # found an equivalent arrangement
                    return True
        return False

    @property
    def display_text(self) -> str:
        symbol = f" {self.symbol} "
        return f"({symbol.join([operand.display_text for operand in self.operands])})"

    @property
    def source(self) -> str:
        sources = [operand.source for operand in self.operands]
        return f"({self.operator.join(sources)})"

    @property
    def variables(self) -> List[str]:
        all_variables = []
        for operand in self.operands:
            all_variables += operand.variables
        return unique(all_variables)

    @property
    def sentences(self) -> List[Token]:
        all_sentences = []
        for operand in self.operands:
            all_sentences += operand.sentences
        return all_sentences + [self]


class Conjunction(NaryExpression):
    operator = '&'
    symbol = u'\u2227'

    def __init__(self, *args: List[Token]):
        super().__init__(Conjunction.operator, Conjunction.symbol, *args)


class Disjunction(NaryExpression):
    operator = '|'
    symbol = u'\u2228'

    def __init__(self, *args: List[Token]):
        super().__init__(Disjunction.operator, Disjunction.symbol, *args)


class XDisjunction(NaryExpression):
    operator = '^'
    symbol = u'\u22bb'

    def __init__(self, *args: List[Token]):
        super().__init__(XDisjunction.operator, XDisjunction.symbol, *args)
