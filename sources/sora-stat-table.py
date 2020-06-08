#!/usr/bin/env python3
# Copyright 2020 Google Sans Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont

UPRIGHT_AXES = [
    dict(
        tag="wght",
        name="Weight",
        ordering=0,
        values=[
            dict(value=100, name="Thin"),  # Thin
            dict(value=200, name="ExtraLight"),  # ExtraLight
            dict(value=300, name="Light"),  # Light
            dict(value=400, name="Regular", flags=0x2),  # Regular
            dict(value=600, name="SemiBold"),  # SemiBold
            dict(value=700, name="Bold"),  # Bold
            dict(value=800, name="ExtraBold"),  # ExtraBold
        ],
    ),
]


VARIABLE_DIR = "../fonts/variable"
VR_UPRIGHT = f"{VARIABLE_DIR}/Sora[wght].ttf"


def main():
    filepath = VR_UPRIGHT
    tt = TTFont(filepath)
    buildStatTable(tt, UPRIGHT_AXES)
    tt.save(filepath)
    print(f"[STAT TABLE] Added STAT table to {filepath}")


if __name__ == "__main__":
    main()
