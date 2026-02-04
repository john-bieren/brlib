#!/usr/bin/env python3

"""Tests the output of the find_asg function."""

from brlib import find_asg


def test_seasons():
    """Tests that seasons argument is handled correctly."""
    # standard usage
    assert find_asg("2025") == [("allstar", "2025", "0")]
    # missing season
    assert len(find_asg("1945")) == 0
    # before first ASG
    assert len(find_asg("1932")) == 0
    # two-ASG season
    assert find_asg("1962") == [("allstar", "1962", "1"), ("allstar", "1962", "2")]
    # range
    assert find_asg("1977-1979") == [
        ("allstar", "1977", "0"),
        ("allstar", "1978", "0"),
        ("allstar", "1979", "0"),
    ]
    # reversed range
    assert find_asg("1971-1973") == find_asg("1973-1971")
    # range with two-ASG
    assert find_asg("1958-1959") == [
        ("allstar", "1958", "0"),
        ("allstar", "1959", "1"),
        ("allstar", "1959", "2"),
    ]
    # range with missing season
    assert find_asg("2019-2022") == [
        ("allstar", "2019", "0"),
        ("allstar", "2021", "0"),
        ("allstar", "2022", "0"),
    ]
    # range including years before first ASG
    assert find_asg("1930-1935") == [
        ("allstar", "1933", "0"),
        ("allstar", "1934", "0"),
        ("allstar", "1935", "0"),
    ]
