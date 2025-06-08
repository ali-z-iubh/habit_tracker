from habit_components.db import DBManager
from habit_components.habit import Habit, HabitPeriod, HabitType
from datetime import datetime, timedelta

def reset_database(db):
    """Deletes all the data present in the habits and completions tables."""
    print("Deleting all existing data for habits...")

    db.cursor.execute("DELETE FROM completions")
    db.cursor.execute("DELETE FROM habits")
    db.is_conn.commit()
    print("Database reset completed.\n")

def create_predefined_habits(db):
    """Adds habit data of 4 weeks in the habits table."""
    habits = [
        Habit("Read a book", HabitPeriod.DAILY, HabitType.POSITIVE),
        Habit("Exercise 15 minutes", HabitPeriod.DAILY, HabitType.POSITIVE),
        Habit("Limit device usage", HabitPeriod.DAILY, HabitType.NEGATIVE),
        Habit("Deep cleaning", HabitPeriod.WEEKLY, HabitType.POSITIVE),
        Habit("Binge-eating", HabitPeriod.WEEKLY, HabitType.NEGATIVE)
        ]
    for habit in habits:
        db.insert_habit_info(habit)
    db.is_conn.commit()
    print("Database has been inserted with predefined habits.")

def simulate_completion_dates(habit_id, habit_period, db, gaps=None):
    """Simulates habit completion data for the predefined habits."""
    if gaps is None:
        gaps = []
    now = datetime.now()
    completions = []

    if habit_period == HabitPeriod.DAILY:
        for i in range(28):
            if i not in gaps:
                date = now - timedelta(days=(27 - i))
                completions.append(date)
    elif habit_period == HabitPeriod.WEEKLY:
        for i in range(4):
            if i not in gaps:
                date = now - timedelta(weeks=(3 - i))
                completions.append(date)

    for date in completions:
        date_str = date.strftime("%b %d, %Y at %H:%M")
        db.cursor.execute(
            "INSERT INTO completions (habit_id, completed_at) VALUES (?,?)",
            (habit_id, date_str)
        )

    if completions:
        last = completions[-1].strftime("%b %d, %Y at %H:%M")
        streak = len(completions)
        db.cursor.execute('''
        UPDATE habits SET
        last_completed_at = ?,
        current_streak = ?,
        longest_streak = ?
        WHERE id = ?
        ''',
      (last, streak, streak, habit_id)
      )

    db.is_conn.commit()

def seed_data():
    """Runs the functions to reset the database to make it ready for predefined habits additions, and defines those habits in their respective tables."""
    db = DBManager("habit_tracker.db")
    reset_database(db)
    create_predefined_habits(db)

    print("Inserting 4 weeks of completion data...")
    db.cursor.execute("SELECT id, name, habit_period FROM habits")
    all_habits = db.cursor.fetchall()

    for h in all_habits:
        habit_id, name, period_str = h
        period = HabitPeriod(period_str)

        # Customize gaps per habit if needed
        if name == "Limit device usage":
            simulate_completion_dates(habit_id, period, db, gaps=[3, 10])
        elif name == "Binge-eating":
            simulate_completion_dates(habit_id, period, db, gaps=[2])
        else:
            simulate_completion_dates(habit_id, period, db)

        print(f" Added completions for '{name}'")

    db.close_conn()
    print("\nSeeding completed")


if __name__ == "__main__":
    seed_data()
