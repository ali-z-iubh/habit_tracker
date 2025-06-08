from questionary import select, confirm
from habit_components.habit_tracker import HabitTracker
import habit_components.analytics


def main():
    """This function creates the main menu with all the relevant actions."""
    tracker = HabitTracker()
    analytics = habit_components.analytics

    print("Welcome to the Habit Tracker App! \n")
    print("--------- MAIN MENU ---------")

    while True:
        choice = select(
            "What would you like to do?",
            choices=[
                "View all habits",
                "Create a new habit",
                "Analyze habits",
                "Exit"
            ]
        ).ask()

        if choice == "View all habits":
            tracker.view_habits()
        elif choice == "Create a new habit":
            tracker.create_habit()
        elif choice == "Analyze habits":
            analysis_options = select("What would you like to analyze?\n", choices=[
                "List habits by time-period",
                "List habits by type",
                "List habits by longest streak",
                "Show current streak for all habits",
                "View longest streak for a specific habit",
                "Back to main menu..."
            ]).ask()

            if analysis_options == "List habits by time-period":
                habits = tracker.db.fetch_all_habits()

                if not habits:
                    print("No habits found, please create a habit first.")
                else:
                    habit_period = select("Which period?\n", choices=["Daily", "Weekly"]).ask()
                    results = analytics.get_habits_by_period(habits, habit_period)

                    if not results:
                        print(f"No habits found for period: {habit_period}.")
                    else:
                        for h in results:
                            print(f"{h[1]} - {h[2].title()}")

            elif analysis_options == "List habits by type":
                habits = tracker.db.fetch_all_habits()

                if not habits:
                    print("No habits found, please create a habit first.")
                else:
                    habit_type = select("Which type?", choices=["Positive", "Negative"]).ask()

                    results = analytics.get_habits_by_type(habits, habit_type)
                    if not results:
                        print(f"No habits found for type: {habit_type}.")

                    else:
                        for h in results:
                            print(f"{h[1]} - {h[3].title()}")

            elif analysis_options == "List habits by longest streak":
                habits = tracker.db.fetch_all_habits()
                if not habits:
                    print("No habits found, please create a habit first.")
                else:
                    results = analytics.list_habits_by_longest_streak(habits)
                    
                    if not results:
                        print("No habit data available for analysis.")                    
                    else:
                        print("Habits by longest streak:\n")
                        for idx, h in enumerate(results, start=1):
                            print(f"{idx}. {h[1]} — 🔥 {h[7]} days")


            elif analysis_options == "Show current streak for all habits":
                habits = tracker.db.fetch_all_habits()
                streaks = analytics.get_current_streaks(habits)

                if not streaks:
                    print("No active habits with a current streak...")

                else:
                    for name, habit_period, current_streak in streaks:
                        print(f"{name} ({habit_period.title()}): ⏳ Current Streak = {current_streak}")

            elif analysis_options == "View longest streak for a specific habit":
                habits = tracker.db.fetch_all_habits()
                names = [h[1] for h in habits if  h [8] == 1]
                if not names:
                    print("No active habits found...please create a habit.")
                else:
                    selected = select("Choose a habit", choices=names).ask()
                    data = analytics.get_longest_streak_for_name(habits, selected)


                    if data:
                        print(f"Habit: {data[1]}\nCurrent Streak: {data[6]}\nLongest Streak: {data[7]}")
                    else:
                        print("Habit not found.")


            elif analysis_options == "Back to main menu...":
                pass
        
        elif choice == "Exit":
            if confirm("Are you sure you want to exit?").ask():
                print("Thank you for using the Habit Tracker App! Goodbye!")
                break


if __name__ == "__main__":
    main()