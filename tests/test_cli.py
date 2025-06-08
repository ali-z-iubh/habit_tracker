import os
import pytest
from unittest.mock import patch, MagicMock
import cli
from habit_components.habit_tracker import HabitTracker

@pytest.fixture(autouse=True)
def disable_prompt_toolkit_console():
    """Disables prompt toolkit in testing to bypass questionary and user input."""
    with patch("prompt_toolkit.output.defaults.create_output"), \
         patch("prompt_toolkit.input.defaults.create_input"):
        yield

class TestCLI:
    """
    Tests methods used in the component file cli.py.
    """

    def setup_method(self):
        self.db_name = "test_habit_tracker.db"
        self.tracker = HabitTracker(db_name=self.db_name, test_mode=True)
        self.tracker.db.cursor.execute("DELETE FROM completions")
        self.tracker.db.cursor.execute("DELETE FROM habits")
        self.tracker.db.is_conn.commit()

    @patch("cli.confirm")
    @patch("cli.select")
    def test_main_menu_exit(self, mock_select, mock_confirm):
        mock_select.return_value.ask.side_effect = ["Exit"]
        mock_confirm.return_value.ask.return_value = True

        with patch("builtins.print") as mock_print:
            cli.main()

        mock_print.assert_any_call("Thank you for using the Habit Tracker App! Goodbye!")

    @patch("cli.confirm")
    @patch("cli.select")
    @patch("cli.HabitTracker")
    def test_main_menu_create_habit_called(self, mock_tracker_class, mock_select, mock_confirm):
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        mock_select.return_value.ask.side_effect = [
            "Create a new habit",
            "Exit"
        ]

        with patch("cli.confirm") as mock_confirm:
            mock_confirm.return_value.ask.return_value = True
            cli.main()

        assert mock_tracker.create_habit.called

    @patch("cli.confirm")
    @patch("cli.select")
    @patch("cli.HabitTracker")
    def test_main_menu_view_habits_called(self, mock_tracker_class, mock_select, mock_confirm):
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        # Mock a valid habits list (tuple format from the DB)
        mock_tracker.db.fetch_all_habits.return_value = [
            (1, "Test Habit", "DAILY", "POSITIVE", "", "", 1, 3, 1)
        ]

        # Enough select inputs to enter and then exit
        mock_select.return_value.ask.side_effect = [
            "View all habits",  
            "[1] 🔲 Test Habit - Daily, Positive",  # habit selection
            "Go back to selection",        # inside habit action menu
            "Go back to main menu",        # exit outer view loop
            "Exit"                         # finally exit   # main menu# inside view_habits loop
        ]
        mock_confirm.return_value.ask.return_value = True

        cli.main()

        assert mock_tracker.view_habits.called

    @patch("cli.confirm")
    @patch("cli.select")
    @patch("habit_components.analytics.list_habits_by_longest_streak")
    @patch("cli.HabitTracker")
    def test_analytics_menu_accessed(
        self,
        mock_tracker_class,
        mock_list_longest_streak,
        mock_select,
        mock_confirm
    ):
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        mock_tracker.db.fetch_all_habits.return_value = [
            (1, "Test Habit", "DAILY", "POSITIVE", "", "", 2, 5, 1)
        ]

        # ✅ Return a list of habits
        mock_list_longest_streak.return_value = [
            (1, "Test Habit", "DAILY", "POSITIVE", "", "", 2, 5, 1)
        ]

        mock_select.return_value.ask.side_effect = [
            "Analyze habits",
            "List habits by longest streak",
            "Exit"
        ]
        mock_confirm.return_value.ask.return_value = True

        with patch("builtins.print") as mock_print:
            cli.main()

        mock_print.assert_any_call("1. Test Habit — 🔥 5 days")

    def teardown_method(self):
        self.tracker.db.close_conn()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
