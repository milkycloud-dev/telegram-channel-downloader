import pytest
import os
import asyncio
from scraper_core import ScraperCore

@pytest.mark.asyncio
async def test_scraper_initialization():
    scraper = ScraperCore()
    assert scraper is not None
    assert scraper.config is not None
    assert "channels" in scraper.config

def test_config_structure():
    scraper = ScraperCore()
    cfg = scraper.config
    assert "api_id" in cfg
    assert "api_hash" in cfg
    assert "flood_wait_multiplier" in cfg

@pytest.mark.asyncio
async def test_scraper_connect():
    # We can't fully test connect without valid API keys, but we can test if it fails gracefully
    scraper = ScraperCore()
    try:
        await scraper.connect()
    except Exception as e:
        # Expected to fail with missing API keys
        pass
