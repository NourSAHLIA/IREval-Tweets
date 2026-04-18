"""
fetch_tweets.py — Scrapes tweets from X using Playwright.
Opens a real browser, logs in via cookies, searches each query, collects tweets.
"""

import time
import re
import random
from playwright.sync_api import sync_playwright
from scripts.utils import get_logger

logger = get_logger(__name__)

X_SEARCH_URL = "https://x.com/search?q={query}&src=typed_query&f=live"


def scrape_tweets_for_query(
    page,
    query_id: str,
    query_text: str,
    tweets_per_query: int,
) -> list[dict]:
    """
    Search a query on X and scrape up to tweets_per_query tweets.
    Returns list of tweet dicts.
    """
    url = X_SEARCH_URL.format(query=query_text.replace(" ", "%20"))
    logger.info(f"[{query_id}] Searching: '{query_text}'")
    page.goto(url, wait_until="domcontentloaded")

    try:
        page.wait_for_selector("article[data-testid='tweet']", timeout=15000)
    except Exception:
        logger.warning(f"[{query_id}] Tweets slow to load, waiting extra 5s...")
        time.sleep(5)

    collected = []
    seen_ids  = set()
    scroll_attempts = 0
    max_scrolls = 60

    while len(collected) < tweets_per_query and scroll_attempts < max_scrolls:
        tweets = page.query_selector_all("article[data-testid='tweet']")

        for tweet in tweets:
            try:
                text_el = tweet.query_selector("div[data-testid='tweetText']")
                if not text_el:
                    continue
                text = text_el.inner_text().strip()
                if not text:
                    continue

                link_el = tweet.query_selector("a[href*='/status/']")
                if not link_el:
                    continue
                href = link_el.get_attribute("href")
                match = re.search(r"/status/(\d+)", href)
                if not match:
                    continue
                doc_id = match.group(1)

                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)

                author_el = tweet.query_selector("div[data-testid='User-Name']")
                author = author_el.inner_text().split("\n")[0] if author_el else "unknown"

                time_el = tweet.query_selector("time")
                created_at = time_el.get_attribute("datetime") if time_el else ""

                collected.append({
                    "doc_id":     doc_id,
                    "query_id":   query_id,
                    "rank":       len(collected) + 1,
                    "text":       text,
                    "created_at": created_at,
                    "author_id":  author,
                })

                if len(collected) >= tweets_per_query:
                    break

            except Exception as e:
                logger.warning(f"[{query_id}] Skipped a tweet: {e}")
                continue

        if len(collected) >= tweets_per_query:
            break

        scroll_distance = random.randint(1000, 2000)
        page.evaluate(f"window.scrollBy(0, {scroll_distance})")
        time.sleep(random.uniform(2, 4))
        scroll_attempts += 1
        logger.info(f"[{query_id}] {len(collected)}/{tweets_per_query} tweets — scroll {scroll_attempts}")

    logger.info(f"[{query_id}] Done. Collected {len(collected)} tweets.")
    return collected


def fetch_all_queries(
    queries: list[dict],
    settings: dict,
    auth_token: str,
    ct0: str,
) -> list[dict]:
    """
    Launch browser with injected cookies, then scrape all queries.
    Returns combined list of all tweet records.
    """
    cfg = settings["collection"]
    all_tweets = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # Inject session cookies so we appear logged in
        context.add_cookies([
            {"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/"},
            {"name": "ct0",        "value": ct0,        "domain": ".x.com", "path": "/"},
        ])

        page = context.new_page()
        page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        for query in queries:
            tweets = scrape_tweets_for_query(
                page=page,
                query_id=query["id"],
                query_text=query["text"],
                tweets_per_query=cfg["tweets_per_query"],
            )
            all_tweets.extend(tweets)
            sleep_s = settings.get("api", {}).get("sleep_between_queries", 3)
            logger.info(f"Pausing {sleep_s}s before next query...")
            time.sleep(sleep_s)

        browser.close()

    logger.info(f"Total tweets collected: {len(all_tweets)}")
    return all_tweets