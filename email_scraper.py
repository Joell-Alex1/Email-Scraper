from collections import deque
import urllib.parse
import re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
import requests.exceptions as request_exception


def get_base_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}"


def get_page_path(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    return url[:url.rfind('/') + 1] if '/' in parts.path else url


def extract_emails(text: str) -> set[str]:
    email_pattern = r'[a-z0-9\.\-+]+@[a-z0-9\.\-+]+\.[a-z]+'
    return set(re.findall(email_pattern, text, re.I))


def extract_mailto_emails(soup) -> set[str]:
    emails = set()
    for anchor in soup.find_all("a", href=re.compile(r'^mailto:', re.I)):
        href = anchor.get("href", "")
        email = href.split("mailto:")[-1].split("?")[0].strip()
        if email:
            emails.add(email)
    return emails


def normalize_link(link: str, base_url: str, page_path: str):

    if link.startswith("/"):
        return base_url + link

    if not link.startswith("http"):
        return page_path + link

    return link


def filter_relevant_emails(emails, website):

    domain = urlparse(website).netloc.replace("www.", "")

    filtered = set()

    for email in emails:
        if domain in email.split("@")[-1]:
            filtered.add(email)

    return filtered


def _create_session():
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    return session


def _fetch_url(session, url):
    try:
        response = session.get(url, timeout=5)
        response.raise_for_status()
        return url, response.text
    except request_exception.RequestException:
        return url, None


def scrape_website(start_url: str, max_count: int = 20, workers: int = 5):

    queued_urls = {start_url}
    scraped_urls = set()
    collected_emails = set()
    lock = threading.Lock()

    base_domain = urlparse(start_url).netloc
    base_url = get_base_url(start_url)

    priority_paths = [
        "/contact",
        "/contact-us",
        "/about",
        "/about-us",
        "/team",
        "/support",
        "/impressum"
    ]

    # Build initial URL list: start_url first, then priority pages
    urls_to_process = deque([start_url])
    for path in priority_paths:
        priority_url = base_url + path
        if priority_url not in queued_urls:
            urls_to_process.append(priority_url)
            queued_urls.add(priority_url)

    session = _create_session()

    count = 0

    while urls_to_process and count < max_count:

        # Grab a batch of URLs to fetch in parallel
        batch = []
        while urls_to_process and len(batch) < workers:
            url = urls_to_process.popleft()
            if url not in scraped_urls:
                batch.append(url)
                scraped_urls.add(url)

        if not batch:
            break

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(_fetch_url, session, url): url for url in batch}

            for future in as_completed(futures):
                url, html = future.result()
                count += 1
                print(f"[{count}] Processing {url}")

                if html is None:
                    continue

                collected_emails.update(extract_emails(html))

                soup = BeautifulSoup(html, "lxml")
                collected_emails.update(extract_mailto_emails(soup))

                # Stop early if emails found
                if collected_emails:
                    continue

                for anchor in soup.find_all("a"):
                    link = anchor.get("href", "")
                    if link.startswith("mailto:"):
                        continue
                    normalized_link = normalize_link(
                        link,
                        get_base_url(url),
                        get_page_path(url)
                    )
                    parsed = urlparse(normalized_link)
                    if parsed.netloc != base_domain:
                        continue
                    if normalized_link not in queued_urls and normalized_link not in scraped_urls:
                        urls_to_process.append(normalized_link)
                        queued_urls.add(normalized_link)

        # If we found emails after this batch, stop crawling more pages
        if collected_emails:
            break

    session.close()
    return filter_relevant_emails(collected_emails, start_url)


if __name__ == "__main__":

    try:

        user_url = input("[+] Enter url to scan: ")

        emails = scrape_website(user_url)

        if emails:

            print("\n[+] Relevant emails found:\n")

            for email in emails:
                print(email)

        else:

            print("[-] No relevant emails found.")

    except KeyboardInterrupt:

        print("[-] Closing!")