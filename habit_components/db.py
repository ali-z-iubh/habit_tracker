import os
import sqlite3
from datetime import datetime
from habit_components.habit import Habit


class DBManager:
    """Handles all database operations for the Habit Tracker app.

    Manages the SQLite3 database connection, schema creation, and all interactions involving habits and their completions.

    Attributes:
        is_conn (sqlite3.Connection): Active SQLite3 connection object.
        cursor (sqlite3.Cursor): Cursor used for executing SQL queries.
        """
    def __init__(self, db_name='habit_tracker.db'):
        """Initializes the database manager and creates tables if not present.

        Args:
            db_name (str): Name of the SQLite database file.
            """
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(root_path, db_name)
        self.is_conn = sqlite3.connect(db_path)
        self.cursor = self.is_conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates the tables if they don't already exist for habits and completions to track habits and streaks.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                habit_period TEXT NOT NULL,
                habit_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_completed_at TEXT,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
            );
        ''')
        self.is_conn.commit()

    # Habit CRUD methods
    def insert_habit_info(self, habit: Habit):
        """Inserts a new habit into the database.

        Args:
            habit (Habit): The Habit object containing habit details.
        """
        self.cursor.execute('''
            INSERT INTO habits (name, habit_period, habit_type, created_at, last_completed_at, current_streak, longest_streak, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (habit.name, habit.habit_period.value, habit.habit_type.value, habit.created_at, habit.last_completed_at,
              habit.current_streak, habit.longest_streak, int(habit.is_active)))
        self.is_conn.commit()

    def change_habit_info(self, habit_id, new_name, new_habit_period, new_habit_type):
        """Updates a habit's name, period, and type.

        Args:
            habit_id(int): The ID of the habit to update.
            new_name(str): The updated name for the habit.
            new_habit_period (HabitPeriod): The updated frequency/period for the habit.
            new_habit_type (HabitType): The updated type for the habit.
        """
        self.cursor.execute('''
            UPDATE habits SET name = ?, habit_period = ?, habit_type = ?
            WHERE id = ?
        ''', (new_name, new_habit_period.value, new_habit_type.value, habit_id))
        self.is_conn.commit()

    def archive_habit_info(self, habit_id: int):
        """Archives a habit by marking it as inactive.

        Args:
            habit_id(int): The ID of the habit to archive.
        """
        self.cursor.execute('''
            UPDATE habits SET is_active = 0 WHERE id = ?
        ''', (habit_id,))
        self.is_conn.commit()

    def delete_habit_info(self, habit_id: int):
        """Deletes a habit from the database.

        Args:
            habit_id(int): The ID of the habit to delete.
        """
        try:
            self.cursor.execute('''
                DELETE FROM habits WHERE id = ?
            ''', (habit_id,))
            self.is_conn.commit()
        except sqlite3.Error as e:
            print(f"Failed to delete habit {habit_id}: {e}")

    def fetch_all_habits(self, include_archived=False):
        """Fetches all habits from the database.

        Args:
            include_archived (bool): If True, includes archived habits.

        Returns:
            list: A list of habit records.
        """
        if include_archived:
            self.cursor.execute('SELECT * FROM habits')
        else:
            self.cursor.execute('SELECT * FROM habits WHERE is_active = 1')
        rows = self.cursor.fetchall()
        return rows
    
    # Habit tracking methods
    def insert_habit_completion(self, habit_id: int):
        """Marks a habit as completed and updates streaks in the database.

        Args:
            habit_id(int): The habit to be completed and its streak to be updated.

        Returns:
            dict or None: a dictionary with streak info:
                - "new_streak" (int): Updated streak count.
                - "streak_broken" (bool): True if streak was broken.
            Returns None if the habit is not found.
        """
        now = datetime.now()
        now_str = now.strftime("%b %d, %Y at %H:%M")

        self.cursor.execute(
            'SELECT last_completed_at, habit_period, current_streak, longest_streak FROM habits WHERE id = ?',
            (habit_id,))
        row = self.cursor.fetchone()

        if not row:
            print("Habit not found.")
            return

        last_completed_at, habit_period, current_streak, longest_streak = row
        new_streak = 1
        streak_broken = False

        if last_completed_at:
            try:
                last_time = datetime.strptime(last_completed_at, "%b %d, %Y at %H:%M")
                delta_days = (now - last_time).days

                if habit_period == "DAILY":
                    if delta_days == 1:
                        new_streak = current_streak + 1
                    elif delta_days > 1:
                        streak_broken = True

                elif habit_period == "WEEKLY":
                    if 1 <= delta_days <= 7:
                        new_streak = current_streak + 1
                    else:
                        streak_broken = True

            except ValueError:
                print("Could not parse last completed date.")

        new_longest = max(longest_streak, new_streak)

        self.cursor.execute('''
            INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)
        ''', (habit_id, now_str))

        self.cursor.execute('''
            UPDATE habits SET last_completed_at = ?, current_streak = ?, longest_streak = ?
            WHERE id = ?
        ''', (now_str, new_streak, new_longest, habit_id))

        self.is_conn.commit()

        return {
            "new_streak" : new_streak,
            "streak_broken" : streak_broken
        }

    def is_habit_completed(self, habit):
        """Checks whether a habit has already been completed today or this week.
        Args:
            habit (tuple): A habit record from the database.

        Returns:
            bool: True if the habit has already been completed within its period.
        """
        last_completed_at = habit[5]
        habit_period = habit[2]

        if not last_completed_at:
            return False

        try:
            last_time = datetime.strptime(last_completed_at, "%b %d, %Y at %H:%M")
            now = datetime.now()
            delta_days = (now - last_time).days

            if habit_period == "DAILY":
                return delta_days == 0

            elif habit_period == "WEEKLY":
                return delta_days < 7

        except Exception as e:
            print("Error parsing last_completed_at:", e)

        return False

    def fetch_habit_names(self):
        """Fetches names of active habits.

        Returns:
            list: A list of habit names.
        """
        self.cursor.execute('SELECT name FROM habits WHERE is_active = 1')
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_habit_by_id(self, habit_id: int):
        """Retrieves a single habit record by its ID.

        Args:
            habit_id (int): The ID of the habit.

        Returns:
            tuple or None: The habit record, or None if not found.
        """
        self.cursor.execute('SELECT * FROM habits WHERE id = ?', (habit_id,))
        return self.cursor.fetchone()

    def fetch_habit_completions(self, habit_id: int):
        """Gets all completion dates for a specific habit.

        Args:
            habit_id (int): The ID of the habit.

        Returns:
            list: A list of completion timestamps.
        """
        self.cursor.execute('''
            SELECT completed_at FROM completions
            WHERE habit_id = ? ORDER BY completed_at ASC
        ''', (habit_id,))
        return self.cursor.fetchall()


    def fetch_all_streaks(self):
        """Retrieves the current streaks of all active habits.

        Returns:
            list: A list of tuples with name, habit_period, and current_streak.
        """
        self.cursor.execute('SELECT name, habit_period, current_streak FROM habits WHERE is_active = 1')
        return self.cursor.fetchall()


    def reset_broken_streak(self, habit):
        """Resets the streak of a missed habit.

        Args:
            habit (tuple): A habit record.

        Returns:
            tuple: (bool, int) where bool indicates if the streak was reset, and int is the number of missed days.
        """
        habit_id = habit[0]
        last_completed_at = habit[5]
        habit_period = habit[2]

        if not last_completed_at:
            return False, 0

        try:
            last_time = datetime.strptime(last_completed_at, "%b %d, %Y at %H:%M")
            now = datetime.now()
            delta = (now - last_time).days

            if (habit_period == "DAILY" and delta > 1) or (habit_period == "WEEKLY" and delta > 7):
                self.cursor.execute('UPDATE habits SET current_streak = 0 WHERE id = ?', (habit_id,))
                self.is_conn.commit()
                return True, delta
        except Exception as e:
            print(f"Error checking streak for habit {habit_id}: {e}")

        return False, 0

  
    def close_conn(self):
        """Closes the database connection if found open."""
        if self.is_conn:
            self.is_conn.close()
            print("Connection closed.")
        else:
            print("No connection to close.")


if __name__ == "__main__":
    db_manager = DBManager()
    print("Database initialized and tables created.")
    db_manager.close_conn()