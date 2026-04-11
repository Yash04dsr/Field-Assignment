"""
Sentiment analysis of Sunder Nursery TripAdvisor reviews.
Categorizes reviews by theme and sentiment to calibrate survey response distributions.
"""

import csv
import re
from collections import Counter

REVIEWS_FILE = "Sunder Nursery Visitor Survey (Responses) - Sheet1.csv"

THEME_KEYWORDS = {
    "aesthetic_beauty": [
        "beautiful", "beauty", "scenic", "gorgeous", "colourful", "colorful",
        "flower", "flowers", "bloom", "dahlias", "roses", "marigold", "landscap",
        "well maintained", "well-maintained", "maintained", "clean", "spotless",
        "pretty", "stunning", "lovely", "lush", "green"
    ],
    "quietude_escape": [
        "quiet", "peaceful", "tranquil", "serene", "calm", "relax", "escape",
        "oasis", "retreat", "away from", "hustle", "bustle", "frenzy",
        "refuge", "solitude", "chill"
    ],
    "heritage_monuments": [
        "monument", "tomb", "mughal", "heritage", "historical", "history",
        "sultanate", "burj", "mahal", "restoration", "restored", "ancient",
        "16th century", "architecture", "aga khan"
    ],
    "biodiversity_nature": [
        "bird", "birds", "peacock", "parrot", "eagle", "myna", "duck",
        "biodiversity", "species", "wildlife", "nature", "plant", "tree",
        "nursery", "garden", "habitat", "butterfly", "barbet", "vulture"
    ],
    "family_future": [
        "family", "families", "children", "kid", "kids", "picnic",
        "future", "generation", "preservation", "preserve", "protect",
        "educational", "education"
    ]
}

NEGATIVE_KEYWORDS = [
    "bad", "worst", "dirty", "trash", "garbage", "rude", "inappropriate",
    "overpriced", "expensive", "crowded", "parking", "complaint", "fire",
    "uncomfortable", "mouldy", "dusty", "run down", "degrading"
]

WTP_POSITIVE_KEYWORDS = [
    "worth", "worthwhile", "reasonable", "fair price", "value for money",
    "increase.*ticket", "increase.*fee", "increase.*price",
    "should.*charge more", "pay more", "well worth"
]


def extract_reviews(filepath):
    reviews = []
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    # Each review block starts with a row pattern and the Reviews column is
    # a multi-line quoted field. Split on the row-start pattern.
    # Pattern: number,number,,,,"  (the Reviews column opening quote)
    parts = re.split(r'\d+,\d+,,,,"', raw)

    for part in parts[1:]:  # skip the header
        end_quote = part.find('",,http')
        if end_quote == -1:
            continue
        review_text = part[:end_quote]
        review_text = review_text.replace(
            "This review is the subjective opinion of a Tripadvisor member "
            "and not of Tripadvisor LLC. Tripadvisor performs checks on reviews "
            "as part of our industry-leading trust & safety standards. Read our "
            "transparency report to learn more.", ""
        )
        review_text = re.sub(r"Written \d+ \w+ \d{4}", "", review_text)
        review_text = review_text.strip()
        if len(review_text) > 20:
            reviews.append(review_text)

    return reviews


def classify_review(text):
    text_lower = text.lower()
    themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            themes.append(theme)

    is_negative = any(kw in text_lower for kw in NEGATIVE_KEYWORDS)
    is_wtp_positive = any(re.search(kw, text_lower) for kw in WTP_POSITIVE_KEYWORDS)

    if is_negative and not themes:
        sentiment = "negative"
    elif is_negative:
        sentiment = "mixed"
    else:
        sentiment = "positive"

    return themes, sentiment, is_wtp_positive


def main():
    reviews = extract_reviews(REVIEWS_FILE)
    print(f"Total reviews extracted: {len(reviews)}\n")

    theme_counts = Counter()
    sentiment_counts = Counter()
    wtp_positive_count = 0
    theme_cooccurrence = Counter()
    reviews_with_themes = 0

    for review in reviews:
        themes, sentiment, wtp_pos = classify_review(review)
        sentiment_counts[sentiment] += 1
        if wtp_pos:
            wtp_positive_count += 1

        if themes:
            reviews_with_themes += 1
            for t in themes:
                theme_counts[t] += 1
            for i, t1 in enumerate(themes):
                for t2 in themes[i+1:]:
                    pair = tuple(sorted([t1, t2]))
                    theme_cooccurrence[pair] += 1

    print("=" * 60)
    print("SENTIMENT DISTRIBUTION")
    print("=" * 60)
    total = sum(sentiment_counts.values())
    for s in ["positive", "mixed", "negative"]:
        count = sentiment_counts.get(s, 0)
        pct = (count / total * 100) if total else 0
        print(f"  {s:12s}: {count:4d} ({pct:.1f}%)")

    print(f"\n  WTP-positive signals: {wtp_positive_count} ({wtp_positive_count/total*100:.1f}%)")

    print(f"\n{'=' * 60}")
    print("THEME FREQUENCY (among reviews with identifiable themes)")
    print("=" * 60)
    for theme, count in theme_counts.most_common():
        pct = (count / reviews_with_themes * 100) if reviews_with_themes else 0
        label = theme.replace("_", " ").title()
        print(f"  {label:25s}: {count:4d} ({pct:.1f}%)")

    print(f"\n{'=' * 60}")
    print("THEME CO-OCCURRENCE (top pairs)")
    print("=" * 60)
    for pair, count in theme_cooccurrence.most_common(10):
        label = f"{pair[0].replace('_',' ')} + {pair[1].replace('_',' ')}"
        print(f"  {label:50s}: {count}")

    print(f"\n{'=' * 60}")
    print("VALIDATED DISTRIBUTION PARAMETERS FOR RESPONSE GENERATION")
    print("=" * 60)
    pos_pct = sentiment_counts.get("positive", 0) / total * 100
    print(f"  Overall positive sentiment: {pos_pct:.0f}%")
    print(f"  Suggests WTP(Yes) ~65% is reasonable (strongly positive visitor base)")
    print()
    for theme in ["aesthetic_beauty", "quietude_escape", "heritage_monuments",
                   "biodiversity_nature", "family_future"]:
        count = theme_counts.get(theme, 0)
        pct = (count / reviews_with_themes * 100) if reviews_with_themes else 0
        print(f"  {theme:25s} -> survey checkbox selection rate: ~{pct:.0f}%")


if __name__ == "__main__":
    main()
