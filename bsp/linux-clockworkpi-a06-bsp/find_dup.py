entries = {}
with open('config', 'r') as txt:
    while True:
        line = txt.readline()
        if not line: 
            break
        line = line.strip()
        if not line:
            print()
        elif line[0] == '#':
            if line.endswith(' is not set'):
                conf = line[2:-11]
                if conf in entries:
                    print(f'# [DUP] {conf} is not set')
                    continue
                entries[conf] = line
            print(line)
        else:
            conf = line.split('=')[0]
            if conf in entries:# and entries[conf] != line:
                # print(f'{entries[conf]}, {line}')
                print(f'# [DUP] {line}')
                continue
            entries[conf] = line
            print(line)
