# -*- coding: utf-8 -*-

from typing import Optional

from cmyui.logging import Ansi
from cmyui.logging import log
from quart import render_template

from objects import glob


async def flash(status, msg, template):
    """Flashes a success/error message on a specified template."""
    return await render_template(f'{template}.html', flash=msg, status=status)


def mode_mods_to_int(mode: str) -> int:
    """Converts mode_mods (str) to mode_mods (int)."""

    # NOTE: This is a temporary function to convert the leaderboard mode to an int.
    # It will be removed when the site is fully converted to use the new
    # stats table.

    for mode_num, mode_str in enumerate((
        'vn_std', 'vn_taiko', 'vn_catch', 'vn_mania',
        'rx_std', 'rx_taiko', 'rx_catch',
        'ap_std'
    )):
        if mode == mode_str:
            return mode_num
    else:
        return 0

from typing import TYPE_CHECKING

from cmyui.logging import Ansi
from cmyui.logging import log
from pathlib import Path
from quart import render_template
from quart import session

from objects import glob
from objects import utils

if TYPE_CHECKING:
    from PIL import Image

async def flash(status: str, msg: str, template: str) -> str:
    """Flashes a success/error message on a specified template."""
    return await render_template(f'{template}.html', flash=msg, status=status)

async def flash_with_customizations(status: str, msg: str, template: str) -> str:
    """Flashes a success/error message on a specified template. (for customisation settings)"""
    profile_customizations = utils.has_profile_customizations(session['user_data']['id'])
    return await render_template(
        template_name_or_list=f'{template}.html',
        flash=msg,
        status=status,
        customizations=profile_customizations
    )

def get_safe_name(name: str) -> str:
    """Returns the safe version of a username."""
    return name.lower().replace(' ', '_')

def convert_mode_int(mode: str) -> Optional[int]:
    """Converts mode (str) to mode (int)."""
    if mode not in _str_mode_dict:
        print('invalid mode passed into utils.convert_mode_int?')
        return
    return _str_mode_dict[mode]

_str_mode_dict = {
    'std': 0,
    'taiko': 1,
    'catch': 2,
    'mania': 3
}

def convert_mode_str(mode: int) -> Optional[str]:
    """Converts mode (int) to mode (str)."""
    if mode not in _mode_str_dict:
        print('invalid mode passed into utils.convert_mode_str?')
        return
    return _mode_str_dict[mode]

_mode_str_dict = {
    0: 'std',
    1: 'taiko',
    2: 'catch',
    3: 'mania'
}

async def fetch_geoloc(ip: str) -> str:
    """Fetches the country code corresponding to an IP."""
    url = f'http://ip-api.com/line/{ip}'

    async with glob.http.get(url) as resp:
        if not resp or resp.status != 200:
            if glob.config.debug:
                log('Failed to get geoloc data: request failed.', Ansi.LRED)
            return 'xx'
        status, *lines = (await resp.text()).split('\n')
        if status != 'success':
            if glob.config.debug:
                log(f'Failed to get geoloc data: {lines[0]}.', Ansi.LRED)
            return 'xx'
        return lines[1].lower()

async def validate_captcha(data: str) -> bool:
    """Verify `data` with hcaptcha's API."""
    url = f'https://hcaptcha.com/siteverify'

    data = {
        'secret': glob.config.hCaptcha_secret,
        'response': data
    }

    async with glob.http.post(url, data=data) as resp:
        if not resp or resp.status != 200:
            if glob.config.debug:
                log('Failed to verify captcha: request failed.', Ansi.LRED)
            return False

        res = await resp.json()

        return res['success']

def get_required_score_for_level(level: int) -> float:
	if level <= 100:
		if level >= 2:
			return 5000 / 3 * (4 * (level ** 3) - 3 * (level ** 2) - level) + 1.25 * (1.8 ** (level - 60))
		elif level <= 0 or level == 1:
			return 1.0  # Should be 0, but we get division by 0 below so set to 1
	elif level >= 101:
		return 26931190829 + 1e11 * (level - 100)

def get_level(totalScore: int) -> int:
	level = 1
	while True:
		# Avoid endless loops
		if level > 120:
			return level

		# Calculate required score
		reqScore = get_required_score_for_level(level)

		# Check if this is our level
		if totalScore <= reqScore:
			# Our level, return it and break
			return level - 1
		else:
			# Not our level, calculate score for next level
			level += 1

BANNERS_PATH = Path.cwd() / '.data/banners'
BACKGROUND_PATH = Path.cwd() / '.data/backgrounds'
def has_profile_customizations(user_id: int = 0) -> dict[str, bool]:
    # check for custom banner image file
    for ext in ('jpg', 'jpeg', 'png', 'gif'):
        path = BANNERS_PATH / f'{user_id}.{ext}'
        if has_custom_banner := path.exists():
            break

    # check for custom background image file
    for ext in ('jpg', 'jpeg', 'png', 'gif'):
        path = BACKGROUND_PATH / f'{user_id}.{ext}'
        if has_custom_background := path.exists():
            break

    return {
        'banner' : has_custom_banner,
        'background': has_custom_background
    }

def crop_image(image: 'Image') -> 'Image':
    width, height = image.size
    if width == height:
        return image

    offset = int(abs(height-width) / 2)

    if width > height:
        image = image.crop([offset, 0, width-offset, height])
    else:
        image = image.crop([0, offset, width, height-offset])

    return image
