import os
from datetime import datetime, timedelta
from habit_components.db import DBManager
from habit_components.habit import Habit, HabitPeriod, HabitType

class TestDBManager:
    """Tests all the methods found in the DBManager class."""
    def setup_method(self):
        self.db_name = "test_habit_tracker.db"
        self.db = DBManager(db_name=self.db_name)

        self.db.cursor.execute('DELETE FROM completions')
        self.db.cursor.execute('DELETE FROM habits')
        self.db.is_conn.commit()

    def test_insert_and_fetch_habit(self):
        habit = Habit("Test Habit", HabitPeriod.DAILY, HabitType.POSITIVE)
        self.db.insert_habit_info(habit)

        results = self.db.fetch_all_habits()
        assert len(results) == 1
        assert results[0][1] == "Test Habit"
        assert results[0][2] == "DAILY"
        assert results[0][3] == "POSITIVE"

    def test_change_habit_info(self):
        habit = Habit("Old Habit", HabitPeriod.DAILY, HabitType.POSITIVE)
        self.db.insert_habit_info(habit)
        habit_id = self.db.fetch_all_habits()[0][0]

        self.db.change_habit_info(
            habit_id = habit_id,
            new_name="Updated Habit",
            new_habit_period=HabitPeriod.WEEKLY,
            new_habit_type=HabitType.NEGATIVE
        )

        updated = self.db.fetch_habit_by_id(habit_id)
        assert updated[1] == "Updated Habit"
        assert updated[2] == "WEEKLY"
        assert updated[3] == "NEGATIVE"

    def test_archive_and_delete_habit(self):
        habit = Habit("Archivable Habit", HabitPeriod.DAILY, HabitType.NEGATIVE)
        self.db.insert_habit_info(habit)
        habit_id = self.db.fetch_all_habits()[0][0]

        self.db.archive_habit_info(habit_id)
        archived = self.db.fetch_habit_by_id(habit_id)
        assert archived[8] == 0

        self.db.delete_habit_info(habit_id)
        deleted = self.db.fetch_habit_by_id(habit_id)
        assert deleted is None

    def test_insert_habit_completion_and_streak(self):
        habit = Habit("Daily Test", HabitPeriod.DAILY, HabitType.POSITIVE)
        self.db.insert_habit_info(habit)
        habit_id = self.db.fetch_all_habits()[0][0]

        result_1 = self.db.insert_habit_completion(habit_id)
        assert result_1 is not None, "insert_habit_completion returned None"
        assert result_1["new_streak"] == 1
        assert not result_1["streak_broken"]

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%b %d, %Y at %H:%M")
        self.db.cursor.execute("UPDATE habits SET last_completed_at = ? WHERE id = ?", (yesterday, habit_id))
        self.db.is_conn.commit()
        
        result_2 = self.db.insert_habit_completion(habit_id)
        assert result_2 is not None, "insert_habit_completion returned None"
        assert result_2["new_streak"] == 2

    def test_reset_broken_streak(self):
        habit = Habit("Weekly Test", HabitPeriod.WEEKLY, HabitType.NEGATIVE, last_completed_at=(datetime.now() - timedelta(days=10)).strftime("%b %d, %Y at %H:%M"))
        self.db.insert_habit_info(habit)

        habit_record = self.db.fetch_all_habits()[0]
        broken, days = self.db.reset_broken_streak(habit_record)

        assert broken is True
        assert days > 7
        updated = self.db.fetch_habit_by_id(habit_record[0])
        assert updated[6] == 0

    def test_is_habit_completed_true_false(self):
        now = datetime.now().strftime("%b %d, %Y at %H:%M")
        habit = Habit("Today Done", HabitPeriod.DAILY, HabitType.POSITIVE, last_completed_at=now)
        self.db.insert_habit_info(habit)

        daily_habit = self.db.fetch_all_habits()[0]
        assert self.db.is_habit_completed(daily_habit) is True

        old = (datetime.now() - timedelta(days=8)).strftime("%b %d, %Y at %H:%M")
        habit2 = Habit("Late Weekly", HabitPeriod.WEEKLY, HabitType.NEGATIVE, last_completed_at=old)
        self.db.insert_habit_info(habit2)

        weekly_habit = self.db.fetch_all_habits()[1]
        assert self.db.is_habit_completed(weekly_habit) is False

    def test_fetch_completions_and_names(self):
        habit = Habit("Completions Habit", HabitPeriod.DAILY, HabitType.POSITIVE)
        self.db.insert_habit_info(habit)
        habit_id = self.db.fetch_all_habits()[0][0]
        self.db.insert_habit_completion(habit_id)

        completions = self.db.fetch_habit_completions(habit_id)
        assert len(completions) >= 1

        names = self.db.fetch_habit_names()
        assert "Completions Habit" in names    

    def test_streak_reports(self):
        habit1 = Habit("Streak A", HabitPeriod.DAILY, HabitType.POSITIVE)
        habit2 = Habit("Streak B", HabitPeriod.WEEKLY, HabitType.NEGATIVE)
        self.db.insert_habit_info(habit1)
        self.db.insert_habit_info(habit2)

        streaks = self.db.fetch_all_streaks()
        assert any(row[0] == "Streak A" for row in streaks)
        assert any(row[0] == "Streak B" for row in streaks)

    def teardown_method(self):
        self.db.close_conn()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    