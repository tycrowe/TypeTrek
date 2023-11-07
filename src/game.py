import json
import random
import re
import tkinter as tk
from tkinter import scrolledtext


class Dice:
    dice_types: str = None
    dice_sides: int = 0

    def __init__(self, dice_types, dice_sides):
        self.dice_types = dice_types
        self.dice_sides = dice_sides

    def roll(self):
        return random.randint(1, self.dice_sides)

    def roll_multiple(self, number_of_rolls):
        rolls = []
        for i in range(number_of_rolls):
            rolls.append(self.roll())
        return rolls


class Item:
    item_name: str = None
    item_description: str = None
    item_type: str = None
    item_properties: dict = {}

    def __init__(self, item_name, item_description, item_type, item_properties):
        self.item_name = item_name
        self.item_description = item_description
        self.item_type = item_type
        self.item_properties = item_properties

    def get_property(self, property_name):
        return self.item_properties[property_name]

    def has_type(self, item_type):
        return item_type == self.item_type

    def has_property(self, property_name):
        return property_name in self.item_properties.keys()

    def __str__(self):
        return f"Item: {self.item_name}\nDescription: {self.item_description}\nType: {self.item_type}\nProperties: {json.dumps(self.item_properties)}"


class Adventurer:
    stats: dict = {
        "health": 100,
        "attack": 10,
        "defense": 10,
        "gold": 10
    }
    # Items in the adventurer's inventory
    items: list[Item] = []
    # Equipment is being worn by the adventurer
    equipment: list[Item] = []
    location: str = None
    statuses: list[str] = []

    def __init__(self, stats):
        self.stats = stats

    def get_stat(self, stat_name):
        return self.stats[stat_name]

    def set_stat(self, stat_name, stat_value):
        self.stats[stat_name] = stat_value

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def add_equipment(self, item):
        self.equipment.append(item)
        self.adjust_stats_based_on_equipment()

    def remove_equipment(self, item):
        self.equipment.remove(item)

    def adjust_health(self, health):
        self.stats["health"] += health

    def adjust_attack(self, attack):
        self.stats["attack"] += attack

    def adjust_defense(self, defense):
        self.stats["defense"] += defense

    def adjust_gold(self, gold):
        self.stats["gold"] += gold

    def adjust_stat(self, stat, value):
        self.stats[stat] += value

    def add_status(self, status):
        self.statuses.append(status)

    def remove_status(self, status):
        self.statuses.remove(status)

    def has_status(self, status):
        return status in self.statuses

    def adjust_stats_based_on_equipment(self):
        for item in self.equipment:
            if item.has_type("weapon"):
                self.adjust_attack(item.get_property("attack") if item.has_property("attack") else 0)
            elif item.has_type("armor"):
                self.adjust_defense(item.get_property("defense") if item.has_property("defense") else 0)

    def __str__(self):
        # Print the stats
        return f"Status: {json.dumps(self.stats, indent=4)}\nItems: {[item.item_name for item in self.items]}\nEquipment: {[item.item_name for item in self.equipment]}"


