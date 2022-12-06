entries = {}
with open('config', 'r') as txt:
    while True:
        line = txt.readline()
        if not line: 
            break
        line = line.strip()
        if not line or line[0] == '#':
            continue
        else:
            conf = line.split('=')[0]
            if conf in entries:# and entries[conf] != line:
                # print(f'{entries[conf]}, {line}')
                continue
            entries[conf] = line

mainline = {}
with open('mainline.config', 'r') as txt:
    while True:
        line = txt.readline()
        if not line: 
            break
        line = line.strip()
        if not line or line[0] == '#':
            continue
        else:
            conf = line.split('=')[0]
            if conf in mainline:# and entries[conf] != line:
                continue
            mainline[conf] = line

for k in entries:
    if not k in mainline:
        print(f'+{entries[k]}')

for k in mainline:
    if not k in entries:
        print(f'-{mainline[k]}')
