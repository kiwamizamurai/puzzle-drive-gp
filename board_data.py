from constants import COL_CYAN, COL_GREEN, COL_ORANGE


def make_rookie_board():
    return {
        "name": "ROOKIE LOOP",
        "tile_count": 20,
        "theme_col": COL_GREEN,
        "rival_template_ids": ["spark_red", "wave_blue", "vine_green"],
        "rival_level": 3,
    }


def make_normal_board():
    return {
        "name": "CIRCUIT RUSH",
        "tile_count": 24,
        "theme_col": COL_CYAN,
        "rival_template_ids": ["novice_red", "novice_blue", "novice_yellow"],
        "rival_level": 6,
    }


def make_hard_board():
    return {
        "name": "CHAMPION TRACK",
        "tile_count": 28,
        "theme_col": COL_ORANGE,
        "rival_template_ids": ["blaze_red", "torrent_blue", "thunder_yellow"],
        "rival_level": 10,
    }


BOARDS = [make_rookie_board(), make_normal_board(), make_hard_board()]
