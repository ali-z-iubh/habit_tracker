import habit_components.analytics

class TestAnalytics:
    """Tests all the methods inside the analytics module."""

    def setup_method(self):
        self.sample_habits = [
            (1, "Limit device usage", "DAILY", "NEGATIVE", "", "", 3, 5, 1),
            (2, "Workout", "WEEKLY", "POSITIVE", "", "", 1, 2, 1),
            (3, "Deep cleaning", "WEEKLY", "POSITIVE", "", "", 0, 1, 1),
            (4, "Read", "DAILY", "POSITIVE","", "", 0, 3, 0)
        ]

    def test_get_habits_by_period(self):
        """Tests whether habits are retrieved accurately according to their period selected."""
        daily = habit_components.analytics.get_habits_by_period(self.sample_habits, "Daily")
        weekly = habit_components.analytics.get_habits_by_period(self.sample_habits, "Weekly")

        assert all (h[2] == "DAILY" for h in daily)
        assert all (h[2] == "WEEKLY" for h in weekly)
        assert len(daily) == 2
        assert len(weekly) == 2

    def test_get_habits_by_type(self):
        """Tests whether habits are retrieved accurately according to their type selected."""
        positive = habit_components.analytics.get_habits_by_type(self.sample_habits, "Positive")
        negative = habit_components.analytics.get_habits_by_type(self.sample_habits, "Negative")

        assert all(h[3] == "POSITIVE" for h in positive)
        assert all(h[3] == "NEGATIVE" for h in negative)
        assert len(positive) == 3
        assert len(negative) == 1

    def test_list_habits_by_longest_streak(self):
        """Tests that all habits with the longest streak are returned correctly."""
        result = habit_components.analytics.list_habits_by_longest_streak(self.sample_habits)
        
        assert isinstance(result, list)
        assert len(result) > 0

        longest_streak = max(h[7] for h in self.sample_habits)

        for habit in result:
            assert habit[7] == longest_streak

        habit_names = [h[1] for h in result]
        assert "Limit device usage" in habit_names
        
    def test_get_current_streaks(self):
        """Tests the return of the list of habits with their current streaks."""
        streaks = habit_components.analytics.get_current_streaks(self.sample_habits)
        assert ("Limit device usage", "DAILY", 3) in streaks
        assert ("Workout", "WEEKLY", 1) in streaks
        assert all(s[2] > 0 for s in streaks)

    def test_get_longest_streak_for_name(self):
        """Tests to make sure the name of habit returns its longest streak."""
        result = habit_components.analytics.get_longest_streak_for_name(self.sample_habits, "Limit device usage")
        assert result is not None
        assert result[1] == "Limit device usage"
        assert result[7] == 5
        