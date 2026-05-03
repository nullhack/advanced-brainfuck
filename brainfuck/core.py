"""This module contains all classes and functions to run BrainFuck commands.

    Examples:

        >>> bf = BrainFuck()
        >>> bf.execute('++++++++++++++++++++++++++++++++++++++++++++++++++.')
        2
        >>> bf.execute('*')
        |50|
        >>> bf.execute('{toint}*')
        importing: bflib/toint.bf
        |2|
        >>> bf.execute('&')
        102 ++++++++++++++++++++++++++++++++++++++++++++++++++.*------------------------------------------------*&
        >>> BrainFuck.is_balanced('[[-][-][][{sum}+++.>]]')
        True
        >>> BrainFuck.is_balanced('[.[>>>[+++{sum]<<+++.]*]')
        False
        >>> BrainFuck.is_balanced('[.[>>>[+++[{sum}<<+++.]*]')
        False

"""

import argparse
import os
import re
import sys
from collections import defaultdict

import numpy as np
from numba import jit

# Operation codes for JIT compilation
OP_ADD = 0
OP_MOVE = 1
OP_OUTPUT = 2
OP_INPUT = 3
OP_JUMP_ZERO = 4
OP_JUMP_NZ = 5
OP_PRINT_CELLS = 6
OP_PRINT_HISTORY = 7

# Execution status codes
STATUS_COMPLETE = 0
STATUS_NEED_INPUT = 1
STATUS_PRINT_CELLS = 2
STATUS_PRINT_HISTORY = 3
STATUS_OUTPUT_OVERFLOW = 4

OUTPUT_BUF_SIZE = 1_000_000

help_text = """
BrainFuck Commands

    >         increment the data pointer.
    <         decrement the data pointer.
    +         increment the value at the data pointer.
    -         decrement the value at the data pointer.
    .         output the value at the data pointer.
    ,         accept one integer of inputer.
    [         jump if value is false.
    ]         continue if value is true.

Additional Commands

    {LIB}         import external brainfuck code to current process.
    *             output all the cells.
    &             output command history.
    help          show this help message.
    quit          exit the interpreter.
    save [FILE]   save tape state to JSON (default: tape.json)."""


@jit(nopython=True)
def execute_jit(program, tape, state, output_buf, max_iterations):
    """JIT-compiled BrainFuck execution engine with checkpoint/resume.

    Runs until: program ends, max_iterations reached, an I/O op is hit,
    or the output buffer overflows.

    Args:
        program: NumPy array of shape (N, 2) with (op_code, arg) pairs
        tape: NumPy array — memory tape, modified in-place
        state: NumPy array of shape (3,) — [pointer, pc, output_count]
               Modified in-place to track execution state across segments.
        output_buf: Pre-allocated buffer for output cell values
        max_iterations: Maximum iterations to run in this segment

    Returns:
        (status, iterations) where status is one of STATUS_*
    """
    pointer = int(state[0])
    pc = int(state[1])
    out_idx = int(state[2])
    iterations = 0

    while pc < len(program) and iterations < max_iterations:
        op_code = program[pc, 0]
        arg = program[pc, 1]

        if op_code == OP_ADD:
            tape[pointer] = (tape[pointer] + arg) & 0xFF
        elif op_code == OP_MOVE:
            new_pointer = pointer + arg
            if 0 <= new_pointer < len(tape):
                pointer = new_pointer
        elif op_code == OP_OUTPUT:
            if out_idx < len(output_buf):
                output_buf[out_idx] = tape[pointer]
            out_idx += 1
            if out_idx >= len(output_buf):
                state[0] = pointer
                state[1] = pc + 1
                state[2] = out_idx
                return (STATUS_OUTPUT_OVERFLOW, iterations)
        elif op_code == OP_INPUT:
            state[0] = pointer
            state[1] = pc
            state[2] = out_idx
            return (STATUS_NEED_INPUT, iterations)
        elif op_code == OP_JUMP_ZERO:
            if tape[pointer] == 0:
                pc = arg
                iterations += 1
                continue
        elif op_code == OP_JUMP_NZ:
            if tape[pointer] != 0:
                pc = arg
                iterations += 1
                continue
        elif op_code == OP_PRINT_CELLS:
            state[0] = pointer
            state[1] = pc
            state[2] = out_idx
            return (STATUS_PRINT_CELLS, iterations)
        elif op_code == OP_PRINT_HISTORY:
            state[0] = pointer
            state[1] = pc
            state[2] = out_idx
            return (STATUS_PRINT_HISTORY, iterations)

        pc += 1
        iterations += 1

    state[0] = pointer
    state[1] = pc
    state[2] = out_idx
    return (STATUS_COMPLETE, iterations)


