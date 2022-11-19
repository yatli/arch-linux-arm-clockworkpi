entries = {}
with open('config', 'r') as txt:
    while True:
        line = txt.readline()
        if not line: 
            break
        line = line.strip()
        conf = line.split('=')[0]
        if conf in entries and entries[conf] != line:
            print(f'{entries[conf]}, {line}')
        entries[conf] = line
