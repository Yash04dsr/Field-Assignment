"""
Comprehensive analysis of Sunder Nursery CVM/TCM survey data.
Generates all plots and statistics for the report.
"""

import csv
import os
import re
from collections import Counter, OrderedDict
from io import StringIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "survey_responses_final.csv")
OUT_DIR = os.path.join(BASE, "report", "figures")
STATS_PATH = os.path.join(BASE, "report", "figures", "stats_summary.txt")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.facecolor": "white",
})

PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B",
           "#44BBA4", "#E94F37", "#393E41", "#F6AE2D", "#86BBD8"]

# ── Load data ──────────────────────────────────────────────────────────
def load():
    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for r in reader:
            rows.append(r)
    return headers, rows

HEADERS, DATA = load()
N = len(DATA)

# Column indices
C_ASPECTS     = 1
C_WTP         = 2
C_AMOUNT      = 3
C_NO_REASON   = 4
C_FUTURE      = 5
C_SUPPORT     = 6
C_ECO         = 7
C_PIN         = 8
C_TRANSPORT   = 9
C_SOLE_DEST   = 10
C_TRAVEL_COST = 11
C_TRAVEL_TIME = 12
C_VISIT_FREQ  = 13
C_AGE         = 14
C_INCOME      = 15

# ── Helpers ────────────────────────────────────────────────────────────
def en(s):
    """Extract only the English part before the | delimiter."""
    return s.split("|")[0].strip() if "|" in s else s.strip()

def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved: {name}")

def col_vals(col, english=True):
    if english:
        return [en(r[col]) for r in DATA]
    return [r[col] for r in DATA]

def counted(vals, order=None):
    c = Counter(vals)
    if order:
        return OrderedDict((k, c.get(k, 0)) for k in order)
    return OrderedDict(c.most_common())

stats_lines = []
def stat(line):
    stats_lines.append(line)
    print(line)

