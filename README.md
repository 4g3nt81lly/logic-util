# ✖️ logic-util
An easy-to-use utility for propositional logic written in vanilla Python.

## 🤔&ensp;Why?
Let's admit it, anyone would find equivalency/validity tests with truth tables tedious, especially when it comes to something like this:

$(a\lor\neg c)\veebar(\neg b\lor c)\equiv\left(\neg a\land(\neg b\to c))\lor(a\land\neg(b\to c)\right)$

(okay for those of who don't think this is a hard proof, you guys rock)

I grew weary of doing long-winded truth tables to verify if I had done a proof right, so I decided to write a tool that does the dirty work for me.

I use it occasionally to check if my "logic" is right, and I think it may benefit many propositional logic learners out there!

**Scenarios:**

1. You drew a truth table and wanted to see if you did it right.
2. You're done with quite a long proof and you want to see if your steps are right.
3. You need to show someone some "logic." (tutoring maybe?)
4. You need to check if your argument is valid before embarrassing yourself in front of your geeky friends. (this one's a bit far-fetched)
5. ~~You're too lazy to do your homework and you...~~ (uh no no)
6. And more... Really, you're only limited by your imagination...


## 🧩&ensp;Features
1. Draw and/or export a truth table **w/wo constituent sentences**.
2. Logical equivalency test for multiple propositional statements.
3. Validity test for logical arguments.
4. Light-weighted and no dependencies needed.
5. Fast and beautiful (okay-looking) output format.
6. More features are coming...

## 🛠️&ensp;Getting Ready
<details>
 <summary><h3 style="margin-top: .5em; margin-bottom: .25em;">&ensp;Working with source code</h3><br/>Windows-friendly.</summary>
 
 #### Install Python 3.8+
 Here I'm only showing Homebrew (but really, you can get it from anywhere, as long as it's legit):
 
 ```shell
 brew install python3
 ```
 
 #### Download source code
 Download the source code and decompress it.
 
 #### Done!
 You're all set! No dependencies whatsoever!  
 Feel free to do this and get started:
 
 ```shell
 cd /source/code/root
 python3 ./logic.py [...] # do this instead of ./logic-util
 ```
</details>
<details>
 <summary><h3 style="margin-top: .25em; margin-bottom: .25em;">&ensp;Working with binary</h3><br/>Sorry Windows users, you'll need the source code (for now). 😢</summary>
 
 #### Download binary
 Download the latest binary from [releases](https://github.com/4g3nt81lly/logic-util/releases).


 #### Change file mode
 You may need to change the file mode of `logic-util` to use it:
 ```shell
 cd /root/of/binary
 chmod +x ./logic-util
 ```
 
 #### Done!
 You're all set! No dependencies, not even Python!
</details>

### Requirements
- macOS<br/>**OR**
- Python 3.8+

## 🔨&ensp;Usage
### Supported Operators
|                              |  Operators        	                                              |
|------------------------------|------------------------------------------------------------------|
| **Negation**                 | `not`&ensp;`NOT`&ensp;`~`&ensp;`∼`&ensp;`¬`&ensp;`!`          	  |
| **(Inclusive) Disjunction**  | `or`&ensp;`OR`&ensp;`∨`&ensp;`\|`&ensp;`+`                       |
| **Conjunction**              | `and`&ensp;`AND`&ensp;`∧`&ensp;`&`&ensp;`*`&ensp;`⋅`             |
| **Implication**              | `to`&ensp;`->`&ensp;`→`&ensp;`⟹`&ensp;`⟶`&ensp;`⇒`              |
| **Bicondition**              | `iff`&ensp;`IFF`&ensp;`<->`&ensp;`↔`&ensp;`⇔`&ensp;`⟷`&ensp;`⟺` |
| **Exclusive Disjunction**    | `xor`&ensp;`XOR`&ensp;`⊻`&ensp;`⊕`&ensp;`⨁`&ensp;`^`             |

### Operator Precedence
(from high to low)
1. Parentheses: `()`
2. Negation (NOT)
3. Conjunction (AND)
4. (Inclusive) Disjunction (OR)
5. Exclusive Disjunction (XOR)
6. Implication (→)
7. Bicondition (↔︎)

---

### Making Truth Tables
The standard way of making a truth table for a proposition logic statement:
```shell
> ./logic-util make-table '(a or b) -> c'
┏━━━┯━━━┯━━━┯━━━━━━━┯━━━━━━━━━━━━━┓
┃ a │ b │ c │ a ∨ b │ (a ∨ b) → c ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 0 │ 0 │ 0 │   0   │      1      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 0 │ 0 │ 1 │   0   │      1      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 0 │ 1 │ 0 │   1   │      0      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 0 │ 1 │ 1 │   1   │      1      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 1 │ 0 │ 0 │   1   │      0      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 1 │ 0 │ 1 │   1   │      1      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 1 │ 1 │ 0 │   1   │      0      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ 1 │ 1 │ 1 │   1   │      1      ┃
┗━━━┷━━━┷━━━┷━━━━━━━┷━━━━━━━━━━━━━┛
```

> **Note**  
> Your statement should be wrapped in a pair of quotation marks `''` or `""`.

The rightmost column is the output column of the propositional statement $(a\lor b)\to c$.

By default, the truth table is drawn with columns for all the constituent atomic sentences ($a\lor b$ in this example). To suppress this behavior, use the flag `-n` or `--no-atoms`. Now, only the output column will be drawn:
```shell
> ./logic-util make-table '(a or b) -> c' -n
┏━━━┯━━━┯━━━┯━━━━━━━━━━━━━┓
┃ a │ b │ c │ (a ∨ b) → c ┃
┠───┼───┼───┼─────────────┨
┃ 0 │ 0 │ 0 │      1      ┃
┠───┼───┼───┼─────────────┨
┃ 0 │ 0 │ 1 │      1      ┃
┠───┼───┼───┼─────────────┨
┃ 0 │ 1 │ 0 │      0      ┃
┠───┼───┼───┼─────────────┨
┃ 0 │ 1 │ 1 │      1      ┃
┠───┼───┼───┼─────────────┨
┃ 1 │ 0 │ 0 │      0      ┃
┠───┼───┼───┼─────────────┨
┃ 1 │ 0 │ 1 │      1      ┃
┠───┼───┼───┼─────────────┨
┃ 1 │ 1 │ 0 │      0      ┃
┠───┼───┼───┼─────────────┨
┃ 1 │ 1 │ 1 │      1      ┃
┗━━━┷━━━┷━━━┷━━━━━━━━━━━━━┛
```
To use custom labels for truth values (e.g. F/T instead of 0/1), use the flag `-l` or `--labels` with an argument specifying the custom labels as such:
```shell
> ./logic-util make-table '(a or b) -> c' -l FT
┏━━━┯━━━┯━━━┯━━━━━━━┯━━━━━━━━━━━━━┓
┃ a │ b │ c │ a ∨ b │ (a ∨ b) → c ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ F │ F │   F   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ F │ T │   F   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ T │ F │   T   │      F      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ T │ T │   T   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ F │ F │   T   │      F      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ F │ T │   T   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ T │ F │   T   │      F      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ T │ T │   T   │      T      ┃
┗━━━┷━━━┷━━━┷━━━━━━━┷━━━━━━━━━━━━━┛
```
The argument is a **two-character** string in the format `[FALSE_LABEL][TRUE_LABEL]`.

To reverse the truth values (e.g. from `TTT` to `FFF` instead of `FFF` to `TTT`, like the convention for truth tables in [this book](https://www.google.ca/books/edition/Formal_Logic/iqvsjhvZCgcC?hl=en&gbpv=0)[^1]), use the flag `-r` or `--reverse`:
```shell
> ./logic-util make-table '(a or b) -> c' -l FT -r
┏━━━┯━━━┯━━━┯━━━━━━━┯━━━━━━━━━━━━━┓
┃ a │ b │ c │ a ∨ b │ (a ∨ b) → c ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ T │ T │   T   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ T │ F │   T   │      F      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ F │ T │   T   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ T │ F │ F │   T   │      F      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ T │ T │   T   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ T │ F │   T   │      F      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ F │ T │   F   │      T      ┃
┠───┼───┼───┼───────┼─────────────┨
┃ F │ F │ F │   F   │      T      ┃
┗━━━┷━━━┷━━━┷━━━━━━━┷━━━━━━━━━━━━━┛
```

Finally, to export the truth table to a `.csv` file, use the flag `-o` or `--output` with an argument specifying the location:
```shell
> ./logic-util make-table '(a or b) -> c' -o ~/Desktop/output.csv
```
Specifying a file extension is _optional_, the utility automatically handles it for you! If no file name is provided, it will be saved at the specified location as `output.csv` by default.

#### Interactive Mode
Alternatively, if no statement is provided as an argument to `make-table`, the utility will enter **interactive mode** with the given options.
```shell
> ./logic-util make-table [OPTIONS]
Enter a statement: ▊
```
Enter a propositional statement to make a truth table out of it. You can do this as many time as you want.

To exit, hit <kbd>Ctrl</kbd> + <kbd>C</kbd>, <kbd>Ctrl</kbd> + <kbd>D</kbd>, or return without any input.

<details>
 <summary><strong>&ensp;Example scenario</strong>: Export multiple truth tables efficiently.</summary>
 <br/>

 ```
   > ./logic-util make-table -l FT -o ~/Desktop/output
   Enter a statement: (a or b) -> c
   Enter a statement: (a and b) -> c
   Enter a statement: (a iff b) or c
   Enter a statement: ▊
 ```
The truth tables will be saved directly to your specified location (they won't be printed in Terminal), you'll now see `output.csv`, `output-1.csv`, and `output-2.csv` with respective truth tables at `~/Desktop`.
</details>

---

### Checking Logical Equivalence
To test if two propositional logic statements are logically equivalent, use the `check-equivalence` keyword:
```shell
> ./logic-util check-equivalence '~(a or b)' '~a and ~b'

1. ¬(a ∨ b)
2. ¬a ∧ ¬b

┏━━━┯━━━┯━━━━━━━━━━┯━━━━━━━━━┯━━━┓
┃ a │ b │ ¬(a ∨ b) │ ¬a ∧ ¬b │   ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 0 │ 0 │    1     │    1    │ ✓ ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 0 │ 1 │    0     │    0    │ ✓ ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 1 │ 0 │    0     │    0    │ ✓ ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 1 │ 1 │    0     │    0    │ ✓ ┃
┗━━━┷━━━┷━━━━━━━━━━┷━━━━━━━━━┷━━━┛

✓ The statements are logically equivalent!
```
Or even multiple statements:
```shell
> ./logic-util check-equivalence '~(a or b)' '~a and ~b' '~(~a -> b)' '~(a and (a or b) or b)'

1. ¬(a ∨ b)
2. ¬a ∧ ¬b
3. ¬(¬a → b)
4. ¬((a ∧ (a ∨ b)) ∨ b)

┏━━━┯━━━┯━━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━┯━━━┓
┃ a │ b │ ¬(a ∨ b) │ ¬a ∧ ¬b │ ¬(¬a → b) │ ¬((a ∧ (a ∨ b)) ∨ b) │   ┃
┠───┼───┼──────────┼─────────┼───────────┼──────────────────────┼───┨
┃ 0 │ 0 │    1     │    1    │     1     │          1           │ ✓ ┃
┠───┼───┼──────────┼─────────┼───────────┼──────────────────────┼───┨
┃ 0 │ 1 │    0     │    0    │     0     │          0           │ ✓ ┃
┠───┼───┼──────────┼─────────┼───────────┼──────────────────────┼───┨
┃ 1 │ 0 │    0     │    0    │     0     │          0           │ ✓ ┃
┠───┼───┼──────────┼─────────┼───────────┼──────────────────────┼───┨
┃ 1 │ 1 │    0     │    0    │     0     │          0           │ ✓ ┃
┗━━━┷━━━┷━━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━┷━━━┛

✓ The statements are logically equivalent!
```
If you wish to see truth table for each test combination, set the mode using the flag `-m` or `--mode` to `paired`:
```shell
> ./logic-util check-equivalence '~(a or b)' '~a and ~b' '~(a -> b)' -m paired

1. ¬(a ∨ b)
2. ¬a ∧ ¬b
3. ¬(a → b)

Test 1: ¬(a ∨ b) ≡ ¬a ∧ ¬b
┏━━━┯━━━┯━━━━━━━━━━┯━━━━━━━━━┯━━━┓
┃ a │ b │ ¬(a ∨ b) │ ¬a ∧ ¬b │   ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 0 │ 0 │    1     │    1    │ ✓ ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 0 │ 1 │    0     │    0    │ ✓ ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 1 │ 0 │    0     │    0    │ ✓ ┃
┠───┼───┼──────────┼─────────┼───┨
┃ 1 │ 1 │    0     │    0    │ ✓ ┃
┗━━━┷━━━┷━━━━━━━━━━┷━━━━━━━━━┷━━━┛

Test 2: ¬(a ∨ b) ≡ ¬(a → b)
┏━━━┯━━━┯━━━━━━━━━━┯━━━━━━━━━━┯━━━┓
┃ a │ b │ ¬(a ∨ b) │ ¬(a → b) │   ┃
┠───┼───┼──────────┼──────────┼───┨
┃ 0 │ 0 │    1     │    0     │ ✗ ┃
┠───┼───┼──────────┼──────────┼───┨
┃ 0 │ 1 │    0     │    0     │ ✓ ┃
┠───┼───┼──────────┼──────────┼───┨
┃ 1 │ 0 │    0     │    1     │ ✗ ┃
┠───┼───┼──────────┼──────────┼───┨
┃ 1 │ 1 │    0     │    0     │ ✓ ┃
┗━━━┷━━━┷━━━━━━━━━━┷━━━━━━━━━━┷━━━┛

Test 3: ¬a ∧ ¬b ≡ ¬(a → b)
┏━━━┯━━━┯━━━━━━━━━┯━━━━━━━━━━┯━━━┓
┃ a │ b │ ¬a ∧ ¬b │ ¬(a → b) │   ┃
┠───┼───┼─────────┼──────────┼───┨
┃ 0 │ 0 │    1    │    0     │ ✗ ┃
┠───┼───┼─────────┼──────────┼───┨
┃ 0 │ 1 │    0    │    0     │ ✓ ┃
┠───┼───┼─────────┼──────────┼───┨
┃ 1 │ 0 │    0    │    1     │ ✗ ┃
┠───┼───┼─────────┼──────────┼───┨
┃ 1 │ 1 │    0    │    0     │ ✓ ┃
┗━━━┷━━━┷━━━━━━━━━┷━━━━━━━━━━┷━━━┛

Summary: 1/3 tests passed.
┏━━━━━━━━━━━━━━━━━━━┯━━━┓
┃       Tests       │   ┃
┠───────────────────┼───┨
┃¬(a ∨ b) ≡ ¬a ∧ ¬b │ ✓ ┃
┠───────────────────┼───┨
┃¬(a ∨ b) ≡ ¬(a → b)│ ✗ ┃
┠───────────────────┼───┨
┃¬a ∧ ¬b ≡ ¬(a → b) │ ✗ ┃
┗━━━━━━━━━━━━━━━━━━━┷━━━┛

✗ The statements are not logically equivalent!
```

Additional flags `-l`/`--labels`, `-r`/`--reverse`, and `-o`/`--output` also apply.

> **Note**  
> The flag `-o`/`--output` will be ignored when `-m`/`--mode` is set to `paired` under interactive mode (no files will be exported).

#### Interactive Mode
Similar to `make-table`, `check-equivalence` also has an interactive mode, which can be used to check multiple pairs/groups of statement at a time.

```shell
> ./logic-util check-equivalence [OPTIONS]
(1) ▊
```

Upon entering the interactive mode, you will be prompted to enter your propositions one by one. When you are done with a group of propositions, hit return on the next prompt to end the group and begin the test.

To exit, hit <kbd>Ctrl</kbd> + <kbd>C</kbd>, <kbd>Ctrl</kbd> + <kbd>D</kbd>, or return without any input.

---

### Checking Validity
To check the validity of an argument, use the keyword `check-validity` as such:
```shell
> ./logic-util check-validity [PREMISE]... -c/--conclusion [CONCLUSION]
```
The `-c`/`--conclusion` flag is _optional_, the last premise will be taken as the conclusion of the argument if one isn't provided.

> **Note**  
> This checks the **validity** of an argument (not whether a single proposition is a logical truth), which requires **at least one premise and one conclusion**.

<details>
 <summary><strong>&ensp;Example: Converse Error</strong></summary>
 <br/>

 ```shell
 > ./logic-util check-validity 'a -> b' 'b' -c 'a'

 1. a → b
 2. b
 ──────────
 ∴ a
 
 ┏━━━┯━━━┯━━━━━━━┯━━━┓
 ┃ a │ b │ a → b │   ┃
 ┠───┼───┼───────┼───┨
 ┃ 0 │ 0 │   1   │ ✓ ┃
 ┠───┼───┼───────┼───┨
 ┃ 0 │ 1 │   1   │ ✗ ┃
 ┠───┼───┼───────┼───┨
 ┃ 1 │ 0 │   0   │ ✓ ┃
 ┠───┼───┼───────┼───┨
 ┃ 1 │ 1 │   1   │ ✓ ┃
 ┗━━━┷━━━┷━━━━━━━┷━━━┛
 Countermodel: a = 0, b = 1

 ✗ The argument is invalid!
 ```
</details>

Additional flags `-l`/`--labels`, `-r`/`--reverse`, and `-o`/`--output` also apply.

#### Interactive Mode
Like `make-table` and `check-equivalence`, you can check the validity of multiple arguments in the interactive mode:

```shell
> ./logic-util check-validity [OPTIONS]
Premise 1: ▊
```

Upon entering the interactive mode, you will be prompted to enter the premise(s) and the conclusion of your argument. If no conclusion is provided, the last premise will be used as the conclusion.

To exit, hit <kbd>Ctrl</kbd> + <kbd>C</kbd> or <kbd>Ctrl</kbd> + <kbd>D</kbd>.

## 🖍&ensp;To Dos
- [ ] Support for tautologies ($\top$) and contradictions ($\bot$).
- [ ] A better documentation.
- [ ] A neater codebase (some ugly code in there).
- [ ] More tests.
- [ ] More helpful error messages.
- [ ] Validity test using formal proof with rules of inference.
- [ ] Validity/Equivalency test with the [truth tree method (the semantic tableaux)](https://en.wikipedia.org/wiki/Method_of_analytic_tableaux).
- [ ] First-order logic statement evaluation and validity/equivalency test (with the truth tree method).
- [ ] A Windows executable.
- [ ] Suggest features...?

## 💪&ensp;Contributing
- 🍴&nbsp;Simply fork the code yourself and submit a pull request to improve the tool!
- 🚩&nbsp;Open an [issue](https://github.com/4g3nt81lly/logic-util/issues) or [discussion](https://github.com/4g3nt81lly/logic-util/discussions) if you have questions, suggestions, or bugs you've found.
- 📧&ensp;Hit me up at my [E-mail](mailto:4g3nt81lly@gmail.com), [Facebook](https://www.facebook.com/billylby), or [Instagram](https://www.instagram.com/4g3nt81lly/) if you'd like to discuss or help with this project (or other projects), or even just chat with me or teach me about something!

[^1]: Burgess, J. P., Jeffrey, R. C. (2006). Formal logic: its scope and limits. Indianapolis: Hackett Publishing Company.