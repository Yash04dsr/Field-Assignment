"""
Compute CVM and TCM statistics from the final survey data for report inclusion.
"""

import csv
import io

INPUT_FILE = "survey_responses_final.csv"


def load_data(filepath):
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            rows.append(row)
    return headers, rows


# Column indices (0-based)
COL_TIMESTAMP = 0
COL_ASPECTS = 1
COL_WTP = 2
COL_AMOUNT = 3
COL_NO_REASON = 4
COL_FUTURE = 5
COL_SUPPORT = 6
COL_ECO = 7
COL_PIN = 8
COL_TRANSPORT = 9
COL_SOLE_DEST = 10
COL_TRAVEL_COST = 11
COL_TRAVEL_TIME = 12
COL_VISIT_FREQ = 13
COL_AGE = 14
COL_INCOME = 15

AMOUNT_MAP = {
    "₹10 extra | ₹10 अतिरिक्त": 10,
    "₹20 extra | ₹20 अतिरिक्त": 20,
    "₹50 extra | ₹50 अतिरिक्त": 50,
    "₹100 extra | ₹100 अतिरिक्त": 100,
}

COST_MIDPOINTS = {
    "₹0–₹20": 10,
    "₹21–₹50": 35,
    "₹51–₹100": 75,
    "₹101–₹200": 150,
    "More than ₹200 | ₹200 से ज़्यादा": 250,
}


