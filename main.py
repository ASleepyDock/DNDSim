from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

from creature import PlayerCharacter, Monster  # Importing the base Creature class

# Function to execute a round of combat
def roundLoop(initiativeOrder):
    """
    Loops through the initiative order and allows each creature to take a turn if they are alive.
    """
    for creature in initiativeOrder:
        if creature.isAlive():  # Check if the creature is alive
            turn(creature, initiativeOrder)  # Execute the creature's turn
        else:
            pass  # Skip if the creature is dead
    pass

# Function to handle a creature's turn
def turn(creature, initiativeOrder):
    """
    Executes a single turn for a creature. The creature attacks the first valid target.
    """
    for target in initiativeOrder:
        # Check if the target is valid (different alignment, alive, and not the same creature)
        if (
        target.alignment != creature.alignment and creature.isAlive and target.name != creature.name and target.isAlive()
        ):
            # Uncomment the line below for debugging attack actions
            #print(f"{creature.name} attacks {target.name}!")
            creature.attack(target)  # Perform the attack
            break  # Stop after attacking the first valid target
    pass

# Function to check for victory conditions
def victoryCheck(initiativeOrder):
    """
    Checks if either the 'Good' or 'Evil' side has won the battle.
    Returns:
        - [True, True, playerHP]: If all monsters are dead (Good wins)
        - [True, False, playerHP]: If all players are dead (Evil wins)
        - [False, None, None]: If the battle is still ongoing
    """
    # Check if any creatures of each alignment are still alive
    evilAlive = any(creature.isAlive() for creature in initiativeOrder if creature.alignment == "Evil")
    goodAlive = any(creature.isAlive() for creature in initiativeOrder if creature.alignment == "Good")
    
    # Collect the hit points of all players (sorted by id)
    playerHP = [
        [creature.hitPoints for creature in sorted(initiativeOrder, key=lambda c: c.id) if creature.alignment == "Good"],
        [creature for creature in sorted(initiativeOrder, key=lambda c: c.id) if creature.alignment == "Good"]
    ]
    
    # Determine the outcome of the battle
    if not evilAlive:
        #print("All monsters are dead, Good wins!\n\n")
        return [True, True, playerHP]  # All monsters are dead, Good wins
    if not goodAlive:
        #print("All players are dead, Evil wins!\n\n")
        return [True, False, playerHP]  # All players are dead, Evil wins
    return [False, None, None]  # Battle is still ongoing

# Function to initialize the turn order based on initiative rolls
def initOrder(creatures):
    """
    Sorts the creatures by their initiative rolls in descending order.
    """
    initiativeOrder = sorted(creatures, key=lambda creature: creature.initiativeRoll(), reverse=True)
    return initiativeOrder
        
