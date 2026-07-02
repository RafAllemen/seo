"""
SEO Content Gap Analyzer
Senior Python Developer + Technical SEO Expert
Streamlit + asyncio + aiohttp + OpenAI
"""

import asyncio
import json
import re
import ssl
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin

import aiohttp
import nest_asyncio
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Patch event loop for Streamlit compatibility
nest_asyncio.apply()

# Load .env if present
load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SEO Content Gap Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — premium dark design
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0d1321 100%);
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid rgba(99,102,241,0.2);
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stMarkdown {
    color: #ffffff !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(30,41,59,0.8) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

/* Main CTA Button */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(99,102,241,0.6) !important;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.9) 100%);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    backdrop-filter: blur(10px);
}

/* Progress bar color */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    border-radius: 10px !important;
}

/* Status */
.stAlert {
    border-radius: 10px !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
}

/* Tables */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(30,41,59,0.5) !important;
    border-radius: 10px !important;
    color: #818cf8 !important;
    font-weight: 600 !important;
}

/* Header gradient text */
.hero-title {
    background: linear-gradient(135deg, #6366f1 0%, #a78bfa 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}

.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 2rem;
}

.tag {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #818cf8;
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.2rem;
}

.log-box {
    background: rgba(15,23,42,0.9);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 1rem;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #94a3b8;
    max-height: 300px;
    overflow-y: auto;
}

.log-ok   { color: #34d399; }
.log-warn { color: #fbbf24; }
.log-err  { color: #f87171; }
.log-info { color: #60a5fa; }

.result-card {
    background: linear-gradient(135deg, rgba(30,41,59,0.95) 0%, rgba(15,23,42,0.95) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
}

.badge-green  { color: #34d399; font-weight: 700; }
.badge-purple { color: #a78bfa; font-weight: 700; }
.badge-blue   { color: #60a5fa; font-weight: 700; }
.badge-yellow { color: #fbbf24; font-weight: 700; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
BLOG_KEYWORDS = [
    "/blog/", "/porady/", "/artykul/", "/post/", "/news/",
    "/article/", "/insights/", "/guides/", "/poradnik/",
    "/wiedza/", "/aktualnosci/", "/publikacje/"
]
SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
    "/sitemap-posts-post-1.xml",
    "/post-sitemap.xml",
    "/blog-sitemap.xml",
    "/news-sitemap.xml",
    "/sitemap/sitemap.xml",
    "/sitemaps/sitemap.xml",
    "/sitemap1.xml",
    "/sitemap-index.xml",
    "/mapa-strony.xml",
    "/page-sitemap.xml",
    "/article-sitemap.xml",
    "/sitemap-blog.xml",
    "/media/sitemap/sitemap.xml",   # Magento
    "/media/sitemap.xml",           # Magento alt
    "/pub/sitemap.xml",             # Magento pub
]
CHUNK_SIZE = 6000
MAX_CONCURRENT = 8


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def is_blog_url(url: str, sitemap_url: str = "") -> bool:
    """Heuristic: keep content/editorial URLs, discard products/categories."""
    url_lower = url.lower()
    sitemap_lower = sitemap_url.lower()

    # Hard reject list
    reject = ["/category/", "/tag/", "/product/", "/sklep/", "/catalog/",
              "/salony/", "/marki/", "/vin-in", "?p=", "#",
              "/page/", "/feed", ".jpg", ".png", ".pdf",
              "/koszyk", "/checkout", "/konto", "/regulamin",
              "/dostawa", "/reklamacje", "/privacy"]
    if any(r in url_lower for r in reject):
        return False

    # If sitemap itself is blog-related, accept all its links
    if any(k in sitemap_lower for k in ["post", "blog", "article", "news", "porad"]):
        return True

    # URL contains explicit blog keyword
    if any(k in url_lower for k in BLOG_KEYWORDS):
        return True

    return False


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]


def format_log(msg: str, level: str = "info") -> str:
    ts = datetime.now().strftime("%H:%M:%S")
    cls = {"ok": "log-ok", "warn": "log-warn", "err": "log-err", "info": "log-info"}.get(level, "log-info")
    icons = {"ok": "✅", "warn": "⚠️", "err": "❌", "info": "ℹ️"}
    icon = icons.get(level, "ℹ️")
    return f'<span class="{cls}">[{ts}] {icon} {msg}</span>'


# ─────────────────────────────────────────────
# ASYNC: FETCH SITEMAP
# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


async def fetch_text_cloudscraper(url: str) -> str | None:
    """Fallback: use cloudscraper to bypass Cloudflare JS challenges."""
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        resp = await asyncio.to_thread(scraper.get, url, timeout=30)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception:
        return None


async def fetch_text(session, url: str, timeout: int = 30, retries: int = 2) -> str | None:
    """Fetch URL as text with realistic browser headers and retry logic."""
    for attempt in range(retries + 1):
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                ssl=False,
                headers=HEADERS,
                allow_redirects=True,
            ) as resp:
                if resp.status == 200:
                    return await resp.text(errors="ignore")
                elif resp.status in (429, 503) and attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None
        except asyncio.TimeoutError:
            if attempt < retries:
                await asyncio.sleep(1)
                continue
            return None
        except Exception:
            return None
    return None



async def find_sitemap_urls(session, domain: str, log_fn=None) -> list[str]:
    """Try robots.txt, HTML homepage link tag, then fallback paths."""
    sitemaps_found = []

    # 1) Try robots.txt
    robots_txt = await fetch_text(session, f"{domain}/robots.txt")
    if robots_txt:
        sm_from_robots = re.findall(r"(?i)Sitemap:\s*(https?://\S+)", robots_txt)
        if sm_from_robots:
            sitemaps_found.extend(sm_from_robots)
            if log_fn:
                log_fn(f"Znaleziono {len(sm_from_robots)} sitemapę(y) w robots.txt: {domain}", "ok")

    # 2) Parse homepage HTML — look for <link rel="sitemap" href="..."> or sitemap mentions
    if not sitemaps_found:
        homepage_html = await fetch_text(session, domain)
        if homepage_html:
            # <link rel="sitemap" ...>
            link_tags = re.findall(
                r'<link[^>]+rel=["\']sitemap["\'][^>]+href=["\']([^"\']+)["\']',
                homepage_html, re.IGNORECASE
            )
            link_tags += re.findall(
                r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']sitemap["\']',
                homepage_html, re.IGNORECASE
            )
            for href in link_tags:
                full_url = href if href.startswith("http") else domain.rstrip("/") + "/" + href.lstrip("/")
                sitemaps_found.append(full_url)
                if log_fn:
                    log_fn(f"Znaleziono sitemapę w HTML: {full_url}", "ok")

    # 3) Fallback paths
    if not sitemaps_found:
        if log_fn:
            log_fn(f"Próbuję fallback ścieżki dla {domain}...", "info")
        for path in SITEMAP_PATHS:
            url = domain.rstrip("/") + path
            content = await fetch_text(session, url)
            if content and len(content) > 100 and (
                "<url" in content.lower() or
                "<sitemap" in content.lower() or
                "<loc>" in content.lower()
            ):
                sitemaps_found.append(url)
                if log_fn:
                    log_fn(f"Znaleziono sitemapę (fallback): {url}", "ok")
                break

    if not sitemaps_found and log_fn:
        log_fn(f"Nie znaleziono sitemapy dla {domain} — spróbuję scrapować blog bezpośrednio", "warn")

    return sitemaps_found


async def extract_urls_from_sitemap(session, sitemap_url: str, log_fn=None) -> list[str]:
    """Download sitemap, treat as text, extract URLs via regex. Handles sitemap index."""
    content = await fetch_text(session, sitemap_url)
    if not content:
        if log_fn:
            log_fn(f"Nie udało się pobrać sitemapy: {sitemap_url}", "warn")
        return []

    # Check if this is a sitemap index
    all_urls = []
    if "<sitemapindex" in content.lower() or "<sitemap>" in content.lower():
        # Extract nested sitemap URLs
        nested = re.findall(r"<loc>\s*(https?://[^\s<>\"]+\.xml[^<]*)\s*</loc>", content, re.IGNORECASE)
        if log_fn:
            log_fn(f"Sitemap index — znaleziono {len(nested)} pod-sitemapów", "info")
        for ns in nested[:30]:  # increased limit
            sub_urls = await extract_urls_from_sitemap(session, ns.strip(), log_fn)
            all_urls.extend(sub_urls)
        return all_urls

    # Extract all http(s) URLs from content using regex (no XML parser!)
    raw_urls = re.findall(r"https?://[^\s<>\"'\]]+", content)
    # Filter to page URLs (not .xml, .xsl etc)
    page_urls = [u.rstrip("/.,;") for u in raw_urls
                 if not u.lower().endswith((".xml", ".xsl", ".xsd", ".txt", ".jpg", ".png", ".gif", ".pdf"))]
    filtered = [u for u in page_urls if is_blog_url(u, sitemap_url)]
    if log_fn:
        log_fn(f"Sitemap {sitemap_url}: {len(raw_urls)} URL-i → {len(filtered)} po filtrze blogowym", "info")
    return filtered


async def try_scrape_blog_directly(session, domain: str, limit: int, log_fn=None) -> list[str]:
    """Last resort: scrape homepage/blog page looking for article links."""
    blog_candidates = [
        domain + "/blog",
        domain + "/blog/",
        domain + "/porady",
        domain + "/porady/",
        domain + "/artykuly",
        domain + "/wiedza",
        domain,
    ]
    found = []
    for url in blog_candidates:
        html = await fetch_text(session, url)
        if not html:
            continue
        # Find all internal links
        all_links = re.findall(r'href=["\']((https?://[^"\']+|/[^"\']+))["\']', html)
        for href_tuple in all_links:
            href = href_tuple[0]
            if not href.startswith("http"):
                href = domain.rstrip("/") + "/" + href.lstrip("/")
            if is_blog_url(href):
                found.append(href)
        if found:
            if log_fn:
                log_fn(f"Bezpośredni scraping bloga {url}: {len(found)} artykułów", "ok")
            break
    # deduplicate
    seen = set()
    result = []
    for u in found:
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result[:limit]


async def collect_blog_urls(session, domain: str, limit: int, log_fn=None) -> list[str]:
    sitemap_urls = await find_sitemap_urls(session, domain, log_fn)
    if not sitemap_urls:
        if log_fn:
            log_fn(f"Brak sitemapy dla {domain} — próbuję scrapować blog bezpośrednio", "warn")
        direct = await try_scrape_blog_directly(session, domain, limit, log_fn)
        if direct:
            return direct
        if log_fn:
            log_fn(f"Nie udało się znaleźć artykułów dla {domain}", "err")
        return []

    all_blog_urls = []
    for sm_url in sitemap_urls:
        urls = await extract_urls_from_sitemap(session, sm_url, log_fn)
        all_blog_urls.extend(urls)

    # deduplicate
    seen = set()
    deduped = []
    for u in all_blog_urls:
        if u not in seen:
            seen.add(u)
            deduped.append(u)

    result = deduped[:limit]
    if log_fn:
        log_fn(f"Domena {domain}: {len(result)} artykułów do analizy", "ok")
    return result


# ─────────────────────────────────────────────
# ASYNC: SCRAPE CONTENT
# ─────────────────────────────────────────────
async def scrape_article(session, url: str, semaphore: asyncio.Semaphore) -> dict | None:
    async with semaphore:
        # Try aiohttp first, fallback to cloudscraper for Cloudflare-protected sites
        html = await fetch_text(session, url, timeout=20)
        if not html:
            html = await fetch_text_cloudscraper(url)
        if not html:
            return None
        try:
            soup = BeautifulSoup(html, "lxml")

            # Remove noise
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "noscript", "iframe", "form", "button"]):
                tag.decompose()

            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else ""

            meta_desc = ""
            meta = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
            if meta:
                meta_desc = meta.get("content", "")

            h1 = soup.find("h1")
            h1_text = h1.get_text(strip=True) if h1 else ""

            h2_tags = soup.find_all("h2")
            h2_texts = [h.get_text(strip=True) for h in h2_tags[:15]]

            body = soup.find("body")
            body_text = body.get_text(separator=" ", strip=True) if body else soup.get_text(separator=" ", strip=True)
            # Collapse whitespace
            body_text = re.sub(r"\s+", " ", body_text).strip()

            return {
                "url": url,
                "title": title_text,
                "meta_description": meta_desc,
                "h1": h1_text,
                "h2s": h2_texts,
                "content_chunks": chunk_text(body_text),
                "word_count": len(body_text.split()),
            }
        except Exception as e:
            return {"url": url, "error": str(e)}


async def scrape_all(urls: list[str], log_fn=None) -> list[dict]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    connector = aiohttp.TCPConnector(ssl=False, limit=20)
    results = []
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [scrape_article(session, url, semaphore) for url in urls]
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            if result:
                results.append(result)
                if log_fn and len(results) % 3 == 0:
                    log_fn(f"Pobrano {len(results)}/{len(urls)} artykułów...", "info")
            else:
                if log_fn:
                    log_fn(f"Pominięto URL #{i+1} (brak odpowiedzi / błąd HTTP)", "warn")
    if log_fn:
        log_fn(f"Scrapowanie zakończone: {len(results)}/{len(urls)} pobranych", "ok" if results else "warn")
    return results


# ─────────────────────────────────────────────
# AI ANALYSIS
# ─────────────────────────────────────────────
async def analyze_article_ai(client, article: dict, topic: str, model_name: str = "gpt-4o-mini") -> dict:
    """Send article chunk to OpenAI/DeepSeek to extract main topic, search intent, and subtopics."""
    if "error" in article:
        return {"url": article["url"], "error": article["error"], "subtopics": [], "intent": "unknown"}

    # Use first chunk as representative content
    content_sample = article["content_chunks"][0] if article["content_chunks"] else ""
    prompt = f"""Analyze this article for the topic: "{topic}".

Title: {article.get('title', '')}
H1: {article.get('h1', '')}
H2s: {', '.join(article.get('h2s', []))}
Content excerpt: {content_sample[:3000]}

Return ONLY valid JSON with this structure:
{{
  "url": "<same url>",
  "main_topic": "<main topic in 5-10 words>",
  "subtopics": ["subtopic 1", "subtopic 2", ...],
  "search_intent": "informacyjna|transakcyjna|nawigacyjna|komercyjna",
  "content_depth": "płytka|średnia|głęboka",
  "key_phrases": ["phrase1", "phrase2", "phrase3"],
  "missing_aspects": ["co brakuje lub można poprawić"]
}}

CRITICAL INSTRUCTION: All generated text values must be in Polish language!"""

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=800,
        )
        data = json.loads(response.choices[0].message.content)
        data["url"] = article["url"]
        data["title"] = article.get("title", "")
        data["word_count"] = article.get("word_count", 0)
        return data
    except Exception as e:
        return {
            "url": article.get("url", ""),
            "title": article.get("title", ""),
            "error": str(e),
            "subtopics": [],
            "search_intent": "unknown",
        }


async def generate_gap_report(client, my_analysis: list[dict], competitor_analysis: list[dict], topic: str, model_name: str = "gpt-4o") -> dict:
    """Send all data to OpenAI/DeepSeek for final Content Gap report."""

    my_summary = json.dumps([{
        "url": a.get("url"), "main_topic": a.get("main_topic"),
        "subtopics": a.get("subtopics", []), "key_phrases": a.get("key_phrases", [])
    } for a in my_analysis[:30]], ensure_ascii=False)

    if not competitor_analysis:
        comp_summary = "[]"
        gap_context = "I don't have competitor data. You MUST use your own internal knowledge of the internet and this niche to simulate the market, find missing topics, and propose what MY website should cover to get maximum SEO traffic."
    else:
        comp_summary = json.dumps([{
            "url": a.get("url"), "main_topic": a.get("main_topic"),
            "subtopics": a.get("subtopics", []), "key_phrases": a.get("key_phrases", [])
        } for a in competitor_analysis[:60]], ensure_ascii=False)
        gap_context = "Analyze the content gap between MY website and COMPETITORS provided."

    topic_instruction = (
        "First, identify the main topic/niche of this website based on the content provided."
        if topic == "auto" else f'The main topic/niche is: "{topic}".'
    )
    prompt = f"""You are an expert SEO Content Strategist. {gap_context} {topic_instruction}

MY WEBSITE CONTENT:
{my_summary[:4000]}

COMPETITOR CONTENT (if empty, use global knowledge):
{comp_summary[:6000]}

Provide a comprehensive Content Gap Analysis. Return ONLY valid JSON:
{{
  "executive_summary": "<2-3 sentence summary of the gap>",
  "my_strengths": ["topic I cover well 1", "topic 2"],
  "critical_gaps": [
    {{"topic": "gap topic", "why_important": "reason", "competition_coverage": "how many competitors cover it"}}
  ],
  "content_ideas": [
    {{
      "title": "Proposed article title",
      "target_keyword": "main keyword",
      "search_intent": "informacyjna|transakcyjna|komercyjna",
      "priority": "wysoki|średni|niski",
      "brief": "2-3 zdaniowy opis co artykuł powinien zawierać",
      "competitors_covering": "brak|mała|duża"
    }}
  ],
  "quick_wins": ["Quick win 1 - what to improve immediately", "Quick win 2"],
  "topic_clusters": [
    {{"cluster_name": "cluster", "covered_topics": ["t1"], "missing_topics": ["m1"]}}
  ],
  "recommendations": ["Strategic recommendation 1", "recommendation 2"]
}}

Generate exactly 20 content_ideas. Be specific, actionable, and data-driven.
CRITICAL INSTRUCTION: You must write the ENTIRE report (all text fields, summaries, ideas, titles, briefs) in Polish language!"""

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=4000,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        import traceback
        err_msg = str(e)
        return {
            "error": err_msg,
            "executive_summary": f"Błąd generowania raportu: {err_msg}",
            "content_ideas": []
        }


# ─────────────────────────────────────────────
# GENERATING DETAILED BRIEF
# ─────────────────────────────────────────────
async def generate_detailed_brief(client, idea: dict, my_blog_urls: list[str], model_name: str = "gpt-4o") -> str:
    links_text = "\n".join(my_blog_urls[:100])
    prompt = f"""Twoim zadaniem jest opracowanie struktury i szczegółowego konspektu dla nowego artykułu SEO na podstawie najlepszych praktyk.

Główny temat: {idea.get('title')}
Główne słowo kluczowe: {idea.get('target_keyword')}
Intencja: {idea.get('search_intent')}
Opis: {idea.get('brief')}

Przeanalizuj temat i wykonaj następujące kroki:

1. Określ główny temat tekstu (do 60 znaków, próbuj zbliżyć się do max długości).
2. Utwórz tabelę zawierającą najważniejsze informacje, które muszą znaleźć się w artykule (kolumny: "Informacja" i "Szczegóły").
3. Utwórz tabelę z najważniejszymi słowami kluczowymi i podmiotami do użycia w tekście (kolumny: "Słowa kluczowe" i "Podmioty").
4. Zaproponuj plan nagłówków (H1, H2, H3), który w pełni wyczerpie temat.
5. Zaproponuj konspekt artykułu, który w pełni pokrywa plan nagłówków oraz najważniejsze informacje i słowa kluczowe.
6. Zasugeruj, jak strukturyzować artykuł, aby spełniał wymagania przeglądów AI (AI Overviews), bazując na powyższych informacjach. Zasugeruj stworzenie tabeli porównującej, jeśli temat jest do tego odpowiedni.
7. Dodaj szacowanie trudności (Keyword Difficulty) oraz potencjał ruchu dla tego tematu.
8. Zaproponuj automatyczne linkowanie wewnętrzne.
ZASADY LINKOWANIA (BARDZO WAŻNE):
- Przejrzyj dokładnie poniższą listę "DOSTĘPNE LINKI WEWNĘTRZNE".
- Jeśli (i TYLKO jeśli) na liście znajduje się artykuł, który IDEALNIE pasuje tematycznie do akapitu, wstaw do niego pełny link.
- JEŚLI ŻADEN LINK Z LISTY NIE PASUJE IDEALNIE DO TEMATU (np. lista zawiera odzież roboczą, a artykuł jest o dywanach), BEZWZGLĘDNIE ZABRANIA SIĘ podawania jakichkolwiek linków z listy. NIE ZMYŚLAJ LINKÓW. W takiej sytuacji użyj wyłącznie znaczników (placeholderów), np. `[Wstaw tu link do kategorii: dywany]` lub `[Wstaw tu link do produktu: kask roboczy]`.

DOSTĘPNE LINKI WEWNĘTRZNE (Wyciągnięte z sitemapy):
{links_text}

Na końcu swojej odpowiedzi umieść następujące sekcje w podanej kolejności, używając odpowiednich tagów (zastosuj formatowanie Markdown):

### Główny temat:
[Tutaj wpisz główny temat]

### Najważniejsze informacje:
[Tutaj wstaw tabelę z najważniejszymi informacjami]

### Najważniejsze słowa kluczowe:
[Tutaj wstaw tabelę z najważniejszymi słowami kluczowymi i podmiotami]

### Szacowanie trudności i potencjał ruchu:
[Ocena trudności i potencjału]

### Plan nagłówków:
[Tutaj wstaw plan nagłówków]

### Konspekt artykułu:
[Tutaj wpisz proponowany konspekt artykułu]

### Sugestie dotyczące struktury artykułu (w tym AI Overviews):
[Tutaj wpisz sugestie]

### Zalecane linkowanie wewnętrzne:
[Tutaj wstaw wybrane linki z listy i propozycje ich użycia]

Twoja końcowa odpowiedź powinna zawierać tylko te sekcje, bez dodatkowych komentarzy czy wyjaśnień.
Cała odpowiedź musi być w języku polskim.
"""
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Błąd podczas generowania konspektu: {str(e)}"


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
async def run_analysis_pipeline(
    my_url: str,
    competitor_urls: list[str],
    topic: str,
    limit: int,
    ai_provider: str,
    api_key: str,
    progress_bar,
    log_container,
    status_text,
):
    import aiohttp
    from openai import OpenAI

    logs = []

    def log(msg: str, level: str = "info"):
        entry = format_log(msg, level)
        logs.append(entry)
        log_html = "<br>".join(logs[-40:])  # show last 40 lines
        log_container.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

    if "DeepSeek" in ai_provider:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        model_mini = "deepseek-chat"
        model_pro = "deepseek-chat"
        log("Silnik AI: DeepSeek-Chat", "info")
    else:
        client = OpenAI(api_key=api_key)
        model_mini = "gpt-4o-mini"
        model_pro = "gpt-4o"
        log("Silnik AI: OpenAI (GPT-4o)", "info")

    all_domains = [my_url] + competitor_urls
    total_steps = len(all_domains) * 2 + 3  # sitemap + scrape per domain + AI steps
    step = 0

    def advance(msg=""):
        nonlocal step
        step += 1
        progress_bar.progress(min(step / total_steps, 0.99))
        if msg:
            status_text.markdown(f"**🔄 {msg}**")

    # ── STEP 1: Collect URLs ──
    log("=== KROK 1: Zbieranie URL-ów z Sitemapek ===", "info")
    connector = aiohttp.TCPConnector(ssl=False, limit=10)

    my_blog_urls = []
    competitor_blog_urls = {}

    async with aiohttp.ClientSession(connector=connector) as session:
        my_domain = extract_domain(my_url)
        advance(f"Szukam sitemapy: {my_domain}")
        log(f"Przetwarzam moją stronę: {my_domain}", "info")
        my_blog_urls = await collect_blog_urls(session, my_domain, limit, log)
        advance()

        for comp_url in competitor_urls:
            comp_domain = extract_domain(comp_url)
            advance(f"Szukam sitemapy: {comp_domain}")
            log(f"Przetwarzam konkurenta: {comp_domain}", "info")
            comp_urls = await collect_blog_urls(session, comp_domain, limit, log)
            competitor_blog_urls[comp_domain] = comp_urls
            advance()

    all_comp_urls = []
    for urls in competitor_blog_urls.values():
        all_comp_urls.extend(urls)

    log(f"Łącznie: {len(my_blog_urls)} moich artykułów, {len(all_comp_urls)} artykułów konkurencji", "ok")

    # ── STEP 2: Scrape Content ──
    log("=== KROK 2: Scrapowanie Treści ===", "info")
    advance("Pobieranie treści artykułów...")

    log(f"Scrapuję {len(my_blog_urls)} artykułów mojej strony...", "info")
    my_articles = await scrape_all(my_blog_urls, log)
    log(f"Pobrano {len(my_articles)} artykułów (moja strona)", "ok")

    log(f"Scrapuję {len(all_comp_urls)} artykułów konkurencji...", "info")
    comp_articles = await scrape_all(all_comp_urls, log)
    log(f"Pobrano {len(comp_articles)} artykułów (konkurencja)", "ok")

    advance()

    # ── STEP 3: AI Analysis per article ──
    log(f"=== KROK 3: Analiza AI artykułów ({model_mini}) ===", "info")
    advance("Analiza AI artykułów...")

    async def analyze_batch(articles, label):
        results = []
        for i, art in enumerate(articles):
            # Tu używamy opcjonalnie deepseek
            r = await analyze_article_ai(client, art, topic, model_mini)
            results.append(r)
            if (i + 1) % 3 == 0 or i == len(articles) - 1:
                log(f"AI: przeanalizowano {i+1}/{len(articles)} artykułów ({label})", "info")
            await asyncio.sleep(0.1)  # gentle rate limiting
        return results

    my_analysis = await analyze_batch(my_articles, "moja strona")
    comp_analysis = await analyze_batch(comp_articles, "konkurencja")

    advance()

    # ── STEP 4: Final Gap Report ──
    log(f"=== KROK 4: Generowanie Raportu Content Gap ({model_pro}) ===", "info")
    advance("Generuję finalny raport SEO Content Gap...")

    gap_report = await generate_gap_report(client, my_analysis, comp_analysis, topic, model_pro)

    advance()
    progress_bar.progress(1.0)
    log("=== ANALIZA ZAKOŃCZONA! ===", "ok")

    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "topic": topic,
            "my_url": my_url,
            "competitor_urls": competitor_urls,
            "my_articles_count": len(my_articles),
            "competitor_articles_count": len(comp_articles),
            "limit_per_domain": limit,
        },
        "my_blog_urls": my_blog_urls,
        "competitor_blog_urls": competitor_blog_urls,
        "my_article_analysis": my_analysis,
        "competitor_article_analysis": comp_analysis,
        "gap_report": gap_report,
    }


# ─────────────────────────────────────────────
# UI RENDERING
# ─────────────────────────────────────────────
def render_gap_report(report_data: dict):
    gap = report_data.get("gap_report", {})
    meta = report_data.get("metadata", {})

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <h2 style="color:#818cf8; font-size:1.8rem; font-weight:700;">📊 Wyniki Analizy SEO Content Gap</h2>
    </div>
    """, unsafe_allow_html=True)

    # Metadata row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Moje artykuły", meta.get("my_articles_count", 0))
    with col2:
        st.metric("🏆 Artykuły konkurencji", meta.get("competitor_articles_count", 0))
    with col3:
        ideas = gap.get("content_ideas", [])
        st.metric("💡 Pomysły na artykuły", len(ideas))
    with col4:
        gaps = gap.get("critical_gaps", [])
        st.metric("🔴 Krytyczne luki", len(gaps))

    st.markdown("---")

    # Executive Summary
    if gap.get("executive_summary"):
        st.markdown(f"""
        <div class="result-card">
            <h3 style="color:#a78bfa; margin-bottom:0.8rem;">🎯 Podsumowanie Wykonawcze</h3>
            <p style="color:#e2e8f0; line-height:1.7; font-size:1.05rem;">{gap['executive_summary']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Two column layout
    col_left, col_right = st.columns(2)

    with col_left:
        # My Strengths
        if gap.get("my_strengths"):
            st.markdown("### ✅ Moje Mocne Strony")
            for s in gap["my_strengths"]:
                st.markdown(f'<div class="tag">✅ {s}</div>', unsafe_allow_html=True)
            st.markdown("")

        # Quick Wins
        if gap.get("quick_wins"):
            st.markdown("### ⚡ Szybkie Poprawki (Najłatwiejsze zadania)")
            for i, qw in enumerate(gap["quick_wins"], 1):
                st.markdown(f"""
                <div style="background:rgba(16,185,129,0.1); border-left:3px solid #10b981;
                     border-radius:6px; padding:0.6rem 1rem; margin:0.4rem 0; color:#e2e8f0;">
                    <b style="color:#34d399;">#{i}</b> {qw}
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        # Critical Gaps
        if gap.get("critical_gaps"):
            st.markdown("### 🔴 Krytyczne Luki Tematyczne")
            for g in gap["critical_gaps"][:8]:
                st.markdown(f"""
                <div style="background:rgba(239,68,68,0.08); border-left:3px solid #ef4444;
                     border-radius:6px; padding:0.6rem 1rem; margin:0.4rem 0; color:#e2e8f0;">
                    <b style="color:#f87171;">{g.get('topic','')}</b><br>
                    <span style="font-size:0.85rem; color:#94a3b8;">{g.get('why_important','')}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Content Ideas Table
    st.markdown("### 💡 Pomysły na Nowe Artykuły")
    ideas = gap.get("content_ideas", [])
    if not ideas:
        st.warning("⚠️ Brak pomysłów na artykuły — AI nie wygenerował wyników. Sprawdź czy zebrano wystarczającą liczbę artykułów (ustaw wyższy limit).")
    else:
        priority_color = {"wysoki": "🔴", "średni": "🟡", "niski": "🟢"}
        intent_color = {"informacyjna": "📖", "transakcyjna": "🛒", "komercyjna": "💼", "nawigacyjna": "🧭"}
        st.markdown(f"<p style='color:#94a3b8;'>Wygenerowano <b style='color:#818cf8;'>{len(ideas)}</b> pomysłów na artykuły</p>", unsafe_allow_html=True)
        for i, idea in enumerate(ideas, 1):
            if not isinstance(idea, dict):
                continue
            pri_raw = str(idea.get("priority", "średni")).lower().strip()
            intent_raw = str(idea.get("search_intent", "informacyjna")).lower().strip()
            
            # Wymuszone tłumaczenie na wypadek błędu AI
            pri = {"high": "wysoki", "medium": "średni", "low": "niski"}.get(pri_raw, pri_raw)
            intent = {"informational": "informacyjna", "transactional": "transakcyjna", "commercial": "komercyjna", "navigational": "nawigacyjna"}.get(intent_raw, intent_raw)
            
            title = idea.get("title") or idea.get("temat") or f"Pomysł #{i}"
            keyword = idea.get("target_keyword") or idea.get("keyword") or ""
            brief = idea.get("brief") or idea.get("opis") or ""
            
            comp_raw = str(idea.get("competitors_covering", "—")).lower().strip()
            comp_cov = {"none": "brak", "few": "mała", "many": "duża"}.get(comp_raw, comp_raw)
            
            with st.expander(f"{priority_color.get(pri,'🟡')} #{i}: {title}", expanded=(i <= 5)):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**🔑 Keyword:** `{keyword}`")
                with c2:
                    st.markdown(f"**{intent_color.get(intent,'📖')} Intencja:** {intent}")
                with c3:
                    st.markdown(f"**🏆 Konkurencja:** {comp_cov}")
                if brief:
                    st.markdown(f"**📝 Brief:** {brief}")
                
                # Przycisk generowania konspektu
                btn_key = f"btn_brief_{i}_{title}"
                if st.button("✨ Wygeneruj Pełny Konspekt SEO", key=btn_key):
                    with st.spinner("Generuję potężny konspekt (to może potrwać kilkanaście sekund)..."):
                        from openai import OpenAI
                        import os
                        api_key = st.session_state.get("api_key_input", "")
                        ai_prov = st.session_state.get("ai_provider_input", "OpenAI")
                        if not api_key:
                            st.error("Brak klucza API. Podaj klucz w panelu bocznym.")
                        else:
                            if "DeepSeek" in ai_prov:
                                client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                                model_name = "deepseek-chat"
                            else:
                                client = OpenAI(api_key=api_key)
                                model_name = "gpt-4o"
                            
                            my_blog_urls = report_data.get("my_blog_urls", [])
                            detailed_brief = asyncio.run(generate_detailed_brief(client, idea, my_blog_urls, model_name))
                            st.markdown(f"### 📋 Wygenerowany Konspekt\n{detailed_brief}")
                            st.download_button(
                                label="⬇️ Pobierz Konspekt jako Markdown",
                                data=detailed_brief.encode("utf-8"),
                                file_name=f"konspekt_{i}.md",
                                mime="text/markdown",
                                key=f"dl_brief_{i}"
                            )

    st.markdown("---")

    # Topic Clusters
    if gap.get("topic_clusters"):
        st.markdown("### 🗂️ Klastry Tematyczne")
        cols = st.columns(min(len(gap["topic_clusters"]), 3))
        for i, cluster in enumerate(gap["topic_clusters"]):
            with cols[i % len(cols)]:
                covered_html = "".join(f'<div class="tag">✅ {t}</div>' for t in cluster.get('covered_topics',[])[:4])
                missing_html = "".join(f'<div class="tag" style="border-color:rgba(239,68,68,0.4);color:#f87171;">❌ {t}</div>' for t in cluster.get('missing_topics',[])[:4])
                
                html_card = f"""
<div class="metric-card">
<h4 style="color:#818cf8; margin-bottom:0.8rem;">{cluster.get('cluster_name','')}</h4>
<p style="color:#34d399; font-size:0.85rem; margin-bottom:0.4rem;"><b>✅ Pokryte:</b></p>
{covered_html}
<p style="color:#f87171; font-size:0.85rem; margin: 0.6rem 0 0.4rem;"><b>❌ Brakujące:</b></p>
{missing_html}
</div>
"""
                st.markdown(html_card.strip(), unsafe_allow_html=True)

    st.markdown("---")

    # Recommendations
    if gap.get("recommendations"):
        st.markdown("### 🎯 Rekomendacje Strategiczne")
        for i, rec in enumerate(gap["recommendations"], 1):
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.08); border-left:3px solid #6366f1;
                 border-radius:6px; padding:0.8rem 1rem; margin:0.5rem 0; color:#e2e8f0;">
                <b style="color:#818cf8;">Rekomendacja #{i}:</b> {rec}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────
def generate_pdf(results: dict) -> bytes:
    from fpdf import FPDF
    import os

    gap = results.get("gap_report", {})
    meta = results.get("metadata", {})

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font_reg = "C:/Windows/Fonts/arial.ttf"
    font_bold = "C:/Windows/Fonts/arialbd.ttf"
    has_arial = os.path.exists(font_reg) and os.path.exists(font_bold)
    
    if has_arial:
        pdf.add_font("Arial_Custom", "", font_reg)
        pdf.add_font("Arial_Custom", "B", font_bold)
        font_name = "Arial_Custom"
    else:
        font_name = "Helvetica"

    # ── Fonts (built-in, Latin)
    pdf.set_font(font_name, "B", 22)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 12, "SEO Content Gap Report", ln=True, align="C")
    pdf.set_font(font_name, "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Wygenerowano: {meta.get('generated_at', '')[:19]}  |  Moja strona: {meta.get('my_url', '')}", ln=True, align="C")
    pdf.ln(4)

    def section_title(txt):
        pdf.set_font(font_name, "B", 13)
        pdf.set_text_color(99, 102, 241)
        pdf.set_fill_color(240, 240, 255)
        pdf.cell(0, 8, txt, ln=True, fill=True)
        pdf.set_text_color(30, 30, 30)
        pdf.ln(2)

    def break_long_words(text: str, max_len: int = 50) -> str:
        words = text.split(" ")
        new_words = []
        for w in words:
            if len(w) > max_len:
                # split word into chunks of max_len
                chunks = [w[i:i+max_len] for i in range(0, len(w), max_len)]
                new_words.append(" ".join(chunks))
            else:
                new_words.append(w)
        return " ".join(new_words)

    def safe_multi_cell(txt, h=6):
        pdf.set_x(pdf.l_margin)
        try:
            pdf.multi_cell(0, h, break_long_words(str(txt)))
        except Exception:
            pass

    def body(txt, bold=False):
        pdf.set_font(font_name, "B" if bold else "", 10)
        pdf.set_text_color(30, 30, 30)
        safe_multi_cell(txt)

    def bullet(txt, color=(60, 60, 60)):
        pdf.set_font(font_name, "", 10)
        pdf.set_text_color(*color)
        safe_multi_cell(f"  - {txt}")

    # ── Metadata
    section_title("Parametry analizy")
    body(f"Artykuly mojej strony: {meta.get('my_articles_count', 0)}    Artykuly konkurencji: {meta.get('competitor_articles_count', 0)}")
    safe_my_url = break_long_words(str(meta.get('my_url', '')))
    safe_comp_urls = break_long_words(', '.join(meta.get('competitor_urls', [])))
    body(f"Moja strona: {safe_my_url}")
    if safe_comp_urls:
        body(f"Konkurenci: {safe_comp_urls}")
    pdf.ln(4)

    # ── Executive Summary
    if gap.get("executive_summary"):
        section_title("Podsumowanie")
        body(gap["executive_summary"])
        pdf.ln(4)

    # ── Strengths
    if gap.get("my_strengths"):
        section_title("Mocne strony mojej strony")
        for s in gap["my_strengths"]:
            bullet(s, (34, 197, 100))
        pdf.ln(4)

    # ── Critical Gaps
    if gap.get("critical_gaps"):
        section_title("Krytyczne luki tematyczne")
        for g in gap["critical_gaps"]:
            topic_txt = g.get("topic", "")
            why = g.get("why_important", "")
            bullet(f"{topic_txt}: {why}", (220, 50, 50))
        pdf.ln(4)

    # ── Quick Wins
    if gap.get("quick_wins"):
        section_title("Szybkie poprawki (Najlatwiejsze zadania)")
        for qw in gap["quick_wins"]:
            bullet(qw, (16, 185, 130))
        pdf.ln(4)

    # ── Content Ideas
    ideas = gap.get("content_ideas", [])
    if ideas:
        section_title(f"Pomysly na artykuly ({len(ideas)})")
        for i, idea in enumerate(ideas, 1):
            if not isinstance(idea, dict):
                continue
            title = idea.get("title") or idea.get("temat") or f"Pomysl #{i}"
            keyword = idea.get("target_keyword") or idea.get("keyword") or ""
            
            pri_raw = str(idea.get("priority", "średni")).lower().strip()
            intent_raw = str(idea.get("search_intent", "informacyjna")).lower().strip()
            
            priority = {"high": "wysoki", "medium": "średni", "low": "niski"}.get(pri_raw, pri_raw)
            intent = {"informational": "informacyjna", "transactional": "transakcyjna", "commercial": "komercyjna", "navigational": "nawigacyjna"}.get(intent_raw, intent_raw)
            
            brief = idea.get("brief") or idea.get("opis") or ""
            
            pdf.set_font(font_name, "B", 10)
            pdf.set_text_color(80, 80, 200)
            safe_title = break_long_words(f"{i}. {title}")
            try:
                pdf.multi_cell(0, 6, str(safe_title))
            except Exception:
                pass
            pdf.set_font(font_name, "", 9)
            pdf.set_text_color(80, 80, 80)
            meta_line = break_long_words(f"   Keyword: {keyword}  |  Intencja: {intent}  |  Priorytet: {priority}")
            try:
                pdf.multi_cell(0, 5, str(meta_line))
            except Exception:
                pass
            if brief:
                pdf.set_text_color(50, 50, 50)
                brief_safe = break_long_words(f"   {brief}")
                try:
                    pdf.multi_cell(0, 5, str(brief_safe))
                except Exception:
                    pass
            pdf.ln(2)
        pdf.ln(4)

    # ── Topic Clusters
    if gap.get("topic_clusters"):
        section_title("Klastry tematyczne")
        for cluster in gap["topic_clusters"]:
            cluster_name = cluster.get("cluster_name", "")
            pdf.set_font(font_name, "B", 11)
            pdf.set_text_color(80, 80, 200)
            safe_multi_cell(cluster_name)
            
            cov = cluster.get('covered_topics', [])
            mis = cluster.get('missing_topics', [])
            
            if cov:
                pdf.set_font(font_name, "B", 9)
                pdf.set_text_color(34, 197, 100)
                safe_multi_cell("   Pokryte: " + ", ".join(cov), h=5)
            
            if mis:
                pdf.set_font(font_name, "B", 9)
                pdf.set_text_color(220, 50, 50)
                safe_multi_cell("   Brakujace: " + ", ".join(mis), h=5)
            pdf.ln(2)
        pdf.ln(4)

    # ── Recommendations
    if gap.get("recommendations"):
        section_title("Rekomendacje strategiczne")
        for rec in gap["recommendations"]:
            bullet(rec)
        pdf.ln(4)

    return pdf.output()


# ─────────────────────────────────────────────
# SIDEBAR UI
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:1rem 0 0.5rem;">
            <div style="font-size:2.5rem;">🔍</div>
            <h2 style="color:#818cf8; font-size:1.2rem; font-weight:700; margin:0.3rem 0;">
                SEO Content Gap
            </h2>
            <p style="color:#64748b; font-size:0.8rem;">Analiza luk w treści</p>
        </div>
        <hr style="border-color:rgba(99,102,241,0.2);">
        """, unsafe_allow_html=True)

        st.markdown("#### 🌐 Moja strona")
        my_url = st.text_input(
            "URL strony",
            placeholder="https://moja-strona.pl",
            label_visibility="collapsed",
            key="my_url"
        )

        has_competitor = st.checkbox("Zbadaj też konkurencję (Content Gap)", value=True, help="Jeśli odznaczysz, AI znajdzie luki na podstawie własnej bazy wiedzy o internecie.")
        
        if has_competitor:
            st.markdown("#### 🏆 Konkurenci")
            competitors_raw = st.text_area(
                "URL-e konkurentów (każdy w nowej linii)",
                placeholder="https://konkurent1.pl\nhttps://konkurent2.pl\nhttps://konkurent3.pl",
                height=130,
                label_visibility="collapsed",
                key="competitors"
            )
        else:
            competitors_raw = ""

        st.markdown("#### 📄 Limit artykułów / domenę")
        limit = st.slider(
            "Limit (ostrożnie przy > 100 ze względu na koszty API)", 
            min_value=1, 
            max_value=500, 
            value=20, 
            key="limit"
        )

        # st.markdown("#### 🎯 Główny temat (opcjonalnie)")
        # topic = st.text_input(
        #     "Nisza/Temat strony",
        #     placeholder="np. Sklep z odzieżą BHP, Fotografia ślubna...",
        #     help="Jeśli zostawisz puste, AI samo zgadnie temat na podstawie artykułów."
        # )
        topic = "auto"
        
        st.markdown("#### 🧠 Silnik AI")
        ai_provider = st.selectbox(
            "Wybierz model analizy",
            ["OpenAI (GPT-4o)", "DeepSeek (Chat)"],
            index=0,
            help="DeepSeek jest znacznie tańszy przy przetwarzaniu dużych sitemapek.",
            key="ai_provider_input"
        )

        st.markdown(f"#### 🔑 Klucz API ({'OpenAI' if 'OpenAI' in ai_provider else 'DeepSeek'})")
        env_key_openai = os.getenv("OPENAI_API_KEY", "")
        env_key_deepseek = os.getenv("DEEPSEEK_API_KEY", "")
        
        if "OpenAI" in ai_provider:
            api_key_input = st.text_input(
                "OpenAI API Key",
                value=env_key_openai,
                type="password",
                placeholder="sk-proj-...",
                label_visibility="collapsed",
                key="api_key_input"
            )
        else:
            api_key_input = st.text_input(
                "DeepSeek API Key",
                value=env_key_deepseek,
                type="password",
                placeholder="sk-...",
                label_visibility="collapsed",
                key="api_key_input"
            )

        if api_key_input:
            st.caption("✅ Klucz gotowy do użycia")
        else:
            st.caption(f"Wpisz klucz lub dodaj go do pliku .env")

        st.markdown("---")

        # Info box
        st.markdown("""
        <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
             border-radius:10px; padding:0.8rem; font-size:0.8rem; color:#94a3b8;">
            <b style="color:#818cf8;">ℹ️ Jak to działa?</b><br><br>
            1️⃣ Pobiera sitemapy (regex, bez XML)<br>
            2️⃣ Filtruje URL-e blogowe<br>
            3️⃣ Scrapuje treści asynchronicznie<br>
            4️⃣ Analizuje AI<br>
            5️⃣ Generuje raport PDF
        </div>
        """, unsafe_allow_html=True)

        return my_url, competitors_raw, limit, topic, ai_provider, api_key_input


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # HERO HEADER
    st.markdown("""
    <div style="padding: 2rem 0 1rem;">
        <p class="hero-title">🔍 SEO Content Gap Analyzer</p>
        <p class="hero-subtitle">
            Odkryj luki tematyczne między Twoją stroną a konkurencją.
            Generuj gotowe pomysły na artykuły z pomocą AI.
        </p>
        <span class="tag">🤖 GPT-4o</span>
        <span class="tag">⚡ Async</span>
        <span class="tag">📊 Content Gap</span>
        <span class="tag">🕷️ Smart Scraping</span>
        <span class="tag">🛡️ SSL Safe</span>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar inputs
    my_url, competitors_raw, limit, topic, ai_provider, api_key = render_sidebar()

    # Session state for results
    if "results" not in st.session_state:
        st.session_state.results = None

    # ── RUN BUTTON ──
    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        run_btn = st.button("🚀 Uruchom Analizę SEO Gap", key="run_btn")

    with col_info:
        if my_url and api_key:
            comp_list = [u.strip() for u in competitors_raw.strip().splitlines() if u.strip()]
            status_comp = f"{len(comp_list)} konkurentów" if comp_list else "Tryb Solo (bez konkurencji)"
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3);
                 border-radius:10px; padding:0.6rem 1rem; color:#34d399; font-size:0.9rem;">
                ✅ Gotowy do startu: <b>{status_comp}</b>, limit <b>{limit}</b> art./domenę &nbsp;|&nbsp; Temat: auto-detect AI
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(251,191,36,0.1); border:1px solid rgba(251,191,36,0.3);
                 border-radius:10px; padding:0.6rem 1rem; color:#fbbf24; font-size:0.9rem;">
                ⚠️ Uzupełnij pola: URL swojej strony i klucz API
            </div>
            """, unsafe_allow_html=True)

    # ── VALIDATION & EXECUTION ──
    if run_btn:
        errors = []
        if not my_url or not my_url.startswith("http"):
            errors.append("Podaj poprawny URL swojej strony (zaczynający się od http/https)")
        if not api_key.strip():
            errors.append("Podaj klucz API")

        if errors:
            for err in errors:
                st.error(f"❌ {err}")
        else:
            comp_list = [u.strip() for u in competitors_raw.strip().splitlines()
                         if u.strip() and u.strip().startswith("http")]

            st.markdown("---")
            st.markdown("### ⚙️ Postęp Analizy")

            # Progress + log containers
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.empty()

            try:
                results = asyncio.run(
                    run_analysis_pipeline(
                        my_url=my_url.strip(),
                        competitor_urls=comp_list,
                        topic=topic.strip() if topic.strip() else "auto",
                        limit=limit,
                        ai_provider=ai_provider,
                        api_key=api_key.strip(),
                        progress_bar=progress_bar,
                        log_container=log_container,
                        status_text=status_text,
                    )
                )
                st.session_state.results = results
                status_text.markdown("**✅ Analiza zakończona pomyślnie!**")
                st.balloons()

            except Exception as e:
                st.error(f"❌ Krytyczny błąd: {str(e)}")
                st.exception(e)

    # ── SHOW RESULTS ──
    if st.session_state.results:
        results = st.session_state.results

        render_gap_report(results)

        # Download buttons
        st.markdown("---")
        st.markdown("### 📥 Eksport Wyników")
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            try:
                pdf_bytes = generate_pdf(results)
                st.download_button(
                    label="⬇️ Pobierz Raport PDF",
                    data=bytes(pdf_bytes),
                    file_name=f"seo_gap_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    key="dl_pdf"
                )
            except Exception as e:
                st.error(f"Błąd generowania PDF: {e}")

        with col_dl2:
            gap = results.get("gap_report", {})
            ideas_list = gap.get("content_ideas", [])
            if ideas_list:
                import pandas as pd
                import io
                try:
                    df_ideas = pd.DataFrame(ideas_list)
                    csv_buffer = io.StringIO()
                    df_ideas.to_csv(csv_buffer, index=False, sep=";")
                    # Streamlit requires explicit utf-8-sig encoding to bytes to preserve BOM for Excel
                    csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")
                    st.download_button(
                        label="📊 Pobierz Pomysły do Excela (CSV)",
                        data=csv_bytes,
                        file_name=f"pomysly_seo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        key="dl_csv"
                    )
                except Exception as e:
                    st.error(f"Błąd generowania CSV: {str(e)}")
        with col_dl2:
            json_str = json.dumps(results, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Pobierz pełny raport JSON",
                data=json_str.encode("utf-8"),
                file_name=f"seo_gap_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                key="dl_json"
            )


if __name__ == "__main__":
    main()
