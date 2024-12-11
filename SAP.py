import copy
import random

class Pet:
    def __init__(self, name, attack, health, ability, ability_trigger):
        self.name = name
        self.attack = attack
        self.health = health
        self.ability = ability        
        self.ability_trigger = ability_trigger
        original_health = health
        original_attack = attack
    
    def is_alive(self):
        return self.health > 0
    
    def reset_stats(self):
        self.health = self.original_health
        self.attack = self.original_attack


class Shop:
    def __init__(self, pet_pool):
        self.pet_pool = pet_pool
        self.slots = 3  # Start with 3 shop slots
        self.gold = 10
        self.pets_for_sale = []
        self.refresh_cost = 1
        self.pet_cost = 3

    def generate_shop(self):
        available_pets = list(self.pet_pool.values())
        self.pets_for_sale = []

        for _ in range(self.slots):
            random_pet = random.choice(available_pets)
            pet_copy = copy.deepcopy(random_pet)
            self.pets_for_sale.append(pet_copy)

    def buy_pet(self, slot_index):
        if self.gold < self.pet_cost:
            print("Not enough gold to buy pet!")
            return None
            
        if 0 <= slot_index < len(self.pets_for_sale):
            pet = self.pets_for_sale[slot_index]
            self.gold -= self.pet_cost
            self.pets_for_sale[slot_index] = None  # Empty the slot
            return copy.deepcopy(pet)
        return None

class SAPGame:
    def __init__(self):
        self.shop_tier = 1
        self.gold = 10
        self.team = []
        self.max_team_size = 5
        self.pet_pool = {
            "ant": Pet("Ant", 2, 1, ability = "give_stats", ability_trigger = "faint"),
            "cricket": Pet("Cricket", 1, 2, ability = "summon_friend", ability_trigger = "faint"),
            "horse": Pet("Horse", 2, 1, ability = "buff_summoned", ability_trigger = "friend_summoned"),
            "otter": Pet("Otter", 1, 2, ability = "buff_friend", ability_trigger = "on_buy"),
            "mosquito": Pet("Mosquito", 1,2, ability= "start_battle_damage", ability_trigger = "start_of_battle"),
            "beaver": Pet("Beaver", 2, 2, ability = "give_stats", ability_trigger = "on_sell")
        }
        self.shop = Shop(self.pet_pool)

    #calculates the utility score of the team setup sent in and returns a float
    def calculate_team_utility(self, team):
        if not team: return 0

        utility = 0

        #calculate base utility from attack and health (numbers based on personal game experience)
        for pet in team: 
            utility += pet.attack * 1.5 + pet.health * 2
        
        #add synergy points from abilities and triggers 
        ability_triggers = [pet.ability_trigger for pet in team]

        #synergy points from summon team
        if "summon_friend" in [p.ability for p in team] and "buff_summoned" in [p.ability for p in team]:
            utility += 5
        
        #start battle damage utility
        utility += 2 * sum(p.ability for p in team if p.ability == "start_battle_damage")

        #buy/sell utility (buffs up team)
        utility += 2 * ability_triggers.count("on_buy") + ability_triggers.count("on_sell")

        return utility
    
    def get_team_combination(self, available_pets, current_team, remaining_gold, best_team, best_utility, depth = 0):
        utility = self.calculate_team_utility(current_team)
        if utility > best_utility and len(current_team) <= self.max_team_size:
            best_utility = utility
            best_team = current_team.copy()

        # Base cases for recursion
        if depth >= self.max_team_size or remaining_gold < self.shop.pet_cost:
            return
        
        # Try adding each available pet
        for pet in available_pets:
            if remaining_gold >= self.shop.pet_cost:
                current_team.append(copy.deepcopy(pet))
                self.get_team_combination(
                    available_pets=available_pets,
                    current_team=current_team,
                    remaining_gold=remaining_gold - self.shop.pet_cost,
                    best_team=best_team,
                    best_utility=best_utility,
                    depth=depth + 1
                )
                current_team.pop()
   
    #get best team build
    def get_best_team(self):
        best_team = []
        best_utility = 0
        available_pets = [p for p in self.shop.pets_for_sale if p is not None]

        self.get_team_combination(
            available_pets=available_pets,
            current_team=[],
            remaining_gold=10,
            best_team=best_team,
            best_utility=best_utility,
            depth=0
        )

    #method to get a random team build
    def get_random_team(self, team_size: int = 5):
        available_pets = list(self.pet_pool.values())
        team = []
        for _ in range(team_size):
            pet = random.choice(available_pets)
            team.append(copy.deepcopy(pet))
        return team


