# python-project-builder

Based on Nas Banov's [implementation](http://stackoverflow.com/questions/2588163/implementing-brainfuck-loops-in-an-interpreter#2588195)

This code implement a simpler version of [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) language. 
This version **DOESN'T** skip [ if the current value is 0. This way we don't need to wait for ]


----

## Quick links
- [Requirements](#requirements)
- [Project Setup](#project-setup)
- [Usage](#usage)
  - [Positional Arguments](#positional-arguments)
- [Project Structure](#project-structure)
- [License](#license)

----

## Requirements

* [python](https://www.python.org/download/releases/3.0/) >= 3.2

----

## Project Setup

* **Clone** the project
* Move into the **project dir**
* *(Optional)* Run the **tests**
* **Run** a brainfuck code

**Step 1**: Clone the project:

    git clone https://github.com/nullhack/simple-brainfuck.git

**Step 2**: Move into the new created project path:

    cd simple-brainfuck

**Step 3**: *(Optional)* Run the tests:

    python3 -m doctest -v ./examples.txt
    
**Step 4**: Run a brainfuck code:

    python3 brainfuck.py bfcode

----

## Usage: 

    brainfuck.py bfcode

### Positional arguments:

    bfcode             brainfuck code that will be parsed

----

## Project Structure

    simple-brainfuck
    ├── brainfuck.py
    ├── examples.txt
    └── README.md

----

## License

MIT License

Copyright (c) 2016 Eric Lopes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

----

