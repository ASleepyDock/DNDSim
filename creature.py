import random as rand

class Creature:
    def __init__(self, name: str, hit_points: int, armour_class: int, alignment: str, dexterity: int, ID: int):
        self.ID = 0
        self.name = name
        self.alignment = alignment
        
        self.max_hit_points = hit_points
        self.hit_points = hit_points
        
        self.armour_class = armour_class
        
        self.dexterity = dexterity

    def initiativeRoll(self, initiative: int):
        self.initiative = rand.randint(1, 20) + ((self.dexterity - 10) // 2)
        return self.initiative
            
    def take_damage(self, damage: int):
            self.hit_points = max(0, self.hit_points - damage)
            if self.hit_points < 0:
                self.hit_points = 0

    def attack(self, target):
        to_hit = rand.randint(1, 20)+ self.attack_bonus 
        #print(to_hit)
        if to_hit >= target.armour_class:
            damage = rand.randint(1, 6) + self.attack_damage
            target.take_damage(damage)
            #print(f"{self.name} hits {target.name} for {damage} damage! {target.name} has {target.hit_points} HP left.")
        else:
            #print(f"{self.name} misses {target.name}!")
            pass 
        
    def is_alive(self) -> bool:
        return self.hit_points > 0

    def __str__(self):
        return f"PlayerCharacter(name={self.name}, HP={self.hit_points}, AC={self.armour_class})"
    
    def reset(self):
        self.hit_points = self.max_hit_points