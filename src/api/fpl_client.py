"""
FPL API Client
Handles all communication with Fantasy Premier League API
"""
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time


class FPLClient:
    """Client for interacting with the FPL API"""

    BASE_URL = "https://fantasy.premierleague.com/api"

    def __init__(self, cache_duration: int = 300):
        """
        Initialize FPL Client

        Args:
            cache_duration: How long to cache responses in seconds (default: 5 min)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FPL-Analysis-Tool/1.0'
        })
        self.cache = {}
        self.cache_duration = cache_duration
        self.last_request_time = 0
        self.min_request_interval = 1  # Minimum 1 second between requests

    def _rate_limit(self):
        """Ensure we don't make requests too quickly"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get data from cache if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_duration:
                return data
        return None

    def _set_cache(self, key: str, data: Dict):
        """Store data in cache"""
        self.cache[key] = (data, time.time())

    def _make_request(self, endpoint: str, use_cache: bool = True) -> Dict:
        """
        Make HTTP request to FPL API

        Args:
            endpoint: API endpoint (without base URL)
            use_cache: Whether to use cached response

        Returns:
            JSON response as dictionary
        """
        # Check cache first
        if use_cache:
            cached = self._get_cached(endpoint)
            if cached:
                return cached

        # Rate limiting
        self._rate_limit()

        # Make request
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cache the response
            if use_cache:
                self._set_cache(endpoint, data)

            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"FPL API request failed: {str(e)}")

    def get_bootstrap_static(self, use_cache: bool = True) -> Dict:
        """
        Get bootstrap-static data (all game data)
        Contains: teams, elements (players), element_types, events (gameweeks)

        Returns:
            Dictionary with all FPL game data
        """
        return self._make_request("/bootstrap-static/", use_cache)

    def get_fixtures(self, use_cache: bool = True) -> List[Dict]:
        """
        Get all fixtures (matches)

        Returns:
            List of fixture dictionaries
        """
        return self._make_request("/fixtures/", use_cache)

    def get_fixture(self, fixture_id: int, use_cache: bool = True) -> Dict:
        """
        Get specific fixture details

        Args:
            fixture_id: The fixture ID

        Returns:
            Fixture details dictionary
        """
        fixtures = self.get_fixtures(use_cache)
        for fixture in fixtures:
            if fixture['id'] == fixture_id:
                return fixture
        raise ValueError(f"Fixture {fixture_id} not found")

    def get_player_summary(self, player_id: int, use_cache: bool = True) -> Dict:
        """
        Get detailed player summary including history and fixtures

        Args:
            player_id: The player element ID

        Returns:
            Player summary with history and upcoming fixtures
        """
        return self._make_request(f"/element-summary/{player_id}/", use_cache)

    def get_live_gameweek(self, gameweek: int, use_cache: bool = False) -> Dict:
        """
        Get live gameweek data (usually don't cache this)

        Args:
            gameweek: Gameweek number (event)
            use_cache: Whether to cache (default False for live data)

        Returns:
            Live gameweek data
        """
        return self._make_request(f"/event/{gameweek}/live/", use_cache)

    def get_current_gameweek(self) -> Optional[int]:
        """
        Get current active gameweek number

        Returns:
            Current gameweek number or None if season not started
        """
        data = self.get_bootstrap_static()
        for event in data['events']:
            if event['is_current']:
                return event['id']
        return None

    def get_next_gameweek(self) -> Optional[int]:
        """
        Get next gameweek number

        Returns:
            Next gameweek number or None
        """
        data = self.get_bootstrap_static()
        for event in data['events']:
            if event['is_next']:
                return event['id']
        return None

    def get_all_players(self) -> List[Dict]:
        """
        Get all players data

        Returns:
            List of all player dictionaries
        """
        data = self.get_bootstrap_static()
        return data['elements']

    def get_all_teams(self) -> List[Dict]:
        """
        Get all teams data

        Returns:
            List of all team dictionaries
        """
        data = self.get_bootstrap_static()
        return data['teams']

    def get_player_by_id(self, player_id: int) -> Optional[Dict]:
        """
        Get specific player by ID

        Args:
            player_id: Player element ID

        Returns:
            Player dictionary or None
        """
        players = self.get_all_players()
        for player in players:
            if player['id'] == player_id:
                return player
        return None

    def get_team_by_id(self, team_id: int) -> Optional[Dict]:
        """
        Get specific team by ID

        Args:
            team_id: Team ID

        Returns:
            Team dictionary or None
        """
        teams = self.get_all_teams()
        for team in teams:
            if team['id'] == team_id:
                return team
        return None

    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about current cache state

        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_endpoints': len(self.cache),
            'endpoints': list(self.cache.keys()),
            'cache_duration': self.cache_duration
        }


if __name__ == "__main__":
    # Quick test
    print("Testing FPL API Client...")
    client = FPLClient()

    try:
        # Test bootstrap-static
        print("\n1. Fetching bootstrap-static data...")
        data = client.get_bootstrap_static()
        print(f"   ✓ Found {len(data['elements'])} players")
        print(f"   ✓ Found {len(data['teams'])} teams")
        print(f"   ✓ Found {len(data['events'])} gameweeks")

        # Test current gameweek
        print("\n2. Getting current gameweek...")
        gw = client.get_current_gameweek()
        print(f"   ✓ Current gameweek: {gw}")

        # Test fixtures
        print("\n3. Fetching fixtures...")
        fixtures = client.get_fixtures()
        print(f"   ✓ Found {len(fixtures)} fixtures")

        # Test player summary
        print("\n4. Fetching player summary (Salah - ID 300)...")
        summary = client.get_player_summary(300)
        print(f"   ✓ Got history: {len(summary.get('history', []))} past gameweeks")
        print(f"   ✓ Got fixtures: {len(summary.get('fixtures', []))} upcoming fixtures")

        # Cache info
        print("\n5. Cache information...")
        cache_info = client.get_cache_info()
        print(f"   ✓ Cached endpoints: {cache_info['cached_endpoints']}")

        print("\n✅ All API tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