class Location:
    # Read from .res/adventure.json
    class Path:
        path_id: str = None
        path_name: str = None
        path_description: str = None
        path_destination: str = None

        def __init__(self, path_id, path_name, path_description, path_destination):
            self.path_id = path_id
            self.path_name = path_name
            self.path_description = path_description
            self.path_destination = path_destination

    class Choice:
        class ChoiceReference:
            reference_description: str = None
            reference_difficulty: dict = {}
            reference_success: dict = {}
            reference_fail: dict = {}

            def __init__(self, reference_description, reference_difficulty=None, reference_success=None,
                         reference_fail=None):
                self.reference_description = reference_description
                self.reference_difficulty = reference_difficulty
                self.reference_success = reference_success
                self.reference_fail = reference_fail

            def __str__(self):
                return f"Description: {self.reference_description}\nDifficulty: {self.reference_difficulty}\nSuccess: {self.reference_success}\nFail: {self.reference_fail}"

        choice_action: str = None
        choice_target: str = None
        choice_description: str = None
        choice_interaction: dict = {}
        choice_trigger_event: list[str] = []
        choice_trigger_path: str = None
        choice_settings: dict = {}
        choice_references: dict[str, ChoiceReference] = {}

        def __init__(self, choice_action, choice_target, choice_description=None, choice_interaction=None,
                     choice_trigger_event=None,
                     choice_trigger_path=None,
                     choice_settings=None,
                     choice_references=None):
            self.choice_action = choice_action
            self.choice_target = choice_target
            self.choice_description = choice_description
            self.choice_interaction = choice_interaction
            self.choice_trigger_event = choice_trigger_event
            self.choice_trigger_path = choice_trigger_path
            self.choice_settings = choice_settings
            # Build choice references
            if choice_references is not None:
                for choice_reference in choice_references.keys():
                    for choice_ref in choice_references[choice_reference].keys():
                        self.choice_references[choice_ref] = self.ChoiceReference(
                            choice_references[choice_reference][choice_ref]["description"],
                            choice_references[choice_reference][choice_ref]["difficulty"] if "difficulty" in
                                                                                             choice_references[
                                                                                                 choice_reference][
                                                                                                 choice_ref].keys() else None,
                            choice_references[choice_reference][choice_ref]["success"] if "success" in
                                                                                          choice_references[
                                                                                              choice_reference][
                                                                                              choice_ref].keys() else None,
                            choice_references[choice_reference][choice_ref]["fail"] if "fail" in
                                                                                       choice_references[
                                                                                           choice_reference][
                                                                                           choice_ref].keys() else None
                        )

        def get_reference(self, reference_name) -> ChoiceReference:
            return self.choice_references[reference_name]

        def __str__(self):
            return f"Action: {self.choice_action}\nTarget: {self.choice_target}\nDescription: {self.choice_description}\nInteraction: {json.dumps(self.choice_interaction)}\nTrigger Event: {self.choice_trigger_event}\nTrigger Path: {self.choice_trigger_path}"

    location_id: str = None
    location_name: str = None
    location_description: str = None
    location_paths: list[Path] = []
    location_choices: list[Choice] = []

    def __init__(self, location_id, location_name, location_description, location_paths, location_choices):
        self.location_id = location_id
        self.location_name = location_name
        self.location_description = location_description
        self.location_paths = location_paths
        self.location_choices = location_choices

    def get_path(self, path_id):
        for path in self.location_paths:
            if path.path_id == path_id:
                return path
        return None


class Game:
    json_adventure_file: str = None
    json_adventure_contents: dict = {}
    adventurer: Adventurer = None
    current_location: Location = None

    loaded_items: dict[str, Item] = {}
    loaded_dice: dict[str, Dice] = {}
    loaded_locations: dict[str, Location] = {}

    adventure_name: str = None
    adventure_description: str = None

    def __init__(self, json_adventure_file):
        print("Loading adventure...")
        self.json_adventure_file = json_adventure_file

        with open(self.json_adventure_file) as adventure_file:
            self.json_adventure_contents = json.load(adventure_file)
            self.load_dice()
            self.load_items()
            self.load_character()
            self.load_locations()
            self.load_settings()
        print(f"Adventure loaded. Starting at {self.current_location.location_name}...")

    def load_items(self):
        for item in self.json_adventure_contents["items"]:
            if item["id"] not in self.loaded_items.keys():
                self.loaded_items[item["id"]] = Item(item["name"], item["description"], item["type"],
                                                     item["properties"])
            else:
                print(f"Item {item['id']} already exists.")
        print(f"Loaded {len(self.loaded_items)} items.")

    def load_dice(self):
        for dice in self.json_adventure_contents["dice"]:
            if dice["type"] not in self.loaded_dice.keys():
                self.loaded_dice[dice["type"]] = Dice(dice["type"], dice["sides"])
        print(f"Loaded {len(self.loaded_dice)} dice.")

    def load_locations(self):
        for location in self.json_adventure_contents["locations"]:
            location_id = location["id"]
            location_name = location["name"]
            location_description = location["description"]
            location_paths: list[Location.Path] = []
            location_choices: list[Location.Choice] = []

            for path in location["paths"]:
                path_id = path["id"]
                path_name = path["name"]
                path_description = path["description"]
                path_destination = path["destination"]
                location_paths.append(Location.Path(path_id, path_name, path_description, path_destination))

            for choice in location["choices"]:
                choice_action = choice["action"]
                choice_target = choice["target"] if "target" in choice.keys() else None
                choice_description = choice["description"] if "description" in choice.keys() else None
                choice_interaction = choice["interaction"] if "interaction" in choice.keys() else None
                choice_trigger_event = choice["trigger_event"] if "trigger_event" in choice.keys() else None
                choice_trigger_path = choice["trigger_path"] if "trigger_path" in choice.keys() else None
                choice_settings = choice["settings"] if "settings" in choice.keys() else None
                choice_references = choice["choice_refs"] if "choice_refs" in choice.keys() else None
                location_choices.append(Location.Choice(choice_action, choice_target, choice_description,
                                                        choice_interaction, choice_trigger_event, choice_trigger_path,
                                                        choice_settings, choice_references))

            self.loaded_locations[location_id] = Location(location_id, location_name, location_description,
                                                          location_paths, location_choices)
        print(f"Loaded {len(self.loaded_locations)} locations.")

    def load_character(self):
        # Let's grab the starting stats for the adventurer
        adventurer_stats = self.json_adventure_contents["stats"]
        # Create the adventurer
        self.adventurer = Adventurer(adventurer_stats)
        # Let's grab the starting items for the adventurer
        for item in adventurer_stats["starting_items"]:
            if item in self.loaded_items.keys():
                self.adventurer.add_item(self.loaded_items[item])
            else:
                print(f"Item {item} does not exist.")
        # Let's grab the starting equipment for the adventurer
        for item in adventurer_stats["starting_equipment"]:
            if item in self.loaded_items.keys():
                self.adventurer.add_equipment(self.loaded_items[item])
            else:
                print(f"Item {item} does not exist.")
        print(f"Character loaded.\n{self.adventurer}")

    def load_settings(self):
        settings = self.json_adventure_contents["settings"]
        if "starting_location" in settings.keys():
            self.current_location = self.loaded_locations[settings["starting_location"]]
        else:
            raise Exception("No starting location specified.")
        self.adventure_name = settings["name"]
        self.adventure_description = settings["description"]


