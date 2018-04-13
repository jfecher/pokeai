import re
import json

class Pokemon():
    def __init__(self, species, item, ability, evs, nature, ivs, moves):
        self.species = species
        self.item = item
        self.ability = ability
        self.evs = evs
        self.nature = nature
        self.ivs = ivs
        self.moves = moves

    def __str__(self):
        s = self.species
        if self.item:
            s += " @ " + self.item

        s += "\nAbility: " + self.ability
        s += "\nEVs: " + self.evs
        s += "\n" + self.nature + " Nature"

        if self.ivs:
            s += "\nIVs: " + self.ivs

        for move in self.moves:
            s += "\n- " + move

        return s


def parse_sideupdate(msg):
    lines = re.compile(r'.*\n').findall(msg)

    for l in lines:
        if l.startswith('|request|'):
            l = l[9:]

            j = json.loads(l)
            for i in j['side']['pokemon']:
                print(i['ident'], end='\t')
                print(i['moves'])
            print('')

        else:
            print(l, end='')
            continue

        # print(json.dumps(j, sort_keys=False, indent=4, separators=(',', ': ')))