@jit(nopython=True)
def convert_ir_to_numeric_jit(op_codes, args):
    """Convert parallel arrays to numeric format for JIT compilation."""
    program = np.empty((len(op_codes), 2), dtype=np.int32)

    for i in range(len(op_codes)):
        program[i, 0] = op_codes[i]
        program[i, 1] = args[i]

    return program


def convert_ir_to_numeric(ir_list):
    """Convert IR tuples to numeric format for JIT compilation."""
    if not ir_list:
        return np.empty((0, 2), dtype=np.int32)

    op_codes = np.empty(len(ir_list), dtype=np.int32)
    args = np.empty(len(ir_list), dtype=np.int32)

    op_map = {
        'add': OP_ADD,
        'move': OP_MOVE,
        'output': OP_OUTPUT,
        'input': OP_INPUT,
        'jump_zero': OP_JUMP_ZERO,
        'jump_nz': OP_JUMP_NZ,
        'print_cells': OP_PRINT_CELLS,
        'print_history': OP_PRINT_HISTORY,
    }

    for i, ir_op in enumerate(ir_list):
        op_name = ir_op[0]
        arg = ir_op[1] if len(ir_op) > 1 else 0

        op_codes[i] = op_map.get(op_name, 0)
        args[i] = arg

    return convert_ir_to_numeric_jit(op_codes, args)


