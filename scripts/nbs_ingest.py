"""Ingest independent surveyed NBS crude processing from public releases."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.stats.gov.cn/sj/zxfb/"
FIELDS = ["period", "processing_mt", "publication_date", "source_url", "flags"]


def fetch(url: str, raw: Path) -> str:
    """Cache exact responses; prohibit non-official hosts and HTTP errors."""
    if not url.startswith("https://www.stats.gov.cn/"):
        raise ValueError("Only official NBS HTTPS URLs are supported")
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    path = raw / (key + ".html")
    if not path.exists():
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 2:
                    raise
                time.sleep(1 + attempt)
        path.write_bytes(response.content)
        metadata = {
            "source_url": url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": hashlib.sha256(response.content).hexdigest(),
        }
        path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return path.read_bytes().decode("utf-8-sig")


def parse_release(html: str, url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    if "Please enable JavaScript" in html:
        raise ValueError("official_release_access_challenge;not_parsed")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    heading = re.search(r"(20\d{2})\u5e74(\d{1,2})(?:[\u2014\u2013\uff0d-]2)?\u6708", title)
    if not heading:
        return []
    year, month = map(int, heading.groups())
    combined = month == 1 or bool(re.search(r"1[\u2014\u2013\uff0d-]2\u6708", title))
    # Migration URLs contain 2023 dates; use publication metadata/body instead.
    date_meta = soup.find("meta", attrs={"name": "PubDate"})
    text = soup.get_text(" ", strip=True)
    date_match = re.search(r"20\d{2}[/-]\d{2}[/-]\d{2}", date_meta.get("content", "") if date_meta else text)
    publication = date_match.group().replace("/", "-") if date_match else ""
    value = None
    for row in soup.find_all("tr"):
        cells = [re.sub(r"\s+", "", c.get_text()) for c in row.find_all(["td", "th"])]
        if cells and re.fullmatch(r"\u539f\u6cb9\u52a0\u5de5\u91cf[\uff08(]\u4e07\u5428[\uff09)]", cells[0]):
            if len(cells) > 1 and re.fullmatch(r"[\d,.]+", cells[1]):
                value = float(cells[1].replace(",", "")) / 100
                break
    if value is None and "\u80fd\u6e90\u751f\u4ea7" in title:
        # Require the reporting-month sentence; never parse year-to-date totals.
        flat = re.sub(r"\s+", "", text)
        month_label = r"1[\u2014\u2013\uff0d-]2" if combined else str(month)
        pattern = rf"(?<![\d-]){month_label}\u6708\u4efd?[\uff0c,](?:\u89c4\u4e0a\u5de5\u4e1a)?\u539f\u6cb9\u52a0\u5de5\u91cf([\d.]+)\u4e07\u5428"
        found = re.search(pattern, flat)
        if found:
            value = float(found.group(1)) / 100
    if value is None:
        return []
    if not 10 < value < 200:
        raise ValueError(f"Implausible crude processing volume: {value} at {url}")
    if not publication:
        raise ValueError(f"Missing publication date: {url}")
    common = {"publication_date": publication, "source_url": url}
    if combined:
        # Keep the reported total separately; do not invent monthly measurements.
        return [dict(period=f"{year}-{m:02d}-01", processing_mt="", flags=f"jan_feb_combined_total_mt={value};monthly_unavailable", **common) for m in (1, 2)]
    return [dict(period=f"{year}-{month:02d}-01", processing_mt=value, flags="independent_survey;release_snapshot", **common)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int, default=2015)
    parser.add_argument("--max-pages", type=int, default=67)
    args = parser.parse_args()
    raw = ROOT / "data" / "raw" / "nbs"
    out = ROOT / "data" / "processed"
    raw.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    links = {
        "https://www.stats.gov.cn/sj/zxfb/202302/t20230203_1899018.html": "2015 December confirmed release",
        "https://www.stats.gov.cn/sj/zxfb/202601/t20260119_1962322.html": "2025 December confirmed release",
        "https://www.stats.gov.cn/sj/zxfb/202609/t20260915_1965312.html": "2026 August confirmed release",
    }
    failures = []
    urls = [BASE + ("index.html" if page == 0 else f"index_{page}.html") for page in range(args.max_pages)]
    def get_archive(url):
        try:
            return url, fetch(url, raw), None
        except requests.RequestException as exc:
            return url, "", str(exc)
    with ThreadPoolExecutor(max_workers=3) as executor:
        archives = list(executor.map(get_archive, urls))
    for page, (url, html, error) in enumerate(archives):
        if error:
            failures.append({"url": url, "reason": error})
            continue
        soup = BeautifulSoup(html, "html.parser")
        page_years = []
        for anchor in soup.find_all("a", href=True):
            label = anchor.get("title", "") or anchor.get_text(" ", strip=True)
            if "\u80fd\u6e90\u751f\u4ea7\u60c5\u51b5" not in label and "\u89c4\u6a21\u4ee5\u4e0a\u5de5\u4e1a\u589e\u52a0\u503c" not in label:
                continue
            match = re.search(r"(20\d{2})\u5e74", label)
            if match:
                year = int(match.group(1))
                page_years.append(year)
                if year < args.start_year:
                    continue
            links[urljoin(url, anchor["href"])] = label
        print(f"Archive page {page}: {len(links)} unique candidate releases", flush=True)
        if page_years and max(page_years) < args.start_year:
            break
    rows = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        releases = list(executor.map(get_archive, links))
    for i, (url, html, error) in enumerate(releases, 1):
        label = links[url]
        try:
            if error:
                raise ValueError(error)
            parsed = parse_release(html, url)
            for record in parsed:
                if int(record["period"][:4]) < args.start_year:
                    continue
                existing = rows.get(record["period"])
                if existing and existing["processing_mt"] != record["processing_mt"]:
                    failures.append({"url": url, "reason": "duplicate_value_disagreement", "record": record, "existing": existing})
                    continue
                if not existing:
                    rows[record["period"]] = record
            if not parsed:
                failures.append({"url": url, "reason": "no_monthly_processing_parsed", "title": label})
        except (requests.RequestException, ValueError) as exc:
            failures.append({"url": url, "reason": str(exc)})
        if i % 10 == 0:
            print(f"Parsed {i}/{len(links)} releases; {len(rows)} periods", flush=True)
    # Verified text snapshots are retained when direct downloads are challenged.
    supplemental_counts = {}
    for name in ("nbs_web_history.csv", "nbs_web_supplement.csv"):
        path = out / name
        if not path.exists():
            continue
        count = 0
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for record in csv.DictReader(handle):
                period = record["period"]
                if len(period) == 7:
                    period += "-01"
                record["period"] = period
                if record["processing_mt"]:
                    record["processing_mt"] = float(record["processing_mt"])
                existing = rows.get(period)
                if existing and existing["processing_mt"] != record["processing_mt"]:
                    raise ValueError(f"Conflicting verified monthly values for {period}")
                rows[period] = record
                count += 1
        supplemental_counts[name] = count
    with (out / "nbs_processing.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows[key] for key in sorted(rows))
    (out / "nbs_ingestion_audit.json").write_text(json.dumps({"candidate_releases": len(links), "periods": len(rows), "numeric_periods": sum(r["processing_mt"] != "" for r in rows.values()), "verified_supplemental_counts": supplemental_counts, "failures": failures, "limitations": ["Independent above-designated-size enterprise survey; annual coverage changes", "January-February combined totals retained in flags; monthly values missing", "Published snapshots, not complete vintage histories", "National Data API returned 403; public releases used", "Most direct NBS downloads return JavaScript access challenge; checked-in official web-rendered snapshots and verified transcriptions merged reproducibly", "Earlier sparse 2015 sample is not continuous history; common independent window begins August 2019"]}, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} periods to {out / 'nbs_processing.csv'}", flush=True)


if __name__ == "__main__":
    main()
