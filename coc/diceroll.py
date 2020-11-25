import numpy as np


def dice(dice_num, dice_size):
    result = np.random.randint(1, int(dice_size+1), int(dice_num))
    return result


def judge(dice_value, skill_value, bonus=0, penalty=0):

    def get_achivement(dice_value, skill_value):
        if dice_value == 1:
            return 'Critical'
        elif dice_value <= int(skill_value / 5):
            return 'Extreme'
        elif dice_value <= int(skill_value / 2):
            return 'Hard'
        elif dice_value <= skill_value:
            return 'Regular'
        elif dice_value >= 96:
            return 'Failure(Fumble)'
        else:
            return 'Failure'

    if bonus == penalty:
        pass

    else:
        one_place = int(str(dice_value)[-1])
        ten_place = int(str(dice_value)[:-1]) if len(str(dice_value)) > 1 else 0   

        if bonus > penalty:
            addition = (dice(int(bonus-penalty), 10) - 1).min() 
            dice_value = 10 * min(ten_place, addition) + one_place 

        else:
            addition = (dice(int(penalty-bonus), 10) - 1).max() 
            dice_value = 10 * max(ten_place, addition) + one_place 

    achivement = get_achivement(dice_value, skill_value)

    return (achivement, dice_value) 

