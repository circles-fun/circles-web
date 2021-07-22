# -*- coding: utf-8 -*-

# NOTE: this branch of gulag-web will soon be deprecated
# by the developing api within cmyui/gulag; you should
# refer there instead if you're looking to use our api.
# api docs: https://github.com/JKBGL/gulag-api-docs

__all__ = ()

from cmyui.logging import Ansi
from cmyui.logging import log
from quart import Blueprint
from quart import jsonify
from quart import request

from objects import glob
from objects import utils

api = Blueprint('api', __name__)

""" valid modes, mods, sorts """
valid_modes = frozenset({'std', 'taiko', 'catch', 'mania'})
valid_mods = frozenset({'vn', 'rx', 'ap'})
valid_sorts = frozenset({'tscore', 'rscore', 'pp', 'plays',
                         'playtime', 'acc', 'max_combo'})

"""/get_player_rank"""


@api.route('/get_player_rank')  # GET
async def api_get_player_rank() -> tuple:
    """Return the ranking of a given player."""

    if request.args.get('userid') is None:
        return b'Must provide player id!'

    if not request.args.get('userid').isnumeric():
        return b'Invalid player id.'

    if (
            request.args.get('mode') is None or
            request.args.get('mode') not in valid_modes):
        return b'Must provide mode (std/taiko/mania).'

    if (
            request.args.get('mods') is None or
            request.args.get('mods') not in valid_mods):
        return b'Must provide mod (vn/rx/ap).'

    sql_0 = utils.mode_mods_to_int(
        f"{request.args.get('mods')}_{request.args.get('mode')}")

    q = [
        "SELECT u.id user_id, pp FROM stats"
        "JOIN users u ON stats.id=u.id"
        f"WHERE mode={sql_0}"
        "AND u.priv >= 3"
    ]

    if 'country' in request.args:
        q.append(f"AND country='{request.args.get('country')}'")

    q.append("ORDER BY pp DESC")

    output = await glob.db.fetchall(' '.join(q))

    rank = 1
    for i in range(len(output)):  # loop through ids in order of pp
        if output[i]['user_id'] == int(request.args.get('userid')):
            break
        rank += 1

    # return player rank
    return jsonify({"status": "success",
                    "global_rank": rank,
                    "country_rank": "soon"})


"""/get_player_info"""


@api.route('/get_player_info')  # GET
async def api_get_player_info() -> tuple:
    """Return info on a given player."""

    if 'userid' not in request.args.get('userid'):
        return b'Must provide player id!'

    if not request.args.get('userid').isnumeric():
        return b'Invalid player id.'

    if (
            'mode' not in request.args.get('mode') or
            request.args.get('mode') not in valid_modes):
        return b'Must provide mode (std/taiko/mania).'

    if (
            'mods' not in request.args.get('mods') or
            request.args.get('mods') not in valid_mods):
        return b'Must provide mod (vn/rx/ap).'

    sql_0 = utils.mode_mods_to_int(
        f"{request.args.get('mode')}_{request.args.get('mods')}")

    q = f"SELECT u.id user_id, pp, username, mode, mods, accuracy, max_combo FROM stats JOIN users u ON stats.id=u.id WHERE mode={sql_0} AND u.priv >= 3 ORDER BY pp DESC"

    try:
        rows = await glob.db.fetchall(q)
    except utils.db.DatabaseError as e:
        log.error(f'{Ansi.red(type(e))} - {Ansi.red(e)}')
        return jsonify({'error': str(e)}), 500

    if not rows:
        return jsonify({'error': 'No stats found!'}), 404

    return jsonify({'rank': rows}), 200

    rank = 1
    for i in range(len(output)):  # loop through ids in order of pp
        if output[i]['user_id'] == int(request.args.get('userid')):
            break
        rank += 1

    # return player rank
    return jsonify({"status": "success",
                    "global_rank": rank,
                    "country_rank": "soon"})


""" /get_leaderboard """


