# Training Journal
# A training log with correlation analysis for marathon runners

import json
from datetime import datetime, timedelta

# File to store data
DATA_FILE = "training_data.json"

# Your marathon goal
GOAL = "2:32:00 Boston"

# All entries stored here
entries = []


# =============================================================================
# DATA PERSISTENCE
# =============================================================================

def load_data():
    """Load entries from file"""
    global entries
    try:
        with open(DATA_FILE, "r") as f:
            entries = json.load(f)
        print(f"Loaded {len(entries)} entries.")
    except FileNotFoundError:
        entries = []


def save_data():
    """Save entries to file"""
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2)


# =============================================================================
# INPUT HELPERS
# =============================================================================

def get_input(prompt, input_type="str", required=True, options=None):
    """Get validated input from user"""
    while True:
        value = input(prompt).strip()

        # Handle optional fields
        if not required and value == "":
            return None

        # Validate options (for choice fields)
        if options:
            if value.lower() in [o.lower() for o in options]:
                return value.lower()
            print(f"  Please enter one of: {', '.join(options)}")
            continue

        # Validate by type
        if input_type == "str":
            if value:
                return value
        elif input_type == "float":
            try:
                return float(value)
            except ValueError:
                print("  Please enter a number.")
                continue
        elif input_type == "int":
            try:
                return int(value)
            except ValueError:
                print("  Please enter a whole number.")
                continue
        elif input_type == "yn":
            if value.lower() in ["y", "n", "yes", "no"]:
                return value.lower() in ["y", "yes"]
            print("  Please enter y or n.")
            continue
        elif input_type == "date":
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return value
            except ValueError:
                print("  Please use format YYYY-MM-DD.")
                continue
        elif input_type == "pace":
            try:
                parts = value.split(":")
                if len(parts) == 2:
                    int(parts[0])
                    int(parts[1])
                    return value
            except:
                pass
            print("  Please use format M:SS (e.g., 7:30).")
            continue
        elif input_type == "rating":
            try:
                num = int(value)
                if 1 <= num <= 10:
                    return num
            except:
                pass
            print("  Please enter a number from 1-10.")
            continue

        if required:
            print("  This field is required.")


# =============================================================================
# ADD ENTRY
# =============================================================================

def add_entry():
    """Add a new training entry"""
    print("\n" + "=" * 40)
    print("  ADD NEW ENTRY")
    print("=" * 40)

    entry = {}

    # Basic info
    print("\n-- Basic Info --")
    entry["date"] = get_input("Date (YYYY-MM-DD): ", "date")
    entry["time_of_day"] = get_input("Time of day (am/afternoon/pm): ", options=["am", "afternoon", "pm"])
    entry["type"] = get_input("Type (workout/easy/rest): ", options=["workout", "easy", "rest"])

    # Run data (skip if rest day)
    if entry["type"] == "rest":
        entry["miles"] = 0
        entry["pace"] = None
        entry["hr"] = None
    else:
        print("\n-- Run Data --")
        entry["miles"] = get_input("Miles: ", "float")
        entry["pace"] = get_input("Pace (M:SS): ", "pace")
        entry["hr"] = get_input("Avg HR during run: ", "int", required=False)

    # Device metrics
    print("\n-- Device Metrics --")
    entry["rhr"] = get_input("Resting HR: ", "int", required=False)
    entry["hrv"] = get_input("HRV: ", "int", required=False)

    # Subjective scores
    print("\n-- Subjective Scores (1-10) --")
    entry["rpe"] = get_input("RPE (effort level): ", "rating", required=False)
    entry["sleep_quality"] = get_input("Sleep quality: ", "rating", required=False)
    entry["stress"] = get_input("Stress level: ", "rating", required=False)

    # Lifestyle factors
    print("\n-- Lifestyle Factors --")
    entry["caffeine"] = get_input("Caffeine (cups, 0 if none): ", "int", required=False)
    entry["alcohol"] = get_input("Alcohol yesterday (y/n): ", "yn", required=False)
    entry["nicotine"] = get_input("Nicotine yesterday (y/n): ", "yn", required=False)
    entry["travel"] = get_input("Travel (y/n): ", "yn", required=False)
    entry["stretch"] = get_input("Stretched (y/n): ", "yn", required=False)
    entry["music"] = get_input("Music (y/n): ", "yn", required=False)

    # Add timestamp for sorting
    entry["created_at"] = datetime.now().isoformat()

    # Save
    entries.append(entry)
    save_data()

    print("\n✓ Entry saved!")


