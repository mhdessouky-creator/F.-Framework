"""
Player Analyzer
Analyzes player performance, form, value, and differentials
"""
import pandas as pd
from typing import List, Dict, Optional
import sys
from src.api.fpl_client import FPLClient


class PlayerAnalyzer:
    """Analyzes FPL player data"""

    def __init__(self, client: Optional[FPLClient] = None):
        """
        Initialize analyzer

        Args:
            client: FPLClient instance (creates new one if not provided)
        """
        self.client = client if client else FPLClient()
        self.players_df = None
        self.teams_df = None
        self._load_data()

    def _load_data(self):
        """Load and prepare player and team data"""
        data = self.client.get_bootstrap_static()

        # Create players DataFrame
        self.players_df = pd.DataFrame(data['elements'])

        # Create teams DataFrame
        self.teams_df = pd.DataFrame(data['teams'])

        # Add team names to players
        team_map = dict(zip(self.teams_df['id'], self.teams_df['name']))
        self.players_df['team_name'] = self.players_df['team'].map(team_map)

        # Add position names
        positions = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        self.players_df['position'] = self.players_df['element_type'].map(positions)

        # Calculate value metrics
        self.players_df['value'] = self.players_df['now_cost'] / 10.0
        self.players_df['points_per_million'] = (
            self.players_df['total_points'] / self.players_df['value']
        ).round(2)

    def get_top_form_players(self, n: int = 10, position: Optional[str] = None) -> pd.DataFrame:
        """
        Get players with best recent form

        Args:
            n: Number of players to return
            position: Filter by position (GKP, DEF, MID, FWD)

        Returns:
            DataFrame of top form players
        """
        df = self.players_df.copy()

        # Filter by position if specified
        if position:
            df = df[df['position'] == position.upper()]

        # Filter available players
        df = df[df['status'] == 'a']

        # Sort by form (string, convert to float)
        df['form_float'] = df['form'].astype(float)
        df = df.sort_values('form_float', ascending=False)

        # Select relevant columns
        columns = [
            'web_name', 'team_name', 'position', 'value',
            'form', 'total_points', 'points_per_game',
            'selected_by_percent', 'points_per_million'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def get_best_value_players(self, n: int = 10, position: Optional[str] = None,
                                max_price: Optional[float] = None) -> pd.DataFrame:
        """
        Get best value players (points per million)

        Args:
            n: Number of players to return
            position: Filter by position
            max_price: Maximum price in millions

        Returns:
            DataFrame of best value players
        """
        df = self.players_df.copy()

        # Filter by position
        if position:
            df = df[df['position'] == position.upper()]

        # Filter by price
        if max_price:
            df = df[df['value'] <= max_price]

        # Filter available players with points
        df = df[(df['status'] == 'a') & (df['total_points'] > 0)]

        # Sort by points per million
        df = df.sort_values('points_per_million', ascending=False)

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'total_points', 'points_per_million', 'form',
            'selected_by_percent'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def get_differential_picks(self, n: int = 10, max_ownership: float = 5.0,
                               min_points: int = 20) -> pd.DataFrame:
        """
        Get differential picks (low ownership, good points)

        Args:
            n: Number of players to return
            max_ownership: Maximum ownership percentage
            min_points: Minimum total points

        Returns:
            DataFrame of differential players
        """
        df = self.players_df.copy()

        # Filter criteria
        df = df[
            (df['status'] == 'a') &
            (df['selected_by_percent'].astype(float) <= max_ownership) &
            (df['total_points'] >= min_points)
        ]

        # Calculate differential score (points per million * form)
        df['diff_score'] = (
            df['points_per_million'] * df['form'].astype(float)
        ).round(2)

        df = df.sort_values('diff_score', ascending=False)

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'total_points', 'form', 'selected_by_percent',
            'diff_score', 'points_per_million'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def compare_players(self, player_ids: List[int]) -> pd.DataFrame:
        """
        Compare multiple players side by side

        Args:
            player_ids: List of player IDs to compare

        Returns:
            DataFrame with player comparison
        """
        df = self.players_df[self.players_df['id'].isin(player_ids)].copy()

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'total_points', 'points_per_game', 'form',
            'selected_by_percent', 'points_per_million',
            'minutes', 'goals_scored', 'assists',
            'clean_sheets', 'bonus'
        ]

        return df[columns].reset_index(drop=True)

    def get_players_by_team(self, team_name: str) -> pd.DataFrame:
        """
        Get all players from a specific team

        Args:
            team_name: Name of the team

        Returns:
            DataFrame of team's players
        """
        df = self.players_df[
            self.players_df['team_name'].str.contains(team_name, case=False)
        ].copy()

        df = df.sort_values('total_points', ascending=False)

        columns = [
            'web_name', 'position', 'value', 'total_points',
            'form', 'points_per_game', 'selected_by_percent'
        ]

        return df[columns].reset_index(drop=True)

    def get_price_changes(self) -> Dict[str, pd.DataFrame]:
        """
        Get players with recent price changes

        Returns:
            Dictionary with 'risers' and 'fallers' DataFrames
        """
        df = self.players_df.copy()

        # Players who rose in price
        risers = df[df['cost_change_start'] > 0].copy()
        risers = risers.sort_values('cost_change_start', ascending=False)

        # Players who fell in price
        fallers = df[df['cost_change_start'] < 0].copy()
        fallers = fallers.sort_values('cost_change_start')

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'cost_change_start', 'total_points', 'form'
        ]

        return {
            'risers': risers[columns].head(10).reset_index(drop=True),
            'fallers': fallers[columns].head(10).reset_index(drop=True)
        }

    def get_injury_list(self) -> pd.DataFrame:
        """
        Get currently injured/unavailable players

        Returns:
            DataFrame of unavailable players
        """
        df = self.players_df[self.players_df['status'] != 'a'].copy()

        status_map = {
            'i': 'Injured',
            'd': 'Doubtful',
            's': 'Suspended',
            'u': 'Unavailable'
        }
        df['status_text'] = df['status'].map(status_map)

        df = df.sort_values('selected_by_percent', ascending=False)

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'status_text', 'news', 'selected_by_percent'
        ]

        return df[columns].reset_index(drop=True)

    def get_player_details(self, player_id: int) -> Dict:
        """
        Get detailed information about a specific player

        Args:
            player_id: Player ID

        Returns:
            Dictionary with player details
        """
        player = self.players_df[self.players_df['id'] == player_id].iloc[0]

        details = {
            'name': f"{player['first_name']} {player['second_name']}",
            'web_name': player['web_name'],
            'team': player['team_name'],
            'position': player['position'],
            'price': player['value'],
            'total_points': int(player['total_points']),
            'form': float(player['form']),
            'points_per_game': float(player['points_per_game']),
            'ownership': float(player['selected_by_percent']),
            'points_per_million': player['points_per_million'],
            'minutes': int(player['minutes']),
            'goals': int(player['goals_scored']),
            'assists': int(player['assists']),
            'clean_sheets': int(player['clean_sheets']),
            'bonus': int(player['bonus']),
            'status': player['status']
        }

        # Get additional history if available
        try:
            summary = self.client.get_player_summary(player_id)
            details['history'] = summary.get('history', [])
            details['fixtures'] = summary.get('fixtures', [])
        except:
            pass

        return details

    def refresh_data(self):
        """Refresh player data from API"""
        self.client.clear_cache()
        self._load_data()


if __name__ == "__main__":
    print("Testing Player Analyzer...")
    analyzer = PlayerAnalyzer()

    print("\n1. Top 5 Form Players:")
    print(analyzer.get_top_form_players(5))

    print("\n2. Best Value Players (under £7m):")
    print(analyzer.get_best_value_players(5, max_price=7.0))

    print("\n3. Differential Picks:")
    print(analyzer.get_differential_picks(5))

    print("\n✅ Player Analyzer tests passed!")
