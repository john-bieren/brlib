"""Tests the output of the `find_asg` function."""

from brlib import find_asg


def test_seasons():
    """Tests that the `seasons` argument is handled correctly."""
    # standard usage
    assert find_asg("2025") == ["2025-allstar-game"]
    # missing season
    assert len(find_asg("1945")) == 0
    # before first ASG
    assert len(find_asg("1932")) == 0
    # two-ASG season
    assert find_asg("1962") == ["1962-allstar-game-1", "1962-allstar-game-2"]
    # range
    assert find_asg("1977-1979") == [
        "1977-allstar-game",
        "1978-allstar-game",
        "1979-allstar-game",
    ]
    # reversed range
    assert find_asg("1971-1973") == find_asg("1973-1971")
    # range with two-ASG
    assert find_asg("1958-1959") == [
        "1958-allstar-game",
        "1959-allstar-game-1",
        "1959-allstar-game-2",
    ]
    # range with missing season
    assert find_asg("2019-2022") == [
        "2019-allstar-game",
        "2021-allstar-game",
        "2022-allstar-game",
    ]
    # range including years before first ASG
    assert find_asg("1930-1935") == [
        "1933-allstar-game",
        "1934-allstar-game",
        "1935-allstar-game",
    ]
