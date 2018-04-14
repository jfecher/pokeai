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
    def __init__(self, species="", item="", ability="", evs="", nature="", ivs="", moves=None, stats="", hp=100):
        self.species = species
        self.item = item
        self.ability = ability
        self.evs = evs
        self.nature = nature
        self.ivs = ivs
        self.moves = moves if moves else ["", "", "", ""]
        self.stats = stats
        self.hp = hp
        self.status = ""
        self.boost = ""

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
        if self.status: s += ", " + self.status
        if self.boost: s += "\nBoost: " + str(self.boost)
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

            # whirlwind / roar
            elif l.startswith('|drag|'):
                regex = re.compile(r'\|drag\|(p1|p2)a: ([^|]+)\|([^,]+)[^|]+\|(\d+)/100')
                match = regex.match(l)
                if match:
                    p_name, poke, species, hp = match.groups()
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
                updates += l

            elif l.startswith('|-item|'):
                regex = re.compile(r'\|-item\|(p1|p2)a: (\w+)\|([ A-Za-z0-9_]+)\|')
                match = regex.match(l)
                if match:
                    p_name, poke, item = match.groups()
                    if p_name == "p1":
                        p1.update_item(poke, item)
                        p2.update_enemy_item(poke, item)
                    else:
                        p1.update_enemy_item(poke, item)
                        p2.update_item(poke, item)
                updates += l

            elif l.startswith('|-damage|') or l.startswith('|-heal|'):
                regex = re.compile(r'\|-damage\|(p1|p2)a: (\w+)\|(\d+)/100')
                match = regex.match(l)

                # If the mon faints the hp is not given as a percentage
                if not match:
                    match = re.compile(r'\|-damage\|(p1|p2)a: ([^|]+)\|(0) fnt').match(l)

                if not match:
                    match = re.compile(r'\|-heal\|(p1|p2)a: ([^|]+)\|(\d+)/100').match(l)

                if match:
                    p_name, poke, hp = match.groups()
                    if p_name == "p1":
                        p1.update_hp(poke, hp)
                        p2.update_enemy_hp(poke, hp)
                    else: 
                        p1.update_enemy_hp(poke, hp)
                        p2.update_hp(poke, hp)

                updates += l

            elif l.startswith('|move|'):
                regex = re.compile(r'\|move\|(p1|p2)a: ([ \w]+)\|([^|]+)')
                match = regex.match(l)
                if match:
                    p_name, poke, move = match.groups()
                    if p_name == "p1":
                        p2.update_enemy_move(poke, move)
                    else: 
                        p1.update_enemy_move(poke, move)
                updates += l

            elif l.startswith('|-ability|'):
                regex = re.compile(r'\|-ability\|(p1|p2)a: ([^|]+)\|([^|\n]+)')
                match = regex.match(l)
                if match:
                    p_name, poke, ability = match.groups()
                    if p_name == "p1":
                        p1.update_ability(poke, ability)
                        p2.update_enemy_ability(poke, ability)
                    else: 
                        p1.update_enemy_ability(poke, ability)
                        p2.update_ability(poke, ability)
                updates += l

            # TODO: update boost field to array of stats
            elif l.startswith('|-boost|'):
                regex = re.compile(r'\|-boost\|(p1|p2)a: ([^|]+)\|(atk|def|spa|spd|spe)\|(\d+)')
                match = regex.match(l)
                if match:
                    p_name, poke, ability, boost = match.groups()
                    if p_name == "p1":
                        p1.update_boost(poke, ability, int(boost))
                        p2.update_enemy_boost(poke, ability, int(boost))
                    else:
                        p1.update_enemy_boost(poke, ability, int(boost))
                        p2.update_boost(poke, ability, int(boost))
                updates += l

            elif l.startswith('|-unboost|'):
                regex = re.compile(r'\|-boost\|(p1|p2)a: ([^|]+)\|(atk|def|spa|spd|spe|evasion|accuracy)\|(\d+)')
                match = regex.match(l)
                if match:
                    p_name, poke, ability, boost = match.groups()
                    if not boost: boost = 1
                    if p_name == "p1":
                        p1.update_boost(poke, ability, -int(boost))
                        p2.update_enemy_boost(poke, ability, -int(boost))
                    else:
                        p1.update_enemy_boost(poke, ability, -int(boost))
                        p2.update_boost(poke, ability, -int(boost))
                updates += l

            # bellydrum, mainly
            elif l.startswith('|-setboost|'):
                regex = re.compile(r'\|-setboost\|(p1|p2)a: ([^|]+)\|(atk|def|spa|spd|spe|evasion|accuracy)\|(-?\d+)')
                match = regex.match(l)
                if match:
                    p_name, poke, ability, boost = match.groups()
                    if p_name == "p1":
                        p1.update_set_boost(poke, ability, int(boost))
                        p2.update_enemy_set_boost(poke, ability, int(boost))
                    else:
                        p1.update_enemy_set_boost(poke, ability, int(boost))
                        p2.update_set_boost(poke, ability, int(boost))
                updates += l

            elif l.startswith('|-weather|'):
                regex = re.compile(r'\|-weather\|(\w+)\|')
                match = regex.match(l)
                if match:
                    weather = match.groups()
                    p1.update_weather(weather)
                    p2.update_weather(weather)
                updates += l

            elif l.startswith('|-status|'):
                regex = re.compile(r'\|-status\|(p1|p2)a: (\w+)\|(\w+)')
                match = regex.match(l)
                if match:
                    p_name, poke, status = match.groups()
                    if p_name == "p1":
                        p1.update_status(poke, status)
                        p2.update_enemy_status(poke, status)
                    else:
                        p1.update_enemy_status(poke, status)
                        p2.update_status(poke, status)
                updates += l

            # stealthrocks, spikes, barrier, reflect, ...
            elif l.startswith('|-sidestart|'):
                regex = re.compile(r'\|-sidestart\|(p1|p2): (\w+)\|(\w+)')
                match = regex.match(l)
                if match:
                    p_name, p_nickname, hazards = match.groups()
                    p1.update_hazards(hazards)
                    p2.update_hazards(hazards)
                updates += l

            elif l.startswith('|turn|'):
                # Generate turn decision
                updates += l
                pass

            elif l.startswith('|faint|'):
                regex = re.compile(r'\|faint\|(p1|p2)a: (\w+)')
                match = regex.match(l)
                if match:
                    p_name, poke = match.groups()
                    # TODO
                updates += l

            # formechange is given for, eg. minior to minior-meteor
            # formechange does NOT include mega evolution or moves like substitute
            elif l.startswith('|-formechange|'):
                regex = re.compile(r'\|-formechange\|(p1|p2)a: ([ \w]+)\|([^|]+)')
                match = regex.match(l)
                if match:
                    p_name, poke, forme = match.groups()
                    # TODO
                updates += l

            # Most likely cause is from mega-evolution
            elif l.startswith('|detailschange|'):
                regex = re.compile(r'\|detailschange\|(p1|p2)a: ([^|]+)\|([^|]+),')
                match = regex.match(l)
                if match:
                    p_name, poke, species = match.groups()
                    if p_name == "p1":
                        p1.update_species(poke, species)
                        p2.update_enemy_species(poke, species)
                    else:
                        p1.update_enemy_species(poke, species)
                        p2.update_species(poke, species)
                updates += l

            # Pain Split
            # May need to be extended to only set 1 pokemon's hp instead of both.
            elif l.startswith('|-sethp|'):
                regex = re.compile(r'\|-sethp\|(p1|p2)a: ([^|]+)\|(\d+)/100\|(p1|p2)a: ([^|]+)\|(\d+)/100')
                match = regex.match(l)
                pl, pokel, hpl, pr, poker, hpr = match.groups()
                if pl == "p1":
                    p1.update_hp(pokel, hpl)
                    p2.update_enemy_hp(pokel, hpl)
                    p1.update_enemy_hp(poker, hpr)
                    p2.update_hp(poker, hpr)
                else: 
                    p1.update_hp(poker, hpr)
                    p2.update_enemy_hp(poker, hpr)
                    p1.update_enemy_hp(pokel, hpl)
                    p2.update_hp(pokel, hpl)
                updates += l

            # For moves like substitute
            elif l.startswith('|-start|'):
                regex = re.compile(r'\|-start\|(p1|p2)a: ([^|]+)\|(.+)')
                match = regex.match(l)
                if match:
                    p_name, poke, event = match.groups()
                    # TODO

            elif not l.startswith('|request|') and l != 'sideupdate\n' and l != 'p1\n' and l != 'p2\n':
                updates += "unhandled - " + l


            regex = re.compile(r'.*(p1|p2).+\[from\] item: ([^|\n]+)')
            match = regex.match(l)
            if match:
                p_name, item = match.groups()
                if p_name == "p1":
                    p1.update_item(poke, item)
                    p2.update_enemy_item(poke, item)
                else:
                    p1.update_enemy_item(poke, item)
                    p2.update_item(poke, item)


    return p1, p2, updates
