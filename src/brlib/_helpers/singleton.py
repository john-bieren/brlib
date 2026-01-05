#!/usr/bin/env python3

"""Defines Singleton class."""

class Singleton:
    """Parent for singleton classes."""
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
