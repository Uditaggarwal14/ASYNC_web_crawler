import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
import ssl
import time
import concurrent.futures
import functools

class BaseScraper:
    def __init__(self):
        self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
   }

    async def get_page_content(self, session, url, retries=3):
        for attempt in range(retries):
            try:
                async with session.get(url, headers=self.headers, timeout=500) as response:
                    response.raise_for_status()
                    return await response.text()
            except asyncio.TimeoutError:
                print(f"Timeout error while fetching: {url}")
            except aiohttp.ClientConnectorError as e:
                print(f"Failed to connect to {url}: {e}")
            except aiohttp.ClientSSLError as e:
                print(f"SSL error while fetching {url}: {e}")
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")

class FileHandler:
    def create_directory(self, folder_path):
        if len(folder_path) > 255:
            folder_path = self.shorten_path(folder_path)
        os.makedirs(folder_path, exist_ok=True)

    def shorten_path(self, path):
        hash_object = hashlib.md5(path.encode())
        return path[:200] + "_" + hash_object.hexdigest()

    def save_html(self, folder_path, filename, content):
        self.create_directory(folder_path)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

class WebScraper(BaseScraper, FileHandler):
    def __init__(self, base_url, output_folder, max_depth=2):
        BaseScraper.__init__(self)
        FileHandler.__init__(self)
        self.base_url = base_url
        self.output_folder = output_folder
        self.max_depth = max_depth
        self.visited_links = set()
        self.nav_footer_links = set()

    def extract_links(self, soup, current_url, exclude_nav_footer=False):
        links = set()
        for a in soup.find_all('a', href=True):
            absolute_link = urljoin(current_url, a['href'])
            parsed_link = urlparse(absolute_link)
            if parsed_link.netloc == urlparse(self.base_url).netloc:
                if exclude_nav_footer and absolute_link in self.nav_footer_links:
                    continue
                links.add(absolute_link)
        return links

    def extract_nav_footer_links(self, soup):
        nav_footer_links = set()
        for section in soup.find_all(['nav', 'footer']):
            for a in section.find_all('a', href=True):
                absolute_link = urljoin(self.base_url, a['href'])
                nav_footer_links.add(absolute_link)
        return nav_footer_links

    async def process_links_batch(self, links, parent_folder, depth, session):
        tasks = []
        for link in links:
            tasks.append(self.scrape_recursive(link, depth, parent_folder, session))
        await asyncio.gather(*tasks)

    async def scrape_recursive(self, url, depth=0, parent_folder="", session=None):
        if depth > self.max_depth or url in self.visited_links:
            return

        print(f"Scraping: {url} (Depth: {depth})")
        html = await self.get_page_content(session, url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        parsed_url = urlparse(url)
        page_name = parsed_url.path.strip("/").replace("/", "_") or "home"
        current_folder = os.path.join(parent_folder, page_name)
        full_path = os.path.join(self.output_folder, current_folder)

        self.save_html(full_path, "page.html", html)
        self.visited_links.add(url)

        if depth == 0:
            self.nav_footer_links = self.extract_nav_footer_links(soup)

        links = self.extract_links(soup, url, exclude_nav_footer=(depth > 0))
        print(f"Extracted {len(links)} links from {url}")

        batch_size = 10
        links_list = list(links)
        batches = [links_list[i:i + batch_size] for i in range(0, len(links_list), batch_size)]

        if depth == 0:
            for batch in batches:
                await self.process_links_batch(batch, current_folder, depth + 1, session)
        else:
            batch_tasks = []
            for batch in batches:
                batch_tasks.append(self.process_links_batch(batch, current_folder, depth + 1, session))
            await asyncio.gather(*batch_tasks)

    async def scrape_parallel(self, urls, depth, parent_folder, session):
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            tasks = []
            for url in urls:
                task = loop.run_in_executor(executor, functools.partial(self.scrape_recursive, url, depth, parent_folder, session))
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def run(self):
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(limit=None, ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            await self.scrape_recursive(self.base_url, depth=0, parent_folder="", session=session)

async def main():
    base_url = "https://exam.net/en"
    output_directory = "scraped_pages"
    scraper = WebScraper(base_url, output_directory, max_depth=3)
    
    start_time = time.time()
    await scraper.run()
    end_time = time.time()
    
    print(f"Total time taken: {end_time - start_time} seconds")
    print("hello")

f
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