class BrainFuck:
    """BrainFuck language specification.

    This class implements all commands of the BrainFuck language and
    some advanced functions.

    This class also implements a full featured interpreter.

    You can run from python code or shell.

    Attributes:
        cells (Cells): Advanced structure to handle the language registers.
        pointer (int): Pointer to current cell position.
        _cmd_parts (list): List of command strings executed so far.
        _pc (int): Program counter for the compiled instruction pointer.

    """

    def __init__(self):
        self.cells = Cells()
        self.pointer = 0
        self._cmd_parts = []
        self._pc = 0

    def _print_value(self, output_file=None):
        value = self.cells[self.pointer]
        if not value:
            print(file=output_file)
        elif value > 0 and value < 256:
            print(chr(value), end="", file=output_file)
        else:
            print(value, end="", file=output_file)

    def _read_value(self):
        try:
            while True:
                ui = input('<< ')
                if not ui:
                    break
                try:
                    self.cells[self.pointer] = int(ui)
                    break
                except (ValueError, TypeError):
                    pass
                try:
                    self.cells[self.pointer] = ord(ui[0])
                    break
                except (ValueError, TypeError):
                    print("Invalid value! Please try again:")
        except EOFError:
            self.cells[self.pointer] = -1

    @staticmethod
    def _read_input_direct():
        try:
            while True:
                ui = input('<< ')
                if not ui:
                    return None
                try:
                    return int(ui)
                except (ValueError, TypeError):
                    pass
                try:
                    return ord(ui[0])
                except (ValueError, TypeError):
                    print("Invalid value! Please try again:")
        except EOFError:
            return -1

    def print_cells(self):
        """Print all cells."""
        print(self.cells.print_pos(self.pointer))

    def print_cmd_history(self):
        """Print all the commands executed so far."""
        cmd_history = ''.join(self._cmd_parts)
        print(len(cmd_history), cmd_history)

    @staticmethod
    def is_balanced(cmd_line):
        """Check if a given command line is balanced or not.

        Args:
            cmd_line: The line to be verified.

        Returns:
            True if cmd_line is balanced (False if not).

        """
        brackets = {'[': ']', '{': '}'}
        stack = []
        for cmd in cmd_line:
            d = brackets.get(cmd, None)
            if d:
                stack.append(d)
            elif cmd in brackets.values():
                if not stack or cmd != stack.pop():
                    return False
        return not stack

    @staticmethod
    def _resolve_imports(cmd_line, visited=None):
        """Recursively resolve library imports.

        Args:
            cmd_line: Command line with potential {LIB} imports.
            visited: Set of already visited libraries to prevent cycles.

        Returns:
            Fully resolved command string with all imports inlined.

        Raises:
            Exception: If could not import some library.
        """
        if visited is None:
            visited = set()

        BASE_DIR = os.path.join(os.path.dirname(__file__), 'bflib')
        EXT = ['.bf', '']

        import_list = re.findall(r'\{([a-zA-Z0-9_\.\-\/]+)\}', cmd_line)
        path_ext = [(BASE_DIR, ext) for ext in EXT]

        for lib in import_list:
            if lib in visited:
                continue
            visited.add(lib)

            lib_path = ''
            for base, ext in path_ext:
                vpath = os.path.join(base, '{}{}'.format(lib, ext))
                if os.path.isfile(vpath):
                    lib_path = vpath
                    break

            if not lib_path:
                raise Exception('Could not import: {}'.format(lib))

            with open(lib_path) as flib:
                print('importing: bflib/{}{}'.format(lib, ext if ext else ''))
                lib_content = ''.join(flib.readlines())
                valid_cmds = set('><+-.,[]')
                lib_content = ''.join(c for c in lib_content if c in valid_cmds)
                lib_content = BrainFuck._resolve_imports(lib_content, visited)
                cmd_line = cmd_line.replace('{{{}}}'.format(lib), lib_content)

        return cmd_line

    @staticmethod
    def import_lib(cmds):
        """Import a set of external codes.

        Args:
            cmds: A line with one or more libs to import.

        Returns:
            import_dict (dict): A dictionary containing all the lib code.

        Raises:
            Exception: If could not import some of the external code.

        """
        resolved = BrainFuck._resolve_imports(cmds)
        import_list = re.findall(r'\{([a-zA-Z0-9_\.\-\/]+)\}', cmds)

        import_dict = {}
        for lib in import_list:
            import_dict[lib] = resolved
        return import_dict

    def _compile_to_ir(self, cmd_line):
        """Compile BrainFuck commands to intermediate representation.

        Args:
            cmd_line: String of BrainFuck commands (imports should already be resolved).

        Returns:
            List of IR operations: [('add', count), ('move', offset), ('jump_zero', target), ...]
        """
        valid_cmds = set('><+-.,[]&*')
        filtered_cmds = [c for c in cmd_line if c in valid_cmds]

        ir = []
        i = 0
        while i < len(filtered_cmds):
            cmd = filtered_cmds[i]

            if cmd == '+':
                count = 1
                while i + count < len(filtered_cmds) and filtered_cmds[i + count] == '+':
                    count += 1
                ir.append(('add', count))
                i += count
            elif cmd == '-':
                count = 1
                while i + count < len(filtered_cmds) and filtered_cmds[i + count] == '-':
                    count += 1
                ir.append(('add', -count))
                i += count
            elif cmd == '>':
                count = 1
                while i + count < len(filtered_cmds) and filtered_cmds[i + count] == '>':
                    count += 1
                ir.append(('move', count))
                i += count
            elif cmd == '<':
                count = 1
                while i + count < len(filtered_cmds) and filtered_cmds[i + count] == '<':
                    count += 1
                ir.append(('move', -count))
                i += count
            elif cmd == '.':
                ir.append(('output',))
                i += 1
            elif cmd == ',':
                ir.append(('input',))
                i += 1
            elif cmd == '[':
                ir.append(('jump_zero', -1))
                i += 1
            elif cmd == ']':
                ir.append(('jump_nz', -1))
                i += 1
            elif cmd == '*':
                ir.append(('print_cells',))
                i += 1
            elif cmd == '&':
                ir.append(('print_history',))
                i += 1
            else:
                i += 1

        stack = []
        for i, op in enumerate(ir):
            if op[0] == 'jump_zero':
                stack.append(i)
            elif op[0] == 'jump_nz':
                if stack:
                    match_pos = stack.pop()
                    ir[match_pos] = ('jump_zero', i + 1)
                    ir[i] = ('jump_nz', match_pos)

        return ir

    def _sync_cells_from_tape(self, tape, tape_center):
        """Sync tape array state back to Cells object."""
        self.cells = Cells()
        for i in range(len(tape)):
            if tape[i] != 0:
                self.cells[i - tape_center] = int(tape[i])

    @staticmethod
    def _flush_outputs(output_buf, count, output_file=None):
        for i in range(count):
            value = int(output_buf[i])
            if not value:
                print(file=output_file)
            elif 0 < value < 256:
                print(chr(value), end="", file=output_file)
            else:
                print(value, end="", file=output_file)

    def _execute_segmented_jit(
        self,
        numeric_program,
        tape,
        tape_center,
        state,
        output_buf,
        max_iterations,
        output_file=None,
    ):
        """Execute program using segmented JIT with Python I/O checkpoints.

        Runs JIT for computation segments, pausing at I/O operations
        for Python to handle them, then resuming JIT execution.

        Args:
            numeric_program: NumPy array of (op_code, arg) pairs
            tape: NumPy array — memory tape (modified in-place)
            tape_center: Offset of cell 0 in tape array
            state: NumPy array [pointer, pc, output_count] — execution state
            output_buf: NumPy array — pre-allocated output buffer
            max_iterations: Maximum total iterations

        Returns:
            True if program completed, False if max_iterations reached
        """
        remaining = max_iterations

        while remaining > 0 and state[1] < len(numeric_program):
            status, iters = execute_jit(
                numeric_program, tape, state, output_buf, remaining
            )
            remaining -= iters

            self._flush_outputs(output_buf, state[2], output_file)
            state[2] = 0

            if status == STATUS_NEED_INPUT:
                value = self._read_input_direct()
                if value is not None:
                    tape[int(state[0])] = value
                state[1] += 1

            elif status == STATUS_PRINT_CELLS:
                self._sync_cells_from_tape(tape, tape_center)
                self.pointer = int(state[0]) - tape_center
                self.print_cells()
                state[1] += 1

            elif status == STATUS_PRINT_HISTORY:
                self.print_cmd_history()
                state[1] += 1

            elif status == STATUS_OUTPUT_OVERFLOW:
                pass

            elif status == STATUS_COMPLETE:
                return state[1] >= len(numeric_program)

        return False

    def _execute_interpreted(self, ir_program, max_iterations, output_file=None):
        """Fallback interpreted execution for when JIT is unavailable."""
        backup_cells = self.cells.backup()
        backup_pointer = self.pointer

        try:
            pc = 0
            exec_count = 0

            while pc < len(ir_program) and exec_count < max_iterations:
                op = ir_program[pc]
                tag = op[0]

                if tag == 'add':
                    self.cells[self.pointer] = (
                        self.cells[self.pointer] + op[1]
                    ) & 0xFF
                elif tag == 'move':
                    self.pointer += op[1]
                elif tag == 'output':
                    self._print_value(output_file)
                elif tag == 'input':
                    self._read_value()
                elif tag == 'jump_zero':
                    if not self.cells[self.pointer]:
                        pc = op[1]
                        continue
                elif tag == 'jump_nz':
                    if self.cells[self.pointer]:
                        pc = op[1]
                        continue
                elif tag == 'print_cells':
                    self.print_cells()
                elif tag == 'print_history':
                    self.print_cmd_history()

                pc += 1
                exec_count += 1

        except Exception:
            print('MAX recursion reached!')
            self.cells = backup_cells
            self.pointer = backup_pointer
            if self._cmd_parts:
                self._cmd_parts.pop()

    def execute(self, cmd_line, MAX_RECURSION=10**5, output_file=None):
        if not self.is_balanced(cmd_line):
            raise Exception("brackets not balanced!")

        try:
            expanded_cmd_line = self._resolve_imports(cmd_line)
        except Exception as e:
            print(e)
            return

        self._cmd_parts.append(expanded_cmd_line)
        ir_program = self._compile_to_ir(expanded_cmd_line)

        if not ir_program:
            return

        numeric_program = convert_ir_to_numeric(ir_program)
        if len(numeric_program) == 0:
            return

        try:
            TAPE_SIZE = 65536
            tape_center = TAPE_SIZE // 2
            tape = np.zeros(TAPE_SIZE, dtype=np.int32)

            for pos, value in self.cells._sparse.items():
                idx = tape_center + pos
                if 0 <= idx < TAPE_SIZE:
                    tape[idx] = value
            for i, value in enumerate(self.cells._tape):
                if i < len(self.cells._tape):
                    idx = tape_center + i
                    if 0 <= idx < TAPE_SIZE:
                        tape[idx] = value

            state = np.array(
                [tape_center + self.pointer, np.int64(0), np.int64(0)],
                dtype=np.int64,
            )
            output_buf = np.empty(OUTPUT_BUF_SIZE, dtype=np.int32)

            self._execute_segmented_jit(
                numeric_program,
                tape,
                tape_center,
                state,
                output_buf,
                MAX_RECURSION,
                output_file,
            )

            self._sync_cells_from_tape(tape, tape_center)
            self.pointer = int(state[0]) - tape_center

        except Exception:
            self._execute_interpreted(ir_program, MAX_RECURSION, output_file)

    def save_tape(self, path='tape.json'):
        import json

        data = {'pointer': self.pointer, 'cells': {}}
        for i, val in enumerate(self.cells._tape):
            if val != 0:
                data['cells'][str(i)] = val
        for key, val in self.cells._sparse.items():
            if val != 0:
                data['cells'][str(key)] = val
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_tape(self, path):
        import json

        with open(path) as f:
            data = json.load(f)
        self.pointer = data.get('pointer', 0)
        self.cells = Cells()
        for key_str, value in data.get('cells', {}).items():
            self.cells[int(key_str)] = value

    def interpreter(self, MAX_RECURSION=10**5):
        while True:
            cmd_line = input('>> ')
            while not self.is_balanced(cmd_line):
                tmp = input('.. ')
                cmd_line = cmd_line + tmp if tmp else 'skip'
            if cmd_line == 'help':
                print(help_text)
            elif cmd_line in ('quit', 'exit'):
                break
            elif cmd_line.startswith('save'):
                parts = cmd_line.split(maxsplit=1)
                path = parts[1] if len(parts) > 1 else 'tape.json'
                self.save_tape(path)
                print(f'Tape saved to {path}')
            elif not cmd_line:
                break
            else:
                self.execute(cmd_line, MAX_RECURSION)


