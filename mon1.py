def badFunc(lev, badDesc):
    def func():
        global level
        print badDesc
        level -= lev
        print "You lost %d level%s." % (lev, 's' if lev > 1 else '')
    return func

def hostileFunc(minLevel):
    return lambda: level >= minLevel

MONSTERS.append(Monster("Lame Goblin", 1, 1, badFunc(1, "He whacks you with his crutch.")))

def orcBad():
    global level
    res = random.randint(1, 6)
    if res > 2:
        print "You lost %d levels." % res
        level -= res
    else:
        dead("They stomp you to death.")

def deadFunc(desc):
    return lambda: dead(desc)

MONSTERS.append(Monster("3872 Orcs", 10, 3, orcBad))
MONSTERS.append(Monster("Plutonium Dragon", 20, 5, deadFunc("You are roasted and eaten."),
        2, hostileFunc(5)))
MONSTERS.append(Monster("Squidzilla", 18, 4, deadFunc("You are grabbed, slimed, crushed and gobbled."),
        2, hostileFunc(4)))

def leperBad():
    global inventory
    removed = random.sample(inventory, 2) if len(inventory) > 1 else inventory
    for item in removed:
        print "Leperchaun takes %s." % item.name
        if item.equipped:
            unequip_internal(item)
        inventory.remove(item)

MONSTERS.append(Monster("Leperchaun", 4, 2, leperBad))
