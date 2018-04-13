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
    updates_re = re.compile(r'sideupdate\n.+\n.+\n\n')
    updates = updates_re.findall(msg)

    lines = re.compile(r'.*\n')

    braces = re.compile(r'\{.*\}', re.M)
    for update in updates:
        l = lines.findall(update)[2]
        if l.startswith('|request|'):
            l = l[9:]

        j = json.loads(l)
        print(json.dumps(j, sort_keys=True, indent=4, separators=(',', ': ')))
