import sys

HFM_TO_MAP = {
    '+': {'section': 'wa', 'value': '0'},
    '-': {'section': 'wa', 'value': '1'},
    '|': {'section': 'wa', 'value': '2'},
    '#': {'section': 'wa', 'value': '0'},  # Spy-only door
    '@': {'section': 'wa', 'value': '0'},  # Mercenary-only door
    'M': {'section': 'sp', 'value': '0'},
    'S': {'section': 'sp', 'value': '1'},
    'T': {'section': 'it', 'value': '0'},  # Terminal
    'B': {'section': 'it', 'value': '1'},  # Briefcase
    'C': {'section': 'it', 'value': '2'},  # Camera
    'L': {'section': 'it', 'value': '3'}   # Lamp
}


def to_legacy_format(parsedMap):
    output = {
        'wa': [],
        'sp': [],
        'it': []
    }
    for y in range(len(parsedMap)):
        for x in range(len(parsedMap[y])):
            c = parsedMap[y][x]
            if c in HFM_TO_MAP:
                mapc = HFM_TO_MAP[c]
                output[mapc['section']].append(
                    ','.join([str(x), str(y), mapc['value']]))

    return output


def parse_map(filename):
    parsedMap = []
    size = []
    nbPlayers = []
    output = []

    with open(filename, 'r') as f:
        for line in f:
            if line == "" or line[0] == '#':  # Empty line or comment
                continue
            elif line.find('size') == 0:  # Line starts with size
                size = line.split()[1:]
            elif line.find('players') == 0:  # Line starts with players
                nbPlayers = line.split()[1:]
            else:  # Regular map line
                mapLine = []
                for c in line:
                    mapLine.append(c)
                parsedMap.append(mapLine)

    output = to_legacy_format(parsedMap)

    print "SLMap 1"
    print "Carte de test 2"
    print size[0], size[1]
    print 'sp:'
    print '\n'.join(''.join(l) for l in output['sp'])
    print 'wa:'
    print '\n'.join(''.join(l) for l in output['wa'])
    print 'it:'
    print '\n'.join(''.join(l) for l in output['it'])
    # print nbPlayers


if __name__ == '__main__':
    parse_map(sys.argv[1])
