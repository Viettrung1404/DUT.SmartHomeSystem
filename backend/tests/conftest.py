"""Shared pytest configuration for the current backend package layout.

Most current backend tests either build their own fixtures or exercise pure
service helpers. Keep this file intentionally lightweight so stale imports do
not prevent focused test modules from running.
"""
