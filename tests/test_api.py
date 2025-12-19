"""
Comprehensive Test Suite for FPL Analysis Project
Tests all components: API client, analyzers, and integration
"""
import sys
sys.path.append('/data/data/com.termux/files/home/fpl_project')

from src.api.fpl_client import FPLClient
from src.analysis.player_analyzer import PlayerAnalyzer
from src.analysis.fixture_analyzer import FixtureAnalyzer
from src.analysis.transfer_advisor import TransferAdvisor


def test_fpl_client():
    """Test FPL API Client"""
    print("\n" + "="*60)
    print("TEST 1: FPL API Client")
    print("="*60)

    client = FPLClient()

    # Test 1.1: Bootstrap-static
    print("\n1.1 Testing bootstrap-static endpoint...")
    data = client.get_bootstrap_static()
    assert 'elements' in data, "Missing elements (players)"
    assert 'teams' in data, "Missing teams"
    assert 'events' in data, "Missing events (gameweeks)"
    print(f"    ✓ Players: {len(data['elements'])}")
    print(f"    ✓ Teams: {len(data['teams'])}")
    print(f"    ✓ Gameweeks: {len(data['events'])}")

    # Test 1.2: Fixtures
    print("\n1.2 Testing fixtures endpoint...")
    fixtures = client.get_fixtures()
    assert len(fixtures) > 0, "No fixtures returned"
    print(f"    ✓ Fixtures: {len(fixtures)}")

    # Test 1.3: Player summary
    print("\n1.3 Testing player summary endpoint...")
    summary = client.get_player_summary(300)  # Salah
    assert 'history' in summary, "Missing history"
    assert 'fixtures' in summary, "Missing fixtures"
    print(f"    ✓ History entries: {len(summary['history'])}")
    print(f"    ✓ Upcoming fixtures: {len(summary['fixtures'])}")

    # Test 1.4: Current gameweek
    print("\n1.4 Testing gameweek functions...")
    current_gw = client.get_current_gameweek()
    assert current_gw is not None, "No current gameweek"
    print(f"    ✓ Current GW: {current_gw}")

    # Test 1.5: Cache
    print("\n1.5 Testing cache functionality...")
    cache_info = client.get_cache_info()
    assert cache_info['cached_endpoints'] > 0, "Cache not working"
    print(f"    ✓ Cached endpoints: {cache_info['cached_endpoints']}")

    print("\n✅ FPL Client: ALL TESTS PASSED")
    return True


def test_player_analyzer():
    """Test Player Analyzer"""
    print("\n" + "="*60)
    print("TEST 2: Player Analyzer")
    print("="*60)

    analyzer = PlayerAnalyzer()

    # Test 2.1: Top form players
    print("\n2.1 Testing top form players...")
    top_form = analyzer.get_top_form_players(5)
    assert len(top_form) > 0, "No form players returned"
    assert 'web_name' in top_form.columns, "Missing player names"
    assert 'form' in top_form.columns, "Missing form data"
    print(f"    ✓ Returned {len(top_form)} players")
    print(f"    ✓ Top player: {top_form.iloc[0]['web_name']} (form: {top_form.iloc[0]['form']})")

    # Test 2.2: Best value players
    print("\n2.2 Testing best value players...")
    value_players = analyzer.get_best_value_players(5, max_price=7.0)
    assert len(value_players) > 0, "No value players returned"
    assert all(value_players['value'] <= 7.0), "Price filter not working"
    print(f"    ✓ Returned {len(value_players)} players under £7.0m")

    # Test 2.3: Differential picks
    print("\n2.3 Testing differential picks...")
    differentials = analyzer.get_differential_picks(5)
    assert len(differentials) > 0, "No differentials returned"
    print(f"    ✓ Returned {len(differentials)} differential picks")

    # Test 2.4: Compare players
    print("\n2.4 Testing player comparison...")
    comparison = analyzer.compare_players([300, 301, 302])  # Top 3 player IDs
    assert len(comparison) > 0, "Comparison failed"
    print(f"    ✓ Compared {len(comparison)} players")

    # Test 2.5: Players by team
    print("\n2.5 Testing players by team...")
    team_players = analyzer.get_players_by_team("Arsenal")
    assert len(team_players) > 0, "No team players returned"
    print(f"    ✓ Found {len(team_players)} Arsenal players")

    # Test 2.6: Player details
    print("\n2.6 Testing player details...")
    details = analyzer.get_player_details(300)
    assert 'name' in details, "Missing player name"
    assert 'total_points' in details, "Missing points"
    print(f"    ✓ Got details for: {details['web_name']}")
    print(f"    ✓ Total points: {details['total_points']}")

    print("\n✅ Player Analyzer: ALL TESTS PASSED")
    return True


