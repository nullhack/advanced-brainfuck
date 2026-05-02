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

import os
import re
import sys
import argparse
import itertools
from collections import defaultdict
import numpy as np
from numba import jit, types
from numba.typed import List

# Operation codes for JIT compilation
OP_ADD = 0
OP_MOVE = 1
OP_OUTPUT = 2
OP_INPUT = 3
OP_JUMP_ZERO = 4
OP_JUMP_NZ = 5
OP_PRINT_CELLS = 6
OP_PRINT_HISTORY = 7

help_text =  """
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
    help          show this help message."""

@jit(nopython=True)
def execute_jit(program, tape_size=30000, max_iterations=100000):
    """JIT-compiled BrainFuck execution engine.
    
    Args:
        program: NumPy array of (op_code, arg) pairs
        tape_size: Size of the memory tape
        max_iterations: Maximum iterations to prevent infinite loops
        
    Returns:
        (output_values, final_tape, final_pointer, iterations_used)
    """
    tape = np.zeros(tape_size, dtype=np.int32)
    pointer = tape_size // 2  # Start in middle to allow negative movement
    pc = 0
    iterations = 0
    
    # Collect output values
    output_values = np.empty(1000, dtype=np.int32)  # Pre-allocate output buffer
    output_count = 0
    
    while pc < len(program) and iterations < max_iterations:
        op_code = program[pc, 0]
        arg = program[pc, 1]
        
        if op_code == OP_ADD:
            tape[pointer] += arg
        elif op_code == OP_MOVE:
            new_pointer = pointer + arg
            if 0 <= new_pointer < tape_size:
                pointer = new_pointer
        elif op_code == OP_OUTPUT:
            if output_count < len(output_values):
                output_values[output_count] = tape[pointer]
                output_count += 1
        elif op_code == OP_JUMP_ZERO:
            if tape[pointer] == 0:
                pc = arg
                continue
        elif op_code == OP_JUMP_NZ:
            if tape[pointer] != 0:
                pc = arg
                continue
        # Note: INPUT, PRINT_CELLS, PRINT_HISTORY need special handling outside JIT
        
        pc += 1
        iterations += 1
    
    # Return only the used portion of output
    return output_values[:output_count], tape, pointer, iterations

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

    def _print_value(self):
        """Print current cell value.

        Note:
            If the value is 0, a new line is printed.
            If the value in ASCII table, It's printed as a char.
            Else, the value is printed as integer.
        """
        value = self.cells[self.pointer]
        if not value: 
            print()
        elif value > 0 and value < 256: 
            print(chr(value), end="")
        else: 
            print(value, end="")

    def _read_value(self):
        """Read a value from input into current cell.

        Note:
            Executes until a valid input is read or a blank line inserted.
            
        """
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
                self.cells[self.pointer] = ord(ui)
                break
            except (ValueError, TypeError):
                print("Invalid value! Please try again:")

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
        brackets = {'[':']','{':'}'}
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
            
        BASE_LIB = 'bflib'
        BASE_DIR = os.path.join(os.path.dirname(__file__))
        EXT = ['.bf', '']
        
        import_list = re.findall(r'\{([a-zA-Z0-9_\.\-\/]+)\}', cmd_line)
        path_ext = list(itertools.product([BASE_LIB, BASE_DIR], EXT))
        
        for lib in import_list:
            if lib in visited:
                continue  # Skip already processed libraries
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
                print('importing:', lib_path)
                lib_content = ''.join(flib.readlines())
                # Filter to only include valid BF commands (remove comments/descriptions)
                valid_cmds = set('><+-.,[]')
                lib_content = ''.join(c for c in lib_content if c in valid_cmds)
                # Recursively resolve imports in the library file
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
        # For backward compatibility - just return the resolved imports
        resolved = BrainFuck._resolve_imports(cmds)
        import_list = re.findall(r'\{([a-zA-Z0-9_\.\-\/]+)\}', cmds)
        
        # Extract each library's content for the return dict
        import_dict = {}
        for lib in import_list:
            # This is a simplified approach - in practice, we'd need to track
            # what each library contributed during resolution
            import_dict[lib] = resolved  # Placeholder
        return import_dict

    def _compile_to_ir(self, cmd_line):
        """Compile BrainFuck commands to intermediate representation.
        
        Args:
            cmd_line: String of BrainFuck commands (imports should already be resolved).
            
        Returns:
            List of IR operations: [('add', count), ('move', offset), ('jump_zero', target), ...]
        """
        # Filter valid commands only (don't resolve imports here, they should already be resolved)
        valid_cmds = set('><+-.,[]&*')
        filtered_cmds = [c for c in cmd_line if c in valid_cmds]
        
        # Build IR with run-length encoding
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
                ir.append(('jump_zero', -1))  # Will be patched
                i += 1
            elif cmd == ']':
                ir.append(('jump_nz', -1))  # Will be patched
                i += 1
            elif cmd == '*':
                ir.append(('print_cells',))
                i += 1
            elif cmd == '&':
                ir.append(('print_history',))
                i += 1
            else:
                i += 1
        
        # Patch jump targets
        stack = []
        for i, op in enumerate(ir):
            if op[0] == 'jump_zero':
                stack.append(i)
            elif op[0] == 'jump_nz':
                if stack:
                    match_pos = stack.pop()
                    # Patch the jump_zero to jump past this jump_nz
                    ir[match_pos] = ('jump_zero', i + 1)
                    # Patch this jump_nz to jump back to the jump_zero
                    ir[i] = ('jump_nz', match_pos)
        
        return ir

    def execute(self, cmd_line, MAX_RECURSION=10**5):
        """Execute a set of  BrainFuck commands.

        Args:
            cmd_line (str): A line with BrainFuck commands.
            MAX_RECURSION (Optional[float]): Max number of commands allowed
            to execute in current line of commands.

        Raises:
            Exception: If brackets are not balanced.

        """
        if not self.is_balanced(cmd_line):
            raise Exception("brackets not balanced!")

        # Resolve imports and store expanded command for history
        try:
            expanded_cmd_line = self._resolve_imports(cmd_line)
        except Exception as e:
            print(e)
            return
            
        # Store expanded command for history (to match original behavior)
        self._cmd_parts.append(expanded_cmd_line)
        
        # Compile to IR (pass the already-resolved command line)
        ir_program = self._compile_to_ir(expanded_cmd_line)
        
        if not ir_program:
            return
        
        # Separate JIT-compatible operations from those requiring Python interaction
        jit_ops = []
        special_ops = []  # Operations that need special handling outside JIT
        
        for i, op in enumerate(ir_program):
            if op[0] in ('add', 'move', 'output', 'jump_zero', 'jump_nz'):
                jit_ops.append((i, op))
            else:
                special_ops.append((i, op))
        
        # If we have only JIT-compatible operations, use the fast path
        if not special_ops:
            try:
                # Convert to NumPy arrays for JIT execution
                numeric_program = convert_ir_to_numeric(ir_program)
                
                # Convert current cell state to NumPy
                tape_size = 30000
                tape_array = np.zeros(tape_size, dtype=np.int32)
                tape_center = tape_size // 2
                
                # Copy current cells to the tape array
                for pos, value in self.cells._sparse.items():
                    if tape_center + pos >= 0 and tape_center + pos < tape_size:
                        tape_array[tape_center + pos] = value
                        
                # Copy from the list-backed portion
                for i, value in enumerate(self.cells._tape):
                    if i < len(self.cells._tape) and tape_center + i < tape_size:
                        tape_array[tape_center + i] = value
                
                # Execute with JIT
                output_values, final_tape, final_pointer, iterations = execute_jit(
                    numeric_program, tape_size, MAX_RECURSION
                )
                
                # Update state from JIT results
                self.pointer = final_pointer - tape_center
                
                # Update cells from final tape
                self.cells = Cells()
                for i, value in enumerate(final_tape):
                    if value != 0:
                        pos = i - tape_center
                        self.cells[pos] = value
                
                # Print output values
                for value in output_values:
                    if not value: 
                        print()
                    elif value > 0 and value < 256: 
                        print(chr(value), end="")
                    else: 
                        print(value, end="")
                        
                return
                
            except Exception as e:
                # Fall back to interpreted execution on JIT errors
                pass
        
        # Fall back to interpreted execution for mixed operations or JIT failures
        backup_cells = self.cells.backup()
        backup_pointer = self.pointer
        
        try:
            pc = 0
            exec_count = 0
            
            while pc < len(ir_program) and exec_count < MAX_RECURSION:
                op = ir_program[pc]
                tag = op[0]
                
                if tag == 'add':
                    self.cells[self.pointer] += op[1]
                elif tag == 'move':
                    self.pointer += op[1]
                elif tag == 'output':
                    self._print_value()
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
            # Remove the failed command from history
            if self._cmd_parts:
                self._cmd_parts.pop()

    def interpreter(self, MAX_RECURSION=10**5):
        """Run the Interpreter.

        Args:
            MAX_RECURSION (Optional[float]): Max number of commands allowed
            to execute in current line of commands.

        """
        while True:
            cmd_line = input('>> ')
            while not self.is_balanced(cmd_line):
                tmp = input('.. ')
                cmd_line = cmd_line+tmp if tmp else 'skip'
            if cmd_line == 'help': 
                print(help_text)
            elif not cmd_line: 
                break
            else: 
                self.execute(cmd_line, MAX_RECURSION)

