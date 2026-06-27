#!/usr/bin/env python3

"""
Refreshes the expected data for games, players, and teams to match their current outputs. This is
meant to automate the process of adapting to stat adjustments and other changes on Baseball
Reference. To avoid introducing errors into the test suite, all changes should be manually reviewed
to make sure that they accurately reflect changes to the site.
"""

import json
from pathlib import Path

from tqdm import tqdm

import brlib as br
from tests.case_ids import game_test_cases, player_test_cases, team_test_cases


def main() -> None:
    """Refreshes the expected data for games, players, and teams to match their current outputs."""
    expected_dir = Path(__file__).parent.parent / "tests" / "expected"
    br.options.add_no_hitters = False
    br.options.update_team_names = False
    br.options.update_venue_names = False

    tqdm.write("Refreshing expected game data")
    refresh_games(expected_dir / "games")

    tqdm.write("Refreshing expected player data")
    refresh_players(expected_dir / "players")

    tqdm.write("Refreshing expected team data")
    refresh_teams(expected_dir / "teams")


def refresh_games(games_dir: Path) -> None:
    """Refreshes expected data for games in `games_dir`."""
    for game_id in tqdm(game_test_cases, unit="game"):
        # locate, create target directories
        (original_dir := games_dir / "original" / game_id).mkdir(exist_ok=True)
        (updated_dir := games_dir / "updated" / game_id).mkdir(exist_ok=True)

        # refresh original data
        game = br.Game(game_id)
        game.info.to_csv(original_dir / "info.csv", index=False)
        game.batting.to_csv(original_dir / "batting.csv", index=False)
        game.pitching.to_csv(original_dir / "pitching.csv", index=False)
        game.fielding.to_csv(original_dir / "fielding.csv", index=False)
        game.team_info.to_csv(original_dir / "team_info.csv", index=False)
        game.ump_info.to_csv(original_dir / "ump_info.csv", index=False)
        game.linescore.to_csv(original_dir / "linescore.csv", index=False)
        (original_dir / "players.json").write_text(json.dumps(game.players))
        (original_dir / "teams.json").write_text(json.dumps(game.teams))

        # refresh updated data
        game.add_no_hitters()
        game.update_team_names()
        game.update_venue_names()
        game.info.to_csv(updated_dir / "info.csv", index=False)
        game.pitching.to_csv(updated_dir / "pitching.csv", index=False)
        game.team_info.to_csv(updated_dir / "team_info.csv", index=False)
        game.linescore.to_csv(updated_dir / "linescore.csv", index=False)


def refresh_players(players_dir: Path) -> None:
    """Refreshes expected data for players in `players_dir`."""
    for player_id in tqdm(player_test_cases, unit="player"):
        # locate, create target directories
        (original_dir := players_dir / "original" / player_id).mkdir(exist_ok=True)
        (updated_dir := players_dir / "updated" / player_id).mkdir(exist_ok=True)

        # refresh original data
        player = br.Player(player_id)
        player.info.to_csv(original_dir / "info.csv", index=False)
        player.bling.to_csv(original_dir / "bling.csv", index=False)
        player.batting.to_csv(original_dir / "batting.csv", index=False)
        player.pitching.to_csv(original_dir / "pitching.csv", index=False)
        player.fielding.to_csv(original_dir / "fielding.csv", index=False)
        player.salaries.to_csv(original_dir / "salaries.csv", index=False)
        (original_dir / "relatives.json").write_text(json.dumps(player.relatives))
        (original_dir / "teams.json").write_text(json.dumps(player.teams))

        # refresh updated data
        player.add_no_hitters()
        player.update_team_names()
        player.info.to_csv(updated_dir / "info.csv", index=False)
        player.pitching.to_csv(updated_dir / "pitching.csv", index=False)


def refresh_teams(teams_dir: Path) -> None:
    """Refreshes expected data for the teams in `teams_dir`."""
    teams_list = []
    for team_id in tqdm(team_test_cases, unit="team"):
        # locate, create target directories
        (original_dir := teams_dir / "original" / team_id).mkdir(exist_ok=True)
        (updated_dir := teams_dir / "updated" / team_id).mkdir(exist_ok=True)

        # refresh original data
        team = br.Team(team_id)
        team.info.to_csv(original_dir / "info.csv", index=False)
        team.bling.to_csv(original_dir / "bling.csv", index=False)
        team.batting.to_csv(original_dir / "batting.csv", index=False)
        team.pitching.to_csv(original_dir / "pitching.csv", index=False)
        team.fielding.to_csv(original_dir / "fielding.csv", index=False)
        (original_dir / "players.json").write_text(json.dumps(team.players))

        # refresh updated data
        team.add_no_hitters()
        team.update_team_names()
        team.update_venue_names()
        team.info.to_csv(updated_dir / "info.csv", index=False)
        team.pitching.to_csv(updated_dir / "pitching.csv", index=False)

        teams_list.append(team)
    team_set = br.TeamSet(teams_list)
    team_set.records.to_csv(teams_dir / "records.csv", index=False)


if __name__ == "__main__":
    main()