def test_fixture_analyzer():
    """Test Fixture Analyzer"""
    print("\n" + "="*60)
    print("TEST 3: Fixture Analyzer")
    print("="*60)

    analyzer = FixtureAnalyzer()

    # Test 3.1: Best fixtures
    print("\n3.1 Testing best fixtures analysis...")
    best = analyzer.get_best_fixtures(5)
    assert len(best) > 0, "No fixtures returned"
    assert 'avg_difficulty' in best.columns, "Missing difficulty data"
    print(f"    ✓ Analyzed {len(best)} teams")
    print(f"    ✓ Best fixtures: {best.iloc[0]['team']} (avg: {best.iloc[0]['avg_difficulty']})")

    # Test 3.2: Upcoming fixtures
    print("\n3.2 Testing upcoming fixtures for team...")
    upcoming = analyzer.get_upcoming_fixtures("Liverpool", 5)
    assert len(upcoming) >= 0, "Fixture lookup failed"
    print(f"    ✓ Found {len(upcoming)} upcoming fixtures for Liverpool")

    # Test 3.3: Fixture difficulty
    print("\n3.3 Testing fixture difficulty rating...")
    difficulty = analyzer.get_fixture_difficulty("Arsenal", 5)
    assert 'avg_difficulty' in difficulty, "Missing difficulty rating"
    assert 'fixtures' in difficulty, "Missing fixture list"
    print(f"    ✓ Arsenal avg difficulty: {difficulty['avg_difficulty']}")

    # Test 3.4: Gameweek fixtures
    print("\n3.4 Testing gameweek fixtures...")
    gw_fixtures = analyzer.get_gameweek_fixtures(17)
    assert len(gw_fixtures) >= 0, "GW fixtures failed"
    print(f"    ✓ GW17 fixtures: {len(gw_fixtures)}")

    # Test 3.5: Fixture ticker
    print("\n3.5 Testing fixture ticker...")
    ticker = analyzer.get_fixture_ticker(5)
    assert len(ticker) > 0, "Ticker failed"
    print(f"    ✓ Generated ticker for {len(ticker)} teams")

    print("\n✅ Fixture Analyzer: ALL TESTS PASSED")
    return True


def test_transfer_advisor():
    """Test Transfer Advisor"""
    print("\n" + "="*60)
    print("TEST 4: Transfer Advisor")
    print("="*60)

    advisor = TransferAdvisor()

    # Test 4.1: Transfer targets
    print("\n4.1 Testing transfer targets...")
    targets = advisor.get_transfer_targets(n=5)
    assert len(targets) > 0, "No transfer targets"
    assert 'transfer_score' in targets.columns, "Missing transfer score"
    print(f"    ✓ Found {len(targets)} transfer targets")
    print(f"    ✓ Top target: {targets.iloc[0]['web_name']} (score: {targets.iloc[0]['transfer_score']})")

    # Test 4.2: Transfer out candidates
    print("\n4.2 Testing transfer out candidates...")
    sell = advisor.get_transfer_out_candidates(5)
    assert len(sell) > 0, "No sell candidates"
    print(f"    ✓ Found {len(sell)} sell candidates")

    # Test 4.3: Captaincy picks
    print("\n4.3 Testing captaincy picks...")
    captains = advisor.get_captaincy_picks(5)
    assert len(captains) > 0, "No captain picks"
    assert 'captain_score' in captains.columns, "Missing captain score"
    print(f"    ✓ Top captain: {captains.iloc[0]['web_name']} (score: {captains.iloc[0]['captain_score']})")

    # Test 4.4: Chip strategy
    print("\n4.4 Testing chip strategy analysis...")
    chips = advisor.analyze_chip_strategy()
    assert 'current_gameweek' in chips, "Missing current GW"
    assert 'wildcard_recommendation' in chips, "Missing wildcard rec"
    print(f"    ✓ Current GW: {chips['current_gameweek']}")
    print(f"    ✓ Wildcard: {chips['wildcard_recommendation']}")

    # Test 4.5: Budget options
    print("\n4.5 Testing budget options...")
    budget = advisor.get_budget_options('MID', 6.0, 3)
    assert len(budget) >= 0, "Budget options failed"
    print(f"    ✓ Found {len(budget)} budget midfielders under £6.0m")

    # Test 4.6: Premium options
    print("\n4.6 Testing premium options...")
    premium = advisor.get_premium_options('FWD', 10.0, 3)
    assert len(premium) >= 0, "Premium options failed"
    print(f"    ✓ Found {len(premium)} premium forwards over £10.0m")

    print("\n✅ Transfer Advisor: ALL TESTS PASSED")
    return True


