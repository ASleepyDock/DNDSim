import random as rand

class Weapon:
    def __init__(
        self, name: str, 
        priority: int, 
        bonus: int,
        damageDie: int, 
        damageModifier: int, 
        damageType: str, 
        finesse: bool
    ):
        
        self.name = name
        self.priority = priority
        self.bonus = bonus
        self.damageDie = damageDie
        self.damageModifier = damageModifier
        self.finesse = finesse
        self.type = damageType
        
    def weaponsAttack(self, attacker, target):
        """
        Performs an attack against a target creature.
        Rolls to hit and applies damage if successful.
        Natural 20 always hits and crits; natural 1 always misses.
        """
        
        if attacker.monster:
            toHitModifier = self.bonus
        else:
            if self.finesse:
                toHitModifier = (attacker.stats.get('dexterity', 0) - 10) // 2 + attacker.proficiencyBonus + self.bonus
            else:  
                toHitModifier = (attacker.stats.get('strength', 0) - 10) // 2 + attacker.proficiencyBonus + self.bonus
        
        roll = rand.randint(1, 20)

        if roll == 1:
            return  # Natural 1: automatic miss

        crit = roll == 20
        if crit or roll + toHitModifier >= target.armourClass:
            #print("Hit!")
            damage = rand.randint(1, self.damageDie) + self.damageModifier
            target.takeDamage(damage)
