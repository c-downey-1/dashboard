"""Shared APHIS poultry category definitions used across chartbook."""

from __future__ import annotations


HPAI_CATEGORY_GROUPS = {
    "Commercial Layers": (
        "Commercial Table Egg Layer",
        "Commercial Table Egg Pullets",
        "Commercial Table Egg Breeder",
    ),
    "Commercial Broiler": (
        "Commercial Broiler Production",
        "Commercial Broiler Breeder",
        "Commercial Broiler Breeder Pullets",
        "Primary Broiler Breeder Pedigree Farm",
        "Commercial Breeder Operation",
    ),
    "Commercial Turkey": (
        "Commercial Turkey Meat Bird",
        "Commercial Turkey Breeder Hens",
        "Commercial Turkey Breeder Replacement Hens",
        "Commercial Turkey Breeder Toms",
        "Commercial Turkey Poult Supplier",
    ),
    "Commercial Duck": (
        "Commercial Duck Meat Bird",
        "Commercial Duck Breeder",
    ),
    "Commercial Other": (
        "Commercial Breeder (Multiple Bird Species)",
        "Commercial Upland Gamebird Producer",
        "Commercial Raised for Release Upland Game Bird",
        "Commercial Raised for Release Waterfowl",
    ),
    "Other": (
        "Live Bird Market",
        "Live Bird Sales  (non-slaughter)",
        "WOAH Poultry",
        "WOAH Non-Poultry",
    ),
}

COMMERCIAL_LAYER_TYPES = HPAI_CATEGORY_GROUPS["Commercial Layers"]
ALL_POULTRY_PRODUCTION_TYPES = tuple(
    production
    for members in HPAI_CATEGORY_GROUPS.values()
    for production in members
)
