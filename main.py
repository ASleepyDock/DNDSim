import random as rand
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

from creature import Creature  # Importing the base Creature class

# Function to execute a round of combat
def roundLoop(initiative_order):
    """
    Loops through the initiative order and allows each creature to take a turn if they are alive.
    """
    for creature in initiative_order:
        if creature.is_alive():  # Check if the creature is alive
            turn(creature, initiative_order)  # Execute the creature's turn
        else:
            pass  # Skip if the creature is dead
    pass

# Function to handle a creature's turn
def turn(creature, initiative_order):
    """
    Executes a single turn for a creature. The creature attacks the first valid target.
    """
    for target in initiative_order:
        # Check if the target is valid (different alignment, alive, and not the same creature)
        if target.alignment != creature.alignment and creature.is_alive() and target.name != creature.name and target.is_alive():
            # Uncomment the line below for debugging attack actions
            # print(f"{creature.name} attacks {target.name}!")
            creature.attack(target)  # Perform the attack
            break  # Stop after attacking the first valid target
    pass

# Function to check for victory conditions
def victoryCheck(initiative_order):
    """
    Checks if either the 'Good' or 'Evil' side has won the battle.
    Returns:
        - [True, True, playerHP]: If all monsters are dead (Good wins)
        - [True, False, playerHP]: If all players are dead (Evil wins)
        - [False, None, None]: If the battle is still ongoing
    """
    # Check if any creatures of each alignment are still alive
    evil_alive = any(creature.is_alive() for creature in initiative_order if creature.alignment == "Evil")
    good_alive = any(creature.is_alive() for creature in initiative_order if creature.alignment == "Good")
    
    # Collect the hit points of all players (sorted by ID)
    playerHP = [
        [creature.hit_points for creature in sorted(initiative_order, key=lambda c: c.ID) if creature.alignment == "Good"],
        [creature for creature in sorted(initiative_order, key=lambda c: c.ID) if creature.alignment == "Good"]
    ]
    
    # Determine the outcome of the battle
    if not evil_alive:
        return [True, True, playerHP]  # All monsters are dead, Good wins
    if not good_alive:
        return [True, False, playerHP]  # All players are dead, Evil wins
    return [False, None, None]  # Battle is still ongoing

# Function to initialize the turn order based on initiative rolls
def initOrder(creatures):
    """
    Sorts the creatures by their initiative rolls in descending order.
    """
    initiative_order = sorted(creatures, key=lambda creature: creature.initiativeRoll(0), reverse=True)
    return initiative_order

# Class representing a player character
class PlayerCharacter(Creature):
    """
    A subclass of Creature representing a player character.
    """
    def __init__(self, name: str, hit_points: int, armour_class: int, alignment: str, dexterity: int):
        super().__init__(name, hit_points, armour_class, alignment, dexterity, ID=0)
        self.attack_damage = 2  # Base attack damage
        self.attack_bonus = 8  # Bonus to attack rolls

# Class representing a monster
class Monster(Creature):
    """
    A subclass of Creature representing a monster.
    """
    def __init__(self, name: str, hit_points: int, armour_class: int, alignment: str, dexterity: int):
        super().__init__(name, hit_points, armour_class, alignment, dexterity, ID=0)
        self.attack_damage = 5
        self.attack_bonus = 4
        
