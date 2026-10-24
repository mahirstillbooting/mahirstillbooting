import urllib.request
import re
from pathlib import Path

SVG_PATH = Path(__file__).resolve().parent.parent / "assets" / "streak-stats.svg"

def fetch_streak_data(username="mahirstillbooting"):
    url = f"https://streak-stats.demolab.com?user={username}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read().decode("utf-8")

    tc_match = re.search(r'Total Contributions big number.*?<text[^>]*>\s*([0-9,]+)\s*</text>', content, re.DOTALL)
    tc_range = re.search(r'Total Contributions range.*?<text[^>]*>\s*([^<]+)\s*</text>', content, re.DOTALL)
    cs_match = re.search(r'Current Streak big number.*?<text[^>]*>\s*([0-9,]+)\s*</text>', content, re.DOTALL)
    cs_range = re.search(r'Current Streak range.*?<text[^>]*>\s*([^<]+)\s*</text>', content, re.DOTALL)
    ls_match = re.search(r'Longest Streak big number.*?<text[^>]*>\s*([0-9,]+)\s*</text>', content, re.DOTALL)
    ls_range = re.search(r'Longest Streak range.*?<text[^>]*>\s*([^<]+)\s*</text>', content, re.DOTALL)

    if not all([tc_match, tc_range, cs_match, cs_range, ls_match, ls_range]):
        raise ValueError("Could not parse all streak fields from API response.")

    return {
        "total_contributions": tc_match.group(1).strip(),
        "total_range": tc_range.group(1).strip(),
        "current_streak": cs_match.group(1).strip(),
        "current_range": cs_range.group(1).strip(),
        "longest_streak": ls_match.group(1).strip(),
        "longest_range": ls_range.group(1).strip(),
    }

def update_svg(data):
    if not SVG_PATH.exists():
        raise FileNotFoundError(f"SVG file not found at {SVG_PATH}")

    svg_content = SVG_PATH.read_text(encoding="utf-8")

    # Update total contributions
    svg_content = re.sub(
        r"(<text\s+id='total-contributions-num'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['total_contributions']}\n                \g<2>",
        svg_content
    )
    svg_content = re.sub(
        r"(<text\s+id='total-contributions-range'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['total_range']}\n                \g<2>",
        svg_content
    )

    # Update current streak
    svg_content = re.sub(
        r"(<text\s+id='current-streak-num'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['current_streak']}\n                \g<2>",
        svg_content
    )
    svg_content = re.sub(
        r"(<text\s+id='current-streak-range'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['current_range']}\n                \g<2>",
        svg_content
    )

    # Update longest streak
    svg_content = re.sub(
        r"(<text\s+id='longest-streak-num'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['longest_streak']}\n                \g<2>",
        svg_content
    )
    svg_content = re.sub(
        r"(<text\s+id='longest-streak-range'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['longest_range']}\n                \g<2>",
        svg_content
    )

    SVG_PATH.write_text(svg_content, encoding="utf-8")
    print("Successfully updated streak-stats.svg with data:", data)

if __name__ == "__main__":
    data = fetch_streak_data()
    update_svg(data)