# =============================================================================
# VIEW HISTORY
# =============================================================================

def view_history():
    """View list of entries and drill into details"""
    if not entries:
        print("\nNo entries yet.")
        return

    # Sort by date (most recent first)
    sorted_entries = sorted(entries, key=lambda x: x["date"], reverse=True)

    print("\n" + "=" * 40)
    print("  RUN HISTORY")
    print("=" * 40)

    # Show list
    for i, entry in enumerate(sorted_entries[:20], 1):  # Show last 20
        type_str = entry["type"].upper()
        if entry["type"] == "rest":
            print(f"  {i}. {entry['date']} | REST")
        else:
            print(f"  {i}. {entry['date']} | {entry['miles']}mi | {entry['pace']} | {type_str}")

    print("\n  Enter number to view details, or press Enter to go back.")
    choice = input("  Selection: ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(sorted_entries):
            view_single_entry(sorted_entries[idx])


def view_single_entry(entry):
    """Display all details for a single entry"""
    print("\n" + "-" * 40)
    print("  ENTRY DETAILS")
    print("-" * 40)

    print(f"\n  Date:         {entry['date']}")
    print(f"  Time of day:  {entry['time_of_day']}")
    print(f"  Type:         {entry['type']}")

    if entry["type"] != "rest":
        print(f"\n  Miles:        {entry['miles']}")
        print(f"  Pace:         {entry['pace']}")
        if entry.get("hr"):
            print(f"  Avg HR:       {entry['hr']} bpm")

    print(f"\n  Resting HR:   {entry.get('rhr', '-') or '-'}")
    print(f"  HRV:          {entry.get('hrv', '-') or '-'}")

    print(f"\n  RPE:          {entry.get('rpe', '-') or '-'}/10")
    print(f"  Sleep:        {entry.get('sleep_quality', '-') or '-'}/10")
    print(f"  Stress:       {entry.get('stress', '-') or '-'}/10")

    print(f"\n  Caffeine:     {entry.get('caffeine', '-') or '-'} cups")
    print(f"  Alcohol:      {'Yes' if entry.get('alcohol') else 'No' if entry.get('alcohol') is False else '-'}")
    print(f"  Nicotine:     {'Yes' if entry.get('nicotine') else 'No' if entry.get('nicotine') is False else '-'}")
    print(f"  Travel:       {'Yes' if entry.get('travel') else 'No' if entry.get('travel') is False else '-'}")
    print(f"  Stretch:      {'Yes' if entry.get('stretch') else 'No' if entry.get('stretch') is False else '-'}")
    print(f"  Music:        {'Yes' if entry.get('music') else 'No' if entry.get('music') is False else '-'}")

    print("-" * 40)
    input("\n  Press Enter to go back...")


# =============================================================================
# WEEKLY SUMMARY
# =============================================================================

def get_week_bounds(date_str):
    """Get Monday and Sunday of the week containing date_str"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


def weekly_summary():
    """Show weekly summary statistics"""
    if not entries:
        print("\nNo entries yet.")
        return

    # Get available weeks
    weeks = set()
    for entry in entries:
        monday, sunday = get_week_bounds(entry["date"])
        weeks.add((monday, sunday))

    weeks = sorted(weeks, reverse=True)

    print("\n" + "=" * 40)
    print("  WEEKLY SUMMARY")
    print("=" * 40)
    print("\n  Available weeks:")

    for i, (monday, sunday) in enumerate(weeks[:10], 1):
        print(f"  {i}. {monday} to {sunday}")

    print("\n  Enter number to view, or press Enter for most recent.")
    choice = input("  Selection: ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(weeks):
            show_week_stats(weeks[idx])
    elif choice == "" and weeks:
        show_week_stats(weeks[0])


def show_week_stats(week_tuple):
    """Calculate and display stats for a specific week"""
    monday, sunday = week_tuple

    # Filter entries for this week
    week_entries = [
        e for e in entries
        if monday <= e["date"] <= sunday
    ]

    if not week_entries:
        print("\n  No entries for this week.")
        return

    # Calculate stats
    run_entries = [e for e in week_entries if e["type"] != "rest"]
    rest_days = len([e for e in week_entries if e["type"] == "rest"])

    total_miles = sum(e["miles"] for e in week_entries)
    num_runs = len(run_entries)

    # Averages (only from entries that have the data)
    def avg(key, entry_list=run_entries):
        values = [e.get(key) for e in entry_list if e.get(key) is not None]
        return sum(values) / len(values) if values else None

    avg_rhr = avg("rhr", week_entries)
    avg_hrv = avg("hrv", week_entries)
    avg_hr = avg("hr")
    avg_rpe = avg("rpe")
    avg_sleep = avg("sleep_quality", week_entries)
    avg_stress = avg("stress", week_entries)

    # Calculate average pace
    total_seconds = 0
    pace_count = 0
    for e in run_entries:
        if e.get("pace"):
            parts = e["pace"].split(":")
            total_seconds += int(parts[0]) * 60 + int(parts[1])
            pace_count += 1
    avg_pace = None
    if pace_count > 0:
        avg_sec = total_seconds / pace_count
        avg_pace = f"{int(avg_sec // 60)}:{int(avg_sec % 60):02d}"

    # Display
    print("\n" + "-" * 40)
    print(f"  WEEK: {monday} to {sunday}")
    print("-" * 40)

    print(f"\n  Total Miles:    {total_miles:.1f}")
    print(f"  Runs:           {num_runs}")
    print(f"  Rest Days:      {rest_days}")

    if avg_pace:
        print(f"\n  Avg Pace:       {avg_pace}/mile")
    if avg_hr:
        print(f"  Avg HR (run):   {avg_hr:.0f} bpm")

    if avg_rhr:
        print(f"\n  Avg RHR:        {avg_rhr:.0f} bpm")
    if avg_hrv:
        print(f"  Avg HRV:        {avg_hrv:.0f}")

    if avg_rpe:
        print(f"\n  Avg RPE:        {avg_rpe:.1f}/10")
    if avg_sleep:
        print(f"  Avg Sleep:      {avg_sleep:.1f}/10")
    if avg_stress:
        print(f"  Avg Stress:     {avg_stress:.1f}/10")

    print("-" * 40)
    input("\n  Press Enter to go back...")


# =============================================================================
# INSIGHTS / CORRELATION ANALYSIS
# =============================================================================

def insights():
    """Analyze correlations between lifestyle factors and metrics"""
    if len(entries) < 5:
        print("\n  Need at least 5 entries for insights.")
        return

    print("\n" + "=" * 40)
    print("  INSIGHTS")
    print("=" * 40)

    # Analyze impact of boolean factors on RPE, RHR, HRV
    factors = [
        ("alcohol", "Alcohol"),
        ("nicotine", "Nicotine"),
        ("travel", "Travel"),
        ("stretch", "Stretching"),
        ("music", "Music"),
    ]

    metrics = [
        ("rpe", "RPE", True),      # True = higher is worse
        ("rhr", "RHR", True),      # True = higher is worse
        ("hrv", "HRV", False),     # False = higher is better
    ]

    print("\n  Factor Impact Analysis:")
    print("  " + "-" * 36)

    for factor_key, factor_name in factors:
        impacts = []

        for metric_key, metric_name, higher_is_worse in metrics:
            impact = calculate_impact(factor_key, metric_key, higher_is_worse)
            if impact:
                impacts.append(f"{metric_name}: {impact}")

        if impacts:
            print(f"\n  {factor_name}:")
            for impact in impacts:
                print(f"    • {impact}")

    # Sleep quality correlation
    print("\n  " + "-" * 36)
    print("\n  Sleep Quality Impact:")
    sleep_impact = analyze_sleep_impact()
    if sleep_impact:
        for line in sleep_impact:
            print(f"    • {line}")

    # Caffeine analysis
    print("\n  " + "-" * 36)
    print("\n  Caffeine Impact:")
    caffeine_impact = analyze_caffeine_impact()
    if caffeine_impact:
        for line in caffeine_impact:
            print(f"    • {line}")

    print("\n" + "=" * 40)
    input("\n  Press Enter to go back...")


def calculate_impact(factor_key, metric_key, higher_is_worse):
    """Calculate impact of a boolean factor on a metric"""
    # Split entries by factor
    with_factor = [e for e in entries if e.get(factor_key) is True and e.get(metric_key) is not None]
    without_factor = [e for e in entries if e.get(factor_key) is False and e.get(metric_key) is not None]

    if len(with_factor) < 2 or len(without_factor) < 2:
        return None

    avg_with = sum(e[metric_key] for e in with_factor) / len(with_factor)
    avg_without = sum(e[metric_key] for e in without_factor) / len(without_factor)

    diff = avg_with - avg_without

    # Determine impact direction and magnitude
    if higher_is_worse:
        if diff > 0.5:
            direction = "negative"
        elif diff < -0.5:
            direction = "positive"
        else:
            return "no significant impact"
    else:
        if diff > 0.5:
            direction = "positive"
        elif diff < -0.5:
            direction = "negative"
        else:
            return "no significant impact"

    magnitude = abs(diff)
    if magnitude > 2:
        strength = "strong"
    elif magnitude > 1:
        strength = "moderate"
    else:
        strength = "minor"

    return f"{strength} {direction} impact ({avg_with:.1f} vs {avg_without:.1f})"


def analyze_sleep_impact():
    """Analyze how sleep quality affects metrics"""
    results = []

    # Compare good sleep (7-10) vs poor sleep (1-4)
    good_sleep = [e for e in entries if e.get("sleep_quality") and e["sleep_quality"] >= 7]
    poor_sleep = [e for e in entries if e.get("sleep_quality") and e["sleep_quality"] <= 4]

    if len(good_sleep) < 2 or len(poor_sleep) < 2:
        return ["Not enough data (need entries with varied sleep quality)"]

    for metric_key, metric_name in [("rpe", "RPE"), ("rhr", "RHR"), ("hrv", "HRV")]:
        good_vals = [e[metric_key] for e in good_sleep if e.get(metric_key)]
        poor_vals = [e[metric_key] for e in poor_sleep if e.get(metric_key)]

        if good_vals and poor_vals:
            good_avg = sum(good_vals) / len(good_vals)
            poor_avg = sum(poor_vals) / len(poor_vals)
            diff = poor_avg - good_avg

            if abs(diff) > 0.5:
                direction = "higher" if diff > 0 else "lower"
                results.append(f"{metric_name}: {direction} with poor sleep ({poor_avg:.1f} vs {good_avg:.1f})")

    return results if results else ["No significant correlations found"]


def analyze_caffeine_impact():
    """Analyze caffeine consumption impact"""
    results = []

    # Compare no caffeine vs caffeine
    no_caffeine = [e for e in entries if e.get("caffeine") == 0 or e.get("caffeine") is None]
    with_caffeine = [e for e in entries if e.get("caffeine") and e["caffeine"] > 0]

    if len(no_caffeine) < 2 or len(with_caffeine) < 2:
        return ["Not enough data (need entries with varied caffeine intake)"]

    for metric_key, metric_name in [("rpe", "RPE"), ("rhr", "RHR")]:
        no_caff_vals = [e[metric_key] for e in no_caffeine if e.get(metric_key)]
        with_caff_vals = [e[metric_key] for e in with_caffeine if e.get(metric_key)]

        if no_caff_vals and with_caff_vals:
            no_avg = sum(no_caff_vals) / len(no_caff_vals)
            with_avg = sum(with_caff_vals) / len(with_caff_vals)
            diff = with_avg - no_avg

            if abs(diff) > 0.5:
                direction = "higher" if diff > 0 else "lower"
                results.append(f"{metric_name}: {direction} with caffeine ({with_avg:.1f} vs {no_avg:.1f})")

    return results if results else ["No significant impact detected"]


# =============================================================================
# MAIN MENU
# =============================================================================

def show_menu():
    """Display the main menu"""
    print("\n" + "=" * 40)
    print("  TRAINING JOURNAL")
    print(f"  Goal: {GOAL}")
    print(f"  Entries: {len(entries)}")
    print("=" * 40)
    print("\n  1. Add entry")
    print("  2. View run history")
    print("  3. Weekly summary")
    print("  4. Insights")
    print("  5. Quit")
    print()


def main():
    """Main program loop"""
    load_data()

    while True:
        show_menu()
        choice = input("  Select option: ").strip()

        if choice == "1":
            add_entry()
        elif choice == "2":
            view_history()
        elif choice == "3":
            weekly_summary()
        elif choice == "4":
            insights()
        elif choice == "5":
            print("\n  Good luck with your training!")
            break
        else:
            print("\n  Please enter 1-5.")


# Run the program
if __name__ == "__main__":
    main()
