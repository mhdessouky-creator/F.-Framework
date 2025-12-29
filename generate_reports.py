"""
HTML Report Generator for FPL Analysis
Generates comprehensive HTML reports and dashboard
"""
import os
import sys

from src.api.fpl_client import FPLClient
from src.analysis.player_analyzer import PlayerAnalyzer
from src.analysis.fixture_analyzer import FixtureAnalyzer
from src.analysis.transfer_advisor import TransferAdvisor
from datetime import datetime


# CSS Styling
STYLE = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        min-height: 100vh;
    }
    .container {
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        overflow: hidden;
    }
    .header {
        background: linear-gradient(135deg, #37003c 0%, #4a0049 100%);
        color: white;
        padding: 40px;
        text-align: center;
    }
    .header h1 { font-size: 2.5em; margin-bottom: 10px; }
    .header p { color: #00ff87; font-size: 1.1em; }
    .nav {
        background: #f8f9fa;
        padding: 20px;
        border-bottom: 3px solid #37003c;
    }
    .nav a {
        display: inline-block;
        margin: 5px 10px;
        padding: 10px 20px;
        background: #37003c;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        transition: background 0.3s;
    }
    .nav a:hover { background: #5c0061; }
    .content { padding: 40px; }
    .section {
        background: #f8f9fa;
        padding: 25px;
        margin: 20px 0;
        border-radius: 10px;
        border-left: 5px solid #37003c;
    }
    .section h2 {
        color: #37003c;
        margin-bottom: 20px;
        font-size: 1.8em;
    }
    .section h3 {
        color: #5c0061;
        margin: 20px 0 10px;
        font-size: 1.3em;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        background: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    th {
        background: #37003c;
        color: white;
        padding: 15px;
        text-align: left;
        font-weight: 600;
    }
    td {
        padding: 12px 15px;
        border-bottom: 1px solid #e0e0e0;
    }
    tr:hover { background: #f5f5f5; }
    .highlight {
        background: #00ff87;
        color: #37003c;
        padding: 3px 8px;
        border-radius: 3px;
        font-weight: bold;
    }
    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .badge-success { background: #00ff87; color: #37003c; }
    .badge-warning { background: #ffc107; color: #333; }
    .badge-danger { background: #dc3545; color: white; }
    .badge-info { background: #17a2b8; color: white; }
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    .stat-card {
        background: white;
        padding: 25px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-top: 4px solid #37003c;
    }
    .stat-card h3 { color: #37003c; margin-bottom: 10px; }
    .stat-card .value {
        font-size: 2.5em;
        font-weight: bold;
        color: #00ff87;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .footer {
        background: #f8f9fa;
        padding: 30px;
        text-align: center;
        color: #666;
        border-top: 3px solid #37003c;
    }
    .timestamp {
        color: #999;
        font-size: 0.9em;
        margin-top: 10px;
    }
</style>
"""


def generate_dashboard():
    """Generate main dashboard index.html"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FPL Analysis Dashboard</title>
    {STYLE}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ FPL Analysis Dashboard</h1>
            <p>Fantasy Premier League - Complete Analysis Suite</p>
        </div>

        <div class="nav">
            <a href="index.html">🏠 Dashboard</a>
            <a href="players.html">👤 Player Analysis</a>
            <a href="fixtures.html">📅 Fixture Analysis</a>
            <a href="transfers.html">🔄 Transfer Recommendations</a>
            <a href="phase1_report.html">📦 Phase 1</a>
            <a href="phase4_comprehensive_tests.log">🧪 Test Results</a>
        </div>

        <div class="content">
            <div class="section">
                <h2>🎯 Project Overview</h2>
                <p>Welcome to the FPL Analysis Project - a comprehensive Fantasy Premier League analysis tool built entirely in Termux on Android!</p>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Players Analyzed</h3>
                        <div class="value">760</div>
                    </div>
                    <div class="stat-card">
                        <h3>Teams Tracked</h3>
                        <div class="value">20</div>
                    </div>
                    <div class="stat-card">
                        <h3>Fixtures</h3>
                        <div class="value">380</div>
                    </div>
                    <div class="stat-card">
                        <h3>Current GW</h3>
                        <div class="value">16</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📊 Available Reports</h2>
                <table>
                    <tr>
                        <th>Report</th>
                        <th>Description</th>
                        <th>Action</th>
                    </tr>
                    <tr>
                        <td><strong>Player Analysis</strong></td>
                        <td>Top form players, best value picks, and differential options</td>
                        <td><a href="players.html" style="color: #37003c;">View Report →</a></td>
                    </tr>
                    <tr>
                        <td><strong>Fixture Analysis</strong></td>
                        <td>Upcoming fixtures, difficulty ratings, and fixture ticker</td>
                        <td><a href="fixtures.html" style="color: #37003c;">View Report →</a></td>
                    </tr>
                    <tr>
                        <td><strong>Transfer Recommendations</strong></td>
                        <td>Transfer targets, sell candidates, and captaincy picks</td>
                        <td><a href="transfers.html" style="color: #37003c;">View Report →</a></td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>✅ Project Status</h2>
                <ul style="line-height: 2; list-style: none; padding-left: 20px;">
                    <li>✅ <strong>Phase 1:</strong> Project setup and dependencies - <span class="highlight">COMPLETE</span></li>
                    <li>✅ <strong>Phase 2:</strong> FPL API Client - <span class="highlight">COMPLETE</span></li>
                    <li>✅ <strong>Phase 3:</strong> Analysis Modules - <span class="highlight">COMPLETE</span></li>
                    <li>✅ <strong>Phase 4:</strong> Comprehensive Testing - <span class="highlight">ALL TESTS PASSED</span></li>
                    <li>✅ <strong>Phase 5:</strong> HTML Reports & Dashboard - <span class="highlight">COMPLETE</span></li>
                </ul>
            </div>

            <div class="section">
                <h2>🛠️ Technical Stack</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Python</h3>
                        <div class="value" style="font-size: 1.5em;">3.12.12</div>
                    </div>
                    <div class="stat-card">
                        <h3>Environment</h3>
                        <div class="value" style="font-size: 1.2em;">Termux</div>
                    </div>
                    <div class="stat-card">
                        <h3>Libraries</h3>
                        <div class="value" style="font-size: 1.2em;">Pandas + Requests</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>FPL Analysis Project</strong> - Built with Python in Termux</p>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>
    </div>
</body>
</html>"""

    output_path = os.path.join("reports", "index.html")
    os.makedirs("reports", exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Dashboard generated: {output_path}")


def generate_player_report():
    """Generate player analysis report"""
    analyzer = PlayerAnalyzer()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get data
    top_form = analyzer.get_top_form_players(10)
    best_value = analyzer.get_best_value_players(10, max_price=7.0)
    differentials = analyzer.get_differential_picks(10)

    # Convert dataframes to HTML tables
    form_table = top_form.to_html(index=False, classes='data-table', border=0)
    value_table = best_value.to_html(index=False, classes='data-table', border=0)
    diff_table = differentials.to_html(index=False, classes='data-table', border=0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Analysis Report</title>
    {STYLE}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👤 Player Analysis Report</h1>
            <p>Top performers, value picks, and differentials</p>
        </div>

        <div class="nav">
            <a href="index.html">🏠 Dashboard</a>
            <a href="players.html">👤 Player Analysis</a>
            <a href="fixtures.html">📅 Fixtures</a>
            <a href="transfers.html">🔄 Transfers</a>
        </div>

        <div class="content">
            <div class="section">
                <h2>🔥 Top Form Players</h2>
                <p>Players in the best current form based on recent performances:</p>
                {form_table}
            </div>

            <div class="section">
                <h2>💰 Best Value Players (Under £7.0m)</h2>
                <p>Budget-friendly options with excellent points per million:</p>
                {value_table}
            </div>

            <div class="section">
                <h2>🎯 Differential Picks</h2>
                <p>Low ownership players with strong potential (under 5% ownership):</p>
                {diff_table}
            </div>
        </div>

        <div class="footer">
            <p><strong>FPL Analysis Project</strong></p>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>
    </div>
</body>
</html>"""

    output_path = os.path.join("reports", "players.html")
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Player report generated: {output_path}")


def generate_fixture_report():
    """Generate fixture analysis report"""
    analyzer = FixtureAnalyzer()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get data
    best_fixtures = analyzer.get_best_fixtures(5)
    worst_fixtures = analyzer.get_worst_fixtures(5)
    ticker = analyzer.get_fixture_ticker(5)

    # Convert to HTML
    best_table = best_fixtures.head(10).to_html(index=False, classes='data-table', border=0)
    worst_table = worst_fixtures.head(10).to_html(index=False, classes='data-table', border=0)
    ticker_table = ticker.to_html(index=False, classes='data-table', border=0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fixture Analysis Report</title>
    {STYLE}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Fixture Analysis Report</h1>
            <p>Upcoming fixtures and difficulty ratings</p>
        </div>

        <div class="nav">
            <a href="index.html">🏠 Dashboard</a>
            <a href="players.html">👤 Players</a>
            <a href="fixtures.html">📅 Fixture Analysis</a>
            <a href="transfers.html">🔄 Transfers</a>
        </div>

        <div class="content">
            <div class="section">
                <h2>✅ Best Upcoming Fixtures (Next 5 GWs)</h2>
                <p>Teams with the easiest fixtures ahead:</p>
                {best_table}
            </div>

            <div class="section">
                <h2>⚠️ Worst Upcoming Fixtures (Next 5 GWs)</h2>
                <p>Teams with the toughest fixtures ahead:</p>
                {worst_table}
            </div>

            <div class="section">
                <h2>📊 Fixture Ticker</h2>
                <p>Complete fixture overview for all teams (H=Home, A=Away, [Difficulty]):</p>
                <div style="overflow-x: auto;">
                    {ticker_table}
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>FPL Analysis Project</strong></p>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>
    </div>
</body>
</html>"""

    output_path = os.path.join("reports", "fixtures.html")
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Fixture report generated: {output_path}")


def generate_transfer_report():
    """Generate transfer recommendations report"""
    advisor = TransferAdvisor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get data
    targets = advisor.get_transfer_targets(n=10)
    sell_candidates = advisor.get_transfer_out_candidates(10)
    captains = advisor.get_captaincy_picks(10)
    chips = advisor.analyze_chip_strategy()

    # Convert to HTML
    targets_table = targets.to_html(index=False, classes='data-table', border=0)
    sell_table = sell_candidates.to_html(index=False, classes='data-table', border=0)
    captain_table = captains.to_html(index=False, classes='data-table', border=0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transfer Recommendations</title>
    {STYLE}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Transfer Recommendations</h1>
            <p>Smart transfer targets and captaincy picks</p>
        </div>

        <div class="nav">
            <a href="index.html">🏠 Dashboard</a>
            <a href="players.html">👤 Players</a>
            <a href="fixtures.html">📅 Fixtures</a>
            <a href="transfers.html">🔄 Transfer Recommendations</a>
        </div>

        <div class="content">
            <div class="section">
                <h2>⭐ Top Transfer Targets</h2>
                <p>Best players to bring in based on form, fixtures, and value:</p>
                {targets_table}
            </div>

            <div class="section">
                <h2>👋 Transfer Out Candidates</h2>
                <p>Players to consider selling due to poor form or tough fixtures:</p>
                {sell_table}
            </div>

            <div class="section">
                <h2>©️ Captain Picks for Next GW</h2>
                <p>Recommended captaincy choices for gameweek {chips['current_gameweek'] + 1}:</p>
                {captain_table}
            </div>

            <div class="section">
                <h2>🎴 Chip Strategy</h2>
                <ul style="line-height: 2; padding-left: 20px;">
                    <li><strong>Current Gameweek:</strong> {chips['current_gameweek']}</li>
                    <li><strong>Wildcard:</strong> {chips['wildcard_recommendation']}</li>
                    <li><strong>Best Fixture Teams:</strong> {', '.join(chips['best_fixture_teams'])}</li>
                    <li><strong>Bench Boost GWs:</strong> {', '.join(map(str, chips['bench_boost_gameweeks'])) if chips['bench_boost_gameweeks'] else 'None identified'}</li>
                    <li><strong>Triple Captain GWs:</strong> {', '.join(map(str, chips['triple_captain_gameweeks'])) if chips['triple_captain_gameweeks'] else 'None identified'}</li>
                    <li><strong>Free Hit GWs:</strong> {', '.join(map(str, chips['free_hit_gameweeks'])) if chips['free_hit_gameweeks'] else 'None identified'}</li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <p><strong>FPL Analysis Project</strong></p>
            <p class="timestamp">Generated: {timestamp}</p>
        </div>
    </div>
</body>
</html>"""

    output_path = os.path.join("reports", "transfers.html")
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ Transfer report generated: {output_path}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Generating HTML Reports...")
    print("="*60 + "\n")

    generate_dashboard()
    generate_player_report()
    generate_fixture_report()
    generate_transfer_report()

    print("\n" + "="*60)
    print("✅ ALL REPORTS GENERATED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 Open ~/fpl_project/reports/index.html to view the dashboard")
    print("\nAvailable reports:")
    print("  - index.html (Main Dashboard)")
    print("  - players.html (Player Analysis)")
    print("  - fixtures.html (Fixture Analysis)")
    print("  - transfers.html (Transfer Recommendations)")
    print("="*60 + "\n")
