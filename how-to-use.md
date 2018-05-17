The sequence of initialization is as follow:
- if there's an input code, run it
- after running the input the interpreter enter in 
  shell mode keeping values.
- an empty value finish the interpreter.

from command line:

```
python brainfuck.py -c '+++.>+>[-]*&'

```

or executing shell after running commands:

```
python brainfuck.py '+++.>+>[-]*&'
```

---

Execution inside your module:

Import BrainFuck class from brainfuck module

```
>>> from brainfuck import BrainFuck

```

Create a new instance of BrainFuck object

```
>>> bf = BrainFuck()

```

Execute commands

```
>>> bf.execute('+++++++++++++++++++++++++++++++++++++++++++++++++++.')
3
>>> bf.execute('[-]')
>>> bf.execute('{p10}*{tochar}')
importing: bflib/p10.bf
importing: bflib/tochar.bf
|10|

>>> bf.execute('&')
115 +++++++++++++++++++++++++++++++++++++++++++++++++++.[-]++++++++++*++++++++++++++++++++++++++++++++++++++++++++++++&

```

To initialize the interpreter from Python code:
```
bf.interpreter()

```
