# Marathon Tracker CLI
# A simple running tracker for marathoners

# Store the latest run (starts empty)
latest_run = None

# Your marathon goal
GOAL = "2:32:00 Boston"


def parse_time(time_str):
    """Convert H:MM:SS to total seconds"""
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    return total_seconds


def format_pace(seconds_per_mile):
    """Convert seconds to M:SS format"""
    minutes = int(seconds_per_mile // 60)
    seconds = int(seconds_per_mile % 60)
    return f"{minutes}:{seconds:02d}/mile"


def calculate_pace(distance, time_str):
    """Calculate pace from distance and time"""
    total_seconds = parse_time(time_str)
    seconds_per_mile = total_seconds / distance
    return format_pace(seconds_per_mile)


def add_run():
    """Prompt user for run details and store it"""
    global latest_run

    print("\n--- ADD NEW RUN ---")

    # Get distance
    distance = float(input("Distance (miles): "))

    # Get time
    time_str = input("Time (H:MM:SS): ")

    # Get date
    date = input("Date (YYYY-MM-DD): ")

    # Calculate pace
    pace = calculate_pace(distance, time_str)

    # Store the run
    latest_run = {
        "date": date,
        "distance": distance,
        "time": time_str,
        "pace": pace
    }

    print(f"\nRun added! Pace: {pace}")


def view_latest():
    """Display the latest run"""
    if latest_run is None:
        print("\nNo runs logged yet.")
        return

    print("\n-----------------------------")
    print("  LATEST RUN")
    print("-----------------------------")
    print(f"  Date:     {latest_run['date']}")
    print(f"  Distance: {latest_run['distance']} miles")
    print(f"  Time:     {latest_run['time']}")
    print(f"  Pace:     {latest_run['pace']}")
    print("-----------------------------")


def show_menu():
    """Display the main menu"""
    print("\n============================")
    print("  MARATHON TRACKER")
    print(f"  Goal: {GOAL}")
    print("============================")
    print("\n1. Add run")
    print("2. View latest run")
    print("3. Quit")
    print()


def main():
    """Main program loop"""
    while True:
        show_menu()
        choice = input("Select option: ")

        if choice == "1":
            add_run()
        elif choice == "2":
            view_latest()
        elif choice == "3":
            print("\nGood luck with your training!")
            break
        else:
            print("\nInvalid option. Please enter 1, 2, or 3.")


# Run the program
if __name__ == "__main__":
    main()
