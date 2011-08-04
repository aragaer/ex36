import random
from copy import copy
dbg = True

# these numbers determine the minimum and maximum numbers of yet unopened doors
MIN_DOORS = 3
MAX_DOORS = 7

LEVEL_TO_WIN = 10

n_doors = 0
current_room = None
last_entrance = None

MONSTERS = []
CURSES = []
TREASURES = []

level = 1
bonus = 0
inventory = []
gold = 0
slots = {'headgear': None, 'armor': None, 'footwear': None}
free_hands = 2

DIRECTIONS = ['north', 'south', 'east', 'west', 'up', 'down']
STAIRS = DIRECTIONS.index('up') # lowest number of direction which is described using "stairs <to>"
N_DIRS = len(DIRECTIONS)

def get_opposite_direction(d):
    return d - 1 if d % 2 else d + 1

def nice_print_list(l):
    tail = l.pop()
    return ' and '.join(filter(None, [', '.join(l), tail]))

def nice_parse_list(n):
    if type(n).__name__ == 'list':
        n = ' '.join(n)
    try:
        (n, tail) = n.split('and')
        n = n.split(',')
        n.append(tail)
    except ValueError: # no 'and'
        n = n.split(',')

    return map(lambda x: x.strip(), n)

def debug(string):
    if dbg:
        print 'DBG:', string

class ImmediateTreasure:
    """Treasures that are triggered immediately"""
    def __init__(self, name, desc, effect):
        self.name = name
        self.desc = desc
        self.effect = effect
    def __str__(self):
        return self.name

class EquipmentTreasure:
    """These are equipped"""
    def __init__(self, name, desc, cost, bonus, slot, is_large = False):
        self.name = name
        self.desc = desc if desc else "It's just a %s" % name
        self.bonus = bonus
        self.cost = cost
        self.slot = slot
        self.is_large = is_large
        if slot == 'hand':
            self.need_hands = 1
        elif slot == 'two hands':
            self.need_hands = 2
        else:
            self.need_hands = 0
        self.equipped = False
    def __str__(self):
        return self.name + (' (equipped)' if self.equipped else '')

class Monster:
    """A monster!"""
    def defaultHostile():
        return True
    def defaultRA():
        return random.randint(1, 6) > 4
    def __init__(self, name, level, treasure, bad, exp = 1,
                hostile = defaultHostile, ra = defaultRA):
        self.name = name
        self.level = level
        self.treasure = treasure
        self.bad = bad
        self.exp = exp
        self.hostile = hostile
        self.ra = ra
    def getDesc(self):
        return self.name

class Curse:
    """A curse!"""

class Room:
    types = ['hall', 'cave', 'room']
    sizes = ['huge', 'large', 'average-sized', 'small', 'tiny']
    descs = ['dark', 'filthy', 'clean', 'dry', 'wet']
    def __init__(self, entrance = -1):
        global n_doors
        self.doors = DIRECTIONS[:]
        possible_doors = range(0, N_DIRS)
        new_doors = random.randint(max(0, MIN_DOORS - n_doors), min(N_DIRS, MAX_DOORS - n_doors))

#        debug("min %d max %d got %d" % (MIN_DOORS, MAX_DOORS, n_doors))
#        debug("random from %d to %d gives %d" % (max(0, MIN_DOORS - n_doors), min(N_DIRS, MAX_DOORS - n_doors), new_doors))

        if entrance == -1:
            old_door = 0
        else:
            back = get_opposite_direction(entrance)
            setattr(self, DIRECTIONS[back], current_room)
            setattr(current_room, DIRECTIONS[entrance], self)
            del possible_doors[back]
            new_doors -= 1;
            old_door = 1

        if n_doors + new_doors < MIN_DOORS:
            new_doors = MIN_DOORS - n_doors
        elif n_doors + new_doors > MAX_DOORS:
            new_doors = MAX_DOORS - n_doors

        n_doors += new_doors
        n_walls = N_DIRS - new_doors - old_door

        try:
          for wall in random.sample(possible_doors, n_walls):
            self.doors[wall] = None
        except ValueError as ve:
            debug("picking %d walls from %s: %s" % (n_walls, possible_doors, ve))

        debug("self doors: [%r]" % self.doors)