def main():
    headers, rows = load_data(INPUT_FILE)
    n = len(rows)
    print(f"Total respondents: {n}\n")

    # === DEMOGRAPHICS ===
    print("=" * 60)
    print("SECTION 4.1: DESCRIPTIVE STATISTICS")
    print("=" * 60)

    age_dist = {}
    for r in rows:
        age_dist[r[COL_AGE]] = age_dist.get(r[COL_AGE], 0) + 1
    print("\nAge Distribution:")
    for k in ["Under 18", "18–35", "36–60", "60+"]:
        v = age_dist.get(k, 0)
        print(f"  {k:15s}: {v:3d} ({v/n*100:5.1f}%)")

    income_dist = {}
    for r in rows:
        income_dist[r[COL_INCOME]] = income_dist.get(r[COL_INCOME], 0) + 1
    print("\nIncome/Occupation Distribution:")
    for k, v in sorted(income_dist.items(), key=lambda x: -x[1]):
        print(f"  {k:45s}: {v:3d} ({v/n*100:5.1f}%)")

    freq_dist = {}
    for r in rows:
        freq_dist[r[COL_VISIT_FREQ]] = freq_dist.get(r[COL_VISIT_FREQ], 0) + 1
    print("\nVisit Frequency:")
    for k, v in sorted(freq_dist.items(), key=lambda x: -x[1]):
        print(f"  {k:50s}: {v:3d} ({v/n*100:5.1f}%)")

    transport_dist = {}
    for r in rows:
        transport_dist[r[COL_TRANSPORT]] = transport_dist.get(r[COL_TRANSPORT], 0) + 1
    print("\nTransport Mode:")
    for k, v in sorted(transport_dist.items(), key=lambda x: -x[1]):
        print(f"  {k:55s}: {v:3d} ({v/n*100:5.1f}%)")

    # === CVM ANALYSIS ===
    print(f"\n{'=' * 60}")
    print("SECTION 4.2: CONTINGENT VALUATION METHOD (CVM) ANALYSIS")
    print("=" * 60)

    wtp_yes = [r for r in rows if "Yes" in r[COL_WTP]]
    wtp_no = [r for r in rows if "No" in r[COL_WTP]]
    print(f"\nWillingness to Pay:")
    print(f"  Yes: {len(wtp_yes)} ({len(wtp_yes)/n*100:.1f}%)")
    print(f"  No:  {len(wtp_no)} ({len(wtp_no)/n*100:.1f}%)")

    amounts = []
    for r in wtp_yes:
        amt = AMOUNT_MAP.get(r[COL_AMOUNT], 0)
        amounts.append(amt)
    mean_wtp = sum(amounts) / len(amounts) if amounts else 0
    median_wtp = sorted(amounts)[len(amounts)//2] if amounts else 0
    print(f"\nAmong WTP=Yes ({len(wtp_yes)} respondents):")
    print(f"  Mean WTP:   ₹{mean_wtp:.1f} per visit")
    print(f"  Median WTP: ₹{median_wtp} per visit")

    amt_dist = {}
    for r in wtp_yes:
        amt_dist[r[COL_AMOUNT]] = amt_dist.get(r[COL_AMOUNT], 0) + 1
    print("  Amount distribution:")
    for k, v in sorted(amt_dist.items()):
        print(f"    {k}: {v} ({v/len(wtp_yes)*100:.0f}%)")

    # Overall mean WTP (including zeros for No respondents)
    overall_mean = sum(amounts) / n
    print(f"\n  Overall Mean WTP (incl. zeros): ₹{overall_mean:.1f} per visit")

    # Aggregate WTP estimation
    est_annual_visitors = 1_500_000  # ~1.5M annual visitors (estimate)
    aggregate_wtp = overall_mean * est_annual_visitors
    print(f"\n  Estimated Annual Visitors: {est_annual_visitors:,}")
    print(f"  Aggregate Annual WTP: ₹{aggregate_wtp:,.0f}")
    print(f"  Aggregate Annual WTP: ₹{aggregate_wtp/10000000:.2f} crore")

    # Protest bids
    print(f"\nProtest Bids / Reasons for No ({len(wtp_no)} respondents):")
    reason_dist = {}
    for r in wtp_no:
        reason_dist[r[COL_NO_REASON]] = reason_dist.get(r[COL_NO_REASON], 0) + 1
    for k, v in sorted(reason_dist.items(), key=lambda x: -x[1]):
        label = k[:60] + "..." if len(k) > 60 else k
        print(f"  {label}: {v} ({v/len(wtp_no)*100:.0f}%)")

    # Non-use values
    print(f"\n--- Non-Use Values ---")
    future_dist = {}
    for r in rows:
        future_dist[r[COL_FUTURE]] = future_dist.get(r[COL_FUTURE], 0) + 1
    print("Bequest Value (Future Generation Preservation):")
    for k, v in sorted(future_dist.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v} ({v/n*100:.1f}%)")

    support_yes = sum(1 for r in rows if "Yes" in r[COL_SUPPORT])
    print(f"\nExistence Value (Support without visiting):")
    print(f"  Yes: {support_yes} ({support_yes/n*100:.1f}%)")
    print(f"  No:  {n - support_yes} ({(n-support_yes)/n*100:.1f}%)")

    # Ecological condition
    eco_dist = {}
    for r in rows:
        eco_dist[r[COL_ECO]] = eco_dist.get(r[COL_ECO], 0) + 1
    print(f"\nEcological Condition Rating:")
    for k, v in sorted(eco_dist.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v} ({v/n*100:.1f}%)")

    # Aspects valued
    aspect_counts = {}
    for r in rows:
        aspects = r[COL_ASPECTS].split(", ")
        for a in aspects:
            a = a.strip()
            if a:
                aspect_counts[a] = aspect_counts.get(a, 0) + 1
    print(f"\nAspects Valued (checkbox, n={n}):")
    for k, v in sorted(aspect_counts.items(), key=lambda x: -x[1]):
        short = k[:55] + "..." if len(k) > 55 else k
        print(f"  {short}: {v} ({v/n*100:.1f}%)")

    # Cross-tab: Income vs WTP
    print(f"\n--- Cross-Tabulation: Income vs WTP ---")
    income_groups = sorted(set(r[COL_INCOME] for r in rows))
    for ig in income_groups:
        total_ig = sum(1 for r in rows if r[COL_INCOME] == ig)
        yes_ig = sum(1 for r in rows if r[COL_INCOME] == ig and "Yes" in r[COL_WTP])
        pct = yes_ig / total_ig * 100 if total_ig else 0
        short = ig[:40] + "..." if len(ig) > 40 else ig
        print(f"  {short:42s}: {yes_ig}/{total_ig} ({pct:.0f}% WTP Yes)")

    # === TCM ANALYSIS ===
    print(f"\n{'=' * 60}")
    print("SECTION 4.3: TRAVEL COST METHOD (TCM) ANALYSIS")
    print("=" * 60)

    travel_costs = []
    for r in rows:
        cost = COST_MIDPOINTS.get(r[COL_TRAVEL_COST], 0)
        travel_costs.append(cost)
    mean_tc = sum(travel_costs) / n
    print(f"\nMean one-way travel cost: ₹{mean_tc:.1f}")
    print(f"Mean round-trip travel cost: ₹{mean_tc*2:.1f}")

    cost_dist = {}
    for r in rows:
        cost_dist[r[COL_TRAVEL_COST]] = cost_dist.get(r[COL_TRAVEL_COST], 0) + 1
    print("\nTravel Cost Distribution:")
    for k in ["₹0–₹20", "₹21–₹50", "₹51–₹100", "₹101–₹200", "More than ₹200 | ₹200 से ज़्यादा"]:
        v = cost_dist.get(k, 0)
        print(f"  {k:40s}: {v:3d} ({v/n*100:5.1f}%)")

    time_dist = {}
    for r in rows:
        time_dist[r[COL_TRAVEL_TIME]] = time_dist.get(r[COL_TRAVEL_TIME], 0) + 1
    print("\nTravel Time Distribution:")
    for k, v in sorted(time_dist.items(), key=lambda x: -x[1]):
        print(f"  {k:45s}: {v:3d} ({v/n*100:5.1f}%)")

    sole_yes = sum(1 for r in rows if "only" in r[COL_SOLE_DEST].lower())
    print(f"\nSole Destination: Yes {sole_yes} ({sole_yes/n*100:.0f}%), No {n-sole_yes} ({(n-sole_yes)/n*100:.0f}%)")

    # Consumer surplus estimation (simple approach)
    # CS = (max travel cost - actual travel cost) summed
    max_cost = max(travel_costs)
    consumer_surplus = sum(max_cost - tc for tc in travel_costs)
    cs_per_visit = consumer_surplus / n
    print(f"\n  Max observed travel cost: ₹{max_cost}")
    print(f"  Total consumer surplus (sample): ₹{consumer_surplus:.0f}")
    print(f"  Consumer surplus per visitor: ₹{cs_per_visit:.1f}")
    print(f"  Annual consumer surplus (est.): ₹{cs_per_visit * est_annual_visitors:,.0f}")
    print(f"  Annual consumer surplus: ₹{cs_per_visit * est_annual_visitors / 10000000:.2f} crore")

    # === TOTAL ECONOMIC VALUE ===
    print(f"\n{'=' * 60}")
    print("SECTION 4.4: TOTAL ECONOMIC VALUE ESTIMATE")
    print("=" * 60)
    use_value = cs_per_visit * est_annual_visitors
    cvm_value = overall_mean * est_annual_visitors
    bequest_pct = future_dist.get("Very important | बहुत ज़रूरी", 0) / n
    existence_pct = support_yes / n
    nonuse_multiplier = 1 + (bequest_pct * 0.5 + existence_pct * 0.3)
    total_value = use_value + cvm_value * nonuse_multiplier

    print(f"\n  Use Value (TCM Consumer Surplus): ₹{use_value/10000000:.2f} crore/year")
    print(f"  CVM WTP Value:                   ₹{cvm_value/10000000:.2f} crore/year")
    print(f"  Non-use multiplier:              {nonuse_multiplier:.2f}x")
    print(f"    (Bequest factor: {bequest_pct:.0%} very important)")
    print(f"    (Existence factor: {existence_pct:.0%} support without visiting)")
    print(f"  Estimated Total Economic Value:  ₹{total_value/10000000:.2f} crore/year")


if __name__ == "__main__":
    main()
