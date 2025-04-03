import re
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from config import AFFILIATE_TAG

logger = logging.getLogger(__name__)

# Regular expression to detect Amazon product links
# Matches common Amazon domains and extracts the product ID (ASIN)
AMAZON_REGEX = re.compile(
    r'https?://(?:www\.)?(?:amazon\.(?:com|ca|co\.uk|de|fr|it|es|jp|in|com\.au|com\.br|nl|com\.mx)/(?:[^"\'/]*/)(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})(?:[/?]|$)|amzn\.(?:to|in)/(?:[\w]+/?)*(?:d/)?([A-Z0-9]{5,10}))'
)

def is_amazon_link(url):
    """Check if the URL is an Amazon product link."""
    return bool(AMAZON_REGEX.match(url))

def extract_asin(url):
    """Extract the ASIN (Amazon Standard Identification Number) from an Amazon URL."""
    match = AMAZON_REGEX.match(url)
    if match:
        # Group 1 is for standard Amazon URLs, group 2 is for shortened URLs
        asin = match.group(1) or match.group(2)
        return asin
    return None

def convert_to_affiliate_link(url):
    """
    Convert an Amazon product URL to an affiliate link.
    Returns the converted URL or None if conversion failed.
    """
    if not url or not is_amazon_link(url):
        logger.debug(f"URL is not a valid Amazon link: {url}")
        return None
    
    try:
        asin = extract_asin(url)
        if not asin:
            logger.warning(f"Could not extract ASIN from URL: {url}")
            return None
        
        # Parse the URL
        parsed_url = urlparse(url)
        
        # For shortened URLs (amzn.to or amzn.in), use amazon.in as the domain
        if 'amzn.' in parsed_url.netloc:
            domain = 'www.amazon.in'
        else:
            # Get the domain (e.g., amazon.com)
            domain = parsed_url.netloc
            if not domain.startswith('www.'):
                domain = 'www.' + domain
        
        # Construct a clean, minimal affiliate URL
        path = f"/dp/{asin}"
        
        # Create query parameters with the affiliate tag
        query_params = {'tag': AFFILIATE_TAG}
        
        # Reconstruct the URL
        affiliate_url = urlunparse((
            parsed_url.scheme,  # http or https
            domain,             # www.amazon.com
            path,               # /dp/ASIN
            '',                 # params
            urlencode(query_params),  # query string
            ''                  # fragment
        ))
        
        logger.debug(f"Converted URL: {url} -> {affiliate_url}")
        return affiliate_url
    
    except Exception as e:
        logger.error(f"Error converting URL to affiliate link: {e}")
        return None

def find_and_convert_amazon_links(text):
    """
    Find all Amazon links in the text and convert them to affiliate links.
    Returns a tuple (original_links, converted_links)
    """
    # Find all URLs in the text that look like they might be links
    url_pattern = re.compile(r'https?://\S+')
    potential_urls = url_pattern.findall(text)
    
    original_links = []
    converted_links = []
    
    for url in potential_urls:
        # Clean up URL (remove trailing punctuation or other characters)
        # This handles URLs that might be at the end of a sentence
        clean_url = url.rstrip('.,;:!?)\'"')
        
        if is_amazon_link(clean_url):
            converted_url = convert_to_affiliate_link(clean_url)
            if converted_url:
                original_links.append(clean_url)
                converted_links.append(converted_url)
    
    return original_links, converted_links