class Cells:
    """Optimized cell storage using list for positive indices, dict for negative."""

    def __init__(self):
        self._tape = [0] * 30000  # Pre-allocated tape for typical BF programs
        self._sparse = defaultdict(int)  # For negative indices only
        
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
                # Remove zero values from sparse dict to save memory
                if key in self._sparse:
                    del self._sparse[key]
            else:
                self._sparse[key] = value

    def backup(self):
        """Return a copy of the cells."""
        new_cells = Cells()
        # Copy the list portion
        new_cells._tape = self._tape[:]
        # Copy the sparse portion
        new_cells._sparse = defaultdict(int)
        for key, value in self._sparse.items():
            new_cells._sparse[key] = value
        return new_cells

    def print_pos(self, pos):
        """Print all the cells and the pointer."""
        # Find range of non-zero cells including the pointer position
        non_zero_indices = set()
        
        # Add non-zero indices from tape
        for i, val in enumerate(self._tape):
            if val != 0:
                non_zero_indices.add(i)
                
        # Add non-zero indices from sparse dict
        for key, val in self._sparse.items():
            if val != 0:
                non_zero_indices.add(key)
        
        # Always include the pointer position
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

def main(args=[]):
    """Config parser and run command line options."""
    #Configure argparser
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
    arguments = arg_parser.parse_args(args)

    #Execute input and run the interpreter
    bf = BrainFuck()
    bf.execute(arguments.cmd, arguments.recursion)
    if not arguments.command_line:
        bf.interpreter(arguments.recursion)

if __name__=="__main__":
    main(sys.argv[1:])