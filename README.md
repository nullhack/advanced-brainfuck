|Branch             |Build status                                                  
|-------------------|-----------------------------------------------------
|master             |[![master branch build status](https://api.travis-ci.com/nullhack/advanced-brainfuck.svg?branch=master)](https://travis-ci.com/nullhack/advanced-brainfuck)

# advanced-brainfuck

This project implements an Interpreter for [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) language, some additional features are available, e.g. Import external libs, Cells print, Command history.

----

## Quick links
- [Requirements](#requirements)
- [Project Setup](#project-setup)
- [Usage](#usage)
  - [Positional arguments](#positional-arguments)
  - [Optionalonal arguments](#optional-arguments)
- [BrainFuck Commands](#brainfuck-commands)
  - [Additional commands](#additional-commands)
- [Project Structure](#project-structure)
- [License](#license)

[↑](#advanced-brainfuck)

----

## Requirements

* [python](https://www.python.org/download/releases/3.0/) >= 2.7

[↑](#quick-links)

----

## Project Setup

* **Clone** the project
* Move into the **project dir**
* *(Optional)* Run the **tests**
* **Run** brainfuck commands

**Step 1**: Clone the project:

    git clone https://github.com/nullhack/advanced-brainfuck.git

**Step 2**: Move into the project dir:

    cd advanced-brainfuck

**Step 3**: *(Optional)* Run the tests:

    python -m doctest -v ./how-to-use.md
    
**Step 4**: Run brainfuck COMMANDS:

    python brainfuck.py -c COMMANDS
    
or start the interpreter

    python3 brainfuck.py

[↑](#quick-links)

----

## Usage: 

    brainfuck.py [-h] [-r MAX_RECURSION] [-c] [cmd]

### Positional arguments:

    cmd         BrainFuck commands

### Optional arguments:

    -h, --help            show this help message and exit
    -r MAX_RECURSION, --recursion MAX_RECURSION
                          set MAX_RECURSION value
    -c, --command-line    do not initialize shell, running commands from
                          arguments only

[↑](#quick-links)

----

## BrainFuck Commands

    >         increment the data pointer.
    <         decrement the data pointer.
    +         increment the value at the data pointer.
    -         decrement the value at the data pointer.
    .         output the value at the data pointer.
    ,         accept one integer of inputer.
    [         jump if value is false.
    ]         continue if value is true.

### Additional commands

    {LIB}         import external brainfuck code and run it into current instance.
    *             output all the cells.
    &             output command history.
    help          show this help message.

[↑](#quick-links)

----

## Project Structure

    advanced-brainfuck
    ├── bflib
    │   ├── copy.bf
    │   ├── lower.bf
    │   ├── m100.bf
    │   ├── m10.bf
    │   ├── m50.bf
    │   ├── mul2.bf
    │   ├── p100.bf
    │   ├── p10.bf
    │   ├── p50.bf
    │   ├── sub.bf
    │   ├── sum.bf
    │   ├── tochar.bf
    │   ├── toint.bf
    │   └── upper.bf
    ├── brainfuck.py
    ├── LICENSE
    ├── how-to-use.md
    └── README.md

[↑](#quick-links)

----

## License

This project is released under GPLv3 license.

Advanced Brainfuck Copyright (C) 2016  Eric Lopes

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

For more info, please read the complete [license](LICENSE) file.

[↑](#quick-links)

----
