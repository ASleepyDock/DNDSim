import random as rand
import json

class Creature:
    def __init__(
        self, 
        id: int = 0, 
        filePath: str = None
    ):
        self.id = 0
        
        try:
            assert filePath is not None
            self.filePath = filePath
        except AssertionError as e:
            print("File path not provided. Please provide a valid file path.")
            raise e
        else:
            with open(filePath, 'r') as characterFile:
                self.characterJson = json.load(characterFile)
            
            self.name = self.getCharacterData('name')
            self.alignment = self.getCharacterData('alignment')
        
            self.maxHitPoints = self.getCharacterData('maximumHitPoints')
            self.hitPoints = self.maxHitPoints
            
            self.armourClass = self.getCharacterData('armourClass')
            
            self.stats = self.getCharacterData('stats')
            
    def getCharacterData(self, attrib: str):
        """
        Retrieves character data from a JSON file.
        """
        data = self.characterJson.get('data').get(attrib, None)
        if data is None:
            print(f"Attribute '{attrib}' not found in character data.")
            return None
        else:
            return data
    
    def initiativeRoll(self, initiative: int):
        self.initiative = rand.randint(1, 20) + ((self.stats.get('dexterity') - 10) // 2)
        return self.initiative
            
    def takeDamage(self, damage: int):
        self.hitPoints = max(0, self.hitPoints - damage)
        #print(f"{self.name} takes {damage} damage. Remaining HP: {self.hitPoints}")
        if self.hitPoints <= 0:
            #print(f"{self.name} has been defeated!")
            self.hitPoints = 0

    def attack(self, target):
        toHit = rand.randint(1, 20) + self.attackBonus 
        if toHit >= target.armourClass:
            #print("Hit!")
            damage = rand.randint(1, 6) + self.attackDamage
            target.takeDamage(damage)
        else:
            #print("Miss!")
            pass 
        
    def isAlive(self) -> bool:
        return self.hitPoints > 0

    def __str__(self):
        return f"PlayerCharacter(name={self.name}, HP={self.hitPoints}, AC={self.armourClass})"
    
    def reset(self):
        self.hitPoints = self.maxHitPoints

class PlayerCharacter(Creature):
    """
    A subclass of Creature representing a player character.
    """
    def __init__(self, filePath):
        super().__init__(filePath=filePath)
        self.attackDamage = 2  # Base attack damage
        self.attackBonus = 8  # Bonus to attack rolls

# Class representing a monster
class Monster(Creature):
    """
    A subclass of Creature representing a monster.
    """
    def __init__(self, filePath):
        super().__init__(filePath=filePath)
        self.attackDamage = 5
        self.attackBonus = 4