@api.route('/get_leaderboard')  # GET
async def get_leaderboard():
    mode = request.args.get('mode', default='std', type=str)
    mods = request.args.get('mods', default='vn', type=str)
    sort_by = request.args.get('sort', default='pp', type=str)
    country = request.args.get('country', default=None, type=str)
    page = request.args.get('page', default=1, type=int)

    if mode not in valid_modes:
        return b'invalid mode! (std, taiko, catch, mania)'

    if mods not in valid_mods:
        return b'invalid mods! (vn, rx, ap)'

    if country is not None and len(country) != 2:
        return b'invalid country!'

    if sort_by not in valid_sorts:
        return b'invalid sort param!'

    sql_0 = utils.mode_mods_to_int(f"{mods}_{mode}")

    q = ['SELECT u.id user_id, u.name username, tscore,',
         'rscore, pp, plays, playtime, acc, max_combo',
         'FROM stats JOIN users u ON stats.id = u.id',
         f'WHERE mode = {sql_0} AND u.priv >=3 AND {sort_by} > 0']

    # TODO: maybe cache the top X scores in the db to get a
    # rough estimate on what is a ridiculous page for a request?
    # (and then cache that number in the db)

    if country is not None:
        q.append(f'AND country = {country}')

    q.append(f'LIMIT {page * 50} OFFSET {int(page - 1) * 50}')

    if glob.config.debug:  # log extra info if in debug mode
        log(' '.join(q), Ansi.LMAGENTA)

    # fetch 50 rows
    output = await glob.db.fetchall(' '.join(q))

    # build the response
    response = {
        'status': 'success',
        'page': page,
        'total_pages': int(len(output) / 50),
        'results': []
    }

    # build the results
    for i in range(len(output)):
        response['results'].append({
            'user_id': output[i]['user_id'],
            'username': output[i]['username'],
            'tscore': output[i]['tscore'],
            'rscore': output[i]['rscore'],
            'pp': output[i]['pp'],
            'plays': output[i]['plays'],
            'playtime': output[i]['playtime'],
            'acc': output[i]['acc'],
            'max_combo': output[i]['max_combo']
        })

    # return the response
    return jsonify(response) if response else b'{}'


""" /get_user_info """


@api.route('/get_user_info')  # GET
async def get_user_info():
    # get request args
    id = request.args.get('id', type=int)
    name = request.args.get('name', type=str)

    # check if required parameters are met
    if not name and not id:
        return b'missing parameters! (id or name)'

    # fetch user info and stats
    # user info
    q = ['SELECT u.id user_id, u.name username, u.safe_name username_safe, u.country, u.priv privileges, '
         'u.silence_end, u.donor_end, u.creation_time, u.latest_activity, u.clan_id, u.clan_priv, '

         # total score
         'tscore_vn_std, tscore_vn_taiko, tscore_vn_catch, tscore_vn_mania, '
         'tscore_rx_std, tscore_rx_taiko, tscore_rx_catch, '
         'tscore_ap_std, '

         # ranked score
         'rscore_vn_std, rscore_vn_taiko, rscore_vn_catch, rscore_vn_mania, '
         'rscore_rx_std, rscore_rx_taiko, rscore_rx_catch, '
         'rscore_ap_std, '

         # pp
         'pp_vn_std, pp_vn_taiko, pp_vn_catch, pp_vn_mania, '
         'pp_rx_std, pp_rx_taiko, pp_rx_catch, '
         'pp_ap_std, '

         # plays
         'plays_vn_std, plays_vn_taiko, plays_vn_catch, plays_vn_mania, '
         'plays_rx_std, plays_rx_taiko, plays_rx_catch, '
         'plays_ap_std, '

         # playtime
         'playtime_vn_std, playtime_vn_taiko, playtime_vn_catch, playtime_vn_mania, '
         'playtime_rx_std, playtime_rx_taiko, playtime_rx_catch, '
         'playtime_ap_std, '

         # accuracy
         'acc_vn_std, acc_vn_taiko, acc_vn_catch, acc_vn_mania, '
         'acc_rx_std, acc_rx_taiko, acc_rx_catch, '
         'acc_ap_std, '

         # maximum combo
         'max_combo_vn_std, max_combo_vn_taiko, max_combo_vn_catch, max_combo_vn_mania, '
         'max_combo_rx_std, max_combo_rx_taiko, max_combo_rx_catch, '
         'max_combo_ap_std '

         # join users
         'FROM stats JOIN users u ON stats.id = u.id']

    # achivement
    q2 = ['''
    SELECT userid, achid FROM user_achievements ua
        INNER JOIN users u ON u.id = ua.userid
    ''']

    # argumnts
    args = []

    # append request arguments (id or name)
    if id:
        q.append('WHERE u.id = %s')
        q2.append('WHERE u.id = %s')
        args.append(id)
    elif name:
        q.append('WHERE u.safe_name = %s')
        q2.append('WHERE u.safe_name = %s')
        args.append(utils.get_safe_name(name))

    q2.append('ORDER BY ua.achid ASC')

    if glob.config.debug:
        log(' '.join(q), Ansi.LGREEN)
    res = await glob.db.fetch(' '.join(q), args)
    res_ach = await glob.db.fetch(' '.join(q2), args)
    return jsonify(userdata=res, achivement=res_ach) if res else b'{}'