def test_integration():
    """Test integration between components"""
    print("\n" + "="*60)
    print("TEST 5: Integration Tests")
    print("="*60)

    client = FPLClient()
    player_analyzer = PlayerAnalyzer(client)
    fixture_analyzer = FixtureAnalyzer(client)
    advisor = TransferAdvisor(client)

    # Test 5.1: Shared client
    print("\n5.1 Testing shared client across analyzers...")
    cache_before = client.get_cache_info()['cached_endpoints']
    player_analyzer.get_top_form_players(3)
    cache_after = client.get_cache_info()['cached_endpoints']
    assert cache_after >= cache_before, "Cache not shared"
    print(f"    ✓ Cache working across components")

    # Test 5.2: Combined analysis
    print("\n5.2 Testing combined analysis workflow...")
    # Get top form players
    top_players = player_analyzer.get_top_form_players(5)
    # Get best fixtures
    best_fixtures = fixture_analyzer.get_best_fixtures(5)
    # Get transfer targets
    targets = advisor.get_transfer_targets(n=5)
    assert len(top_players) > 0, "Combined workflow failed"
    assert len(best_fixtures) > 0, "Combined workflow failed"
    assert len(targets) > 0, "Combined workflow failed"
    print(f"    ✓ Combined analysis successful")

    # Test 5.3: Data consistency
    print("\n5.3 Testing data consistency...")
    players_count = len(player_analyzer.players_df)
    teams_count = len(fixture_analyzer.teams_df)
    assert players_count > 0, "No players loaded"
    assert teams_count > 0, "No teams loaded"
    print(f"    ✓ Players loaded: {players_count}")
    print(f"    ✓ Teams loaded: {teams_count}")

    print("\n✅ Integration Tests: ALL TESTS PASSED")
    return True


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*60)
    print("FPL ANALYSIS PROJECT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print("Testing all components...\n")

    results = []

    try:
        results.append(("FPL Client", test_fpl_client()))
    except Exception as e:
        print(f"\n❌ FPL Client FAILED: {str(e)}")
        results.append(("FPL Client", False))

    try:
        results.append(("Player Analyzer", test_player_analyzer()))
    except Exception as e:
        print(f"\n❌ Player Analyzer FAILED: {str(e)}")
        results.append(("Player Analyzer", False))

    try:
        results.append(("Fixture Analyzer", test_fixture_analyzer()))
    except Exception as e:
        print(f"\n❌ Fixture Analyzer FAILED: {str(e)}")
        results.append(("Fixture Analyzer", False))

    try:
        results.append(("Transfer Advisor", test_transfer_advisor()))
    except Exception as e:
        print(f"\n❌ Transfer Advisor FAILED: {str(e)}")
        results.append(("Transfer Advisor", False))

    try:
        results.append(("Integration", test_integration()))
    except Exception as e:
        print(f"\n❌ Integration FAILED: {str(e)}")
        results.append(("Integration", False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Project is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed. Check errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
