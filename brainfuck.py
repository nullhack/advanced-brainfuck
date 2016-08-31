def bf(code, mem_len=1000):
    data = [0] * mem_len
    cp = 0
    dp = 0
    stack = []
    while cp < len(code):
        cmd = code[cp]
        if   cmd == '>': dp += 1
        elif cmd == '<': dp -= 1
        elif cmd == '+': data[dp] += 1 
        elif cmd == '-': data[dp] -= 1 
        elif cmd == '.': print(">> ", chr(data[dp]))
        elif cmd == ',': data[dp] = ord(raw_input("<< "))
        elif cmd == '[':
            stack.append(cp)
        elif cmd == ']':
            back = stack.pop()
            cp = back-1 if data[dp] else cp
        cp += 1

if __name__=="__main__":
    import sys
    bf(sys.argv[1])
