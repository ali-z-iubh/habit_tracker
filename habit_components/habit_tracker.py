from questionary import text, select, confirm
from habit_components.habit import Habit, HabitPeriod, HabitType
from habit_components.db import DBManager


class HabitTracker:
    """
    Controls habit management by bridging user input and database operations.

        This class provides methods for creating, updating, deleting, archiving, and completing habits. It interacts with the `DBManager` to persist data and uses `questionary` to prompt the user for CLI input.

    Attributes:
        db (DBManager): Instance of the DBManager class for handling database interactions.
        test_mode (bool): Flag to bypass confirmation prompts during testing.

    """
    def __init__(self, db_name="habit_tracker.db", test_mode=False):
        self.db = DBManager(db_name)
        self.test_mode = test_mode

    def create_habit(self):
        """Prompts the user to create a new habit and saves it to the database.

        Asks for habit name, period, and type using interactive CLI prompts through questionary.
        Validates user input and creates a new Habit object if all fields are selected.
        """
        name: str = text("Enter the habit name (or type 'cancel' to go back):").ask()

        if not name or name.lower() == 'cancel':
            print("Habit creation cancelled...")
            return

        period_choice = select(
            "Select the habit period:",
            choices=[p.value for p in HabitPeriod] + ["Cancel"]
        ).ask()

        if not period_choice or period_choice == "Cancel":
            print("Habit creation cancelled.\n")
            return

        try:
            habit_period = HabitPeriod(period_choice)
        except KeyError:
            print("Invalid habit period selected.\n")
            return

        type_choice = select(
            "Select the habit type:",
            choices=[t.value for t in HabitType] + ["Cancel"]
        ).ask()

        if not type_choice or type_choice == "Cancel":
            print("Habit creation cancelled.\n")
            return

        try:
            habit_type = HabitType(type_choice)
        except KeyError:
            print("Invalid habit type selected.\n")
            return

        habit = Habit(name=name, habit_period=habit_period, habit_type=habit_type)
        self.db.insert_habit_info(habit)
        print(f"Habit '{name}' created successfully.\n")

    def update_habit(self, habit_id: int):
        """Updates an existing habit's name, period, and type.

        Prompts the user to enter new values for the selected habit. Once the input is collected, the database is updated with the new habit information.

        Args:
            habit_id(int): The ID of the habit to be updated.

        """
        new_name: str = text("Enter the new name for the habit:").ask()

        new_period_choice = select(
            "Select the new habit period:",
            choices=[p.value for p in HabitPeriod]
        ).ask()
        new_period = HabitPeriod[new_period_choice.upper()]

        new_type_choice = select(
            "Select the new habit type:",
            choices=[t.value for t in HabitType]
        ).ask()
        new_type = HabitType[new_type_choice.upper()]

        self.db.change_habit_info(
            habit_id=habit_id,
            new_name=new_name,
            new_habit_period=new_period,
            new_habit_type=new_type
        )

        print(f"\nHabit updated")

    def delete_habit(self, habit_id: int):
        """Deletes a habit from the tracker after user confirmation.

        Args:
            habit_id(int): The ID of the habit to be deleted.
        """
        if habit_id is not None and confirm("Are you sure you want to delete this habit?").ask():
            self.db.delete_habit_info(habit_id)
            print(f"Habit deleted successfully.\n")

    def archive_habit(self, habit_id: int):
        """Archives a habit, making it as inactive after confirmation.

        Args:
            habit_id(int): The ID of the habit to be archived.
        """
        if habit_id is not None and confirm("Are you sure you want to archive this habit?").ask():
            self.db.archive_habit_info(habit_id)
            print(f"Habit archived successfully.\n")

    def mark_habit_completed(self, habit_id: int):
        """Marks the given habit as completed for the current day.

        This also updates the streak information of the habit in the database.

        Args:
            habit_id(int): The ID of the habit to be marked as completed.

        Returns:
            dict or None: A dictionary containing streak info:
                - "new_streak" (int): Updated current streak value.
                - "streak_broken" (bool): True if the user broke their previous streak.
            Returns None if the habit doesn't exist or if the operation is cancelled.
            """
        if habit_id is None:
            print("No habit selected.\n")
            return

        should_continue = True if self.test_mode else confirm("Do you want to mark this habit as completed?").ask()

        if should_continue:
            result = self.db.insert_habit_completion(habit_id)
            if not result:
                print("Could not complete the habit, make sure it exists.\n")
                return

            if result["streak_broken"]:
                print("You missed your habit last time, starting new streak from today...")
            elif result["new_streak"] == 1:
                print("New habit streak started! ⏳")
            else:
                print("Habit marked as completed successfully.\n")

            return result
        else:
            print("Habit completion cancelled.\n")

    def view_habits(self):
        """Displays all active habits and allows the user to select from them.

        Provides a menu interface to:
            - Mark a habit as completed
            - Edit the habit
            - Archive the habit
            - Delete the habit

        Continues until the user chooses to return to the main menu.

        Returns:
            None
        """
        while True:
            habits = self.db.fetch_all_habits()
            if not habits:
                print("No habits found. Please create a habit first.\n")
                return None

            habit_choices = []
            habit_lookup = {}

            for idx, h in enumerate(habits, start=1):
                streak_broken, days_missed = self.db.reset_broken_streak(h)
                if streak_broken:
                    print(
                        f"‼️ You missed your {h[2].title()} streak for habit '{h[1]}'! Missed by {days_missed} day(s)...Better luck next time!")

                completed = self.db.is_habit_completed(h)
                status = "✅" if completed else "🔲"
                habit_choices.append(f"[{idx}] {status} {h[1]} - {h[2].title()}, {h[3].title()}")
                habit_lookup[idx] = h

            habit_choices.append("Go back to main menu")

            selection = select(
                "Select a habit for further actions:",
                choices=habit_choices
            ).ask()

            if selection == "Go back to main menu":
                print("Returning to main menu...")
                break
            
            
            selected_index = int(selection.split("]")[0][1:])
            h = habit_lookup[selected_index]
            habit_id = h[0]

            while True:
                habit_completed = self.db.is_habit_completed(h)
                action = [
                    "Edit habit",
                    "Archive habit",
                    "Delete habit",
                    "Go back to selection"
                ]

                if not habit_completed:
                    action.insert(0, "Mark habit as completed")

                select_actions = select(
                    "What would you like to do with this habit?",
                    choices=action).ask()
                break
            if select_actions == "Mark habit as completed":
                self.mark_habit_completed(habit_id)
            elif select_actions == "Edit habit":
                self.update_habit(habit_id)
            elif select_actions == "Archive habit":
                self.archive_habit(habit_id)
            elif select_actions == "Delete habit":
                self.delete_habit(habit_id)
            elif select_actions == "Go back to selection":
                continue