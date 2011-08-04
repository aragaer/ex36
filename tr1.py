def goUpOneLevel():
    global level
    level += 1
def got1000gold():
    global level, gold
    gold += 1000
    level += 1

TREASURES.append(ImmediateTreasure("1000 gold", "You found 1000 gold and went up one level", got1000gold))
TREASURES.append(ImmediateTreasure("Potion of Power", "You swallowed the potion and went up one level", goUpOneLevel))
TREASURES.append(ImmediateTreasure("Hoard", "You've found a pile of stuff", lambda: get_treasure(3)))

TREASURES.append(EquipmentTreasure("Sneaky Bastard Sword", None, 200, 2, 'hand'))
TREASURES.append(EquipmentTreasure("Chainsaw of Bloody Dismemberment", None, 400, 3, 'two hands'))
TREASURES.append(EquipmentTreasure("Really Cool Title", None, None, 3, None))
TREASURES.append(EquipmentTreasure("Flaming Armor", None, 300, 2, 'armor'))
