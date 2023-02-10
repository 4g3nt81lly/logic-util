from helpers import *

s1 = parsed(standardize_notations('(b -> a)'))
s2 = parsed(standardize_notations('((((b -> a))))'))
print(s1, s2)
print(equivalent_structs(s1, s2))
