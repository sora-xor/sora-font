"""
    Script to use statmake to add STAT table to Sora. Based on Stepehn Nixon's Merriweather script.
"""

import sys
import statmake.classes
import statmake.lib
from fontTools.ttLib import TTFont

font_path = sys.argv[1]

STAT = {
    "axes": [
        {
            "name": "Weight",
            "tag": "wght",
            "locations": [
                {
                    "name": "Thin",
                    "value": 100
                },
                {
                    "name": "ExtraLight",
                    "value": 200
                },
                {
                    "name": "Light",
                    "value": 300
                },
                {
                    "name": "Regular",
                    "value": 400,
                    "linked_value": 700,
                    "flags": ["ElidableAxisValueName"]
                },
                {
                    "name": "SemiBold",
                    "value": 600
                },
                {
                    "name": "Bold",
                    "value": 700
                },
                {
                    "name": "ExtraBold",
                    "value": 800
                }
            ]
        }
    ]
}


def makeStylespace(font_path):

    stylespace = statmake.classes.Stylespace.from_dict(STAT)

    font = TTFont(font_path)

    statmake.lib.apply_stylespace_to_variable_font(
        stylespace=stylespace,
        varfont=font,
        additional_locations=addedLocs
    )
    font.save(font_path)


makeStylespace(font_path)