class GameEngine:
    class Command:
        command_name: str = None
        command_description: str = None
        command_function: callable = None

        def __init__(self, command_name, command_description, command_function):
            self.command_name = command_name
            self.command_description = command_description
            self.command_function = command_function

    game: Game = None
    root: tk.Tk = None
    frame: tk.Frame = None
    text: scrolledtext.ScrolledText = None
    entry: tk.Entry = None
    choices_in_scene: dict[str, Location.Choice] = {}
    command_catalog: dict[str, Command] = {}
    command_by_scene: dict[str, Command] = {}
    commands_hidden_in_scene: dict[str, Command] = {}
    DEBUG = False

    def __init__(self, the_game):
        self.interaction_queue = None
        self.game = the_game
        self.root = tk.Tk()
        self.root.title(game.adventure_name)

        self.frame = tk.Frame(self.root, bg="black")
        self.frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        self.text = scrolledtext.ScrolledText(
            self.frame, bg="black", fg="#00FF00", insertbackground="#00FF00", state=tk.DISABLED, font=("Courier", 14)
        )
        self.text.pack(expand=True, fill=tk.BOTH)

        self.entry = tk.Entry(self.frame, bg="black", fg="#00FF00", insertbackground="#00FF00", font=("Courier", 16))
        self.entry.bind("<Return>", lambda event=None: self.execute_command(self.entry))
        self.entry.pack(fill=tk.X)

        # Center the window on the screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.setup_command_catalog()
        self.set_scene()
        self.root.mainloop()

    def restore_entry(self):
        self.entry.bind("<Return>", lambda event=None: self.execute_command(self.entry))

    def clear_screen(self):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)

    def display_command_catalog(self):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, "Commands:\n")
        for command in self.command_catalog.keys():
            self.text.insert(tk.END, f"{command} - {self.command_catalog[command].command_description}\n")
        self.text.config(state=tk.DISABLED)

    def setup_command_catalog(self):
        self.command_catalog.clear()
        self.command_by_scene.clear()
        self.commands_hidden_in_scene.clear()
        # Add default commands
        self.command_catalog = {
            "exit": self.Command("exit", "Exit the game", self.root.destroy),
            "clear": self.Command("clear", "Clear the screen", self.clear_screen),
            "help": self.Command("help", "Show this help message", self.display_command_catalog),
            "stats": self.Command("stats", "Show your stats", self.show_stats),
        }
        # Add choices as commands from the adventure
        for choice in self.game.current_location.location_choices:
            command = self.Command(
                choice.choice_action,
                choice.choice_description,
                None
            )
            self.command_catalog[choice.choice_action] = command

            command_settings = choice.choice_settings if choice.choice_settings is not None else {}
            if "hidden" in command_settings.keys() and command_settings["hidden"]:
                self.commands_hidden_in_scene[choice.choice_action] = command
            else:
                # If disabled, we don't want to add it to the scene
                if "disabled" in command_settings.keys() and command_settings["disabled"]:
                    continue
                else:
                    self.command_by_scene[choice.choice_action] = command

            if "chances" in command_settings.keys():
                # Chances determines if the action is to be displayed or not.
                chances = command_settings["chances"] * 100
                if random.randint(1, 100) > chances:
                    # If the command is hidden, remove it from hidden_in_scene and add it to commands_by_scene
                    if choice.choice_action in self.commands_hidden_in_scene.keys():
                        self.command_by_scene[choice.choice_action] = self.commands_hidden_in_scene.pop(
                            choice.choice_action)
                        print(f"Added {choice.choice_action} to command_by_scene.")
                    else:
                        self.command_by_scene[choice.choice_action] = command

            command.command_function = lambda the_choice=choice: self.execute_choice(the_choice)
            self.choices_in_scene[choice.choice_action] = choice

    def set_scene(self, clear_screen=True):
        self.restore_entry()
        self.entry.delete(0, tk.END)
        if clear_screen:
            self.clear_screen()
        else:
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"\n--------------------\n")
            self.text.config(state=tk.DISABLED)
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"Location:\t{self.game.current_location.location_name}\n")
        self.text.insert(tk.END, f"{self.game.current_location.location_description}\n\nYou can:\n")
        # Display choices from command_by_scene
        for choice in self.command_by_scene.keys():
            self.text.insert(tk.END, f"{choice} - {self.command_by_scene[choice].command_description}\n")
        if not clear_screen:
            # Simply scroll.
            self.text.yview(tk.END)
        self.text.config(state=tk.DISABLED)

    def execute_choice(self, choice):
        # Add a newline
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, "\n")
        self.text.config(state=tk.DISABLED)
        # If the choice has a trigger event, we need to check if the event has been triggered
        if choice.choice_interaction is not None:
            self.execute_interaction(choice, choice.choice_interaction)

        # Check the settings, if any. We first want to see if performing this action exposes any other actions.
        if choice.choice_settings is not None:
            # If we have the 'exposes_actions' property, we need to expose the actions. This will be a list of actions.
            if "exposes_actions" in choice.choice_settings.keys():
                for action in choice.choice_settings["exposes_actions"]:
                    if action not in self.command_by_scene.keys():
                        # Get choice from scene
                        if action in self.choices_in_scene.keys():
                            is_disabled = self.choices_in_scene[action].choice_settings["disabled"] \
                                if "disabled" in self.choices_in_scene[action].choice_settings.keys() else False
                            if not is_disabled:
                                self.command_by_scene[action] = self.commands_hidden_in_scene[action]
                                print(f"Added {action} to command_by_scene.")
                                self.commands_hidden_in_scene.pop(action)

    def execute_interaction(self, choice, interaction):
        self.interaction_queue = interaction.copy()  # Create a copy to maintain the original list
        self.process_next_interaction_line(choice=choice)

    def process_next_interaction_line(self, choice=None):
        # Check if there are any more lines to process
        if not self.interaction_queue:
            return

        speak = self.interaction_queue.pop(0)
        subcommands = re.findall(r"\{.*?\}", speak)
        ignore_line = False

        # Remove subcommands from the text
        for subcommand in subcommands:
            speak = speak.replace(subcommand, "")
            # If the subcommand contains {conditional_on(action)}, we want to check if the action is disabled.
            #   If it is disabled, we don't want to process the line.
            if "{conditional_on(" in subcommand:
                action = re.search(r'\((.*?)\)', subcommand).group(1)
                if action in self.choices_in_scene.keys():
                    is_disabled = self.choices_in_scene[action].choice_settings["disabled"] \
                        if "disabled" in self.choices_in_scene[action].choice_settings.keys() else False
                    if is_disabled:
                        ignore_line = True
                        break

        if not ignore_line:
            # Insert the text into the widget
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, speak + "\n\n")
            self.text.config(state=tk.DISABLED)
            self.text.yview(tk.END)  # Scroll to the end

            # Process the subcommands
            for subcommand in subcommands:
                if "wait(" in subcommand and not self.DEBUG:
                    time_to_wait = int(re.search(r'\d+', subcommand).group()) * 1000  # Convert to milliseconds
                    self.text.after(time_to_wait, lambda c=choice: self.process_next_interaction_line(choice=c))
                    return  # Exit early to allow the timer to expire before processing the next line
                elif subcommand == "{pause}" or subcommand == "{any_input}":
                    self.text.bind("<Return>", lambda event, c=choice: self.on_enter_press(event, choice=c))
                    return  # Exit early to wait for user input
                elif subcommand == "{remove_action}":
                    self.text.after(100, lambda c=choice: self.remove_action(choice=c))
                    return
                elif subcommand == "{break}":
                    self.text.after(100, lambda c=choice: self.break_action(choice=c))
                    return
                elif "{roll}" in subcommand:
                    # We want to fetch the difficulty from the settings of the choice
                    difficulty = choice.choice_settings[
                        "difficulty"] if "difficulty" in choice.choice_settings.keys() else {}
                    if not difficulty:
                        raise Exception("No difficulty specified for this choice.")
                    else:
                        result = game.loaded_dice[difficulty["type"]].roll()
                        more_than = difficulty["moreThan"] if "moreThan" in difficulty.keys() else 10
                        # After 1 second, we want to process the result
                        self.text.after(
                            500,
                            lambda r=result, c=choice.choice_settings, m=more_than: self.process_roll_result(r, c, m)
                        )
                    return
                elif "{trigger_path}" in subcommand:
                    # Find the path from the location
                    path = self.game.current_location.get_path(choice.choice_trigger_path)
                    self.text.after(3000, lambda c=choice: self.execute_path(path))
                    return
                elif "{choice_ref(" in subcommand:
                    choice_ref = re.search(r'\((.*?)\)', subcommand).group(1)
                    self.text.after(100, lambda c=choice, cr=choice_ref: self.process_choice_references(c, cr))
                    return

        # If there's no wait or pause, move to the next line immediately
        self.process_next_interaction_line(choice=choice)

    def on_enter_press(self, event, choice=None):
        self.text.unbind("<Return>")  # Unbind the event to avoid interference with other parts
        self.process_next_interaction_line(choice=choice)

    def remove_action(self, choice):
        action_key = choice.choice_action

        # Remove from command_by_scene
        if action_key in self.command_by_scene:
            self.command_by_scene.pop(action_key)
            print(f"Removed {action_key} from command_by_scene.")
            self.set_scene(clear_screen=False)

    def break_action(self, choice):
        self.set_scene(clear_screen=False)

    def process_roll_result(self, result, choice_action_dict, moreThan):
        def process_generic_success():
            # The settings to the choice will contain the success message and the rewards
            success_message = choice_action_dict["success"]["description"]
            # Add the success message to the widget
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"{success_message}\n")
            self.text.config(state=tk.DISABLED)
            success_rewards = choice_action_dict["success"]["rewards"]
            # Add the rewards to the adventurer
            for reward in success_rewards:
                if reward["type"] == "item":
                    if reward["item"] in self.game.loaded_items.keys():
                        item_ref = game.loaded_items[reward["item"]]
                        if item_ref.item_type == "currency":
                            self.game.adventurer.adjust_gold(reward["quantity"] if "quantity" in reward.keys() else 1)
                        else:
                            self.game.adventurer.add_item(item_ref)
                elif reward["type"] == "stat":
                    self.game.adventurer.adjust_stat(reward["stat"], reward["value"])

        def process_generic_failure():
            failure_message = choice_action_dict["fail"]["description"]
            # Add the failure message to the widget
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"{failure_message}\n")
            self.text.config(state=tk.DISABLED)
            failure_consequences = choice_action_dict["fail"]["consequences"]
            for consequence in failure_consequences:
                if consequence["type"] == "item":
                    if consequence["item"] in self.game.adventurer.items:
                        self.game.adventurer.remove_item(game.loaded_items[consequence["item"]])
                elif consequence["type"] == "stat":
                    self.game.adventurer.adjust_stat(consequence["properties"]["stat"], consequence["properties"]["value"])
                elif consequence["type"] == "status":
                    self.game.adventurer.add_status(consequence["status"])
                elif consequence["type"] == "advance_area":
                    # self.game.current_location = self.game.loaded_locations[consequence["location"]]
                    # self.set_scene()
                    pass

        def process_generic_finally():
            if "finally" in choice_action_dict.keys():
                if "remove_actions" in choice_action_dict["finally"]:
                    for action in choice_action_dict["finally"]["remove_actions"]:
                        if action in self.command_by_scene.keys():
                            removed_command = self.command_by_scene.pop(action)
                            print(f"Removed {action} from command_by_scene.")
                            self.commands_hidden_in_scene[action] = removed_command
                            self.choices_in_scene[action].choice_settings["disabled"] = True

        # Check if the result is greater than or equal to the difficulty
        if result >= moreThan:
            # Success
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"Success! You rolled a {result}.\n")
            self.text.config(state=tk.DISABLED)
            process_generic_success()
        else:
            # Failure
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"Failure! You rolled a {result}.\n")
            self.text.config(state=tk.DISABLED)
            process_generic_failure()
        process_generic_finally()
        self.set_scene(clear_screen=False)

    def process_choice_references(self, choice, choice_ref):
        # Choice refs are decisions that players make, which lead to other choices. The effects of which are defined
        #   in the choice_refs section of the choice settings.
        # First, start by displaying the choices to the user. In the case of 'fight drunk patron', the choices are
        #   'yes' and 'no'.
        # Display these choices to the user, and await their input.
        #   Once the user has made their choice, we need to process the choice.
        self.text.config(state=tk.NORMAL)
        for options in choice.choice_references.keys():
            self.text.insert(tk.END, f">\t{options}\n")
        self.text.config(state=tk.DISABLED)
        # Scroll the text to the end
        self.text.yview(tk.END)

        # Let's take over the return key to process the choice
        self.entry.bind("<Return>", lambda event, c=choice, cr=choice_ref: self.process_choice_reference(event, c, cr))

    def process_choice_reference(self, event, choice, choice_ref):
        self.command_by_scene.pop(choice.choice_action)
        # Get the entry input text
        choice_input = self.entry.get()
        # Clear the entry
        self.entry.delete(0, tk.END)
        # Check if the choice input is valid)
        if choice_input in choice.choice_references.keys():
            # Get the choice reference
            choice_reference = choice.get_reference(choice_input)
            # Print the description
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"{choice_reference.reference_description}\n")
            self.text.config(state=tk.DISABLED)
            # Scroll the text to the end
            self.text.yview(tk.END)
            # Check if the choice reference has a difficulty
            if choice_reference.reference_difficulty is not None:
                # Roll the dice
                result = game.loaded_dice[choice_reference.reference_difficulty["type"]].roll()
                more_than = choice_reference.reference_difficulty["moreThan"] if "moreThan" in choice_reference.reference_difficulty else 10
                # After 1 second, we want to process the result
                self.text.after(1000,
                                lambda r=result, cr=choice_reference, m=more_than:
                                self.process_roll_result(r, {
                                    "success": cr.reference_success,
                                    "fail": cr.reference_fail
                                }, m)
                                )
            else:
                self.set_scene(clear_screen=False)

    def show_stats(self):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"Stats:\n{str(self.game.adventurer)}\n--------------------\n")
        self.text.config(state=tk.DISABLED)

    def execute_path(self, path):
        self.game.current_location = self.game.loaded_locations[path.path_destination]
        self.setup_command_catalog()
        self.set_scene()

    def execute_command(self, entry):
        command = entry.get()
        if command in self.command_catalog.keys():
            self.command_catalog[command].command_function()
        else:
            self.text.config(state=tk.NORMAL)
            self.text.insert(tk.END, f"Command '{command}' not found. Use 'help' to view a list of commands.\n")
            self.text.config(state=tk.DISABLED)
        self.text.yview(tk.END)  # Scroll to the end
        entry.delete(0, tk.END)


if __name__ == '__main__':
    file_path = "./src/res/adventure.json"
    game = Game(file_path)
    engine = GameEngine(game)