""" /get_player_scores """


@api.route('/get_player_scores')  # GET
async def get_player_scores():
    # get request args
    id = request.args.get('id', type=int)
    mode = request.args.get('mode', type=str)
    mods = request.args.get('mods', type=str)
    sort = request.args.get('sort', type=str)
    limit = request.args.get('limit', type=int)

    # check if required parameters are met
    if not id:
        return b'missing parameters! (id)'

    if sort == 'recent':
        sort = 'id'
    elif sort == 'best':
        sort = 'pp'
    else:
        return b'invalid sort! (recent or best)'

    if mods not in valid_mods:
        return b'invalid mods! (vn, rx, ap)'

    if (mode := utils.convert_mode_int(mode)) is None:
        return b'invalid mode type! (std, taiko, catch, mania)'

    if not limit:
        limit = 50

    # fetch scores
    q = [f'SELECT scores_{mods}.*, maps.* '
         f'FROM scores_{mods} JOIN maps ON scores_{mods}.map_md5 = maps.md5']
    q2 = [f'SELECT COUNT(scores_{mods}.id) AS result '
          f'FROM scores_{mods} JOIN maps ON scores_{mods}.map_md5 = maps.md5']

    # argumnts
    args = []

    q.append(f'WHERE scores_{mods}.userid = %s '
             f'AND scores_{mods}.mode = {mode} '
             f'AND maps.status = 2')
    q2.append(f'WHERE scores_{mods}.userid = %s '
              f'AND scores_{mods}.mode = {mode}')
    if sort == 'pp':
        q.append(f'AND scores_{mods}.status = 2')
        q2.append(f'AND scores_{mods}.status = 2')
    q.append(f'ORDER BY scores_{mods}.{sort} DESC '
             f'LIMIT {limit}')
    args.append(id)

    if glob.config.debug:
        log(' '.join(q), Ansi.LGREEN)
        log(' '.join(q2), Ansi.LGREEN)
    res = await glob.db.fetchall(' '.join(q), args)
    limit = await glob.db.fetch(' '.join(q2), args)
    return jsonify(scores=res, limit=limit['result']) if res else jsonify(scores=[], limit=limit['result'])


""" /get_player_most """


@api.route('/get_player_most')  # GET
async def get_player_most():
    # get request args
    id = request.args.get('id', type=int)
    mode = request.args.get('mode', type=str)
    mods = request.args.get('mods', type=str)
    limit = request.args.get('limit', type=int)

    # check if required parameters are met
    if not id:
        return b'missing parameters! (id)'

    if mods not in valid_mods:
        return b'invalid mods! (vn, rx, ap)'

    if (mode := utils.convert_mode_int(mode)) is None:
        return b'invalid mode type! (std, taiko, catch, mania)'

    if not limit:
        limit = 50

    # fetch scores
    q = [
        f'SELECT scores_{mods}.mode, scores_{mods}.map_md5, maps.artist, maps.title, maps.set_id, maps.creator, COUNT(*) AS `count` '
        f'FROM scores_{mods} JOIN maps ON scores_{mods}.map_md5 = maps.md5']

    # argumnts
    args = []

    q.append(
        f'WHERE userid = %s AND scores_{mods}.mode = {mode} GROUP BY map_md5')
    q.append(f'ORDER BY COUNT DESC '
             f'LIMIT {limit}')
    args.append(id)

    if glob.config.debug:
        log(' '.join(q), Ansi.LGREEN)
    res = await glob.db.fetchall(' '.join(q), args)
    return jsonify(maps=res) if res else jsonify(maps=[])


@api.route('/get_user_grade')  # GET
async def get_user_grade():
    # get request stuff
    mode = request.args.get('mode', default='std', type=str)
    mods = request.args.get('mods', default='rx', type=str)
    id = request.args.get('id', type=int)

    # validate everything

    if (mode := utils.convert_mode_int(mode)) is None:
        return b'invalid mode type! (std, taiko, catch, mania)'

    if mods not in valid_mods:
        return b'invalid mods! (vn, rx, ap)'

    if not id:
        return b'missing id!'

    # get all scores
    q = f'SELECT grade FROM scores_{mods} WHERE mode = {mode} AND userid = %s'

    scores = await glob.db.fetchall(q, [id])

    grades = {
        "x": 0,
        "xh": 0,
        "s": 0,
        "sh": 0,
        "a": 0
    }

    if not scores:
        return jsonify(grades)

    # count
    for score in (x for x in scores if x['grade'].lower() in grades):
        grades[score['grade'].lower()] += 1

    if glob.config.debug:
        log(q, Ansi.LGREEN)
    # return
    return jsonify(grades)