class Battle:
    def __init__(self, team1, team2):
        self.team1 = copy.deepcopy(team1)  # Utility-based team
        self.team2 = copy.deepcopy(team2) #random team

    def execute_start_abilities(self, team, enemy_team):
        for pet in team:
            if pet.ability_trigger == "start_of_battle":
                if pet.ability == "start_battle_damage":
                    if enemy_team:
                        target = random.choice(enemy_team)
                        target.health -= 1
                        print(f"{pet.name} deals 1 damage to {target.name}")
    
    def process_faint(self, pet: Pet, friendly_team, enemy_team):
        if pet.ability_trigger == "faint":
            if pet.ability == "give_stats":
                if friendly_team:
                    target = random.choice([p for p in friendly_team if p.is_alive()])
                    target.attack += 1
                    target.health += 1
                    print(f"{pet.name} gives +1/+1 to {target.name}")
            elif pet.ability == "summon_friend":
                # Summon a 1/1 Cricket
                zombie = Pet("Cricket Zombie", 1, 1)
                friendly_team.append(zombie)
                print(f"{pet.name} summons a Cricket Zombie")
                
                # Trigger "friend_summoned" abilities
                for friend in friendly_team:
                    if friend.ability_trigger == "friend_summoned" and friend.is_alive():
                        if friend.ability == "buff_summoned":
                            zombie.attack += 1
                            print(f"{friend.name} gives +1 attack to summoned {zombie.name}")
    
    def simulate_battle(self) -> str:
        print("\nBattle Start!")
        print("\nTeam 1 (Utility-based):")
        self.print_team(self.team1)
        print("\nTeam 2 (Random):")
        self.print_team(self.team2)
        
        # Start of battle abilities
        self.execute_start_abilities(self.team1, self.team2)
        self.execute_start_abilities(self.team2, self.team1)
        
        round_number = 1
        while any(pet.is_alive() for pet in self.team1) and any(pet.is_alive() for pet in self.team2):
            print(f"\nRound {round_number}")
            
            # Get first alive pets from each team
            pet1 = next((pet for pet in self.team1 if pet.is_alive()), None)
            pet2 = next((pet for pet in self.team2 if pet.is_alive()), None)
            
            if not pet1 or not pet2:
                break
                
            # Pets attack each other simultaneously
            print(f"{pet1.name} ({pet1.attack}/{pet1.health}) attacks {pet2.name} ({pet2.attack}/{pet2.health})")
            pet1.health -= pet2.attack
            pet2.health -= pet1.attack
            
            # Check for faint abilities
            if not pet1.is_alive():
                print(f"{pet1.name} faints!")
                self.process_faint(pet1, self.team1, self.team2)
            if not pet2.is_alive():
                print(f"{pet2.name} faints!")
                self.process_faint(pet2, self.team2, self.team1)
            
            round_number += 1
        
        # Determine winner
        team1_alive = any(pet.is_alive() for pet in self.team1)
        team2_alive = any(pet.is_alive() for pet in self.team2)
        
        if team1_alive and not team2_alive:
            return "Team 1 (Utility-based) wins!"
        elif team2_alive and not team1_alive:
            return "Team 2 (Random) wins!"
        else:
            return "Draw!"
        
    def print_team(self, team):
        for pet in team:
            if pet != None:
                print(f"{pet.name} - ATK: {pet.attack}, HP: {pet.health}")
                print(f"   Ability: {pet.ability} ({pet.ability_trigger})")


game = SAPGame()
utility_team = game.get_best_team()
random_team = game.get_random_team()
battle = Battle(utility_team, random_team)
battle.simulate_battle()