#        debug("%d unexplored doors" % n_doors)
        have_doors = filter(None, self.doors[:STAIRS])
        have_stairs = filter(None, self.doors[STAIRS:])

        self.doors = have_doors + have_stairs

        d_desc = ['There']

        if have_doors:
            d_desc.append('are doors' if new_doors else 'is a door')
            d_desc.append('leading %s' % nice_print_list(have_doors))

        if have_stairs:
            d_desc.append('and' if have_doors else 'are')
            d_desc.append('stairs leading %s' % nice_print_list(have_stairs))

        self.d_desc = ' '.join(d_desc)                

        t = random.choice(Room.types)
        s = random.choice(Room.sizes)
        if random.random() > 0.5:
            self.desc = "%s %s %s" % (s, random.choice(Room.descs), t)
        else:
            self.desc = "%s %s" % (s, t)

        if entrance == -1:                          # starting room must be empty
            self.obstacle = None
        else:
            obstacle = random.choice([MONSTERS, CURSES, None])
            self.obstacle = random.choice(obstacle) if obstacle else None

    def getObstacle(self):
        if self.obstacle == None:
            return "nothing"
        elif isinstance(self.obstacle, Monster):
            return self.obstacle.getDesc()

def dead(why):
    print why
    print "You are dead. Game over."
    exit(0)

def win():
    print "Congratulations! You are level %d! You won!" % level
    exit(0)

def print_room(unused = None):
    print "You are in a %s" % current_room.desc
    print current_room.d_desc
    print "There is %s here." % current_room.getObstacle()

def print_inventory(unused = None):
    stuff = map(str, inventory)
    if gold:
        stuff.append("%d gold" % gold)

    print 'You have', nice_print_list(stuff) if stuff else 'nothing'

def get_treasure(number):
    global inventory
    new_stuff = []
    while number:
        sample = min(number, len(TREASURES))
        new_stuff += random.sample(TREASURES, sample)
        number -= sample    

    print "You found", nice_print_list(map(str, new_stuff))

    for item in new_stuff:
        if isinstance(item, ImmediateTreasure):
            print item.desc
            item.effect()
        else:
            inventory.append(copy(item))


CMD_GO = 'go'
CMD_FIGHT = 'attack'
CMD_LOOK = 'look'
CMD_INV = 'inventory'
CMD_HELP = 'help'
CMD_ITEM = 'examine'
CMD_EQUIP = 'equip'
CMD_UNEQUIP = 'unequip'
CMD_SELL = 'sell'
CMD_SELF = 'status'
CMD_ATTACK = 'attack'

def print_actions(unused):
    print "You can do the following:"
    for d in current_room.doors:
        print "-", CMD_GO, d
    if isinstance(current_room.obstacle, Monster):
        print "-", CMD_FIGHT, current_room.obstacle.name

def attack(monster_name):
    """used to attack non-hostile monsters"""
    name = ' '.join(monster_name)
    try:
        if name != current_room.obstacle.name:
            raise
    except:
        print "There is no %s to attack here" % name
    else:
        battle(current_room.obstacle)

def battle(monster):
    global current_room, level
    if monster.level < level + bonus:
        print "You easily dispatch %s" % monster.name
        level += monster.exp
        if level >= LEVEL_TO_WIN:
            win()
        current_room.obstacle = None
        get_treasure(monster.treasure)
    else:
        back = DIRECTIONS[last_entrance]
        print "You can't win and have to run back %s from %s" % (back, monster.name)
        if monster.ra():
            print "You ran away succesfully"
            move_to([DIRECTIONS[last_entrance]])
        else:
            print "You failed to run away!"
            monster.bad()
            print "Monster goes away"
            current_room.obstacle = None

def encounter(monster):
    if monster.hostile():
        battle(monster)
    else:
        print "%s is not hostile" % monster.name

def move_to(d):
    global current_room, n_doors, last_entrance
    if len(d) != 1:
        print "Go where?"
        return

    d = d.pop()

    if d not in DIRECTIONS:
        print "You can't go there!"
        return

    didx = DIRECTIONS.index(d)

    if d not in current_room.doors:
        if d == 'up':
            print "You jump for a while."
        elif d == 'down':
            print "You stomp for a while."
        else:
            print "You bump into a wall."
        return

    try:
        current_room = getattr(current_room, d)
    except:
        n_doors -= 1
        current_room = Room(didx)
        rooms.append(current_room)
    last_entrance = get_opposite_direction(didx)
    print_room()
    debug("You entered from %s" % DIRECTIONS[last_entrance])

    if isinstance(current_room.obstacle, Monster):
        encounter(current_room.obstacle)

