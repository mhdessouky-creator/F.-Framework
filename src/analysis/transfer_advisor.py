"""
Transfer Advisor
Provides transfer recommendations based on fixtures, form, and value
"""
import pandas as pd
from typing import List, Dict, Optional, Tuple
import sys
sys.path.append('/data/data/com.termux/files/home/fpl_project')
from src.api.fpl_client import FPLClient
from src.analysis.player_analyzer import PlayerAnalyzer
from src.analysis.fixture_analyzer import FixtureAnalyzer


class TransferAdvisor:
    """Provides intelligent transfer recommendations"""

    def __init__(self, client: Optional[FPLClient] = None):
        """
        Initialize transfer advisor

        Args:
            client: FPLClient instance
        """
        self.client = client if client else FPLClient()
        self.player_analyzer = PlayerAnalyzer(self.client)
        self.fixture_analyzer = FixtureAnalyzer(self.client)

    def get_transfer_targets(self, position: Optional[str] = None,
                            max_price: Optional[float] = None,
                            n: int = 10) -> pd.DataFrame:
        """
        Get recommended transfer targets

        Args:
            position: Filter by position (GKP, DEF, MID, FWD)
            max_price: Maximum price in millions
            n: Number of recommendations

        Returns:
            DataFrame of recommended transfer targets
        """
        # Get players data
        df = self.player_analyzer.players_df.copy()

        # Apply filters
        if position:
            df = df[df['position'] == position.upper()]

        if max_price:
            df = df[df['value'] <= max_price]

        # Filter available players with decent points
        df = df[(df['status'] == 'a') & (df['total_points'] > 20)]

        # Calculate transfer score
        # Factors: form, points per million, upcoming fixtures
        df['form_float'] = df['form'].astype(float)
        df['ownership_float'] = df['selected_by_percent'].astype(float)

        # Get fixture difficulty for each team
        fixture_scores = {}
        for team_id in df['team'].unique():
            team = self.player_analyzer.teams_df[
                self.player_analyzer.teams_df['id'] == team_id
            ].iloc[0]
            fixture_data = self.fixture_analyzer.get_fixture_difficulty(team['name'], 5)
            # Lower difficulty is better, so invert (5 - avg_difficulty)
            fixture_scores[team_id] = 5 - fixture_data['avg_difficulty']

        df['fixture_score'] = df['team'].map(fixture_scores)

        # Calculate overall transfer score
        # Form (40%) + Value (30%) + Fixtures (30%)
        df['transfer_score'] = (
            (df['form_float'] * 4) +
            (df['points_per_million'] * 0.3) +
            (df['fixture_score'] * 3)
        ).round(2)

        df = df.sort_values('transfer_score', ascending=False)

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'form', 'points_per_million', 'selected_by_percent',
            'transfer_score', 'total_points'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def get_transfer_out_candidates(self, n: int = 10) -> pd.DataFrame:
        """
        Get players to consider transferring out

        Args:
            n: Number of recommendations

        Returns:
            DataFrame of players to consider selling
        """
        df = self.player_analyzer.players_df.copy()

        # Filter players with high ownership (likely in many teams)
        df = df[df['selected_by_percent'].astype(float) > 10]

        df['form_float'] = df['form'].astype(float)

        # Get fixture difficulty
        fixture_scores = {}
        for team_id in df['team'].unique():
            team = self.player_analyzer.teams_df[
                self.player_analyzer.teams_df['id'] == team_id
            ].iloc[0]
            fixture_data = self.fixture_analyzer.get_fixture_difficulty(team['name'], 5)
            # High difficulty = bad fixtures
            fixture_scores[team_id] = fixture_data['avg_difficulty']

        df['fixture_difficulty'] = df['team'].map(fixture_scores)

        # Calculate sell score (high = should sell)
        # Bad form + high price + tough fixtures + injured
        df['sell_score'] = (
            (5 - df['form_float']) * 2 +  # Poor form
            (df['fixture_difficulty'] * 2) +  # Tough fixtures
            (df['value'] * 0.5)  # Expensive
        ).round(2)

        # Boost score for injured/unavailable
        df.loc[df['status'] != 'a', 'sell_score'] *= 1.5

        df = df.sort_values('sell_score', ascending=False)

        columns = [
            'web_name', 'team_name', 'position', 'value',
            'form', 'status', 'selected_by_percent',
            'fixture_difficulty', 'sell_score'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def suggest_transfers(self, player_out_id: int, budget: float,
                         same_position: bool = True) -> pd.DataFrame:
        """
        Suggest replacement players for a specific player

        Args:
            player_out_id: ID of player being transferred out
            budget: Available budget (in millions)
            same_position: Only suggest players in same position

        Returns:
            DataFrame of suggested replacements
        """
        player_out = self.player_analyzer.get_player_details(player_out_id)

        position = player_out['position'] if same_position else None

        # Get transfer targets within budget
        targets = self.get_transfer_targets(
            position=position,
            max_price=budget,
            n=15
        )

        # Add comparison columns
        targets['price_diff'] = (targets['value'] - player_out['price']).round(1)
        targets['form_diff'] = (
            targets['form'].astype(float) - player_out['form']
        ).round(2)

        return targets.head(10)

    def get_captaincy_picks(self, n: int = 5) -> pd.DataFrame:
        """
        Get recommended captain picks for next gameweek

        Args:
            n: Number of recommendations

        Returns:
            DataFrame of captain recommendations
        """
        df = self.player_analyzer.players_df.copy()

        # Filter available players with good ownership (template players)
        df = df[
            (df['status'] == 'a') &
            (df['selected_by_percent'].astype(float) > 15)
        ]

        df['form_float'] = df['form'].astype(float)

        # Get next gameweek fixture difficulty
        fixture_scores = {}
        for team_id in df['team'].unique():
            team = self.player_analyzer.teams_df[
                self.player_analyzer.teams_df['id'] == team_id
            ].iloc[0]
            fixtures = self.fixture_analyzer.get_upcoming_fixtures(team['name'], 1)

            if not fixtures.empty:
                fixture = fixtures.iloc[0]
                # Get difficulty for this team
                if team_id == fixture.get('team_h', 0):
                    difficulty = fixture['team_h_difficulty']
                    opponent = fixture['away_short']
                else:
                    difficulty = fixture['team_a_difficulty']
                    opponent = fixture['home_short']

                fixture_scores[team_id] = {
                    'difficulty': difficulty,
                    'opponent': opponent,
                    'score': 5 - difficulty
                }
            else:
                fixture_scores[team_id] = {
                    'difficulty': 3,
                    'opponent': 'TBD',
                    'score': 2
                }

        df['fixture_score'] = df['team'].map(lambda x: fixture_scores.get(x, {}).get('score', 2))
        df['opponent'] = df['team'].map(lambda x: fixture_scores.get(x, {}).get('opponent', 'TBD'))

        # Captain score: Form (50%) + Fixtures (40%) + Points per game (10%)
        df['captain_score'] = (
            (df['form_float'] * 5) +
            (df['fixture_score'] * 4) +
            (df['points_per_game'].astype(float))
        ).round(2)

        df = df.sort_values('captain_score', ascending=False)

        columns = [
            'web_name', 'team_name', 'position',
            'opponent', 'form', 'points_per_game',
            'captain_score', 'selected_by_percent'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def analyze_chip_strategy(self) -> Dict:
        """
        Analyze when to use chips (Wildcard, Bench Boost, Triple Captain, Free Hit)

        Returns:
            Dictionary with chip recommendations
        """
        current_gw = self.client.get_current_gameweek()

        # Check for double gameweeks (good for BB, TC)
        dgw = self.fixture_analyzer.get_double_gameweeks()

        # Check for blank gameweeks (good for Free Hit)
        bgw = self.fixture_analyzer.get_blank_gameweeks()

        # Get fixture difficulty spread
        fixtures = self.fixture_analyzer.get_best_fixtures(5)

        recommendations = {
            'current_gameweek': current_gw,
            'wildcard_recommendation': self._assess_wildcard(),
            'bench_boost_gameweeks': list(dgw['gameweek'].unique()) if not dgw.empty else [],
            'triple_captain_gameweeks': list(dgw['gameweek'].unique()) if not dgw.empty else [],
            'free_hit_gameweeks': list(bgw['gameweek'].unique()) if not bgw.empty else [],
            'best_fixture_teams': list(fixtures.head(3)['team'].values)
        }

        return recommendations

    def _assess_wildcard(self) -> str:
        """Assess if now is a good time for wildcard"""
        # Simple heuristic: Check if many template players have bad fixtures
        fixture_df = self.fixture_analyzer.get_best_fixtures(5)

        avg_difficulty = fixture_df['avg_difficulty'].mean()

        if avg_difficulty > 3.5:
            return "Consider Wildcard - Many teams have tough fixtures"
        elif avg_difficulty < 2.5:
            return "Good time for Wildcard - Many teams have easy fixtures"
        else:
            return "Neutral - No strong signal for Wildcard"

    def get_budget_options(self, position: str, max_price: float, n: int = 5) -> pd.DataFrame:
        """
        Get budget-friendly options for a position

        Args:
            position: Position (GKP, DEF, MID, FWD)
            max_price: Maximum price
            n: Number of options

        Returns:
            DataFrame of budget options
        """
        return self.get_transfer_targets(
            position=position,
            max_price=max_price,
            n=n
        )

    def get_premium_options(self, position: str, min_price: float = 10.0, n: int = 5) -> pd.DataFrame:
        """
        Get premium options for a position

        Args:
            position: Position
            min_price: Minimum price (default 10.0)
            n: Number of options

        Returns:
            DataFrame of premium options
        """
        df = self.player_analyzer.players_df.copy()

        df = df[
            (df['position'] == position.upper()) &
            (df['value'] >= min_price) &
            (df['status'] == 'a')
        ]

        df['form_float'] = df['form'].astype(float)
        df = df.sort_values(['form_float', 'total_points'], ascending=False)

        columns = [
            'web_name', 'team_name', 'value',
            'form', 'total_points', 'points_per_game',
            'selected_by_percent'
        ]

        return df[columns].head(n).reset_index(drop=True)

    def refresh_data(self):
        """Refresh all data"""
        self.client.clear_cache()
        self.player_analyzer.refresh_data()
        self.fixture_analyzer.refresh_data()


if __name__ == "__main__":
    print("Testing Transfer Advisor...")
    advisor = TransferAdvisor()

    print("\n1. Top Transfer Targets:")
    print(advisor.get_transfer_targets(n=5))

    print("\n2. Captain Picks for Next GW:")
    print(advisor.get_captaincy_picks(5))

    print("\n3. Chip Strategy:")
    chips = advisor.analyze_chip_strategy()
    print(f"   Current GW: {chips['current_gameweek']}")
    print(f"   Wildcard: {chips['wildcard_recommendation']}")

    print("\n✅ Transfer Advisor tests passed!")
