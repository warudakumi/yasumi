import re

from parse import parse, search
import numpy as np

from util import pick
from coc.diceroll import dice, judge
from coc.temp_insan_7th import temp_insan
from coc.ind_insan_7th import ind_insan


class CthulhuMessenger():

    def __init__(self, charactors):
        self.temp_insan = temp_insan 
        self.ind_insan = ind_insan
        self.charactors = charactors
        self.on_cheat = False


    def call(self, input_msg, player):
        charactor = self.charactors[player]

        if input_msg.startswith('/dice'):
            return self.__simple_dice(input_msg)
        elif input_msg.startswith('/ci'):
            return self.__charactor_introduce(charactor)
        elif input_msg.startswith('/cm'):
            return self.__charactor_create()
        elif input_msg.startswith('/indef'):
            return self.__get_ind_insan() 
        elif input_msg.startswith('/temp'):
            return self.__get_temp_insan()
        elif input_msg.startswith('/set'):
            return self.__set_status(input_msg, charactor)
        elif input_msg.startswith('/'):
            return self.__skill_roll(input_msg, charactor)
        else:
            return None


    def switch_cheat(self):
        if not self.on_cheat:
            self.on_cheat = True
        else:
            self.on_cheat = False


    def __set_status(self, input_msg, charactor):

        def get_parameters(msg):
            skill_name, parsed_correction = parse('{} {}', msg).fixed
            result = {}
            result['skill_name'] = skill_name

            for opt in ['+', '-', '*', '/']:
                if opt in parsed_correction:
                    correction = pick(opt+'{:d}', parsed_correction) 
                    result['correction'] = (opt, correction) 
                    break
                else:
                    continue

            return result

        input_msg, = parse('/set {}', input_msg)
        roll_info = get_parameters(input_msg)
        skill_name = roll_info['skill_name']
        operator = ' ' + roll_info['correction'][0]
        correction = roll_info['correction'][1]

        current_status = charactor[skill_name]['value']
        query = str(current_status) + operator + str(correction) 
        new_status = eval(query)
        charactor[skill_name]['value'] = new_status
        msg = '[ステータス変動]\n'\
                '<{skill_name}>: [{current_status}]{operator}{correction} '\
                '-> [{new_status}]'\
                .format(
                        skill_name = skill_name,
                        current_status = current_status,
                        operator = operator,
                        correction = correction,
                        new_status = new_status
                        )

        return msg


    def __get_temp_insan(self):
        msg = '[一時的狂気]\n'
        msg += self.temp_insan[dice(1, 20)[0]]
        msg += '\n-> ' + str(dice(1, 10)+4) \
                + 'ラウンドまたは' + str(dice(1, 6)*10+30) + '分'
        return msg


    def __get_ind_insan(self):
        msg = '[不定の狂気]\n'
        msg += self.ind_insan[dice(1, 10)[0]]
        msg += '\n-> ' + str(dice(1, 10)*10) + '時間'
        return msg


    def __charactor_introduce(self, charactor):
        status = {}
        status['探索者名'] = charactor['NAME']['value']
        status['STR'] = charactor['STR']['value']
        status['CON'] = charactor['CON']['value']
        status['SIZ'] = charactor['SIZ']['value']
        status['DEX'] = charactor['DEX']['value']
        status['APP'] = charactor['APP']['value']
        status['INT'] = charactor['INT']['value']
        status['POW'] = charactor['POW']['value']
        status['EDU'] = charactor['EDU']['value']
        status['SAN'] = charactor['SAN']['value']
        status['MP'] = charactor['MP']['value']
        status['幸運'] = charactor['幸運']['value']
        status['耐久力'] = charactor['耐久力']['value']
        status['db'] = charactor['db']['value']
        status['MOV'] = charactor['MOV']['value']

        msg = '[探索者紹介]\n'
        for k, v in zip(status.keys(), status.values()):
            msg += '{k}: {v} \n'.format(k=k, v=v)
        return msg


    def __skill_roll(self, input_msg, charactor):

        def get_parameters(msg):
            result = {}
            skill_name = pick('/{:w}', msg)
            result['skill_name'] = skill_name

            parsed_msg, = parse('/{}', msg).fixed
            result['correction'] = None
            for opt in ['+', '-', '*', '/']:
                if opt in parsed_msg:
                    correction = pick(opt+'{:d}', parsed_msg) 
                    result['correction'] = (opt, correction) 
                    break
                else:
                    continue

            result['bonus'] = pick('b{:d}', msg) if pick('b{:d}', msg) else 0 
            result['penalty'] = pick('p{:d}', msg) if pick('p{:d}', msg) else 0 
            return result

        roll_info = get_parameters(input_msg)
        skill_name = roll_info['skill_name']
        skill_value = charactor[skill_name]['value'] 
        operator = ''
        correction = ''

        if roll_info['correction']:
            operator = ' ' + roll_info['correction'][0]
            correction = roll_info['correction'][1]
            query = str(skill_value) + operator + str(correction) 
            skill_value = eval(query)

        dice_num = int(charactor[skill_name]['dice_num'])
        dice_size = int(charactor[skill_name]['dice_size'])
        dice_value = dice(dice_num, dice_size).min() if not self.on_cheat else np.sum(dice(1, 3))
        result = judge(dice_value, int(skill_value), roll_info['bonus'], roll_info['penalty'])
        msg = '[技能ロール]\n'\
                '<{skill_name}>{operator}{correction} = [{skill_value}] '\
                '-> {result_value}: **{result_msg}**'\
              .format(
                      skill_name = skill_name,
                      operator = operator,
                      correction = correction,
                      skill_value = skill_value,
                      result_value = result[1],
                      result_msg = result[0]
                      )

        return msg


    def __simple_dice(self, input_msg):

        def single_dice(msg):
            dice_info = msg.split('d')
            dice_num = int(dice_info[0])
            dice_size = int(dice_info[1])
            return dice(dice_num, dice_size) 


        def get_parameters(msg):
            result = {}
            parsed_msg, = parse('/dice {}', msg).fixed

            plus_dice = re.findall('\A\d{1,2}d\d{1,3}|(?<=\+)\d{1,2}d\d{1,3}', parsed_msg)
            minus_dice = re.findall('(?<=\-)\d{1,2}d\d{1,3}', parsed_msg)
            plus_opt = re.findall('(?<=\+)\d{1,2}(?!d)', parsed_msg)
            minus_opt = re.findall('(?<=\-)\d{1,2}(?!d)', parsed_msg)

            result['plus_dice'] = tuple(plus_dice)
            result['minus_dice'] = tuple(minus_dice) if minus_dice else None
            result['plus_opt'] = tuple(plus_opt) if plus_opt else None
            result['minus_opt'] = tuple(minus_opt) if minus_opt else None

            result['bonus'] = pick('b{:d}', msg) if pick('b{:d}', msg) else 0 
            result['penalty'] = pick('p{:d}', msg) if pick('p{:d}', msg) else 0 
            
            result['target'] = pick('({:d})', msg) if pick('({:d})', msg) else None
            result['secret'] = True if 'secret' in msg else False
            return result

        input_msg = input_msg.replace('|', '')
        roll_info = get_parameters(input_msg)

        dice_plus = np.concatenate(np.array([single_dice(d) for d in roll_info['plus_dice']]))
        dice_minus = np.concatenate(np.array([single_dice(d) for d in roll_info['minus_dice']])) \
                if roll_info['minus_dice'] else np.array(0)
        opt_plus = np.array([int(v) for v in roll_info['plus_opt']]) if roll_info['plus_opt'] else np.array(0)
        opt_minus = np.array([int(v) for v in roll_info['minus_opt']]) if roll_info['minus_opt'] else np.array(0) 

        dice_sum = np.sum(dice_plus)\
                - np.sum(dice_minus)\
                + np.sum(opt_plus)\
                - np.sum(opt_minus) if not self.on_cheat else np.sum(dice(1, 3)) 
        is_secret = roll_info['secret']

        if roll_info['target']:
            result = judge(dice_sum, roll_info['target'], roll_info['bonus'], roll_info['penalty'])
            msg = '[ダイスロール(目標値あり)]\n'\
                    '<目標値: {target}> '\
                    '-> {result_value}: **{result_msg}**'\
                    .format(
                            target = roll_info['target'] if not is_secret else str('||') + str(roll_info['target']) + str('||'),
                            result_value = result[1] if not is_secret else str('||') + str(result[1]) + str('||'),
                            result_msg = result[0] if not is_secret else str('||') + str(result[0]) + str('||')
                            )
            return msg

        else:
            msg = '[ダイスロール]\n'\
                    '-> {result_value}'\
                    .format(
                            result_value = dice_sum
                            )

        return msg


    def __charactor_create(self):
        status = {}
        status['STR'] = 5 * np.sum(dice(3, 6))
        status['CON'] = 5 * np.sum(dice(3, 6))
        status['SIZ'] = 5 * (np.sum(dice(2, 6)) + 6)
        status['DEX'] = 5 * np.sum(dice(3, 6))
        status['APP'] = 5 * np.sum(dice(3, 6))
        status['INT'] = 5 * (np.sum(dice(2, 6)) + 6)
        status['POW'] = 5 * np.sum(dice(3, 6))
        status['EDU'] = 5 * (np.sum(dice(2, 6)) + 6)
        status['SAN'] = status['POW']
        status['MP'] = int(status['POW'] / 5)
        status['幸運'] = 5 * np.sum(dice(3, 6))
        status['耐久力'] = int((status['CON'] + status['SIZ']) / 10)
        
        ATK = status['STR'] + status['SIZ']

        if 2 <= ATK and ATK <= 64:
            status['db'] = '-2'
            status['ビルド'] = -2
        elif 65 <= ATK and ATK <= 84:
            status['db'] = '-1'
            status['ビルド'] = -1
        elif 85 <= ATK and ATK <= 124:
            status['db'] = '+0'
            status['ビルド'] = 0
        elif 125 <= ATK and ATK <= 164:
            status['db'] = '+1d4'
            status['ビルド'] = 1
        elif 165 <= ATK and ATK <= 204:
            status['db'] = '+1d6'
            status['ビルド'] = 2

        if status['DEX'] < status['SIZ'] and status['STR'] < status['SIZ']:
            status['MOV'] = 7
        elif status['DEX'] > status['SIZ'] and status['STR'] > status['SIZ']:
            status['MOV'] = 9
        else:
            status['MOV'] = 8

        msg = '[探索者作成]\n'
        for k, v in zip(status.keys(), status.values()):
            msg += '{k}: {v} \n'.format(k=k, v=v)
        return msg