if __name__ == "__main__":
    """
    Main execution block for the simulation.
    Initializes player characters, monster configurations, and runs simulations.
    """

    # Initialize player characters
    player = PlayerCharacter("Zylet", 78, 20, "Good", 10)  # Player 1 with specific stats
    player.ID = 1  # Assign unique ID to Player 1
    player2 = PlayerCharacter("Runa", 60, 16, "Good", 16)  # Player 2 with specific stats
    player2.ID = 2  # Assign unique ID to Player 2

    playerCount = 2  # Number of players in the simulation
    simCount = 1000000  # Number of simulations to run

    # Define different configurations for monster hit points
    monster_configs = [
        {"name": "Hp = 7", "hit_points": 7},   # Configuration 1: Monsters with 7 HP
        {"name": "Hp = 10", "hit_points": 10}, # Configuration 2: Monsters with 10 HP
        {"name": "Hp = 15", "hit_points": 15}, # Configuration 3: Monsters with 15 HP
        {"name": "Hp = 20", "hit_points": 20}, # Configuration 4: Monsters with 20 HP
    ]

    # Create subplots for visualizing results for each player
    fig, axs = plt.subplots(playerCount)

    # Iterate through each monster configuration
    for config in tqdm(monster_configs):
        # Initialize monsters with the current configuration's hit points
        gobbo1 = Monster("Goblin 1", config["hit_points"], 15, "Evil", 14)
        gobbo2 = Monster("Goblin 2", config["hit_points"], 15, "Evil", 14)
        gobbo3 = Monster("Goblin 3", config["hit_points"], 15, "Evil", 14)
        gobbo4 = Monster("Goblin 4", config["hit_points"], 15, "Evil", 14)

        # Determine the initiative order for the combat
        initiative_order = initOrder([gobbo1, gobbo2, gobbo3, gobbo4, player, player2])

        # Initialize arrays to store simulation results
        result = np.array([], dtype=bool)  # Array to store win/loss results
        finalHP = np.zeros((simCount, playerCount), dtype=int)  # Array to store final HP of players

        win_threshold = 0.01  # Desired accuracy threshold for win rate
        error_margin = 1  # Initial error margin for win rate calculation
        wins = 0
        losses = 0

        for i in tqdm(range(simCount), desc=f"Simulating {config['name']}"):
            # Stop the simulation early if the error margin is below the desired threshold
            if error_margin < win_threshold:
                break
            while True:
                # Execute a round of combat
                roundLoop(initiative_order)
                
                # Check the victory conditions after the round
                endState, victor, finishHP = victoryCheck(initiative_order)
                if endState == True:  # If the battle has ended
                    if victor:  # If the "Good" side won
                        wins += 1
                    else:  # If the "Evil" side won
                        losses += 1

                    # Store the result of the simulation (win/loss)
                    result = np.append(result, victor)
                    
                    # Store the final HP of the players for this simulation
                    finalHP[i, :] = finishHP[0]
                    
                    # Reset all creatures for the next simulation
                    for creature in initiative_order:
                        creature.reset()
                    
                    # Reinitialize the initiative order for the next simulation
                    initiative_order = initOrder([gobbo1, gobbo2, gobbo3, gobbo4, player, player2])
                    break  # Exit the inner loop to start the next simulation

            # Check if the win rate has stabilized within the desired threshold
            total_simulations = wins + losses  # Total number of simulations completed so far
            if total_simulations > 1000:  # Ensure enough simulations for meaningful statistics
                # Calculate the current win rate
                win_rate = wins / total_simulations
                
                # Calculate the error margin using a 95% confidence interval
                error_margin = 1.96 * np.sqrt((win_rate * (1 - win_rate)) / total_simulations)
                
                # Print the current error margin for debugging purposes
                #print(f"\rCurrent error margin: {error_margin:.6f}", end="")

        for i in range(playerCount):
            """
            Loop through each player to plot their final HP distribution.
            Each player's histogram is plotted on a separate subplot.
            """
            finalHP = np.trim_zeros(finalHP)  # Remove leading and trailing zeros from the final HP array
            hist, bins = np.histogram(finalHP[:, i], bins=10)  # Create a histogram for the player's final HP
            hist_percentage = (hist / total_simulations) * 100  # Convert histogram counts to percentages

            # Plot the histogram for the current player
            axs[i].bar(
                bins[:-1],  # Bin edges (excluding the last edge)
                hist_percentage,  # Percentage of simulations in each bin
                width=np.diff(bins),  # Width of each bar
                edgecolor='black',  # Add a black border to the bars
                align='edge',  # Align bars to the bin edges
                alpha=0.5,  # Set transparency for overlapping bars
                label=config["name"],  # Label for the current configuration
            )

            # Set the x-axis label to indicate the player's name
            axs[i].set_xlabel(f"Final HP of {finishHP[1][i].name}")
            # Set the y-axis label to indicate the percentage of simulations
            axs[i].set_ylabel("Percentage of Simulations")

    # Set the overall title for the figure
    fig.suptitle("Distribution of Player's Final HP Across Configurations")

    # Add a legend to the figure to identify configurations
    plt.legend()

    # Display the figure
    plt.show()