def fix_level():
    global level
    if level >= LEVEL_TO_WIN:
        print "Too bad you have to defeat a monster to get last level"
        level = LEVEL_TO_WIN - 1
    elif level < 1:
        print "Lucky you, can't go below level 1"
        level = 1

def get_inv_item(name, equipped = None):
    """Tries to find an item.
If equipped is None, we don't care if it is equipped, otherwise try to get as requested.
If equipped is not none and we can't find it, find the one ignoring the flag."""
    if not equipped is None:
        for item in inventory:
            if item.name == name and item.equipped == equipped:
                return item

    for item in inventory:
        if item.name == name:
            return item

    return None

def examine(name):
    item = get_inv_item(name)
    if item:
        print "You examine %s" % name
        print item.desc
        print "It is worth", "%d gold" % item.cost if item.cost else "nothing"
    else:
        print "You don't have any %s to examine" % name
    print

def equip(name):
    global bonus, free_hands
    item = get_inv_item(name, False)
    if not item:
        print "You got no %s to equip" % name
        return

    if item.equipped:
        print "%s is already equipped" % name
        return

    if item.slot is None:
        print "You equip %s" % name
        item.equipped = True
        bonus += item.bonus
        return

    if item.need_hands == 0:
        other = slots[item.slot]
        if other:
            print "You can't equip %s since you already got %s as %s" % (name, other.name, item.slot)
        else:
            print "You equip %s as %s" % (name, item.slot)
            slots[item.slot] = item
            item.equipped = True
            bonus += item.bonus
        return

    if free_hands < item.need_hands:
        if item.need_hands == 1:
            print "You need a free hand to hold %s" % name
        else:
            print "You need %d free hands to hold %s and you have %d" % (item.need_hands, name, free_hands)
        return

    free_hands -= item.need_hands

    print "You equip %s" % name
    bonus += item.bonus
    item.equipped = True

def unequip(name):
    item = get_inv_item(name, True)
    if not item:
        print "You got no %s to unequip" % name
        return

    if not item.equipped:
        print "%s is already unequipped" % name
        return

    print "You put %s to your backpack" % name
    unequip_internal(item)

def unequip_internal(item):
    global bonus, free_hands
    item.equipped = False
    bonus -= item.bonus
    if item.need_hands:
        free_hands += item.need_hands
    else:
        slots[item.slot] = None

def sell(name):
    global gold, level, inventory
    item = get_inv_item(name, False)
    if not item:
        print "You got no %s to sell" % name
        return

    if item.equipped:
        print "%s is equipped" % name
        return

    inventory.remove(item)
    if not item.cost:
        print "%s is wortheless. You threw it away." % name
        return

    levels = (gold + item.cost) // 1000 - gold // 1000
    gold += item.cost

    print "Sold %s! You have %d gold now" % (name, gold)

    if levels == 1:
        print "You go up a level"
    elif levels:
        print "You go up %d levels" % levels

def status(unused = None):
    print "You are level %d. Your combat strength is %d." % (level, level + bonus)

def mass(func):
    return lambda names: [func(name) for name in nice_parse_list(names)]

COMMANDS = {
    CMD_GO: move_to,
    CMD_LOOK: print_room,
    CMD_INV: print_inventory,
    CMD_HELP: print_actions,
    CMD_ITEM: mass(examine),
    CMD_EQUIP: mass(equip),
    CMD_UNEQUIP: mass(unequip),
    CMD_SELL: mass(sell),
    CMD_SELF: status,
    CMD_ATTACK: attack,
}

def do_turn():
    fix_level()

    action = raw_input("> ").split(' ');
    print

    act = action.pop(0)
    try:
        COMMANDS[act](action)
    except KeyError:
        print "You have no idea how to do that"

if __name__ == "__main__":
    with open("game.conf") as conf:
        for line in conf.readlines():
            (name, val) = map(lambda s: s.strip(), line.split('='))
            if name in ['treasures', 'monsters', 'curses']:
                for tfile in val.split(','):
                    execfile(tfile.strip())

    current_room = Room()
    rooms = [current_room]
    print_room()
    get_treasure(4)
    while True:
        do_turn()
