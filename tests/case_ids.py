"""Defines lists of test case IDs."""

game_test_cases = [
    # ASG with doubleheader (technically), 10 innings
    "1961-allstar-game-1",
    # ASG, essentially a forfeit, illegal(?) substitution with 1 position and split stats
    "2025-allstar-game",
    # Ohtani plays DH and SP
    "ANA202305090",
    # illegal substitution with 2 positions and split stats, error by pitcher who didn't hit
    "BOS201708250",
    # renamed team, wind "in unknown direction", Colt .45s table id special case
    "CHN196207291",
    # Boom-Boom Beck tests parsing, renamed team, three umps, four OFA
    "CLE192805010",
    # renamed venue, renamed team, relocated team
    "FLO199407290",
    # both teams share names with later ones, limited stats (like SB info), doubleheader, one ump
    "MLA190105301",
    # unassisted triple play
    "NYN200908230",
    # combined no-hitter, WS game (matters for name)
    "PHI202211020",
    # dh = 3, 6 innings, 2 CGs with IP<9, two umps
    "PIT192010023",
    # player with 2 DP, U L Washington tests parsing, 2 identical POCS, renamed venue, doubleheader,
    # DP including pitcher who didn't hit
    "SEA197805231",
    # renamed team, renamed venue, game played at away team's venue
    "SEA201106250",
    # perfect game, renamed venue
    "SEA201208150",
    # triple play, renamed venue, outfield assists
    "SEA201804190",
    # SB cycle with multiple pitcher/catcher combos, a balk
    "SEA201905270",
    # non-WS postseason game (matters for name), 18 innings, unassisted DP
    "SEA202210150",
    # forfeited by team that finished with the lead, 4 innings, doubleheader
    "SLN190710051",
]

player_test_cases = [
    # tons of relatives (including a manager), two missing seasons
    "aloumo01",
    # lots of missing data (especially advanced pitching)
    "bendech01",
    # very little information
    "colli05",
    # born and died in Canada (tests province parsing)
    "cormirh01",
    # multiple AS in certain seasons, catcher (more fielding stats)
    "gibsojo99",
    # regular season and postseason no-hitter
    "hallaro01",
    # lots of postseason stats
    "jacksre01",
    # only played in postseason, drafted multiple times
    "kigerma01",
    # multiple combined no-hitters (in one season, even), multiple high schools
    "pressry01",
    # catcher (with modern fielding stats), renamed draft team
    "vogtst01",
    # no birthplace, incomplete birth and debut dates, but full death info
    "willist03",
]

team_test_cases = [
    # four managers, limited data, partial park factors, no awards
    "BBB1924",
    # non-AL/NL pennant winner, players with multiple AS
    "BEG1939",
    # team gold glove, pandemic season
    "CHC2020",
    # no player stats available
    "COT1932",
    # WS winner, renamed venue, CNH in regular and postseason
    "HOU2022",
    # renamed team
    "LAA2012",
    # same franchise ID as WSH1904 but different team ID (tests TeamSet.records), DH never fielded
    "MIN2019",
    # multiple venues (including a renamed one)
    "PHI1894",
    # perfect game and CNH, renamed venue
    "SEA2012",
    # team shares name with later one
    "WSH1904",
]
