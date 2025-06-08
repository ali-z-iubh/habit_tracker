def get_all_active_habits(habits):
    """Returns a list of all active habits.

    Args:
        habits (list): A list of habit records where index 8 represents the "active" status of the habit.
    """
    return list(filter(lambda h: h[8] == 1, habits))

def get_habits_by_period(habits, habit_period):
    """Returns a list of habits with the chosen period.

    Args:
        habits (list): A list of habit records with index 2 being the habit's period attribute.
        habit_period (str): The period to filter by (daily or weekly).

    Returns:
          list: A list of habits that match the selected period.
    """
    return list(filter(lambda h: h[2].upper() == habit_period.upper(), habits))

def get_habits_by_type(habits, habit_type):
    """Returns a list of habits with the chosen type.

    Args:
        habits (list): A list of habit records with index 2 being the habit's period attribute.
        habit_type (str): The type to filter by (positive or negative).

    Returns:
          list: A list of habits that match the selected type.
    """
    return list(filter(lambda h: h[3].upper() == habit_type.upper(), habits))

def list_habits_by_longest_streak(habits):
    """Returns all habits that have the longest streak value."""
    if not habits:
        return []

    max_streak = max(h[7] for h in habits)
    return [h for h in habits if h[7] == max_streak]

def get_current_streaks(habits):
    """Returns a list of active habits with their current streak.

    Args:
        habits (list): List of habit records.
    
    Returns:
        list: A list of tuples in the order (name, period, current_streak) for active streaks.
    """
    return [(h[1], h[2], h[6]) for h in habits if h[6] > 0]

def get_longest_streak_for_name(habits, name):
    """Returns the habit with the given name to check their longest streak.

    Args:
        habits (list): A list of habit records.
        name (str): The name of the habit to search for.

    Returns:
        list: A list of habit records that match the given name.
    """
    result = list(filter(lambda h: h[1].lower() == name.lower(), habits))
    return result[0] if result else None

