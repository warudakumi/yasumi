from parse import parse

from util import get_gs


def load_charactors(gs):
    worksheets = gs.worksheets()
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


def set_value_to_gs(gs, player_name, skill_val_map, init=True):
    worksheet = gs.worksheet(player_name)

    key_range = 'A2:A16' if init else 'A2:A90'
    target_range = 'D2:D16' if init else 'B2:B90'

    cells_key = worksheet.range(key_range)
    cells_key = [cell.value for cell in cells_key]
    cells_target = worksheet.range(target_range)
    cells_update = []

    for skill_name, skill_val in skill_val_map.items():
        try:
            key_idx = cells_key.index(skill_name)
            cells_update.append(cells_target[key_idx])
            cells_update[-1].value = str(skill_val)
        except Exception as e:
            print(e)
            continue

    worksheet.update_cells(cells_update)