class Cells:
    """Optimized cell storage using list for positive indices, dict for negative."""

    def __init__(self):
        self._tape = [0] * 30000
        self._sparse = defaultdict(int)

    def __getitem__(self, key):
        """Return cell value at key, 0 if undefined."""
        if 0 <= key < len(self._tape):
            return self._tape[key]
        return self._sparse[key]

    def __setitem__(self, key, value):
        """Set cell value at key."""
        if 0 <= key < len(self._tape):
            self._tape[key] = value
        else:
            if value == 0:
                if key in self._sparse:
                    del self._sparse[key]
            else:
                self._sparse[key] = value

    def backup(self):
        """Return a copy of the cells."""
        new_cells = Cells()
        new_cells._tape = self._tape[:]
        new_cells._sparse = defaultdict(int)
        for key, value in self._sparse.items():
            new_cells._sparse[key] = value
        return new_cells

    def print_pos(self, pos):
        """Print all the cells and the pointer."""
        non_zero_indices = set()

        for i, val in enumerate(self._tape):
            if val != 0:
                non_zero_indices.add(i)

        for key, val in self._sparse.items():
            if val != 0:
                non_zero_indices.add(key)

        non_zero_indices.add(pos)

        if non_zero_indices:
            m, M = min(non_zero_indices), max(non_zero_indices)
        else:
            m = M = pos

        print_list = []
        for i in range(m, M + 1):
            val = self[i]
            if i == pos:
                print_list.append('|{}|'.format(val))
            else:
                print_list.append(str(val))

        return ' '.join(print_list)


