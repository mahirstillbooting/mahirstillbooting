import urllib.request
import urllib.error
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STREAK_SVG = BASE_DIR / "assets" / "streak-stats.svg"
GITHUB_STATS_SVG = BASE_DIR / "assets" / "github-stats.svg"

def update_streak(username="mahirstillbooting"):
    print("Updating streak stats...")
    url = f"https://streak-stats.demolab.com?user={username}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8")

    tc_match = re.search(r'Total Contributions big number.*?<text[^>]*>\s*([0-9,]+)\s*</text>', content, re.DOTALL)
    tc_range = re.search(r'Total Contributions range.*?<text[^>]*>\s*([^<]+)\s*</text>', content, re.DOTALL)
    cs_match = re.search(r'Current Streak big number.*?<text[^>]*>\s*([0-9,]+)\s*</text>', content, re.DOTALL)
    cs_range = re.search(r'Current Streak range.*?<text[^>]*>\s*([^<]+)\s*</text>', content, re.DOTALL)
    ls_match = re.search(r'Longest Streak big number.*?<text[^>]*>\s*([0-9,]+)\s*</text>', content, re.DOTALL)
    ls_range = re.search(r'Longest Streak range.*?<text[^>]*>\s*([^<]+)\s*</text>', content, re.DOTALL)

    if not all([tc_match, tc_range, cs_match, cs_range, ls_match, ls_range]):
        raise ValueError("Could not parse all streak fields from API response.")

    data = {
        "total_contributions": tc_match.group(1).strip(),
        "total_range": tc_range.group(1).strip(),
        "current_streak": cs_match.group(1).strip(),
        "current_range": cs_range.group(1).strip(),
        "longest_streak": ls_match.group(1).strip(),
        "longest_range": ls_range.group(1).strip(),
    }

    if not STREAK_SVG.exists():
        raise FileNotFoundError(f"Streak SVG not found at {STREAK_SVG}")

    svg_content = STREAK_SVG.read_text(encoding="utf-8")

    svg_content = re.sub(
        r"(<text\s+id='total-contributions-num'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['total_contributions']}\n                \g<2>",
        svg_content,
        flags=re.DOTALL
    )
    svg_content = re.sub(
        r"(<text\s+id='total-contributions-range'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['total_range']}\n                \g<2>",
        svg_content,
        flags=re.DOTALL
    )
    svg_content = re.sub(
        r"(<text\s+id='current-streak-num'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['current_streak']}\n                \g<2>",
        svg_content,
        flags=re.DOTALL
    )
    svg_content = re.sub(
        r"(<text\s+id='current-streak-range'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['current_range']}\n                \g<2>",
        svg_content,
        flags=re.DOTALL
    )
    svg_content = re.sub(
        r"(<text\s+id='longest-streak-num'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['longest_streak']}\n                \g<2>",
        svg_content,
        flags=re.DOTALL
    )
    svg_content = re.sub(
        r"(<text\s+id='longest-streak-range'[^>]*>).*?(</text>)",
        rf"\g<1>\n                    {data['longest_range']}\n                \g<2>",
        svg_content,
        flags=re.DOTALL
    )

    STREAK_SVG.write_text(svg_content, encoding="utf-8")
    print("Streak stats updated successfully:", data)

def update_github_stats(username="mahirstillbooting"):
    print("Updating GitHub stats...")
    url = (
        f"https://github-readme-stats.vercel.app/api?username={username}"
        "&show_icons=true&bg_color=0D0D0D&text_color=FFFFFF&title_color=E02424"
        "&border_color=222222&icon_color=E02424"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode("utf-8")

    blink_css = """
    @keyframes rankBlink {
      0%, 100% {
        opacity: 1;
        filter: drop-shadow(0 0 6px #E02424);
      }
      50% {
        opacity: 0.2;
        filter: none;
      }
    }
    [data-testid="level-rank-icon"], .rank-text text {
      animation: rankBlink 1.4s ease-in-out infinite !important;
    }
    """

    if "</style>" in content:
        content = content.replace("</style>", blink_css + "\n        </style>")

    GITHUB_STATS_SVG.write_text(content, encoding="utf-8")
    print("GitHub stats updated successfully with blinking rank.")

if __name__ == "__main__":
    streak_ok = False
    stats_ok = False

    try:
        update_streak()
        streak_ok = True
    except Exception as e:
        print(f"Error updating streak stats: {e}")

    try:
        update_github_stats()
        stats_ok = True
    except Exception as e:
        print(f"Notice: GitHub stats API temporarily unavailable ({e}). Preserving existing SVG.")

    # Only fail the workflow if streak update fails
    if not streak_ok:
        sys.exit(1)
    else:
        print("Update step completed successfully.")