if __name__ == "__main__":
    """
    Main execution block for the simulation.
    Initializes player characters, monster configurations, and runs simulations.
    """

    # Initialize player characters
    player = PlayerCharacter('./Characters/zylet.json')  # Player 1 with specific stats
    player.id = 1  # Assign unique id to Player 1
    player2 = PlayerCharacter('./Characters/runa.json')  # Player 2 with specific stats
    player2.id = 2  # Assign unique id to Player 2

    playerCount = 2  # Number of players in the simulation
    simCount = 1000000  # Number of simulations to run

    # Define different configurations for monster hit points
    monsterConfigs = [
        {"name": "Hp = 7", "hitPoints": 7},   # Configuration 1: Monsters with 7 HP
        {"name": "Hp = 10", "hitPoints": 10}, # Configuration 2: Monsters with 10 HP
        {"name": "Hp = 15", "hitPoints": 15}, # Configuration 3: Monsters with 15 HP
        {"name": "Hp = 20", "hitPoints": 20} # Configuration 4: Monsters with 20 HP
    ]

    # Create subplots for visualizing results for each player
    fig, axs = plt.subplots(playerCount)
    
    if playerCount == 1:
        axs = [axs]

    # Iterate through each monster configuration
    for config in tqdm(monsterConfigs):
        # Initialize monsters with the current configuration's hit points
        gobbo1 = Monster("./Characters/goblin.json")
        gobbo1.maxHitPoints = config["hitPoints"]  # Set the hit points for the monster
        gobbo2 = Monster("./Characters/goblin.json")
        gobbo1.maxHitPoints = config["hitPoints"]  # Set the hit points for the monster
        gobbo3 = Monster("./Characters/goblin.json")
        gobbo3.maxHitPoints = config["hitPoints"]  # Set the hit points for the monster
        gobbo4 = Monster("./Characters/goblin.json")
        gobbo4.maxHitPoints = config["hitPoints"]  # Set the hit points for the monster

        # Determine the initiative order for the combat
        initiativeOrder = initOrder([gobbo1, gobbo2, gobbo3, gobbo4, player, player2])

        # Initialize arrays to store simulation results
        result = np.array([], dtype=bool)  # Array to store win/loss results
        finalHP = np.empty((simCount, playerCount))  # Array to store final HP of players

        winThreshold = 0.01  # Desired accuracy threshold for win rate
        errorMargin = 1  # Initial error margin for win rate calculation
        winCount = 0
        lossCount = 0

        for i in tqdm(range(simCount), desc=f"Simulating {config['name']}"):
            # Stop the simulation early if the error margin is below the desired threshold
            if errorMargin < winThreshold:
                break
            while True:
                # Execute a round of combat
                roundLoop(initiativeOrder)
                
                # Check the victory conditions after the round
                endState, victor, finishHP = victoryCheck(initiativeOrder)
                if endState == True:  # If the battle has ended
                    if victor:  # If the "Good" side won
                        winCount += 1
                    else:  # If the "Evil" side won
                        lossCount += 1

                    # Store the result of the simulation (win/loss)
                    result = np.append(result, victor)
                    
                    # Store the final HP of the players for this simulation
                    finalHP[i, :] = finishHP[0]
                    
                    # Reset all creatures for the next simulation
                    for creature in initiativeOrder:
                        creature.reset()
                    
                    # Reinitialize the initiative order for the next simulation
                    initiativeOrder = initOrder([gobbo1, gobbo2, gobbo3, gobbo4, player, player2])
                    break  # Exit the inner loop to start the next simulation

            # Check if the win rate has stabilized within the desired threshold
            totalSimulations = winCount + lossCount  # Total number of simulations completed so far
            if totalSimulations > 1000:  # Ensure enough simulations for meaningful statistics
                # Calculate the current win rate
                winRate = winCount / totalSimulations
                # Calculate the error margin using a 95% confidence interval
                errorMargin = 1.96 * np.sqrt((winRate * (1 - winRate)) / totalSimulations)
                
                # Print the current error margin for debugging purposes
                #print(f"\rCurrent error margin: {errorMargin:.6f}", end="")

        print(f"Current win rate: {winRate:.6f} for config {config['name']}")  # Print the current win rate for debugging

        for i in range(playerCount):
            """
            Loop through each player to plot their final HP distribution.
            Each player's histogram is plotted on a separate subplot.
            """
            finalHP = np.trim_zeros(finalHP)  # Remove leading and trailing zeros from the final HP array
            hist, bins = np.histogram(finalHP[:, i], bins=10)  # Create a histogram for the player's final HP
            histPercentage = (hist / totalSimulations) * 100  # Convert histogram counts to percentages

            # Plot the histogram for the current player
            axs[i].bar(
                bins[:-1],  # Bin edges (excluding the last edge)
                histPercentage,  # Percentage of simulations in each bin
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
            axs[i].set_ylim(0, 100)

    # Set the overall title for the figure
    fig.suptitle(f"Distribution of Player's Final HP Across Configurations.")

    # Add a legend to the figure to identify configurations
    plt.legend()

    # Display the figure
    plt.show()