def main(args=None):
    """Config parser and run command line options."""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        'cmd',
        nargs='?',
        default='',
        type=str,
        help='brainFuck commands',
    )
    arg_parser.add_argument(
        '-r', '--recursion',
        default=10**5,
        type=int,
        metavar='MAX_RECURSION',
        help='set MAX_RECURSION value',
    )
    arg_parser.add_argument(
        '-c', '--command-line',
        action='store_true',
        help='do not initialize shell, running commands from arguments only',
    )
    arg_parser.add_argument(
        '-f', '--file',
        type=str,
        metavar='FILE',
        help='load brainfuck commands from a file',
    )
    arg_parser.add_argument(
        '--load',
        type=str,
        metavar='FILE',
        help='load tape state from JSON file before execution',
    )
    arg_parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='redirect output to file instead of stdout',
    )
    arg_parser.add_argument(
        '--dump',
        type=str,
        metavar='FILE',
        help='save tape state to JSON file after execution',
    )
    arguments = arg_parser.parse_args(args)

    cmd = arguments.cmd
    if arguments.file:
        with open(arguments.file) as f:
            cmd = f.read()

    bf = BrainFuck()
    if arguments.load:
        bf.load_tape(arguments.load)

    output_fh = None
    if arguments.output:
        output_fh = open(arguments.output, 'w')

    try:
        bf.execute(cmd, arguments.recursion, output_file=output_fh)
    finally:
        if output_fh:
            output_fh.close()

    if arguments.dump:
        bf.save_tape(arguments.dump)

    if not arguments.command_line:
        bf.interpreter(arguments.recursion)


if __name__ == "__main__":
    main(sys.argv[1:])
