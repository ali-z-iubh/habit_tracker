import os
import pytest
from unittest.mock import patch, MagicMock
from habit_components.habit_tracker import HabitTracker
from habit_components.habit import Habit, HabitPeriod, HabitType


@pytest.fixture(autouse=True)
def disable_prompt_toolkit_console():
    with patch("prompt_toolkit.output.defaults.create_output"), \
         patch("prompt_toolkit.input.defaults.create_input"):
        yield


class TestHabitTracker:
    """Tests all the methods inside the HabitTracker class."""

    def setup_method(self):
        self.db_name = "test_habit_tracker.db"
        self.tracker = HabitTracker(db_name=self.db_name, test_mode=True)
        self.tracker.db.cursor.execute("DELETE FROM completions")
        self.tracker.db.cursor.execute("DELETE FROM habits")
        self.tracker.db.is_conn.commit()

        # Add 5 habits
        self.tracker.db.insert_habit_info(Habit("Read a book", HabitPeriod.DAILY, HabitType.POSITIVE))
        self.tracker.db.insert_habit_info(Habit("Exercise 15 minutes", HabitPeriod.DAILY, HabitType.POSITIVE))
        self.tracker.db.insert_habit_info(Habit("Limit device usage", HabitPeriod.DAILY, HabitType.NEGATIVE))
        self.tracker.db.insert_habit_info(Habit("Deep cleaning", HabitPeriod.WEEKLY, HabitType.POSITIVE))
        self.tracker.db.insert_habit_info(Habit("Binge-eating", HabitPeriod.WEEKLY, HabitType.NEGATIVE))

    def test_create_habit(self):
        habit = Habit("Test Create", HabitPeriod.DAILY, HabitType.POSITIVE)
        self.tracker.db.insert_habit_info(habit)

        habits = self.tracker.db.fetch_all_habits()
        names = [h[1] for h in habits]

        assert "Test Create" in names

    @patch("habit_components.habit_tracker.confirm")
    def test_mark_habit_completed(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True
        habit = self.tracker.db.fetch_all_habits()[0]
        habit_id = habit[0]
        before = habit[6]

        result = self.tracker.mark_habit_completed(habit_id)
        updated = self.tracker.db.fetch_habit_by_id(habit_id)
        after = updated[6]

        assert result is not None
        assert after == before + 1
        assert result["new_streak"] == after

    def test_update_habit(self):
        habit = self.tracker.db.fetch_all_habits()[0]
        habit_id = habit[0]

        self.tracker.db.change_habit_info(
            habit_id,
            new_name="Updated Habit",
            new_habit_period=HabitPeriod.WEEKLY,
            new_habit_type=HabitType.NEGATIVE
        )

        updated = self.tracker.db.fetch_habit_by_id(habit_id)
        assert updated[1] == "Updated Habit"
        assert updated[2] == "WEEKLY"
        assert updated[3] == "NEGATIVE"

    @patch("habit_components.habit_tracker.confirm")
    def test_archive_habit(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True
        habit = self.tracker.db.fetch_all_habits()[0]
        habit_id = habit[0]

        self.tracker.archive_habit(habit_id)
        updated = self.tracker.db.fetch_habit_by_id(habit_id)
        assert updated[8] == 0

    @patch("habit_components.habit_tracker.confirm")
    def test_delete_habit(self, mock_confirm):
        mock_confirm.return_value.ask.return_value = True
        habit = self.tracker.db.fetch_all_habits()[0]
        habit_id = habit[0]

        self.tracker.delete_habit(habit_id)
        assert self.tracker.db.fetch_habit_by_id(habit_id) is None

    @patch("builtins.print")
    def test_view_habits_when_no_habits(self, mock_print):
        # Clear habits first
        self.tracker.db.cursor.execute("DELETE FROM habits")
        self.tracker.db.is_conn.commit()

        result = self.tracker.view_habits()
        mock_print.assert_any_call("No habits found. Please create a habit first.\n")
        assert result is None

    @patch("builtins.print")
    def test_view_habits_when_none_active(self, mock_print):
        self.tracker.db.cursor.execute("UPDATE habits SET is_active = 0")
        self.tracker.db.is_conn.commit()

        result = self.tracker.view_habits()
        mock_print.assert_any_call("No habits found. Please create a habit first.\n")
        assert result is None

    @patch("habit_components.habit_tracker.select")
    def test_view_habits_uncompleted_habit_completed(self, mock_select):
        habit = Habit("Test Habit", HabitPeriod.DAILY, HabitType.POSITIVE)
        self.tracker.db.insert_habit_info(habit)

        # Configure .ask() to return selections in order
        mock_select_instance = MagicMock()
        mock_select_instance.ask.side_effect = [
            "[6] 🔲 Test Habit - Daily, Positive",  # habit selection
            "Mark habit as completed",              # action
            "[6] ✅ Test Habit - Daily, Positive",  # next habit selection
            "Go back to selection",                 # skip further action
            "Go back to main menu"                  # exit CLI        
            ]
        mock_select.return_value = mock_select_instance

        self.tracker.view_habits()

        updated = self.tracker.db.fetch_habit_by_id(6)
        assert updated[6] == 1  # Current streak incremented

    @patch("habit_components.habit_tracker.select")
    @patch("builtins.print")
    def test_view_habits_with_completed_habit(self, mock_print, mock_select):
        habit = Habit(
            "Already done", HabitPeriod.DAILY, HabitType.POSITIVE,
            last_completed_at="Jun 02, 2025 at 08:00"
        )
        self.tracker.db.insert_habit_info(habit)

        mock_select.return_value.ask.side_effect = [
            "[6] ✅ Already done - Daily, Positive",  # Simulate selection
            "Go back to selection",
            "Go back to main menu"
        ]
        self.tracker.view_habits()

        mock_print.assert_any_call("Returning to main menu...")

    def teardown_method(self):
        self.tracker.db.close_conn()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
