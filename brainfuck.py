class Cells(dict):
    def __getitem__(self, key):
        if key in self:
            return super(Cells, self).__getitem__(key)
        return 0

    def __str__(self):
        m = min(self.keys())
        M = max(self.keys())
        print_list = [0 for _ in range(m, M+1)]
        for key,value in self.items():
            print_list[key-m] = value
        return str(print_list)

class BrainFuck:

    def __init__(self):
        self.cells = Cells()
        self.pointer = 0
        self.cmds = {
            '.':self._print_value,
            ',':self._read_value,
            '>':self._move_right,
            '<':self._move_left,
            '+':self._add,
            '-':self._sub,
            '[':self._open_brackets,
            ']':self._close_brackets,
            #additional commands
            '*':self.print_cells,
            }

    def _print_value(self):
        print(self.cells[self.pointer])

    def _read_value(self):
        self.cells[self.pointer] = int(input('<< '))

    def _move_right(self):
        self.pointer += 1

    def _move_left(self):
        self.pointer -= 1

    def _add(self):
        self.cells[self.pointer] += 1

    def _sub(self):
        self.cells[self.pointer] -= 1

    def _open_brackets(self):
        pass

    def _close_brackets(self):
        pass

    def print_cells(self):
        print(self.cells)

    def execute(self, cmd):
        if cmd in self.cmds: self.cmds[cmd]()

    def interpreter(self):
        while True:
            cmd_line = input('>> ')
            for c in cmd_line: self.execute(c)
            if not cmd_line: break

if __name__=="__main__":
    bf = BrainFuck()
    bf.interpreter()
