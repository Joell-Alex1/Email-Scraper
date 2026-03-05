from collections import deque
import urllib.parse
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
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


def scrape_website(start_url: str, max_count: int = 20):

    urls_to_process = deque([start_url])
    queued_urls = {start_url}
    scraped_urls = set()
    collected_emails = set()

    count = 0

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

    for path in priority_paths:
        priority_url = base_url + path
        urls_to_process.append(priority_url)
        queued_urls.add(priority_url)

    while urls_to_process:

        url = urls_to_process.popleft()

        if url in scraped_urls:
            continue

        scraped_urls.add(url)

        count += 1
        if count > max_count:
            break

        print(f"[{count}] Processing {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

        except (
            request_exception.RequestException,
            request_exception.MissingSchema,
            request_exception.ConnectionError
        ):
            print("Request error")
            continue

        collected_emails.update(extract_emails(response.text))

        # STOP EARLY IF EMAIL FOUND (huge speed gain)
        if collected_emails:
            break

        soup = BeautifulSoup(response.text, "lxml")

        for anchor in soup.find_all("a"):

            link = anchor.get("href", "")
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