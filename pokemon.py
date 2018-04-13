import re, json, player
from player import Player

"""
A sideupdate contains the following information under
sideupdate['side']['pokemon']:

'ident': 'p2: Furfrou'
'details': 'Furfrou, L83, F'
'condition': '260/260'
'active': true,
'stats': {
    'atk': 180,
    'def': 147',
    'spa': 156,
    'spd': 197,
    'spe': 217
},
'moves': [
    'uturn',
    'thunderwave',
    'rest',
    'suckerpunch'
],
'baseability': 'furcoat',
'item': 'chestoberry',
'pokeball': 'pokeball',
'ability': 'furcoat'


of this information, only the following are known to an opponent at all times:
'ident': 'p2: Furfrou'
'details': 'Furfrou, L83, F'
'active': true,
"""

class Pokemon(object):
    def __init__(self, species="", item="", ability="", evs="", nature="", ivs="", moves=["","","",""], stats="", hp=100):
        self.species = species
        self.item = item
        self.ability = ability
        self.evs = evs
        self.nature = nature
        self.ivs = ivs
        self.moves = moves
        self.stats = stats
        self.hp = hp

    def from_json(json):
        self = Pokemon()
        self.species = json['ident'][4:]
        self.item = json['item']
        self.ability = json['ability']
        self.stats = json['stats']
        self.moves = json['moves']
        return self


    def __repr__(self):
        if self.species:
            s = self.species
        else:
            s = "MissingNo"

        if self.item: s += " @ " + self.item
        s += ", " + str(self.hp) + "% hp"
        if self.ability: s += "\nAbility: " + self.ability
        if self.evs: s += "\nEVs: " + self.evs
        if self.nature: s += "\n" + self.nature + " Nature"
        if self.ivs: s += "\nIVs: " + self.ivs
        if self.stats: s += "\nStats: " + str(self.stats)

        for move in self.moves:
            if move: s += "\n- " + move

        return s

"""
Parses the initial teams for each player from a |request| message
"""
def parse_initial_teams(msg, format):
    if not msg.startswith('|request'):
        raise ValueError("Invalid Request")

    msg = msg[9:]

    side = json.loads(msg)['side']
    name = side['id']
    team = side['pokemon']

    for i, e in enumerate(team):
        team[i] = Pokemon.from_json(team[i])

    p = Player(name, team, format)
    return p, name


"""
Parse a response from the battle server.

This handles both sideupdates and regular updates:
    sideupdates: an omniscient update that only the server should know.
        - Contains all information about every pokemon/player (all stats, moves, etc.)

    update: A normal battle update that both players see at the end of each turn
        - May 
"""
def parse_update(msg, p1, p2, format):
    lines = re.compile(r'.*\n').findall(msg)

    updates = ""

    for l in lines:
        if p1 == "" or p2 == "":
            if l.startswith('|request|'):
                p, name = parse_initial_teams(l, format)
                if name == "p1": p1 = p
                else: p2 = p

        # p1 and p2 are defined
        else:
            if l.startswith('|switch|'):
                regex = re.compile(r'\|switch\|(p1|p2)a: (\w+)\|.+\|(\d+)/100')
                match = regex.match(l)
                if match:
                    p_name, poke, hp = match.groups()
                    if p_name == "p1":
                        p1.update_switch(poke, hp)
                        p2.update_enemy_switch(poke, hp)
                    else:
                        p1.update_enemy_switch(poke, hp)
                        p2.update_switch(poke, hp)

                updates += l

            elif l.startswith('|-enditem|'):
                regex = re.compile(r'\|-enditem\|(p1|p2)a')
                match = regex.match(l)
                if match:
                    p_name = match.groups()
                    if p_name == "p1":
                        p1.update_remove_item()
                        p2.update_enemy_remove_item()
                    else:
                        p1.update_enemy_remove_item()
                        p2.update_remove_item()


            elif l.startswith('|-damage|'):
                regex = re.compile(r'\|-damage\|(p1|p2)a: (\w+)\|(\d+)/100')
                match = regex.match(l)
                if match:
                    p_name, poke, hp = match.groups()
                    if p_name == "p1":
                        p1.update_hp(poke, hp)
                        p2.update_enemy_hp(poke, hp)
                    else: 
                        p1.update_enemy_hp(poke, hp)
                        p2.update_hp(poke, hp)

            elif not l.startswith('|request|') and l != 'sideupdate\n' and l != 'p1\n' and l != 'p2\n':
                updates += l

    # p1.update(updates)
    # p2.update(updates)
    return p1, p2, updates
