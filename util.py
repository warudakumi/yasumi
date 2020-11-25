from parse import search
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
import gspread


def get_gs(json_file, doc_id):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    credentials = ServiceAccountCredentials\
            .from_json_keyfile_name(json_file, scopes=scopes)
    http_auth = credentials.authorize(Http())

    gs = gspread.authorize(credentials)
    gfile = gs.open_by_key(doc_id)

    return gfile


def pick(token, input_msg):
    result = search(token, input_msg)
    if result is not None:
        result, = result.fixed
        return result
    else:
        return None

