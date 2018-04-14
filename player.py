import pokemon

"""
Contains all the information a given player would know.

In practice, this is everything about their team, the battle format,
and a subset of the information on the enemy's team.

Unknown information on the enemy's team is filled in as "" and should
be updated as the battle progresses.
"""
class Player(object):
    def __init__(self, name, team, opposing_team, format):
        self.name = name
        self.team = team
        self.format = format
        self.weather = "Clear"
        self.hazards = ""
        self.opposing_team = Player.filter_known_attrs(opposing_team, format)

    def __init__(self, name, team, format):
        self.name = name
        self.team = team
        self.format = format
        self.weather = "Clear"
        self.hazards = ""
        self.opposing_team = [pokemon.Pokemon(), pokemon.Pokemon(), pokemon.Pokemon(),
                              pokemon.Pokemon(), pokemon.Pokemon(), pokemon.Pokemon()]

    """
    Filters out attributes of the enemy's team that are known in the given format.
    For example, in random battles, the enemy's team is not known, but it is in modes
    with a team preview.
    """
    def filter_known_attrs(opposing_team, format):
        ret = []
        if 'random' in format:
            ret = [pokemon.Pokemon(), pokemon.Pokemon(), pokemon.Pokemon(),
                   pokemon.Pokemon(), pokemon.Pokemon(), pokemon.Pokemon()]
        else:
            for p in opposing_team:
                ret.append(pokemon.Pokemon(species=p.species))
        return ret

    def __repr__(self):
        ret = self.name + ' : ' + self.format + ", weather is " + self.weather + "\n"

        # TODO: hazards are not differentiated by side
        if self.hazards:
            ret += "Hazards: " + self.hazards + "\n"

        for p in self.team:
            ret += str(p) + '\n'

        ret += 'Info known about other player:\n'
        for p in self.opposing_team:
            ret += str(p) + '\n'
        return ret + '\n'

    """
    Note: update_switch assumes species clause
    """
    def update_switch(self, poke, hp):
        for i, p in enumerate(self.team):
            # swap pokemon
            if p.species == poke:
                self.team[i] = self.team[0]
                self.team[0] = p
                break

    """
    Note: update_enemy_switch assumes species clause

    Unlike update_switch, this must take into account if the enemy team is unknown.
    Default species in that case is "" but is printed as "MissingNo"
    """
    def update_enemy_switch(self, poke, hp):
        swapped = False
        for i, p in enumerate(self.opposing_team):
            # swap pokemon
            if p.species == poke:
                self.opposing_team[i] = self.opposing_team[0]
                self.opposing_team[0] = p
                swapped = True
                break

        if not swapped:
            for i, p in enumerate(self.opposing_team):
                if not p.species:
                    p.species = poke
                    self.opposing_team[i] = self.opposing_team[0]
                    self.opposing_team[0] = p
                    swapped = True
                    break

        if not swapped:
            raise ValueError("Opponent's team is full and does not contain " + poke)


    def update_hp(self, poke, hp):
        self.team[0].hp = hp

    def update_enemy_hp(self, poke, hp):
        self.opposing_team[0].hp = hp

    def update_remove_item(self):
        self.team[0].item = "(none)"

    def update_enemy_remove_item(self):
        self.opposing_team[0].item = "(none)"
    
    def update_item(self, poke, item):
        self.team[0].item = item

    def update_enemy_item(self, poke, item):
        self.opposing_team[0].item = item

    def update_ability(self, poke, ability):
        # Already know own abilities
        pass

    def update_enemy_ability(self, poke, ability):
        self.opposing_team[0].ability = ability

    def update_weather(self, weather):
        self.weather = weather

    def update_status(self, poke, status):
        self.team[0].status = status

    def update_enemy_status(self, poke, status):
        self.opposing_team[0].status = status

    def update_hazards(self, hazards):
        self.hazards = hazards

    def update_boost(self, poke, ability, boost):
        self.team[0].boost = boost

    def update_enemy_boost(self, poke, ability, boost):
        self.opposing_team[0].boost = boost
    
    def update_set_boost(self, poke, ability, boost):
        self.team[0].boost = boost

    def update_enemy_set_boost(self, poke, ability, boost):
        self.opposing_team[0].boost = boost

    def update_enemy_move(self, poke, move):
        for p in self.opposing_team:
            if p.species == poke:
                if move not in p.moves:
                    p.moves.append(move)
                return

        raise ValueError('Could not find opponent\'s ' + poke)
    
    def update_species(self, species):
        self.team[0].species = species

    def update_enemy_species(self, species):
        self.opposing_team[0].species = species
