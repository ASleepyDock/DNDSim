import random as rand
import json

class Creature:
    """
    Base class representing a generic creature in the simulation.
    Handles loading character data from a JSON file and provides
    common methods for initiative, attacking, damage, and state.
    """
    def __init__(
        self, 
        id: int = 0, 
        filePath: str = None
    ):
        self.id = 0
        
        # Ensure a file path is provided for character data
        try:
            assert filePath is not None
            self.filePath = filePath
        except AssertionError as e:
            print("File path not provided. Please provide a valid file path.")
            raise e
        else:
            # Load character data from the specified JSON file
            with open(filePath, 'r') as characterFile:
                self.characterJson = json.load(characterFile)
            
            # Initialize basic attributes from JSON
            self.name = self.getCharacterData('name')
            self.alignment = self.getCharacterData('alignment')
            self.maxHitPoints = self.getCharacterData('maximumHitPoints')
            self.hitPoints = self.maxHitPoints
            self.armourClass = self.getCharacterData('armourClass')
            self.stats = self.getCharacterData('stats')
            
    def getCharacterData(self, attrib: str):
        """
        Retrieves a specific attribute from the loaded character JSON data.
        Returns None if the attribute is not found.
        """
        data = self.characterJson.get('data').get(attrib, None)
        if data is None:
            print(f"Attribute '{attrib}' not found in character data.")
            return None
        else:
            return data
    
    def initiativeRoll(self):
        """
        Rolls for initiative using a d20 plus the creature's dexterity modifier.
        """
        self.initiative = rand.randint(1, 20) + ((self.stats.get('dexterity') - 10) // 2)
        return self.initiative
            
    def takeDamage(self, damage: int):
        """
        Reduces the creature's hit points by the specified damage amount.
        Ensures hit points do not drop below zero.
        """
        self.hitPoints = max(0, self.hitPoints - damage)
        #print(f"{self.name} takes {damage} damage. Remaining HP: {self.hitPoints}")
        if self.hitPoints <= 0:
            #print(f"{self.name} has been defeated!")
            self.hitPoints = 0

    def attack(self, target):
        """
        Performs an attack against a target creature.
        Rolls to hit and applies damage if successful.
        """
        toHit = rand.randint(1, 20) + self.attackBonus 
        if toHit >= target.armourClass:
            #print("Hit!")
            damage = rand.randint(1, 6) + self.attackDamage
            target.takeDamage(damage)
        else:
            #print("Miss!")
            pass 
        
    def isAlive(self) -> bool:
        """
        Returns True if the creature is still alive (hit points > 0).
        """
        return self.hitPoints > 0

    def __str__(self):
        """
        Returns a string representation of the creature.
        """
        return f"PlayerCharacter(name={self.name}, HP={self.hitPoints}, AC={self.armourClass})"
    
    def reset(self):
        """
        Resets the creature's hit points to maximum.
        Used between simulations.
        """
        self.hitPoints = self.maxHitPoints

class PlayerCharacter(Creature):
    """
    A subclass of Creature representing a player character.
    Sets default attack damage and bonus for players.
    """
    def __init__(self, filePath):
        super().__init__(filePath=filePath)
        self.attackDamage = 2  # Base attack damage
        self.attackBonus = 8  # Bonus to attack rolls

# Class representing a monster
class Monster(Creature):
    """
    A subclass of Creature representing a monster.
    Sets default attack damage and bonus for monsters.
    """
    def __init__(self, filePath):
        super().__init__(filePath=filePath)
        self.attackDamage = 5
        self.attackBonus = 4