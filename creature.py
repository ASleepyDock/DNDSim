import random as rand
import json
import numpy as np

from weapon import Weapon

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
            self.monster = self.getCharacterData('monster')  # True if this is a monster, False if a player
            
            self.maxHitPoints = self.getCharacterData('maximumHitPoints')
            self.hitPoints = self.maxHitPoints
            self.armourClass = self.getCharacterData('armourClass')
            
            self.proficiencyBonus = self.getCharacterData('proficiencyBonus')         
              
            self.stats = self.getCharacterData('stats')

            self.jsonWeapons = self.getCharacterData('weapons')

            self.weaponsPrio = {}
            if self.jsonWeapons:
                for jsonWeapon in self.jsonWeapons:
                    weapon = Weapon(
                        jsonWeapon['name'], 
                        jsonWeapon['priority'],
                        jsonWeapon['bonus'],
                        jsonWeapon['damageDie'],
                        jsonWeapon['damageModifier'],
                        jsonWeapon['damageType'],
                        jsonWeapon['finesse']
                )
                    weapon_attr = "weapon" + jsonWeapon['name'].replace(" ", "_").capitalize()
                    setattr(self, weapon_attr, weapon)
                    self.weaponsPrio.update({weapon.priority:weapon_attr})
                    
            self.__delattr__('jsonWeapons')  # Remove jsonWeapons after loading
            
            self.__delattr__('characterJson')  # Remove characterJson after loading
            
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
        if not self.weaponsPrio:
            print(f"{self.name} has no weapons to attack with!")
            return
        
        # Use the highest priority weapon for the attack
        highest_priority = max(self.weaponsPrio.keys())
        weapon_attr = self.weaponsPrio[highest_priority]
        getattr(self, weapon_attr).weaponsAttack(self, target)
        

        
    def isAlive(self) -> bool:
        """
        Returns True if the creature is still alive (hit points > 0).
        """
        return self.hitPoints > 0
    
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

# Class representing a monster
class Monster(Creature):
    """
    A subclass of Creature representing a monster.
    Sets default attack damage and bonus for monsters.
    """
    def __init__(self, filePath):
        super().__init__(filePath=filePath)