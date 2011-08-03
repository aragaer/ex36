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

level = 1
power = level
inventory = []

DIRECTIONS = ['north', 'south', 'east', 'west', 'up', 'down']
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

class Monster:
    """A monster!"""

class Room:
    types = ['hall', 'cave', 'room']
    sizes = ['huge', 'large', 'average-sized', 'small', 'tiny']
    descs = ['dark', 'filthy', 'clean', 'dry', 'wet']
    def __init__(self, entrance = -1):
        global n_doors
        self.doors = DIRECTIONS[:]
        possible_doors = self.doors[:]
        new_doors = random.randint(0, N_DIRS)

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

        for wall in random.sample(possible_doors, n_walls):
            idx = self.doors.index(wall)
            del self.doors[idx]

        t = random.choice(Room.types)
        s = random.choice(Room.sizes)
        if random.random() > 0.5:
            self.desc = "%s %s %s" % (s, random.choice(Room.descs), t)
        else:
            self.desc = "%s %s" % (s, t)

        self.d_desc = nice_print_list(self.doors)

        obstacle = random.choice([MONSTERS, CURSES, None])
        if obstacle == None or len(obstacle) == 0: # temporary safeguard
            self.obstacle = None
        else:
            self.obstacle = random.choice(obstacle)

    def getObstacle(self):
        if self.obstacle == None:
            return "nothing"
        elif isinstance(self.obstacle, Monster):
            return self.obstacle.getDesc()

def print_room():
    print "You are in a %s" % current_room.desc
    print "There are doors to the %s" % current_room.d_desc
    print "There is %s here." % current_room.getObstacle()

def print_inventory():
    if len(inventory):
        print "You have %s" % nice_print_list(inventory)
    else:
        print "You have nothing"

def print_actions():
    print "You can do the following:"
    for d in current_room.doors:
        print "- go", d

def move_to(d):
    global current_room, n_doors
    if d not in current_room.doors:
        print "You bump into a wall."
        return

    try:
        current_room = getattr(current_room, d)
    except:
        n_doors -= 1
        current_room = Room(DIRECTIONS.index(d))

def do_turn():
    print_room()
    print_inventory()
    print_actions()
    action = raw_input("> ");

    if action.startswith("go "):
        move_to(action[3:])

if __name__ == "__main__":
    current_room = Room()
    rooms = [current_room]
    while level < LEVEL_TO_WIN:
        do_turn()
