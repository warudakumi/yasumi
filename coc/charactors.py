from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from parse import parse
import gspread


def get_gs(json_file, doc_id):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    credentials = ServiceAccountCredentials\
            .from_json_keyfile_name(json_file, scopes=scopes)
    http_auth = credentials.authorize(Http())

    gs = gspread.authorize(credentials)
    gfile = gs.open_by_key(doc_id)

    return gfile

def load_charactors(conf):
    gfile = get_gs(conf['json_file'], conf['doc_id'])
    worksheets = gfile.worksheets()

    charactors = {} 
    for ws in worksheets:
        charactor = {}
        cell_keys = ws.col_values(1)
        cell_values = ws.col_values(2)
        cell_dice = ws.col_values(7)
        for k, v, d in zip(cell_keys, cell_values, cell_dice):
            if d == 'dice':
                dice_num, dice_size = 0, 0

            else:
                dice_info = parse('{}d{}', d)
                dice_num = dice_info[0]
                dice_size = dice_info[1]

            charactor[k] = {
                'value': v,
                'dice_num': dice_num,
                'dice_size': dice_size
            }

        player_name = ws.title
        charactors[player_name] = charactor

    return charactors

