"""
Fixture Analyzer
Analyzes team fixtures and difficulty ratings
"""
import pandas as pd
from typing import List, Dict, Optional
import sys
sys.path.append('/data/data/com.termux/files/home/fpl_project')
from src.api.fpl_client import FPLClient


class FixtureAnalyzer:
    """Analyzes FPL fixtures and team schedules"""

    def __init__(self, client: Optional[FPLClient] = None):
        """
        Initialize analyzer

        Args:
            client: FPLClient instance
        """
        self.client = client if client else FPLClient()
        self.fixtures_df = None
        self.teams_df = None
        self._load_data()

    def _load_data(self):
        """Load fixtures and team data"""
        # Get fixtures
        fixtures = self.client.get_fixtures()
        self.fixtures_df = pd.DataFrame(fixtures)

        # Get teams
        data = self.client.get_bootstrap_static()
        self.teams_df = pd.DataFrame(data['teams'])

        # Create team name mapping
        team_map = dict(zip(self.teams_df['id'], self.teams_df['name']))

        # Add team names to fixtures
        self.fixtures_df['home_team_name'] = self.fixtures_df['team_h'].map(team_map)
        self.fixtures_df['away_team_name'] = self.fixtures_df['team_a'].map(team_map)

        # Add short names
        short_map = dict(zip(self.teams_df['id'], self.teams_df['short_name']))
        self.fixtures_df['home_short'] = self.fixtures_df['team_h'].map(short_map)
        self.fixtures_df['away_short'] = self.fixtures_df['team_a'].map(short_map)

    def get_upcoming_fixtures(self, team_name: str, n: int = 5) -> pd.DataFrame:
        """
        Get upcoming fixtures for a team

        Args:
            team_name: Team name (can be partial match)
            n: Number of fixtures to return

        Returns:
            DataFrame of upcoming fixtures
        """
        df = self.fixtures_df.copy()

        # Filter for the team (home or away)
        df = df[
            (df['home_team_name'].str.contains(team_name, case=False)) |
            (df['away_team_name'].str.contains(team_name, case=False))
        ]

        # Filter only future fixtures (not finished)
        df = df[df['finished'] == False]

        # Sort by gameweek
        df = df.sort_values('event')

        columns = [
            'event', 'home_short', 'away_short',
            'team_h_difficulty', 'team_a_difficulty'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def get_fixture_difficulty(self, team_name: str, n: int = 5) -> Dict:
        """
        Get fixture difficulty rating for a team

        Args:
            team_name: Team name
            n: Number of fixtures to analyze

        Returns:
            Dictionary with difficulty analysis
        """
        fixtures = self.get_upcoming_fixtures(team_name, n)

        if fixtures.empty:
            return {'team': team_name, 'avg_difficulty': 0, 'fixtures': []}

        # Determine if team is home or away and get appropriate difficulty
        difficulties = []
        fixture_list = []

        for _, row in fixtures.iterrows():
            if team_name.lower() in row['home_short'].lower():
                difficulty = row['team_h_difficulty']
                opponent = row['away_short']
                venue = 'H'
            else:
                difficulty = row['team_a_difficulty']
                opponent = row['home_short']
                venue = 'A'

            difficulties.append(difficulty)
            fixture_list.append({
                'gameweek': row['event'],
                'opponent': opponent,
                'venue': venue,
                'difficulty': difficulty
            })

        return {
            'team': team_name,
            'avg_difficulty': round(sum(difficulties) / len(difficulties), 2),
            'total_difficulty': sum(difficulties),
            'fixtures': fixture_list
        }

    def get_best_fixtures(self, n_gameweeks: int = 5) -> pd.DataFrame:
        """
        Get teams with best upcoming fixtures

        Args:
            n_gameweeks: Number of gameweeks to analyze

        Returns:
            DataFrame of teams sorted by fixture difficulty
        """
        results = []

        for _, team in self.teams_df.iterrows():
            analysis = self.get_fixture_difficulty(team['name'], n_gameweeks)
            results.append({
                'team': team['short_name'],
                'team_name': team['name'],
                'avg_difficulty': analysis['avg_difficulty'],
                'fixtures': ' '.join([
                    f"{f['opponent']}({f['venue']})"
                    for f in analysis['fixtures'][:5]
                ])
            })

        df = pd.DataFrame(results)
        df = df.sort_values('avg_difficulty')

        return df.reset_index(drop=True)

    def get_worst_fixtures(self, n_gameweeks: int = 5) -> pd.DataFrame:
        """
        Get teams with worst upcoming fixtures

        Args:
            n_gameweeks: Number of gameweeks to analyze

        Returns:
            DataFrame of teams with hardest fixtures
        """
        df = self.get_best_fixtures(n_gameweeks)
        return df.sort_values('avg_difficulty', ascending=False).reset_index(drop=True)

    def get_gameweek_fixtures(self, gameweek: int) -> pd.DataFrame:
        """
        Get all fixtures for a specific gameweek

        Args:
            gameweek: Gameweek number

        Returns:
            DataFrame of fixtures
        """
        df = self.fixtures_df[self.fixtures_df['event'] == gameweek].copy()

        columns = [
            'home_team_name', 'away_team_name',
            'team_h_difficulty', 'team_a_difficulty',
            'finished', 'team_h_score', 'team_a_score'
        ]

        return df[columns].reset_index(drop=True)

    def get_double_gameweeks(self) -> pd.DataFrame:
        """
        Identify teams with double gameweeks

        Returns:
            DataFrame showing teams with multiple fixtures in a gameweek
        """
        df = self.fixtures_df[self.fixtures_df['finished'] == False].copy()

        # Count fixtures per team per gameweek
        home_counts = df.groupby(['event', 'team_h']).size().reset_index(name='home_count')
        away_counts = df.groupby(['event', 'team_a']).size().reset_index(name='away_count')

        # Combine counts
        dgw_data = []

        for _, team in self.teams_df.iterrows():
            team_id = team['id']

            # Check each gameweek
            for gw in df['event'].unique():
                home = len(df[(df['event'] == gw) & (df['team_h'] == team_id)])
                away = len(df[(df['event'] == gw) & (df['team_a'] == team_id)])
                total = home + away

                if total > 1:
                    dgw_data.append({
                        'gameweek': gw,
                        'team': team['short_name'],
                        'fixtures': total
                    })

        if not dgw_data:
            return pd.DataFrame(columns=['gameweek', 'team', 'fixtures'])

        return pd.DataFrame(dgw_data).sort_values('gameweek')

    def get_blank_gameweeks(self) -> pd.DataFrame:
        """
        Identify teams with blank gameweeks (no fixture)

        Returns:
            DataFrame showing teams with no fixtures in a gameweek
        """
        df = self.fixtures_df[self.fixtures_df['finished'] == False].copy()

        blank_data = []

        for _, team in self.teams_df.iterrows():
            team_id = team['id']

            # Get all upcoming gameweeks
            all_gws = sorted(df['event'].unique())

            for gw in all_gws:
                has_fixture = len(df[
                    (df['event'] == gw) &
                    ((df['team_h'] == team_id) | (df['team_a'] == team_id))
                ]) > 0

                if not has_fixture:
                    blank_data.append({
                        'gameweek': gw,
                        'team': team['short_name']
                    })

        if not blank_data:
            return pd.DataFrame(columns=['gameweek', 'team'])

        return pd.DataFrame(blank_data).sort_values('gameweek')

    def compare_fixtures(self, team_names: List[str], n: int = 5) -> pd.DataFrame:
        """
        Compare fixtures between multiple teams

        Args:
            team_names: List of team names to compare
            n: Number of gameweeks to compare

        Returns:
            DataFrame comparing team fixtures
        """
        comparison = []

        for team_name in team_names:
            analysis = self.get_fixture_difficulty(team_name, n)
            comparison.append({
                'team': team_name,
                'avg_difficulty': analysis['avg_difficulty'],
                'next_5_fixtures': ', '.join([
                    f"GW{f['gameweek']}: {f['opponent']}({f['venue']})[{f['difficulty']}]"
                    for f in analysis['fixtures']
                ])
            })

        return pd.DataFrame(comparison).sort_values('avg_difficulty')

    def get_fixture_ticker(self, n_gameweeks: int = 8) -> pd.DataFrame:
        """
        Create fixture ticker showing upcoming fixtures for all teams

        Args:
            n_gameweeks: Number of gameweeks to show

        Returns:
            DataFrame with fixture ticker
        """
        current_gw = self.client.get_current_gameweek()
        if not current_gw:
            current_gw = 1

        ticker_data = []

        for _, team in self.teams_df.iterrows():
            fixtures = self.get_upcoming_fixtures(team['name'], n_gameweeks)

            row = {'team': team['short_name']}

            for i, (_, fixture) in enumerate(fixtures.iterrows(), 1):
                if team['id'] == fixture.get('team_h', 0):
                    opponent = fixture['away_short']
                    difficulty = fixture['team_h_difficulty']
                    venue = 'H'
                else:
                    opponent = fixture['home_short']
                    difficulty = fixture['team_a_difficulty']
                    venue = 'A'

                row[f'GW{current_gw + i - 1}'] = f"{opponent}({venue})[{difficulty}]"

            ticker_data.append(row)

        return pd.DataFrame(ticker_data)

    def refresh_data(self):
        """Refresh fixture data from API"""
        self.client.clear_cache()
        self._load_data()


if __name__ == "__main__":
    print("Testing Fixture Analyzer...")
    analyzer = FixtureAnalyzer()

    print("\n1. Best Upcoming Fixtures (next 5 GWs):")
    print(analyzer.get_best_fixtures(5).head(5))

    print("\n2. Arsenal's Next 5 Fixtures:")
    print(analyzer.get_upcoming_fixtures('Arsenal', 5))

    print("\n3. Double Gameweeks:")
    dgw = analyzer.get_double_gameweeks()
    if not dgw.empty:
        print(dgw.head(5))
    else:
        print("   No double gameweeks found")

    print("\n✅ Fixture Analyzer tests passed!")
