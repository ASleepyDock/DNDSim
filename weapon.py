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
        """
        
        if attacker.monster:
            toHitModifier = self.bonus
        else:
            if self.finesse:
                toHitModifier = (attacker.stats.get('dexterity', 0) - 10) // 2 + attacker.proficiencyBonus + self.bonus
            else:  
                toHitModifier = (attacker.stats.get('strength', 0) - 10) // 2 + attacker.proficiencyBonus + self.bonus
        toHit = rand.randint(1, 20) + toHitModifier
        if toHit >= target.armourClass:
            #print("Hit!")
            damage = rand.randint(1, self.damageDie) + self.damageModifier
            target.takeDamage(damage)
        else:
            #print("Miss!")
            pass 