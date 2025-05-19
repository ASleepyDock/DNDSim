import random as rand
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

def roundLoop(initiative_order):
    for creature in initiative_order:
        if creature.is_alive():
            turn(creature, initiative_order)
        else:
            pass
    pass

def turn(creature, initiative_order):
    for target in initiative_order:
        if target.alignment != creature.alignment and creature.is_alive() and target.name != creature.name and target.is_alive():
            #print(f"{creature.name} attacks {target.name}!")
            creature.attack(target)
            break
    pass

def victoryCheck(initiative_order):
    evil_alive = any(creature.is_alive() for creature in initiative_order if creature.alignment == "Evil")
    good_alive = any(creature.is_alive() for creature in initiative_order if creature.alignment == "Good")
    if not evil_alive:
        player = next(creature for creature in initiative_order if creature.alignment == "Good")
        return [True, True, player.hit_points]  # All monsters are dead, you win
    if not good_alive:
        return [True, False, 0]  # All players are dead, you lose
    return [False, None, None]

def initOrder(creatures):
    initiative_order = sorted(creatures, key=lambda creature: creature.initiativeRoll(0), reverse=True)
    return initiative_order

class Creature:
    def __init__(self, name: str, hit_points: int, armour_class: int, alignment: str, dexterity: int):
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
            
class PlayerCharacter(Creature):
    def __init__(self, name: str, hit_points: int, armour_class: int, alignment: str, dexterity: int):
        super().__init__(name, hit_points, armour_class, alignment, dexterity)
        self.attack_damage = 2
        self.attack_bonus = 8

class Monster(Creature):
    def __init__(self, name: str, hit_points: int, armour_class: int, alignment:str, dexterity: int):
        super().__init__(name, hit_points, armour_class, alignment, dexterity)
        self.attack_damage = 5
        self.attack_bonus = 4

if __name__ == "__main__":
    player = PlayerCharacter("Zylet", 78, 20, "Good", 10)
    player2 = PlayerCharacter("Runa", 60, 16, "Good", 16)
    simCount = 1000000

    # Different configurations for monster hit points
    monster_configs = [
        {"name": "Hp = 7", "hit_points": 7},
        {"name": "Hp = 10", "hit_points": 10},
        {"name": "Hp = 15", "hit_points": 15},
        {"name": "Hp = 20", "hit_points": 20},
    ]

    plt.figure(figsize=(10, 6))

    for config in tqdm(monster_configs):
        gobbo1 = Monster("Goblin 1", config["hit_points"], 15, "Evil", 14)
        gobbo2 = Monster("Goblin 2", config["hit_points"], 15, "Evil", 14)
        gobbo3 = Monster("Goblin 3", config["hit_points"], 15, "Evil", 14)
        gobbo4 = Monster("Goblin 4", config["hit_points"], 15, "Evil", 14)

        initiative_order = initOrder([gobbo1, gobbo2, gobbo3, gobbo4, player, player2])

        result = np.array([], dtype=bool)
        finalHP = np.array([], dtype=int)

        win_threshold = 0.01  # Desired accuracy threshold for win rate
        error_margin = 1
        wins = 0
        losses = 0

        for i in tqdm(range(simCount), desc=f"Simulating {config['name']}"):
            if error_margin < win_threshold:
                break
            while True:
                roundLoop(initiative_order)
                endState, victor, finishHP = victoryCheck(initiative_order)
                if endState == True:
                    if victor:
                        wins += 1
                    else:
                        losses += 1

                    result = np.append(result, victor)
                    finalHP = np.append(finalHP, finishHP)
                    for creature in initiative_order:
                        creature.reset()
                    initiative_order = initOrder([gobbo1, gobbo2, gobbo3, gobbo4, player, player2])
                    break

                # Check if the win rate has stabilized within the threshold
                total_simulations = wins + losses
                if total_simulations > 1000:  # Ensure enough simulations for meaningful statistics
                    win_rate = wins / total_simulations                
                    error_margin = 1.96 * np.sqrt((win_rate * (1 - win_rate)) / total_simulations)  # 95% confidence interval
                    print(f"\rCurrent error margin: {error_margin:.6f}", end="")
                    if error_margin < win_threshold:
                        print(f"\nWin rate is:{win_rate}\n")
                        break
            
                    

        hist, bins = np.histogram(finalHP, bins=10)
        hist_percentage = (hist / total_simulations) * 100
        plt.bar(
            bins[:-1],
            hist_percentage,
            width=np.diff(bins),
            edgecolor='black',
            align='edge',
            alpha=0.5,
            label=config["name"],
        )

    plt.title("Distribution of Player's Final HP Across Configurations")
    plt.xlabel("Final HP")
    plt.ylabel("Percentage of Simulations")
    plt.legend()
    plt.show()