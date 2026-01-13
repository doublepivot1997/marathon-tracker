# Training Journal - Web Interface
# Flask application for marathon training tracking

from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# File to store data
DATA_FILE = "training_data.json"

# Your marathon goal
GOAL = "2:32:00 Boston"


# =============================================================================
# DATA FUNCTIONS
# =============================================================================

def load_data():
    """Load entries from file"""
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(entries):
    """Save entries to file"""
    with open(DATA_FILE, "w") as f:
        json.dump(entries, f, indent=2)


def get_week_bounds(date_str):
    """Get Monday and Sunday of the week containing date_str"""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    monday = date - timedelta(days=date.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")


# =============================================================================
# ROUTES
# =============================================================================

@app.route("/")
def index():
    """Dashboard / Home page"""
    entries = load_data()
    sorted_entries = sorted(entries, key=lambda x: x["date"], reverse=True) if entries else []

    # Calculate this week's stats
    week_miles = 0
    week_rhr_values = []
    today = datetime.now().strftime("%Y-%m-%d")

    if entries:
        monday, sunday = get_week_bounds(today)
        week_entries = [e for e in entries if monday <= e["date"] <= sunday]
        week_miles = sum(e.get("miles", 0) for e in week_entries)
        week_rhr_values = [e.get("rhr") for e in week_entries if e.get("rhr")]

    avg_rhr = round(sum(week_rhr_values) / len(week_rhr_values), 0) if week_rhr_values else None

    # Get a key insight from last week
    key_insight = None
    if len(entries) >= 3:
        # Simple insight based on available data
        alcohol_entries = [e for e in entries if e.get("alcohol") is True and e.get("rpe")]
        no_alcohol_entries = [e for e in entries if e.get("alcohol") is False and e.get("rpe")]

        if len(alcohol_entries) >= 1 and len(no_alcohol_entries) >= 1:
            avg_rpe_alcohol = sum(e["rpe"] for e in alcohol_entries) / len(alcohol_entries)
            avg_rpe_no_alcohol = sum(e["rpe"] for e in no_alcohol_entries) / len(no_alcohol_entries)
            diff = avg_rpe_alcohol - avg_rpe_no_alcohol
            if diff > 0.5:
                key_insight = f"RPE is {diff:.1f} points higher after alcohol"
            elif diff < -0.5:
                key_insight = f"RPE is {abs(diff):.1f} points lower after alcohol"

        if not key_insight:
            good_sleep = [e for e in entries if e.get("sleep_quality") and e["sleep_quality"] >= 7 and e.get("rpe")]
            poor_sleep = [e for e in entries if e.get("sleep_quality") and e["sleep_quality"] <= 4 and e.get("rpe")]
            if good_sleep and poor_sleep:
                avg_good = sum(e["rpe"] for e in good_sleep) / len(good_sleep)
                avg_poor = sum(e["rpe"] for e in poor_sleep) / len(poor_sleep)
                if avg_poor - avg_good > 0.5:
                    key_insight = f"Poor sleep increases RPE by {avg_poor - avg_good:.1f} points"

        if not key_insight:
            key_insight = "Add more entries to see insights"

    return render_template("index.html",
                         goal=GOAL,
                         entries=sorted_entries,
                         entry_count=len(entries),
                         week_miles=week_miles,
                         avg_rhr=avg_rhr,
                         key_insight=key_insight)


@app.route("/add", methods=["GET", "POST"])
def add_entry():
    """Add a new entry"""
    if request.method == "POST":
        entry = {}

        # Basic info
        entry["date"] = request.form.get("date")
        entry["time_of_day"] = request.form.get("time_of_day")
        entry["type"] = request.form.get("type")

        # Run data
        if entry["type"] == "rest":
            entry["miles"] = 0
            entry["pace"] = None
            entry["hr"] = None
        else:
            miles = request.form.get("miles")
            entry["miles"] = float(miles) if miles else 0
            entry["pace"] = request.form.get("pace") or None
            hr = request.form.get("hr")
            entry["hr"] = int(hr) if hr else None

        # Device metrics
        rhr = request.form.get("rhr")
        entry["rhr"] = int(rhr) if rhr else None
        hrv = request.form.get("hrv")
        entry["hrv"] = int(hrv) if hrv else None

        # Subjective scores
        rpe = request.form.get("rpe")
        entry["rpe"] = int(rpe) if rpe else None
        sleep = request.form.get("sleep_quality")
        entry["sleep_quality"] = int(sleep) if sleep else None
        stress = request.form.get("stress")
        entry["stress"] = int(stress) if stress else None

        # Lifestyle factors
        caffeine = request.form.get("caffeine")
        entry["caffeine"] = int(caffeine) if caffeine else None
        entry["alcohol"] = request.form.get("alcohol") == "y"
        entry["nicotine"] = request.form.get("nicotine") == "y"
        entry["travel"] = request.form.get("travel") == "y"
        entry["stretch"] = request.form.get("stretch") == "y"
        entry["music"] = request.form.get("music") == "y"

        # Timestamp
        entry["created_at"] = datetime.now().isoformat()

        # Save
        entries = load_data()
        entries.append(entry)
        save_data(entries)

        return redirect(url_for("history"))

    # GET request - show form
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("add.html", today=today)


@app.route("/history")
def history():
    """View run history"""
    entries = load_data()
    sorted_entries = sorted(entries, key=lambda x: x["date"], reverse=True)
    return render_template("history.html", entries=sorted_entries)


@app.route("/entry/<int:index>")
def view_entry(index):
    """View single entry details"""
    entries = load_data()
    sorted_entries = sorted(entries, key=lambda x: x["date"], reverse=True)

    if 0 <= index < len(sorted_entries):
        entry = sorted_entries[index]
        return render_template("entry.html", entry=entry, index=index)

    return redirect(url_for("history"))


@app.route("/weekly")
def weekly():
    """Weekly summary"""
    entries = load_data()

    if not entries:
        return render_template("weekly.html", weeks=[], stats=None)

    # Get available weeks
    weeks_set = set()
    for entry in entries:
        monday, sunday = get_week_bounds(entry["date"])
        weeks_set.add((monday, sunday))

    weeks = sorted(weeks_set, reverse=True)

    # Get selected week (default to most recent)
    selected = request.args.get("week", "0")
    try:
        week_idx = int(selected)
    except:
        week_idx = 0

    if week_idx >= len(weeks):
        week_idx = 0

    # Calculate stats for selected week
    monday, sunday = weeks[week_idx]
    week_entries = [e for e in entries if monday <= e["date"] <= sunday]

    run_entries = [e for e in week_entries if e.get("type") != "rest"]
    rest_days = len([e for e in week_entries if e.get("type") == "rest"])

    stats = {
        "monday": monday,
        "sunday": sunday,
        "total_miles": sum(e.get("miles", 0) for e in week_entries),
        "num_runs": len(run_entries),
        "rest_days": rest_days,
    }

    # Calculate averages
    def avg(key, entry_list):
        values = [e.get(key) for e in entry_list if e.get(key) is not None]
        return round(sum(values) / len(values), 1) if values else None

    stats["avg_rhr"] = avg("rhr", week_entries)
    stats["avg_hrv"] = avg("hrv", week_entries)
    stats["avg_hr"] = avg("hr", run_entries)
    stats["avg_rpe"] = avg("rpe", run_entries)
    stats["avg_sleep"] = avg("sleep_quality", week_entries)
    stats["avg_stress"] = avg("stress", week_entries)

    # Average pace
    total_seconds = 0
    pace_count = 0
    for e in run_entries:
        if e.get("pace"):
            parts = e["pace"].split(":")
            if len(parts) == 2:
                total_seconds += int(parts[0]) * 60 + int(parts[1])
                pace_count += 1

    if pace_count > 0:
        avg_sec = total_seconds / pace_count
        stats["avg_pace"] = f"{int(avg_sec // 60)}:{int(avg_sec % 60):02d}"
    else:
        stats["avg_pace"] = None

    return render_template("weekly.html", weeks=weeks, stats=stats, selected=week_idx)


@app.route("/insights")
def insights():
    """Correlation insights"""
    entries = load_data()

    if len(entries) < 5:
        return render_template("insights.html",
                             has_data=False,
                             needed=5 - len(entries))

    results = {}

    # Analyze boolean factors
    factors = [
        ("alcohol", "Alcohol"),
        ("nicotine", "Nicotine"),
        ("travel", "Travel"),
        ("stretch", "Stretching"),
        ("music", "Music"),
    ]

    metrics = [
        ("rpe", "RPE", True),
        ("rhr", "RHR", True),
        ("hrv", "HRV", False),
    ]

    factor_results = []
    for factor_key, factor_name in factors:
        impacts = []
        for metric_key, metric_name, higher_is_worse in metrics:
            impact = calculate_impact(entries, factor_key, metric_key, higher_is_worse)
            if impact:
                impacts.append({"metric": metric_name, "impact": impact})
        if impacts:
            factor_results.append({"name": factor_name, "impacts": impacts})

    results["factors"] = factor_results

    # Sleep impact
    results["sleep"] = analyze_sleep_impact(entries)

    # Caffeine impact
    results["caffeine"] = analyze_caffeine_impact(entries)

    return render_template("insights.html", has_data=True, results=results)


def calculate_impact(entries, factor_key, metric_key, higher_is_worse):
    """Calculate impact of a boolean factor on a metric"""
    with_factor = [e for e in entries if e.get(factor_key) is True and e.get(metric_key) is not None]
    without_factor = [e for e in entries if e.get(factor_key) is False and e.get(metric_key) is not None]

    if len(with_factor) < 2 or len(without_factor) < 2:
        return None

    avg_with = sum(e[metric_key] for e in with_factor) / len(with_factor)
    avg_without = sum(e[metric_key] for e in without_factor) / len(without_factor)

    diff = avg_with - avg_without

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

    return f"{strength} {direction} ({avg_with:.1f} vs {avg_without:.1f})"


def analyze_sleep_impact(entries):
    """Analyze how sleep quality affects metrics"""
    good_sleep = [e for e in entries if e.get("sleep_quality") and e["sleep_quality"] >= 7]
    poor_sleep = [e for e in entries if e.get("sleep_quality") and e["sleep_quality"] <= 4]

    if len(good_sleep) < 2 or len(poor_sleep) < 2:
        return [{"text": "Not enough varied sleep data yet"}]

    results = []
    for metric_key, metric_name in [("rpe", "RPE"), ("rhr", "RHR"), ("hrv", "HRV")]:
        good_vals = [e[metric_key] for e in good_sleep if e.get(metric_key)]
        poor_vals = [e[metric_key] for e in poor_sleep if e.get(metric_key)]

        if good_vals and poor_vals:
            good_avg = sum(good_vals) / len(good_vals)
            poor_avg = sum(poor_vals) / len(poor_vals)
            diff = poor_avg - good_avg

            if abs(diff) > 0.5:
                direction = "higher" if diff > 0 else "lower"
                results.append({
                    "text": f"{metric_name}: {direction} with poor sleep ({poor_avg:.1f} vs {good_avg:.1f})"
                })

    return results if results else [{"text": "No significant correlations found"}]


def analyze_caffeine_impact(entries):
    """Analyze caffeine consumption impact"""
    no_caffeine = [e for e in entries if e.get("caffeine") == 0 or e.get("caffeine") is None]
    with_caffeine = [e for e in entries if e.get("caffeine") and e["caffeine"] > 0]

    if len(no_caffeine) < 2 or len(with_caffeine) < 2:
        return [{"text": "Not enough varied caffeine data yet"}]

    results = []
    for metric_key, metric_name in [("rpe", "RPE"), ("rhr", "RHR")]:
        no_vals = [e[metric_key] for e in no_caffeine if e.get(metric_key)]
        with_vals = [e[metric_key] for e in with_caffeine if e.get(metric_key)]

        if no_vals and with_vals:
            no_avg = sum(no_vals) / len(no_vals)
            with_avg = sum(with_vals) / len(with_vals)
            diff = with_avg - no_avg

            if abs(diff) > 0.5:
                direction = "higher" if diff > 0 else "lower"
                results.append({
                    "text": f"{metric_name}: {direction} with caffeine ({with_avg:.1f} vs {no_avg:.1f})"
                })

    return results if results else [{"text": "No significant impact detected"}]


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)
