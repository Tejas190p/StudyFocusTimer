
import json
import time
import msvcrt
from pathlib import Path

STATS_FILE = Path("study_stats.json")

DEFAULT_FOCUS_MINUTES = 25
DEFAULT_BREAK_MINUTES = 5


def load_stats():
    """Load saved statistics, or start with zero sessions."""
    if STATS_FILE.exists():
        try:
            with STATS_FILE.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            print("Could not read saved stats. Starting fresh.")

    return {
        "completed_sessions": 0,
        "total_focus_minutes": 0
    }


def save_stats(stats):
    """Save statistics to a local JSON file."""
    with STATS_FILE.open("w", encoding="utf-8") as file:
        json.dump(stats, file, indent=4)


def get_minutes(message, default):
    """Ask for a duration, using the default when input is empty."""
    while True:
        answer = input(
            f"{message} (default {default} minutes): "
        ).strip()

        if not answer:
            return default

        try:
            minutes = int(answer)
            if minutes > 0:
                return minutes
            print("Enter a number greater than zero.")
        except ValueError:
            print("Please enter a whole number, such as 25.")


def run_timer(minutes, session_name):
    """Run a countdown. Press P to pause/resume or S to stop."""
    remaining = minutes * 60
    last_tick = time.monotonic()
    paused = False
    last_display = None

    print(f"\n{session_name} started for {minutes} minute(s).")
    print("Press P to pause/resume, or S to stop early.")

    while remaining > 0:
        now = time.monotonic()

        if msvcrt.kbhit():
            key = msvcrt.getwch().lower()

            if key == "p":
                paused = not paused
                print("\nPaused." if paused else "\nResumed.")
                last_tick = time.monotonic()

            elif key == "s":
                print("\nTimer stopped.")
                return False

        now = time.monotonic()

        if not paused:
            remaining -= now - last_tick

        last_tick = now

        if not paused:
            seconds_left = max(0, int(remaining + 0.999))
            if seconds_left != last_display:
                mins, secs = divmod(seconds_left, 60)
                print(
                    f"\rTime remaining: {mins:02d}:{secs:02d} ",
                    end="",
                    flush=True
                )
                last_display = seconds_left

        time.sleep(0.1)

    print("\n\nTime is up! Great work!")
    print("\a", end="", flush=True)
    return True


def show_stats(stats):
    """Display the user's study progress."""
    print("\n--- YOUR STUDY STATISTICS ---")
    print(f"Completed focus sessions: {stats['completed_sessions']}")
    print(f"Total focus time: {stats['total_focus_minutes']} minutes")
    print("-----------------------------")


def main():
    stats = load_stats()

    while True:
        print("\n====== STUDY FOCUS TIMER ======")
        print("1. Start focus session")
        print("2. Start short break")
        print("3. View statistics")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            minutes = get_minutes(
                "Focus duration", DEFAULT_FOCUS_MINUTES
            )

            completed = run_timer(minutes, "Focus session")

            if completed:
                stats["completed_sessions"] += 1
                stats["total_focus_minutes"] += minutes
                save_stats(stats)
                print("Your study progress has been saved!")

        elif choice == "2":
            minutes = get_minutes(
                "Break duration", DEFAULT_BREAK_MINUTES
            )
            run_timer(minutes, "Short break")

        elif choice == "3":
            show_stats(stats)

        elif choice == "4":
            print("Keep learning. See you next time!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
