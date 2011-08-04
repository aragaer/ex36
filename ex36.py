import random
from copy import copy
dbg = True

# these numbers determine the minimum and maximum numbers of yet unopened doors
MIN_DOORS = 3
MAX_DOORS = 7

LEVEL_TO_WIN = 10

n_doors = 0
current_room = None

MONSTERS = []
CURSES = []
TREASURES = []

level = 1
power = level
inventory = []
gold = 0
slots = {
    'headgear': None,
    'armor': None,
    'footwear': None,
}
free_hands = 2

DIRECTIONS = ['north', 'south', 'east', 'west', 'up', 'down']
STAIRS = DIRECTIONS.index('up') # lowest number of direction which is described using "stairs <to>"
N_DIRS = len(DIRECTIONS)

def get_opposite_direction(d):
    return d - 1 if d % 2 else d + 1

def get_opposite_dir_name(d):
    return DIRECTIONS[get_opposite_direction(d)]

def nice_print_list(l):
    if len(l) > 2:
        return " and ".join([", ".join(l[:-1]), l[-1]])
    else:
        return " and ".join(l)

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
        print "DBG:", string

class ImmediateTreasure:
    """Treasures that are triggered immediately"""
    def __init__(self, name, desc, effect):
        self.name = name
        self.desc = desc
        self.effect = effect

class EquipmentTreasure:
    """These are equipped"""
    def __init__(self, name, desc, cost, bonus, slot, is_large = False):
        self.name = name
        self.desc = desc
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
        if self.equipped:
            return self.name + ' (equipped)'
        else:
            return self.name

class Monster:
    """A monster!"""

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
        except Exception as exc:
            debug("Exception: %s\npossible_doors = %s\nn_walls = %d" % (exc, possible_doors, n_walls))

#        debug("self doors: [%r]" % self.doors)
#        debug("%d unexplored doors" % n_doors)
        have_doors = filter(None, self.doors[:STAIRS])
        have_stairs = filter(None, self.doors[STAIRS:])

        self.doors = have_doors + have_stairs

        d_desc = ['There']

        if have_doors:
            d_desc.append('is a door' if len(have_doors) == 1 else 'are doors')
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

        if entrance:
            obstacle = random.choice([MONSTERS, CURSES, None])
            self.obstacle = random.choice(obstacle) if obstacle else None
        else:                                           # starting room must be empty
            self.obstacle = None

    def getObstacle(self):
        if self.obstacle == None:
            return "nothing"
        elif isinstance(self.obstacle, Monster):
            return self.obstacle.getDesc()

def print_room(unused = None):
    print "You are in a %s" % current_room.desc
    print current_room.d_desc
    print "There is %s here." % current_room.getObstacle()

def print_inventory(unused = None):
    stuff = map(lambda x: x.__str__(), inventory)
    if gold:
        stuff.append("%d gold" % gold)

    if stuff:
        print "You have %s" % nice_print_list(stuff)
    else:
        print "You have nothing"

def get_treasure(number):
    global inventory
    new_stuff = []
    while number:
        sample = min(number, len(TREASURES))
        new_stuff += random.sample(TREASURES, sample)
        number -= sample    

    print "You found", nice_print_list(map(lambda x: x.name, new_stuff))

    immediates = []
    for item in new_stuff:
        if isinstance(item, ImmediateTreasure):
            immediates.append(item)
        else:
            inventory.append(copy(item))

    for item in immediates:
        print item.desc
        item.effect()

CMD_GO = 'go'
CMD_FIGHT = 'attack'
CMD_LOOK = 'look'
CMD_INV = 'inventory'
CMD_HELP = 'help'
CMD_ITEM = 'examine'
CMD_EQUIP = 'equip'
CMD_UNEQUIP = 'unequip'
CMD_SELL = 'sell'

def print_actions(unused):
    print "You can do the following:"
    for d in current_room.doors:
        print "-", CMD_GO, d
    if isinstance(current_room.obstacle, Monster):
        print "-", CMD_FIGHT, current_room.obstacle.name

def move_to(d):
    global current_room, n_doors
    if len(d) != 1:
        print "Go where?"
        return

    d = d.pop()

    if d not in DIRECTIONS:
        print "You can't go there!"
        return

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
        current_room = Room(DIRECTIONS.index(d))
        rooms.append(current_room)
    print_room()

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

def examine(name_parts):
    for name in nice_parse_list(name_parts):
        do_examine(name.strip())

def do_examine(name):
    item = get_inv_item(name)
    if not item:
        print "You don't have any %s to examine" % name
        return

    print "You examine %s" % name
    if item.desc:
        print item.desc
    else:
        print "It is just a", item.name

    if item.cost:
        print "It is worth %d gold" % item.cost
    else:
        print "It is worth nothing"
    print

def equip(name_parts):
    for name in nice_parse_list(name_parts):
        do_equip(name.strip())

def do_equip(name):
    global power, free_hands
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
        power += item.bonus
        return

    if item.need_hands == 0:
        other = slots[item.slot]
        if other:
            print "You can't equip %s since you already got %s as %s" % (name, other.name, item.slot)
        else:
            print "You equip %s as %s" % (name, item.slot)
            slots[item.slot] = item
            item.equipped = True
            power += item.bonus
        return

    if free_hands < item.need_hands:
        if item.need_hands == 1:
            print "You need a free hand to hold %s" % name
        else:
            print "You need %d free hands to hold %s and you have %d" % (item.need_hands, name, free_hands)
        return

    free_hands -= item.need_hands

    print "You equip %s" % name
    power += item.bonus
    item.equipped = True

def unequip(name_parts):
    for name in nice_parse_list(name_parts):
        do_unequip(name.strip())

def do_unequip(name):
    global power, free_hands
    item = get_inv_item(name, True)
    if not item:
        print "You got no %s to unequip" % name
        return

    if not item.equipped:
        print "%s is already unequipped" % name
        return

    print "You put %s to your backpack" % name
    item.equipped = False
    power -= item.bonus
    if item.need_hands:
        free_hands += item.need_hands
    else:
        slots[item.slot] = None

def sell(name_parts):
    for name in nice_parse_list(name_parts):
        do_sell(name.strip())

def do_sell(name):
    global gold, level, inventory
    item = get_inv_item(name, False)
    if not item:
        print "You got no %s to sell" % name
        return

    if item.equipped:
        print "%s is equipped" % name
        return

    if not item.cost:
        print "%s is wortheless. You threw it away." % name
        return

    levels = (gold + item.cost) // 1000 - gold // 1000

    inventory.remove(item)
    gold += item.cost

    print "Sold %s! You have %d gold now" % (name, gold)

    if levels == 1:
        print "You go up a level"
    elif levels:
        print "You go up %d levels" % levels

COMMANDS = {
    CMD_GO: move_to,
    CMD_LOOK: print_room,
    CMD_INV: print_inventory,
    CMD_HELP: print_actions,
    CMD_ITEM: examine,
    CMD_EQUIP: equip,
    CMD_UNEQUIP: unequip,
    CMD_SELL: sell
}

def do_turn():
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
    while level < LEVEL_TO_WIN:
        do_turn()
    print "Congratulations! You are level %d! You won!" % level
