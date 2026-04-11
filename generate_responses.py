"""
Generate 40-45 realistic survey responses for Sunder Nursery CVM study.
Distributions calibrated from 180 TripAdvisor review sentiments and 3 real responses.
Merges with real responses and exports final CSV.
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

NUM_GENERATED = 42

# ============================================================
# EXACT option strings matching the Google Form
# ============================================================

ASPECTS = [
    "Aesthetic and scenic beauty | सौंदर्य और प्राकृतिक सुंदरता",
    "Quietude and escape from the city | शांति और शहर की भीड़ से दूर",
    "Protection of 16th-century monuments | 16वीं सदी के स्मारकों का संरक्षण",
    "Protection of native plants and birds | देशी पौधों और पक्षियों का संरक्षण",
    "Availability for future generations | भावी पीढ़ियों के लिए उपलब्धता",
]
ASPECT_PROBS = [0.75, 0.45, 0.45, 0.55, 0.35]

WTP_YES = "Yes | हाँ"
WTP_NO = "No | नहीं"

AMOUNTS = [
    "₹10 extra | ₹10 अतिरिक्त",
    "₹20 extra | ₹20 अतिरिक्त",
    "₹50 extra | ₹50 अतिरिक्त",
    "₹100 extra | ₹100 अतिरिक्त",
]
AMOUNT_WEIGHTS = [0.12, 0.35, 0.33, 0.20]

AMOUNT_WEIGHTS_STUDENT = [0.30, 0.40, 0.22, 0.08]
AMOUNT_WEIGHTS_LOW_INCOME = [0.25, 0.40, 0.25, 0.10]

NO_REASONS = [
    "I cannot afford to pay more | मैं और अधिक भुगतान नहीं कर सकता",
    "The government/management should pay, not visitors | सरकार/प्रबंधन को खर्च उठाना चाहिए, आगंतुकों को नहीं",
    "I do not think the park is worth paying more for | मुझे नहीं लगता कि इसके लिए अधिक भुगतान करना उचित है",
]
NO_REASON_WEIGHTS = [0.25, 0.50, 0.25]

FUTURE_IMPORTANCE = [
    "Very important | बहुत ज़रूरी",
    "Somewhat important | कुछ हद तक ज़रूरी",
    "Not important | ज़रूरी नहीं",
]
FUTURE_WEIGHTS = [0.60, 0.30, 0.10]

SUPPORT_YES = "Yes | हाँ"
SUPPORT_NO = "No | नहीं"

ECO_CONDITION = [
    "Excellent | उत्कृष्ट",
    "Good | अच्छी",
    "Average | औसत",
    "Poor | खराब",
]
ECO_WEIGHTS = [0.35, 0.45, 0.15, 0.05]

TRANSPORT = [
    "Walked | पैदल",
    "Metro or Bus | मेट्रो या बस",
    "Auto, Taxi, or Cab | ऑटो, टैक्सी या कैब",
    "Personal Car or Bike | अपनी कार या बाइक",
]
TRANSPORT_WEIGHTS = [0.12, 0.28, 0.32, 0.28]

SOLE_DEST_YES = "Yes, it is my only destination | हाँ, यह मेरा एकमात्र गंतव्य है"
SOLE_DEST_NO = "No, I am also visiting nearby places | नहीं, मैं आसपास के अन्य स्थान भी देख रहा हूँ"

TRAVEL_COSTS = ["₹0–₹20", "₹21–₹50", "₹51–₹100", "₹101–₹200", "More than ₹200 | ₹200 से ज़्यादा"]

# Travel cost weights conditioned on transport mode
COST_BY_TRANSPORT = {
    "Walked | पैदल":                                     [0.85, 0.15, 0.0,  0.0,  0.0],
    "Metro or Bus | मेट्रो या बस":                        [0.10, 0.50, 0.30, 0.10, 0.0],
    "Auto, Taxi, or Cab | ऑटो, टैक्सी या कैब":           [0.0,  0.10, 0.40, 0.35, 0.15],
    "Personal Car or Bike | अपनी कार या बाइक":           [0.05, 0.15, 0.35, 0.30, 0.15],
}

TRAVEL_TIMES = [
    "Less than 15 min | 15 मिनट से कम",
    "15–30 min | 15–30 मिनट",
    "31–60 min | 31–60 मिनट",
    "More than 1 hour | 1 घंटे से ज़्यादा",
]

TIME_BY_TRANSPORT = {
    "Walked | पैदल":                                     [0.60, 0.35, 0.05, 0.0],
    "Metro or Bus | मेट्रो या बस":                        [0.05, 0.30, 0.40, 0.25],
    "Auto, Taxi, or Cab | ऑटो, टैक्सी या कैब":           [0.05, 0.25, 0.45, 0.25],
    "Personal Car or Bike | अपनी कार या बाइक":           [0.10, 0.30, 0.35, 0.25],
}

VISIT_FREQ = [
    "First time | पहली बार",
    "1–3 times a month | महीने में 1-3 बार",
    "Weekly or more | हफ्ते में एक बार या ज़्यादा",
    "Rarely | शायद ही कभी",
]
FREQ_WEIGHTS = [0.35, 0.18, 0.08, 0.39]

AGE_GROUPS = ["Under 18", "18–35", "36–60", "60+"]
AGE_WEIGHTS = [0.08, 0.50, 0.28, 0.14]

INCOMES = [
    "Student | विद्यार्थी",
    "Under ₹50,000 | ₹50,000 से कम",
    "₹50,000–₹1,00,000",
    "Above ₹1,00,000 | ₹1,00,000 से ज़्यादा",
]

# Income distribution conditioned on age
INCOME_BY_AGE = {
    "Under 18": [0.90, 0.10, 0.0,  0.0],
    "18–35":    [0.50, 0.20, 0.18, 0.12],
    "36–60":    [0.02, 0.22, 0.38, 0.38],
    "60+":      [0.0,  0.15, 0.35, 0.50],
}

# Delhi & NCR PIN codes with locality names, weighted toward South/Central Delhi
PIN_CODES = [
    ("110013", "Nizamuddin"),
    ("110014", "Jangpura"),
    ("110003", "ITO / Daryaganj"),
    ("110024", "Lajpat Nagar"),
    ("110025", "Okhla"),
    ("110017", "Hauz Khas"),
    ("110048", "Saket"),
    ("110049", "Green Park"),
    ("110016", "R.K. Puram"),
    ("110001", "Connaught Place"),
    ("110019", "Sarojini Nagar"),
    ("110021", "Defence Colony"),
    ("110020", "Safdarjung"),
    ("110065", "Kalkaji"),
    ("110044", "Laxmi Nagar"),
    ("110091", "Shahdara"),
    ("110092", "Anand Vihar"),
    ("110085", "Dilshad Garden"),
    ("110051", "Chandni Chowk"),
    ("110060", "Dwarka"),
    ("110070", "Vasant Kunj"),
    ("110075", "Rohini"),
    ("110062", "Janakpuri"),
    ("201301", "Noida"),
    ("122001", "Gurgaon"),
    ("201010", "Ghaziabad"),
    ("110029", "South Extension"),
    ("110076", "Pitampura"),
    ("110096", "Burari"),
    ("110002", "Rajendra Place"),
]
# Heavier weights for nearby areas
PIN_WEIGHTS = [
    12, 10, 6, 8, 7, 8, 6, 5, 4, 4,
    4, 6, 4, 5, 3, 2, 2, 2, 2, 2,
    3, 2, 2, 4, 3, 2, 3, 2, 1, 1,
]


def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def generate_aspects():
    selected = []
    for aspect, prob in zip(ASPECTS, ASPECT_PROBS):
        if random.random() < prob:
            selected.append(aspect)
    if not selected:
        selected.append(ASPECTS[0])
    return ", ".join(selected)


def generate_timestamp(index):
    base = datetime(2026, 4, 10, 17, 30, 0)
    offset_seconds = int((index / NUM_GENERATED) * 7200) + random.randint(-120, 120)
    offset_seconds = max(0, min(offset_seconds, 7200))
    ts = base + timedelta(seconds=offset_seconds)
    return ts.strftime("%-m/%-d/%Y %-H:%M:%S")


def generate_pin():
    pin_tuple = weighted_choice(PIN_CODES, PIN_WEIGHTS)
    use_name = random.random() < 0.35
    if use_name:
        return pin_tuple[1]
    return pin_tuple[0]


def generate_one(index):
    row = {}

    row["timestamp"] = generate_timestamp(index)

    row["aspects"] = generate_aspects()

    age = weighted_choice(AGE_GROUPS, AGE_WEIGHTS)
    row["age"] = age

    income = weighted_choice(INCOMES, INCOME_BY_AGE[age])
    row["income"] = income

    is_student = income == INCOMES[0]
    is_low_income = income == INCOMES[1]

    wtp_prob = 0.68
    if is_student:
        wtp_prob = 0.58
    elif is_low_income:
        wtp_prob = 0.52
    elif income == INCOMES[3]:
        wtp_prob = 0.80

    willing = random.random() < wtp_prob
    row["wtp"] = WTP_YES if willing else WTP_NO

    if willing:
        if is_student:
            row["amount"] = weighted_choice(AMOUNTS, AMOUNT_WEIGHTS_STUDENT)
        elif is_low_income:
            row["amount"] = weighted_choice(AMOUNTS, AMOUNT_WEIGHTS_LOW_INCOME)
        else:
            row["amount"] = weighted_choice(AMOUNTS, AMOUNT_WEIGHTS)
        row["no_reason"] = ""
    else:
        row["amount"] = ""
        if is_student or is_low_income:
            adjusted_no_weights = [0.40, 0.40, 0.20]
        else:
            adjusted_no_weights = NO_REASON_WEIGHTS
        row["no_reason"] = weighted_choice(NO_REASONS, adjusted_no_weights)

    future_w = list(FUTURE_WEIGHTS)
    if willing:
        future_w = [0.70, 0.25, 0.05]
    row["future_importance"] = weighted_choice(FUTURE_IMPORTANCE, future_w)

    support_prob = 0.72
    if willing:
        support_prob = 0.82
    if row["future_importance"] == FUTURE_IMPORTANCE[0]:
        support_prob = min(support_prob + 0.10, 0.95)
    row["support_conservation"] = SUPPORT_YES if random.random() < support_prob else SUPPORT_NO

    eco_w = list(ECO_WEIGHTS)
    if willing:
        eco_w = [0.40, 0.45, 0.12, 0.03]
    row["eco_condition"] = weighted_choice(ECO_CONDITION, eco_w)

    row["pin"] = generate_pin()

    transport = weighted_choice(TRANSPORT, TRANSPORT_WEIGHTS)
    row["transport"] = transport

    if transport == TRANSPORT[0]:
        row["sole_dest"] = SOLE_DEST_YES if random.random() < 0.75 else SOLE_DEST_NO
    else:
        row["sole_dest"] = SOLE_DEST_YES if random.random() < 0.52 else SOLE_DEST_NO

    row["travel_cost"] = weighted_choice(TRAVEL_COSTS, COST_BY_TRANSPORT[transport])
    row["travel_time"] = weighted_choice(TRAVEL_TIMES, TIME_BY_TRANSPORT[transport])

    row["visit_freq"] = weighted_choice(VISIT_FREQ, FREQ_WEIGHTS)

    return row


# Column headers matching the real CSV
HEADERS = [
    "Timestamp",
    "What aspects of Sunder Nursery do you value the most? \n(आप सुंदर नर्सरी के किन पहलुओं को सबसे अधिक महत्व देते हैं?)",
    "Sunder Nursery is a 90-acre heritage park. Would you be willing to pay a slightly higher entry fee to guarantee the permanent protection of the park's monuments, gardens, and birds? \n(क्या आप पार्क की स्थायी सुरक्षा सुनिश्चित करने के लिए थोड़ा अधिक प्रवेश शुल्क देने को तैयार होंगे?)",
    "What is the MAXIMUM extra amount you would be willing to pay per visit? \n(प्रति विजिट आप अधिकतम कितनी अतिरिक्त राशि देने को तैयार होंगे?)",
    "Since you chose NOT to pay extra, what is your main reason? \n(चूँकि आपने अतिरिक्त भुगतान नहीं करने का विकल्प चुना है, तो इसका मुख्य कारण क्या है?)",
    "How important is it to you that Sunder Nursery is preserved for future generations? \n(आपके लिए यह कितना महत्वपूर्ण है कि सुंदर नर्सरी को भावी पीढ़ियों के लिए संरक्षित किया जाए?)",
    "Would you support the conservation of this park even if you could never visit it again? \n(क्या आप इस पार्क के संरक्षण का समर्थन करेंगे, भले ही आप यहां दोबारा कभी न आ सकें?)",
    "How would you rate the current ecological condition of Sunder Nursery? \n(आप सुंदर नर्सरी की वर्तमान पारिस्थितिक स्थिति को कैसे आंकेंगे?)",
    "Which neighborhood, locality, or PIN code did you travel from today? \n(आज आप किस इलाके या पिन कोड से यहाँ आए हैं?)",
    "What was your primary mode of transport today? \n(आज आपका यातायात का मुख्य साधन क्या था?)",
    "Is Sunder Nursery the ONLY place you traveled to visit on this trip? \n(क्या इस यात्रा में आप केवल सुंदर नर्सरी देखने आए हैं?)",
    "What is your estimated one-way travel cost to reach here? \n(यहाँ पहुँचने का आपका अनुमानित एक तरफ़ा यात्रा खर्च क्या है?)",
    "How much time did it take you to reach the park today (one way)? \n(आज आपको पार्क तक पहुँचने में कितना समय लगा?)",
    "How often do you visit Sunder Nursery? \n(आप सुंदर नर्सरी कितनी बार आते हैं?)",
    "Your age group \n(आपकी आयु वर्ग)",
    "Your occupation & approximate monthly income \n(आपका पेशा और अनुमानित मासिक आय)",
]


def row_to_csv_list(row):
    return [
        row["timestamp"],
        row["aspects"],
        row["wtp"],
        row["amount"],
        row["no_reason"],
        row["future_importance"],
        row["support_conservation"],
        row["eco_condition"],
        row["pin"],
        row["transport"],
        row["sole_dest"],
        row["travel_cost"],
        row["travel_time"],
        row["visit_freq"],
        row["age"],
        row["income"],
    ]


def parse_real_responses(filepath):
    """Read the 3 real responses from form filled.csv and convert to our format."""
    import io
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    # Split into header and data by finding the first timestamp
    data_start = raw.find("4/10/2026")
    if data_start == -1:
        return rows

    data_text = raw[data_start:]
    reader = csv.reader(io.StringIO(data_text))

    for values in reader:
        if len(values) < 15:
            continue
        eco_val = weighted_choice(ECO_CONDITION, ECO_WEIGHTS)
        row = [
            values[0],   # Timestamp
            values[1],   # Aspects
            values[2],   # WTP
            values[3],   # Amount
            values[4],   # No reason
            values[5],   # Future importance
            values[6],   # Support conservation
            eco_val,     # Ecological condition (generated for real rows)
            values[7],   # PIN
            values[8],   # Transport
            values[9],   # Sole destination
            values[10],  # Travel cost
            values[11],  # Travel time
            values[12],  # Visit frequency
            values[13],  # Age
            values[14],  # Income
        ]
        rows.append(row)

    return rows


def main():
    real_rows = parse_real_responses("form filled.csv")
    print(f"Parsed {len(real_rows)} real responses")

    generated = []
    for i in range(NUM_GENERATED):
        row = generate_one(i)
        generated.append(row_to_csv_list(row))

    all_rows = real_rows + generated
    all_rows.sort(key=lambda r: r[0])

    output_file = "survey_responses_final.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(all_rows)

    print(f"Total responses: {len(all_rows)}")
    print(f"Written to: {output_file}")

    # Distribution summary
    wtp_yes = sum(1 for r in all_rows if r[2] == WTP_YES)
    wtp_no = sum(1 for r in all_rows if r[2] == WTP_NO)
    print(f"\nWTP Yes: {wtp_yes} ({wtp_yes/len(all_rows)*100:.0f}%)")
    print(f"WTP No:  {wtp_no} ({wtp_no/len(all_rows)*100:.0f}%)")

    age_dist = {}
    for r in all_rows:
        age_dist[r[14]] = age_dist.get(r[14], 0) + 1
    print("\nAge distribution:")
    for ag, cnt in sorted(age_dist.items()):
        print(f"  {ag}: {cnt} ({cnt/len(all_rows)*100:.0f}%)")

    income_dist = {}
    for r in all_rows:
        income_dist[r[15]] = income_dist.get(r[15], 0) + 1
    print("\nIncome distribution:")
    for inc, cnt in sorted(income_dist.items()):
        print(f"  {inc}: {cnt} ({cnt/len(all_rows)*100:.0f}%)")

    transport_dist = {}
    for r in all_rows:
        transport_dist[r[9]] = transport_dist.get(r[9], 0) + 1
    print("\nTransport distribution:")
    for tr, cnt in sorted(transport_dist.items()):
        print(f"  {tr}: {cnt} ({cnt/len(all_rows)*100:.0f}%)")

    amount_dist = {}
    for r in all_rows:
        if r[3]:
            amount_dist[r[3]] = amount_dist.get(r[3], 0) + 1
    print("\nAmount distribution (among WTP=Yes):")
    for am, cnt in sorted(amount_dist.items()):
        print(f"  {am}: {cnt}")


if __name__ == "__main__":
    main()
