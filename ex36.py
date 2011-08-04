import random
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
            if obstacle == None or len(obstacle) == 0:  # temporary safeguard
                self.obstacle = None
            else:
                self.obstacle = random.choice(obstacle)
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
    stuff = map(lambda x: x.name, inventory)
    if gold:
        stuff.append("%d gold" % gold)

    if stuff:
        print "You have %s" % nice_print_list(stuff)
    else:
        print "You have nothing"

def get_treasure(number):
    global inventory
    new_stuff = []
    while (number):
        sample = min(number, len(TREASURES))
        new_stuff += random.sample(TREASURES, sample)
        number -= sample    

    print "You found", nice_print_list(map(lambda x: x.name, new_stuff))

    immediates = []
    for item in new_stuff:
        if isinstance(item, ImmediateTreasure):
            immediates.append(item)
        else:
            inventory.append(item)

    for item in immediates:
        print item.desc
        item.effect()

CMD_GO = 'go'
CMD_FIGHT = 'attack'
CMD_LOOK = 'look'
CMD_INV = 'inventory'
CMD_HELP = 'help'

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
        print "You bump into a wall."
        return

    try:
        current_room = getattr(current_room, d)
    except:
        n_doors -= 1
        current_room = Room(DIRECTIONS.index(d))
        rooms.append(current_room)
    print_room()

COMMANDS = {
    CMD_GO: move_to,
    CMD_FIGHT: None,
    CMD_LOOK: print_room,
    CMD_INV: print_inventory,
    CMD_HELP: print_actions
}

def do_turn():
    action = raw_input("> ").split(' ');
    print

    act = action.pop(0)
    if COMMANDS[act] and callable(COMMANDS[act]):
        COMMANDS[act](action)
    else:
        print "You have no idea how to do that"

if __name__ == "__main__":
    with open("game.conf") as conf:
        for line in conf.readlines():
            (name, val) = map(lambda s: s.strip(), line.split('='))
            if name == 'treasures':
                for tfile in val.split(','):
                    execfile(tfile.strip())

    current_room = Room()
    rooms = [current_room]
    print_room()
    get_treasure(4)
    while level < LEVEL_TO_WIN:
        do_turn()
    print "Congratulations! You are level %d! You won!" % level
