from enum import Enum
from datetime import datetime
from typing import List, Optional

class HabitPeriod(Enum):
    """Enumeration of possible habit tracking periods.

    Attributes:
        DAILY: Represents a daily habit.
        WEEKLY: Represents a weekly habit.
    """
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"

class HabitType(Enum):
    """Enumeration of possible types for the habit.

    Attributes:
        POSITIVE: Represents a positive habit.
        NEGATIVE: Represents a negative habit.
    """
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"

class Habit:
    """Represents a user-defined habit with tracking metadata.

    This class stores information about a habit such as its name, period (daily/weekly),
    type (positive/negative), and tracking details like streaks and completion history.

    Attributes:
        id (Optional[int]): Unique identifier for the habit. Useful for database or file storage.
        name (str): The name of the habit.
        habit_period (HabitPeriod): Frequency at which the habit recurs (e.g., daily or weekly).
        habit_type (HabitType): Category or type of the habit.
        created_at (str): Timestamp of when the habit was created.
        last_completed_at (Optional[str]): Last date/time the habit was marked as completed.
        current_streak (int): Current number of consecutive completions.
        longest_streak (int): Longest recorded streak for this habit.
        is_active (bool): Whether the habit is currently active (not archived or deleted).
        completions (List[str]): Dates on which the habit was completed.
    """
    def __init__(self, name: str, habit_period: 'HabitPeriod', habit_type: 'HabitType', id: Optional[int] = None, created_at: Optional[str] = None,
        last_completed_at: Optional[str] = None, current_streak: int = 0, longest_streak: int = 0, is_active: bool = True, completions: Optional[List[str]] = None):
        self.id: Optional[int] = id
        self.name: str = name
        self.habit_period: 'HabitPeriod' = habit_period
        self.habit_type: 'HabitType' = habit_type
        self.created_at: Optional[str] = created_at or datetime.now().strftime("%b %d, %Y at %H:%M")
        self.last_completed_at: Optional[str] = last_completed_at
        self.current_streak: int = current_streak
        self.longest_streak: int = longest_streak
        self.is_active: bool = is_active
        self.completions: Optional[List[str]] = completions or []