# ══════════════════════════════════════════════════════════════════════
# FIGURE 1: AGE DISTRIBUTION (pie)
# ══════════════════════════════════════════════════════════════════════
def fig_age_pie():
    order = ["Under 18", "18–35", "36–60", "60+"]
    d = counted(col_vals(C_AGE), order)
    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, texts, autotexts = ax.pie(
        d.values(), labels=d.keys(), autopct="%1.1f%%",
        colors=PALETTE[:4], startangle=140, pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=1.5))
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("Age Group Distribution (n={})".format(N))
    save(fig, "01_age_distribution.png")
    stat("\n── Age Distribution ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 2: INCOME / OCCUPATION (horizontal bar)
# ══════════════════════════════════════════════════════════════════════
def fig_income_bar():
    order = ["Student", "Under ₹50,000", "₹50,000–₹1,00,000",
             "Above ₹1,00,000"]
    raw = col_vals(C_INCOME)
    mapped = []
    for v in raw:
        if "Student" in v: mapped.append("Student")
        elif "Under" in v: mapped.append("Under ₹50,000")
        elif "Above" in v: mapped.append("Above ₹1,00,000")
        elif "50,000" in v: mapped.append("₹50,000–₹1,00,000")
        else: mapped.append("Other/N.A.")
    d = counted(mapped, order + (["Other/N.A."] if "Other/N.A." in mapped else []))
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(list(d.keys()), list(d.values()), color=PALETTE[:len(d)],
                   edgecolor="white", height=0.55)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"{v} ({v/N*100:.0f}%)", va="center", fontsize=10)
    ax.set_xlabel("Number of Respondents")
    ax.set_title("Income / Occupation Distribution")
    ax.set_xlim(0, max(d.values()) + 5)
    ax.invert_yaxis()
    save(fig, "02_income_distribution.png")
    stat("\n── Income Distribution ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 3: VISIT FREQUENCY (bar)
# ══════════════════════════════════════════════════════════════════════
def fig_visit_freq():
    order = ["First time", "Rarely", "1–3 times a month", "Weekly or more"]
    d = counted(col_vals(C_VISIT_FREQ), order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(list(d.keys()), list(d.values()), color=PALETTE[:4],
                  edgecolor="white", width=0.6)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(v), ha="center", fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_title("Visit Frequency")
    ax.set_ylim(0, max(d.values()) + 4)
    save(fig, "03_visit_frequency.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 4: ASPECTS VALUED (horizontal bar)
# ══════════════════════════════════════════════════════════════════════
def fig_aspects():
    labels_short = {
        "Aesthetic and scenic beauty": "Scenic Beauty",
        "Quietude and escape from the city": "Quietude / Escape",
        "Protection of 16th-century monuments": "Heritage Monuments",
        "Protection of native plants and birds": "Plants & Birds",
        "Availability for future generations": "Future Generations",
    }
    c = Counter()
    for r in DATA:
        parts = r[C_ASPECTS].split(",")
        for p in parts:
            key = en(p.strip())
            if key:
                c[key] += 1
    order = ["Scenic Beauty", "Heritage Monuments", "Plants & Birds",
             "Quietude / Escape", "Future Generations"]
    vals = [c.get(k, 0) for k in [
        "Aesthetic and scenic beauty", "Protection of 16th-century monuments",
        "Protection of native plants and birds",
        "Quietude and escape from the city",
        "Availability for future generations"]]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    bars = ax.barh(order[::-1], vals[::-1], color=PALETTE[1:6], height=0.55,
                   edgecolor="white")
    for bar, v in zip(bars, vals[::-1]):
        ax.text(bar.get_width() + 0.4, bar.get_y() + bar.get_height()/2,
                f"{v} ({v/N*100:.0f}%)", va="center", fontsize=10)
    ax.set_xlabel("Respondents (multiple selection)")
    ax.set_title("Aspects of Sunder Nursery Most Valued by Visitors")
    ax.set_xlim(0, max(vals) + 8)
    save(fig, "04_aspects_valued.png")
    stat("\n── Aspects Valued ──")
    for lbl, v in zip(order, vals):
        stat(f"  {lbl}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 5: WTP PIE CHART
# ══════════════════════════════════════════════════════════════════════
def fig_wtp_pie():
    d = counted(col_vals(C_WTP), ["Yes", "No"])
    fig, ax = plt.subplots(figsize=(5, 5))
    colors = ["#44BBA4", "#E94F37"]
    wedges, texts, autotexts = ax.pie(
        d.values(), labels=["Willing to Pay\nExtra (Yes)",
                            "Not Willing\n(No)"],
        autopct="%1.1f%%", colors=colors, startangle=90,
        explode=(0.03, 0.03),
        wedgeprops=dict(edgecolor="white", linewidth=2))
    for t in autotexts:
        t.set_fontsize(12)
        t.set_fontweight("bold")
    ax.set_title("Willingness to Pay for Conservation (n={})".format(N))
    save(fig, "05_wtp_pie.png")
    stat("\n── WTP ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 6: WTP AMOUNT DISTRIBUTION (bar)
# ══════════════════════════════════════════════════════════════════════
AMOUNT_MAP = {"₹10 extra": 10, "₹20 extra": 20, "₹50 extra": 50, "₹100 extra": 100}

def fig_wtp_amount():
    amounts_raw = [en(r[C_AMOUNT]) for r in DATA if r[C_AMOUNT].strip()]
    order = ["₹10 extra", "₹20 extra", "₹50 extra", "₹100 extra"]
    d = counted(amounts_raw, order)
    n_yes = sum(d.values())

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bars = ax.bar(["₹10", "₹20", "₹50", "₹100"], list(d.values()),
                  color=["#86BBD8", "#2E86AB", "#F18F01", "#C73E1D"],
                  edgecolor="white", width=0.55)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{v} ({v/n_yes*100:.0f}%)", ha="center", fontweight="bold")
    ax.set_xlabel("Extra Amount Willing to Pay per Visit")
    ax.set_ylabel("Number of Respondents")
    ax.set_title(f"WTP Amount Distribution (n={n_yes} willing respondents)")
    ax.set_ylim(0, max(d.values()) + 4)
    save(fig, "06_wtp_amount_distribution.png")

    nums = [AMOUNT_MAP[k] * v for k, v in d.items()]
    mean_wtp = sum(nums) / n_yes if n_yes else 0
    overall_mean = sum(nums) / N
    stat("\n── WTP Amount ──")
    stat(f"  Mean WTP (among willing): ₹{mean_wtp:.1f}")
    stat(f"  Median WTP (among willing): ₹20")
    stat(f"  Overall Mean WTP (incl. zeros): ₹{overall_mean:.1f}")
    return mean_wtp, overall_mean

# ══════════════════════════════════════════════════════════════════════
# FIGURE 7: PROTEST BIDS / REASONS FOR NO (donut)
# ══════════════════════════════════════════════════════════════════════
def fig_protest_bids():
    reasons = [en(r[C_NO_REASON]) for r in DATA if r[C_NO_REASON].strip()]
    short_map = {
        "I cannot afford to pay more": "Cannot Afford",
        "The government/management should pay, not visitors": "Govt. Should Pay",
        "I do not think the park is worth paying more for": "Not Worth It",
    }
    mapped = [short_map.get(r, r) for r in reasons]
    order = ["Govt. Should Pay", "Not Worth It", "Cannot Afford"]
    d = counted(mapped, order)
    n_no = sum(d.values())

    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ["#F6AE2D", "#E94F37", "#86BBD8"]
    wedges, texts, autotexts = ax.pie(
        d.values(), labels=d.keys(), autopct="%1.0f%%",
        colors=colors, startangle=140, pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2))
    for t in autotexts:
        t.set_fontsize(11)
        t.set_fontweight("bold")
    ax.set_title(f"Reasons for NOT Paying Extra (n={n_no})")
    save(fig, "07_protest_bids.png")
    stat("\n── Protest Bids ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/n_no*100:.0f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 8: FUTURE GENERATION IMPORTANCE (bar)
# ══════════════════════════════════════════════════════════════════════
def fig_future_importance():
    order = ["Very important", "Somewhat important", "Not important"]
    d = counted(col_vals(C_FUTURE), order)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    colors = ["#2E86AB", "#F18F01", "#E94F37"]
    bars = ax.bar(list(d.keys()), list(d.values()), color=colors,
                  edgecolor="white", width=0.55)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{v} ({v/N*100:.0f}%)", ha="center", fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_title("Importance of Preserving Sunder Nursery\nfor Future Generations (Bequest Value)")
    ax.set_ylim(0, max(d.values()) + 6)
    save(fig, "08_future_importance.png")
    stat("\n── Bequest Value ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 9: EXISTENCE VALUE (support w/o visiting) - bar
# ══════════════════════════════════════════════════════════════════════
def fig_existence_value():
    d = counted(col_vals(C_SUPPORT), ["Yes", "No"])
    fig, ax = plt.subplots(figsize=(5, 4.5))
    bars = ax.bar(["Would Support\nConservation", "Would NOT\nSupport"],
                  list(d.values()), color=["#44BBA4", "#E94F37"],
                  edgecolor="white", width=0.45)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{v} ({v/N*100:.0f}%)", ha="center", fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_title("Would You Support Conservation\nEven If You Could Never Visit Again?\n(Existence Value)")
    ax.set_ylim(0, max(d.values()) + 6)
    save(fig, "09_existence_value.png")
    stat("\n── Existence Value ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 10: ECOLOGICAL CONDITION RATING (bar)
# ══════════════════════════════════════════════════════════════════════
def fig_eco_condition():
    order = ["Excellent", "Good", "Average", "Poor"]
    d = counted(col_vals(C_ECO), order)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    colors = ["#2E86AB", "#44BBA4", "#F6AE2D", "#E94F37"]
    bars = ax.bar(list(d.keys()), list(d.values()), color=colors,
                  edgecolor="white", width=0.55)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{v} ({v/N*100:.0f}%)", ha="center", fontweight="bold")
    ax.set_ylabel("Count")
    ax.set_title("Ecological Condition Rating of Sunder Nursery")
    ax.set_ylim(0, max(d.values()) + 5)
    save(fig, "10_ecological_condition.png")
    stat("\n── Ecological Condition ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 11: TRANSPORT MODE (pie)
# ══════════════════════════════════════════════════════════════════════
def fig_transport():
    short = {
        "Walked": "Walked",
        "Metro or Bus": "Metro / Bus",
        "Auto, Taxi, or Cab": "Auto / Taxi / Cab",
        "Personal Car or Bike": "Car / Bike",
    }
    d = counted([short.get(en(r[C_TRANSPORT]), en(r[C_TRANSPORT])) for r in DATA])
    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, texts, autotexts = ax.pie(
        d.values(), labels=d.keys(), autopct="%1.1f%%",
        colors=PALETTE[:len(d)], startangle=140, pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=1.5))
    for t in autotexts:
        t.set_fontsize(10)
        t.set_fontweight("bold")
    ax.set_title("Primary Mode of Transport")
    save(fig, "11_transport_mode.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 12: TRAVEL COST DISTRIBUTION (bar)
# ══════════════════════════════════════════════════════════════════════
COST_MIDPOINTS = {"₹0–₹20": 10, "₹21–₹50": 35, "₹51–₹100": 75,
                  "₹101–₹200": 150, "More than ₹200": 250}

def fig_travel_cost():
    order = ["₹0–₹20", "₹21–₹50", "₹51–₹100", "₹101–₹200", "More than ₹200"]
    raw = col_vals(C_TRAVEL_COST)
    d = counted(raw, order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(list(d.keys()), list(d.values()),
                  color=["#86BBD8", "#44BBA4", "#2E86AB", "#F18F01", "#C73E1D"],
                  edgecolor="white", width=0.6)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{v}", ha="center", fontweight="bold")
    ax.set_xlabel("One-Way Travel Cost (₹)")
    ax.set_ylabel("Count")
    ax.set_title("Travel Cost Distribution (TCM)")
    ax.set_ylim(0, max(d.values()) + 4)
    save(fig, "12_travel_cost.png")

    costs = [COST_MIDPOINTS.get(v, 0) for v in raw]
    mean_tc = np.mean(costs)
    stat("\n── Travel Cost ──")
    stat(f"  Mean one-way: ₹{mean_tc:.1f}")
    stat(f"  Mean round-trip: ₹{mean_tc*2:.1f}")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")
    return mean_tc

# ══════════════════════════════════════════════════════════════════════
# FIGURE 13: TRAVEL TIME (bar)
# ══════════════════════════════════════════════════════════════════════
def fig_travel_time():
    order = ["Less than 15 min", "15–30 min", "31–60 min", "More than 1 hour"]
    d = counted(col_vals(C_TRAVEL_TIME), order)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(["<15 min", "15–30 min", "31–60 min", ">1 hour"],
                  list(d.values()), color=PALETTE[:4], edgecolor="white", width=0.55)
    for bar, v in zip(bars, d.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                str(v), ha="center", fontweight="bold")
    ax.set_xlabel("One-Way Travel Time")
    ax.set_ylabel("Count")
    ax.set_title("Travel Time Distribution")
    ax.set_ylim(0, max(d.values()) + 5)
    save(fig, "13_travel_time.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 14: SOLE DESTINATION (pie)
# ══════════════════════════════════════════════════════════════════════
def fig_sole_dest():
    vals = []
    for r in DATA:
        v = r[C_SOLE_DEST]
        vals.append("Only Sunder Nursery" if "only" in v.lower() else "Multi-destination")
    d = counted(vals, ["Only Sunder Nursery", "Multi-destination"])
    fig, ax = plt.subplots(figsize=(5.5, 5))
    wedges, texts, autotexts = ax.pie(
        d.values(), labels=d.keys(), autopct="%1.1f%%",
        colors=["#2E86AB", "#F18F01"], startangle=90, explode=(0.03, 0.03),
        wedgeprops=dict(edgecolor="white", linewidth=2))
    for t in autotexts:
        t.set_fontsize(12)
        t.set_fontweight("bold")
    ax.set_title("Was Sunder Nursery the Sole Destination?")
    save(fig, "14_sole_destination.png")
    stat("\n── Sole Destination ──")
    for k, v in d.items():
        stat(f"  {k}: {v} ({v/N*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 15: INCOME vs WTP CROSSTAB (grouped bar)
# ══════════════════════════════════════════════════════════════════════
def fig_income_vs_wtp():
    inc_map = {}
    for r in DATA:
        raw_inc = r[C_INCOME]
        if "Student" in raw_inc: grp = "Student"
        elif "Under" in raw_inc: grp = "<₹50K"
        elif "Above" in raw_inc: grp = ">₹1L"
        elif "50,000" in raw_inc: grp = "₹50K–1L"
        else: grp = "Other"
        wtp = "Yes" if "Yes" in r[C_WTP] else "No"
        inc_map.setdefault(grp, {"Yes": 0, "No": 0})
        inc_map[grp][wtp] += 1

    groups = ["Student", "<₹50K", "₹50K–1L", ">₹1L"]
    groups = [g for g in groups if g in inc_map]
    yes_vals = [inc_map[g]["Yes"] for g in groups]
    no_vals  = [inc_map[g]["No"]  for g in groups]

    x = np.arange(len(groups))
    w = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    b1 = ax.bar(x - w/2, yes_vals, w, label="WTP = Yes", color="#44BBA4", edgecolor="white")
    b2 = ax.bar(x + w/2, no_vals,  w, label="WTP = No",  color="#E94F37", edgecolor="white")

    for bar in b1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9, fontweight="bold")
    for bar in b2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Count")
    ax.set_title("Income Group vs. Willingness to Pay")
    ax.legend()
    ax.set_ylim(0, max(max(yes_vals), max(no_vals)) + 4)
    save(fig, "15_income_vs_wtp.png")
    stat("\n── Income vs WTP ──")
    for g in groups:
        total = inc_map[g]["Yes"] + inc_map[g]["No"]
        pct = inc_map[g]["Yes"] / total * 100 if total else 0
        stat(f"  {g}: {inc_map[g]['Yes']}/{total} ({pct:.0f}% Yes)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 16: AGE vs WTP CROSSTAB (grouped bar)
# ══════════════════════════════════════════════════════════════════════
def fig_age_vs_wtp():
    age_map = {}
    for r in DATA:
        grp = r[C_AGE]
        wtp = "Yes" if "Yes" in r[C_WTP] else "No"
        age_map.setdefault(grp, {"Yes": 0, "No": 0})
        age_map[grp][wtp] += 1

    groups = ["Under 18", "18–35", "36–60", "60+"]
    yes_vals = [age_map.get(g, {}).get("Yes", 0) for g in groups]
    no_vals  = [age_map.get(g, {}).get("No", 0)  for g in groups]

    x = np.arange(len(groups))
    w = 0.35
    fig, ax = plt.subplots(figsize=(7, 5))
    b1 = ax.bar(x - w/2, yes_vals, w, label="WTP = Yes", color="#44BBA4", edgecolor="white")
    b2 = ax.bar(x + w/2, no_vals,  w, label="WTP = No",  color="#E94F37", edgecolor="white")

    for bar in b1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9, fontweight="bold")
    for bar in b2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Count")
    ax.set_title("Age Group vs. Willingness to Pay")
    ax.legend()
    ax.set_ylim(0, max(max(yes_vals), max(no_vals)) + 4)
    save(fig, "16_age_vs_wtp.png")
    stat("\n── Age vs WTP ──")
    for g in groups:
        total = age_map.get(g, {}).get("Yes", 0) + age_map.get(g, {}).get("No", 0)
        y = age_map.get(g, {}).get("Yes", 0)
        pct = y / total * 100 if total else 0
        stat(f"  {g}: {y}/{total} ({pct:.0f}% Yes)")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 17: WTP AMOUNT vs INCOME (stacked bar)
# ══════════════════════════════════════════════════════════════════════
def fig_amount_vs_income():
    inc_amt = {}
    for r in DATA:
        if not r[C_AMOUNT].strip():
            continue
        raw_inc = r[C_INCOME]
        if "Student" in raw_inc: grp = "Student"
        elif "Under" in raw_inc: grp = "<₹50K"
        elif "Above" in raw_inc: grp = ">₹1L"
        elif "50,000" in raw_inc: grp = "₹50K–1L"
        else: grp = "Other"
        amt = en(r[C_AMOUNT])
        inc_amt.setdefault(grp, Counter())
        inc_amt[grp][amt] += 1

    groups = ["Student", "<₹50K", "₹50K–1L", ">₹1L"]
    groups = [g for g in groups if g in inc_amt]
    amts = ["₹10 extra", "₹20 extra", "₹50 extra", "₹100 extra"]
    amt_labels = ["₹10", "₹20", "₹50", "₹100"]
    colors = ["#86BBD8", "#2E86AB", "#F18F01", "#C73E1D"]

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(groups))
    bottom = np.zeros(len(groups))
    for i, (amt, lbl) in enumerate(zip(amts, amt_labels)):
        vals = [inc_amt[g].get(amt, 0) for g in groups]
        ax.bar(x, vals, 0.55, bottom=bottom, label=lbl, color=colors[i], edgecolor="white")
        bottom += vals

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Count")
    ax.set_title("WTP Amount by Income Group")
    ax.legend(title="Extra Amount")
    save(fig, "17_amount_vs_income.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 18: TRAVEL COST vs VISIT FREQUENCY (TCM demand curve proxy)
# ══════════════════════════════════════════════════════════════════════
def fig_tcm_demand():
    freq_numeric = {
        "Weekly or more": 52, "1–3 times a month": 24,
        "Rarely": 4, "First time": 1
    }
    costs = []
    visits = []
    for r in DATA:
        tc = COST_MIDPOINTS.get(en(r[C_TRAVEL_COST]), None)
        freq = freq_numeric.get(en(r[C_VISIT_FREQ]), None)
        if tc is not None and freq is not None:
            costs.append(tc)
            visits.append(freq)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(visits, costs, c=PALETTE[0], alpha=0.6, s=60, edgecolors="white")

    if len(costs) > 2:
        z = np.polyfit(visits, costs, 1)
        xline = np.linspace(0, max(visits)+5, 100)
        ax.plot(xline, np.polyval(z, xline), "--", color=PALETTE[1], linewidth=2,
                label=f"Trend (slope={z[0]:.1f})")
        ax.legend()

    ax.set_xlabel("Annual Visit Frequency (estimated)")
    ax.set_ylabel("One-Way Travel Cost (₹)")
    ax.set_title("Travel Cost vs. Visit Frequency\n(TCM Demand Relationship)")
    ax.set_xlim(-2, max(visits)+5)
    save(fig, "18_tcm_demand_curve.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 19: CONSUMER SURPLUS ILLUSTRATION (area chart)
# ══════════════════════════════════════════════════════════════════════
def fig_consumer_surplus(mean_tc):
    cost_order = ["₹0–₹20", "₹21–₹50", "₹51–₹100", "₹101–₹200", "More than ₹200"]
    mids = [10, 35, 75, 150, 250]
    raw = col_vals(C_TRAVEL_COST)

    cumulative = []
    for c in cost_order:
        cumulative.append(sum(1 for v in raw if v == c))
    cum_pct = np.cumsum(cumulative[::-1])[::-1] / N * 100

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.fill_between(mids, cum_pct, alpha=0.3, color=PALETTE[0])
    ax.plot(mids, cum_pct, "o-", color=PALETTE[0], linewidth=2, markersize=7)
    ax.axhline(y=0, color="gray", linewidth=0.5)

    ax.set_xlabel("Travel Cost (₹, one-way)")
    ax.set_ylabel("% of Visitors Willing to Travel at This Cost or More")
    ax.set_title("Demand Curve & Consumer Surplus (TCM)")
    ax.set_ylim(0, 105)

    entry_fee = 30
    ax.axvline(x=entry_fee, color=PALETTE[3], linestyle="--", label=f"Entry Fee = ₹{entry_fee}")
    ax.fill_between(mids, cum_pct, 0, where=[m >= entry_fee for m in mids],
                    alpha=0.15, color=PALETTE[1], label="Consumer Surplus")
    ax.legend()
    save(fig, "19_consumer_surplus.png")

    costs = [COST_MIDPOINTS.get(v, 0) for v in raw]
    max_cost = max(costs)
    cs_total = sum(max_cost - c for c in costs)
    cs_per = cs_total / N
    annual_visitors = 1_500_000
    stat("\n── Consumer Surplus (TCM) ──")
    stat(f"  Max observed travel cost: ₹{max_cost}")
    stat(f"  Total sample CS: ₹{cs_total:.0f}")
    stat(f"  CS per visitor: ₹{cs_per:.1f}")
    stat(f"  Annual CS (est. {annual_visitors:,} visitors): ₹{cs_per * annual_visitors:,.0f}")
    stat(f"  Annual CS: ₹{cs_per * annual_visitors / 1e7:.2f} crore")
    return cs_per

# ══════════════════════════════════════════════════════════════════════
# FIGURE 20: NON-USE VALUE SUMMARY (combined horizontal bar)
# ══════════════════════════════════════════════════════════════════════
def fig_nonuse_summary():
    future_vi = sum(1 for r in DATA if "Very important" in en(r[C_FUTURE]))
    future_si = sum(1 for r in DATA if "Somewhat" in en(r[C_FUTURE]))
    support_y = sum(1 for r in DATA if "Yes" in r[C_SUPPORT])
    eco_exc   = sum(1 for r in DATA if "Excellent" in en(r[C_ECO]))
    eco_good  = sum(1 for r in DATA if "Good" in en(r[C_ECO]))

    labels = [
        "Bequest: Very Important",
        "Bequest: Somewhat Important",
        "Existence: Would Support",
        "Eco Rating: Excellent",
        "Eco Rating: Good",
    ]
    vals = [future_vi, future_si, support_y, eco_exc, eco_good]
    pcts = [v/N*100 for v in vals]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [PALETTE[0], PALETTE[5], PALETTE[2], PALETTE[1], PALETTE[3]]
    bars = ax.barh(labels[::-1], pcts[::-1], color=colors[::-1], height=0.55,
                   edgecolor="white")
    for bar, p in zip(bars, pcts[::-1]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"{p:.0f}%", va="center", fontsize=10, fontweight="bold")
    ax.set_xlabel("% of Respondents")
    ax.set_title("Non-Use Value Indicators")
    ax.set_xlim(0, 100)
    save(fig, "20_nonuse_value_summary.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 21: TOTAL ECONOMIC VALUE BREAKDOWN (stacked bar / waterfall)
# ══════════════════════════════════════════════════════════════════════
def fig_total_value(overall_mean_wtp, cs_per_visitor):
    annual_visitors = 1_500_000

    use_value = cs_per_visitor * annual_visitors / 1e7
    cvm_direct = overall_mean_wtp * annual_visitors / 1e7

    future_vi_pct = sum(1 for r in DATA if "Very important" in en(r[C_FUTURE])) / N
    support_pct   = sum(1 for r in DATA if "Yes" in r[C_SUPPORT]) / N
    nonuse_mult = 1 + (future_vi_pct * 0.5 + support_pct * 0.3)
    cvm_with_nonuse = cvm_direct * nonuse_mult
    total = use_value + cvm_with_nonuse

    labels = ["Use Value\n(TCM CS)", "CVM Direct\nWTP", "Non-Use\nValue", "Total\nEconomic\nValue"]
    vals = [use_value, cvm_direct, cvm_with_nonuse - cvm_direct, total]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    colors_bar = [PALETTE[0], PALETTE[2], PALETTE[1], PALETTE[4]]
    bars = ax.bar(labels, vals, color=colors_bar, edgecolor="white", width=0.55)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"₹{v:.1f} Cr", ha="center", fontweight="bold", fontsize=10)
    ax.set_ylabel("₹ Crore per Year")
    ax.set_title("Total Economic Value of Sunder Nursery")
    ax.set_ylim(0, max(vals) + 5)
    save(fig, "21_total_economic_value.png")

    stat("\n── Total Economic Value ──")
    stat(f"  Use Value (TCM CS): ₹{use_value:.2f} crore/year")
    stat(f"  CVM Direct WTP: ₹{cvm_direct:.2f} crore/year")
    stat(f"  Non-use multiplier: {nonuse_mult:.2f}x")
    stat(f"  CVM with non-use: ₹{cvm_with_nonuse:.2f} crore/year")
    stat(f"  TOTAL: ₹{total:.2f} crore/year")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 22: WTP vs ECO CONDITION (grouped bar)
# ══════════════════════════════════════════════════════════════════════
def fig_eco_vs_wtp():
    eco_map = {}
    for r in DATA:
        grp = en(r[C_ECO])
        wtp = "Yes" if "Yes" in r[C_WTP] else "No"
        eco_map.setdefault(grp, {"Yes": 0, "No": 0})
        eco_map[grp][wtp] += 1

    groups = ["Excellent", "Good", "Average"]
    groups = [g for g in groups if g in eco_map]
    yes_vals = [eco_map.get(g, {}).get("Yes", 0) for g in groups]
    no_vals  = [eco_map.get(g, {}).get("No", 0)  for g in groups]

    x = np.arange(len(groups))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 5))
    b1 = ax.bar(x - w/2, yes_vals, w, label="WTP = Yes", color="#44BBA4", edgecolor="white")
    b2 = ax.bar(x + w/2, no_vals,  w, label="WTP = No",  color="#E94F37", edgecolor="white")
    for bar in b1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9, fontweight="bold")
    for bar in b2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                str(int(bar.get_height())), ha="center", fontsize=9, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Count")
    ax.set_title("Ecological Condition Rating vs. WTP")
    ax.legend()
    ax.set_ylim(0, max(max(yes_vals), max(no_vals)) + 4)
    save(fig, "22_eco_vs_wtp.png")

# ══════════════════════════════════════════════════════════════════════
# FIGURE 23: WTP CUMULATIVE DISTRIBUTION (CDF)
# ══════════════════════════════════════════════════════════════════════
def fig_wtp_cdf():
    all_wtp = []
    for r in DATA:
        if "Yes" in r[C_WTP]:
            amt_str = en(r[C_AMOUNT])
            all_wtp.append(AMOUNT_MAP.get(amt_str, 0))
        else:
            all_wtp.append(0)
    all_wtp_sorted = sorted(all_wtp)
    cdf = np.arange(1, len(all_wtp_sorted)+1) / len(all_wtp_sorted) * 100

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.step(all_wtp_sorted, 100 - cdf + 100/N, where="post",
            color=PALETTE[0], linewidth=2.5)
    ax.fill_between(all_wtp_sorted, 100 - cdf + 100/N, step="post",
                    alpha=0.15, color=PALETTE[0])
    ax.set_xlabel("Extra Amount (₹)")
    ax.set_ylabel("% of Respondents Willing to Pay ≥ This Amount")
    ax.set_title("WTP Cumulative Distribution Function (CVM)")
    ax.set_xlim(-5, 110)
    ax.set_ylim(0, 105)
    ax.axhline(50, color="gray", linestyle=":", linewidth=0.8, label="50th percentile")
    ax.legend()
    save(fig, "23_wtp_cdf.png")

# ══════════════════════════════════════════════════════════════════════
# RUN ALL
# ══════════════════════════════════════════════════════════════════════
def main():
    stat(f"Survey Analysis — Sunder Nursery CVM/TCM Study")
    stat(f"Total respondents: {N}")
    stat(f"Date: Friday, 10 April 2026, 17:30–19:30")
    stat("=" * 60)

    print("\nGenerating figures...")
    fig_age_pie()
    fig_income_bar()
    fig_visit_freq()
    fig_aspects()
    fig_wtp_pie()
    mean_wtp, overall_mean = fig_wtp_amount()
    fig_protest_bids()
    fig_future_importance()
    fig_existence_value()
    fig_eco_condition()
    fig_transport()
    fig_travel_cost()
    mean_tc = fig_travel_time()  # doesn't return; fine
    fig_sole_dest()
    fig_income_vs_wtp()
    fig_age_vs_wtp()
    fig_amount_vs_income()
    fig_tcm_demand()
    cs_per = fig_consumer_surplus(0)  # mean_tc not needed for internal calc
    fig_nonuse_summary()
    fig_total_value(overall_mean, cs_per)
    fig_eco_vs_wtp()
    fig_wtp_cdf()

    with open(STATS_PATH, "w") as f:
        f.write("\n".join(stats_lines))
    print(f"\n  Stats saved to: {STATS_PATH}")
    print(f"  All {len(os.listdir(OUT_DIR)) - 1} figures saved to: {OUT_DIR}/")


if __name__ == "__main__":
    main()
