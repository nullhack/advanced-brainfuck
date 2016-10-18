class BrainFuck:

    def __init__(self):
        self.cells = Cells()
        self.pointer = 0
        self.cmd_history = ''
        self._cmd_pointer = 0
        self._jump = {}

    def _print_value(self):
        print(self.cells[self.pointer])

    def _read_value(self):
        while True:
            try:
                ui = int(input('<< '))
                self.cells[self.pointer] = ui
            except:
                print("Invalid integer!")
                continue
            else:
                break

    def _move_right(self):
        self.pointer += 1

    def _move_left(self):
        self.pointer -= 1

    def _add(self):
        self.cells[self.pointer] += 1

    def _sub(self):
        self.cells[self.pointer] -= 1

    def _open_brackets(self):
        if not self.cells[self.pointer]:
            self._cmd_pointer = self._jump[self._cmd_pointer]

    def _close_brackets(self):
        if self.cells[self.pointer]:
            self._cmd_pointer = self._jump[self._cmd_pointer]

    def print_cells(self):
        print(self.cells.print_pos(self.pointer))

    def print_cmd_history(self):
        print(self._cmd_pointer, self.cmd_history)

    def lib(self):
       print("I'm comming")

    @staticmethod
    def is_balanced(cmd_line):
        s = 0
        b = {'[':1,']':-1}
        for cmd in cmd_line:
            s += b.get(cmd, 0)
            if s<0: break
        return True if s==0 else False
        
    def execute(self, cmd_line):
        if not self.is_balanced(cmd_line):
            raise Exception("brackets not balanced!")
        cmds = {
            #BrainFuck commands
            '.':self._print_value,
            ',':self._read_value,
            '>':self._move_right,
            '<':self._move_left,
            '+':self._add,
            '-':self._sub,
            '[':self._open_brackets,
            ']':self._close_brackets,

            #Additional commands
            '*':self.print_cells,
            '&':self.print_cmd_history,
            '$':self.lib,
            }
        pos = len(self.cmd_history)
        stack = []
        cmd_line = [c for c in cmd_line if c in cmds]
        for cmd in cmd_line:
            self.cmd_history += cmd
            if cmd=='[':
                stack.append(pos)
            elif cmd==']':
                self._jump[pos] = stack.pop()
                self._jump[self._jump[pos]] = pos
            pos+=1
        while self._cmd_pointer<len(self.cmd_history):
            cmds[self.cmd_history[self._cmd_pointer]]()
            self._cmd_pointer += 1

    def interpreter(self):
        while True:
            cmd_line = input('>> ')
            while not self.is_balanced(cmd_line):
                tmp = input('.. ')
                cmd_line = cmd_line+tmp if tmp else 'skip'
            if not cmd_line: break
            self.execute(cmd_line)

class Cells(dict):
    def __init__(self, **kwargs):
        self[0]=0
        super(Cells, self).__init__(**kwargs)

    def __getitem__(self, key):
        if key in self:
            return super(Cells, self).__getitem__(key)
        return 0

    def print_pos(self, pos):
        k = [v for v in self.keys()]+[pos]
        m = min(k)
        M = max(k)
        print_list = [0 for _ in range(m, M+1)]
        for key,value in self.items():
            print_list[key-m] = value
        print_list[pos-m] = '|{}|'.format(print_list[pos-m])
        return ' '.join(map(str, print_list))

if __name__=="__main__":
    bf = BrainFuck()
    #bf.execute("++--[++]+[>+<-]+[+>>.>]-*&")
    bf.execute("")
    bf.interpreter()

