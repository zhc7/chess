import requests
import time
import logging
import traceback


API_GET = 'http://www.eanson.work/ai/status?code={code}'
API_SET = 'http://www.eanson.work/cb/status?i={content}&code={code}'
nAPI_GET = 'http://flamechess.cn/js/1/31/fcdbrw.php?id={code}'
nAPI_SET = 'http://flamechess.cn/js/1/31/fcdbrw.php?i={content}&id={code}'
DELAY = 1


class ChessBoard:
    def __init__(self, code, get=API_GET, set=API_SET):
        self.code = code
        self.get_url = get
        self.set_url = set

    def get(self):
        while True:
            try:
                r = requests.get(self.get_url.format(code=self.code))
            except requests.exceptions:
                print('网络异常')
                logging.debug(traceback.format_exc())
                time.sleep(0.1)
            else: #没有异常发生时，将执行else中语句
                break
        return ''.join(filter(lambda x: x in '0zZ', r.content.decode("utf-8")))#解码后得到example：'\ufeff\ufeff0000000z0000Z000ZZZ0Z0Z0Z<br>'，通过筛选去除不需要的字符

    def set(self, content):
        while True:
            try:
                requests.get(self.set_url.format(code=self.code, content=content))
            except requests.exceptions:
                print('网络异常')
                logging.debug(traceback.format_exc())
                time.sleep(0.1)
            else:
                break
        return True


def read_from_file(file):
    '''读取现有棋谱，返回一个哈希表，每个键为上一局面，每个值为键的下一个局面'''
    with open(file, 'r') as f:
        content = f.readlines()
    policies = {}
    for state, index in zip(content, range(len(content))):
        state = state.strip()
        if index % 2 == 0:
            condition = transfer_to_old_form(state)
        else:
            policies[''.join(condition)] = transfer_to_old_form(state)
            policies[''.join(mirror(condition))] = mirror(transfer_to_old_form(state))
    return policies #type:dict key:str value:list example:{'00z000000000Z000ZZZ0Z0Z0Z':['00z00','00Z00','00000','0ZZZ0','Z0Z0Z']}

def mirror(state):
    '''棋盘是左右对称的，将棋盘左右翻转,返回type:list'''
    mirrored = []
    for line in state:
        mirrored_line = line[::-1]
        mirrored.append(mirrored_line)
    return mirrored

def transfer_to_new_form(old_form):
    new_form = []
    new_form[0] = old_form[0][2]
    new_form[1] = old_form[1][1:4]
    new_form[2] = old_form[2][2]
    new_form[3] = old_form[0][1:4]
    new_form[4] = [old_form[0][0], old_form[0][3], old_form[0][5]]
    new_form = [i.replace('0', "'") for i in new_form]
    return ','.join(new_form)


def get_the_board(code):
    '''获取列表0Zz形式的现有棋盘'''
    def tpe(code):
        if code.isdigit():
            return nAPI_GET, nAPI_SET
        else:
            return API_GET, API_SET
    Board = ChessBoard(code, *tpe(code))
    board = Board.get()
    cut_board = []
    for i in range(5):
        cut_board.append(board[0+5*i:5+5*i])
    return cut_board #type:list example:['00000','00z00','00Z00','0ZZZ0','Z0Z0Z']

def set_new_board(code, board):
    '''根据输入的列表0Zz形棋盘，重设网上棋盘'''
    def tpe(code):
        if code.isdigit():
            return nAPI_GET, nAPI_SET
        else:
            return API_GET, API_SET
    Board = ChessBoard(code, *tpe(code))
    filled_board = ''
    for line in board:
        filled_line = line
        filled_board += filled_line #filled_board:str example:'000000Zz00000000ZZZ0Z0Z0Z'
    return Board.set(filled_board) #重设网上棋盘

def transfer_to_old_form(new_form):
    '''将字符串b'v棋盘形式，转换为列表0Zz形式的棋盘 v->z,b->Z'''
    old_form = []
    i = 0
    for line in new_form.split(','):
        line = line.replace("'", '0').replace('v', 'z').replace('b', 'Z')
        if i == 4:
            old_line = '0'.join(list(line))
        else:
            miss = '0' * int((5-len(line))/2) #补位
            old_line = miss + line + miss
        old_form.append(old_line)
        i += 1
    return old_form #type:list example:['00000','0Zz00','00000','0ZZZ0','Z0Z0Z']

def main(code, policy_text):
    policies = read_from_file(policy_text)
    cleared_board = transfer_to_old_form("','v',b,bbb,bbb")
    set_new_board(code, cleared_board)
    last_board = get_the_board(code) #type:list
    while True:
        '''人机交互，人调整棋盘，于是board与last_board不同，然后在policies中搜寻解法，搜到就调整棋盘'''
        board = get_the_board(code)
        if board == last_board:
            continue
        txt_board = ''.join(board) #convert to str
        if txt_board in policies.keys():
            policy = policies[txt_board]
        else:
            print('no match policy')
            policy = board
        set_new_board(code, policy)
        last_board = policy
        time.sleep(DELAY)

if __name__ == '__main__':
    code = input("code:")
    try:
        main(code, '/Users/yinxi/Documents/高研实验室/鹿棋棋谱.txt')
    except:
        logging.debug(traceback.format_exc())
        raise
    
