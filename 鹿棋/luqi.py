import requests
import time
import logging
import traceback
import configparser


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


def read_from_file(config):
    '''读取现有棋谱，返回一个哈希表，每个键为上一局面，每个值为键的下一个局面'''
    if config['read_continuously'] == 'True':
        return read_continuously(config['policy_file'],config)
    with open(config['policy_file'], 'r') as f:
        content = f.readlines()
    policies = {}
    for state, index in zip(content, range(len(content))):
        state = transfer_to_old_form(state.strip(), config)
        if index % 2 == 0:
            condition = state
        else:
            for c, p in zip(transform(condition,config), transform(state, config)):
                c = ''.join(transfer_to_board_size(c, config))
                p = transfer_to_board_size(p, config)
                policies[c] = p
    return policies #type:dict key:str value:list example:{'00z000000000Z000ZZZ0Z0Z0Z':['00z00','00Z00','00000','0ZZZ0','Z0Z0Z']}

def transfer_to_board_size(reading_size_board,config):
    '''接收0Zz型reading_size的list棋盘，转换为0Zz型board_size的list棋盘'''
    filled_board = ''
    X, Y = eval(config['board_size'])
    x, y = eval(config['reading_size'])
    y_fill = int((Y - y) / 2)   #纵向需要填充的行数
    x_fill = int((X - x) / 2)   #横向需要填充的空格数
    filled_board += y_fill * X * '0'    #填充空行
    for line in reading_size_board:
        filled_line = x_fill * '0' + line    #前面填充
        filled_line += (X - len(filled_line)) * '0'     #后面补齐
        filled_board += filled_line #filled_board:str example:'000000Zz00000000ZZZ0Z0Z0Z'
    filled_board += (X * Y - len(filled_board)) * '0'   #补齐整个棋盘
    new_board=[filled_board[i:i+5] for i in range(len(filled_board)) if i%5==0]
    return new_board

def read_continuously(file,config):
    '''用连续方式读取棋谱，即下一行的状态是上一行状态的策略'''
    with open(file, 'r') as f:
        content = f.readlines()
    policies = {}
    for state, index in zip(content, range(len(content))):
        state = transfer_to_old_form(state.strip(),config)
        if index == 0:
            condition = state
            continue
        for c, p in zip(transform(condition,config), transform(state, config)):
            c = ''.join(transfer_to_board_size(c, config))
            p = transfer_to_board_size(p, config)
            policies[c] = p
        condition=state
    return policies

def transform(state,config):
    '''把棋盘变换，接收reading_size的list棋盘，返回一个list,元素为所有可能变换'''
    def mirror(state):
        '''左右翻转'''
        mirrored = []
        for line in state:
            mirrored_line = line[::-1]
            mirrored.append(mirrored_line)
        return mirrored
    def rotate(state):
        '''旋转'''
        rotation=[]
        #1.上下倒转
        r1=mirror(state)
        r1.reverse()
        #2.90度旋转
        r2=[]
        i=0
        while i<3:
            for line in state:
                r2.append(line[i])
            i+=1
        r2=[''.join(r2[n:n+3]) for n in range(len(r2)) if n%3==0]
        #3.270度旋转
        r3=r2
        r3.reverse()
        r3=mirror(r3)
        ''' 1|2|3      9|8|7       3|6|9       7|4|1
            4|5|6  ->  6|5|4   ->  2|5|8  ->   8|5|2
            7|8|9 上下  3|2|1  90度 1|4|7 270度 9|6|3  '''
        return [r1,r2,r3]
    return_list = [state]
    if config['mirror'] == 'True':
        return_list.append(mirror(state))
    if config['rotation'] == 'True':
        return_list += rotate(state)
    return return_list


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
    '''根据输入的列表0Zz形board_size棋盘，转换为str后重设网上棋盘'''
    def tpe(code):
        if code.isdigit():
            return nAPI_GET, nAPI_SET
        else:
            return API_GET, API_SET
    Board = ChessBoard(code, *tpe(code))
    str_board = ''.join(board)
    return Board.set(str_board) #重设网上棋盘


def transfer_to_old_form(new_form, config):
    '''将字符串b'v棋盘形式，转换为列表0Zz形式的棋盘(size是reading_size) v->z,b->Z'''
    if '|' in new_form:
        new_form = new_form.replace('|', "'")
        new_form = new_form[0:3] + ',' + new_form[3:6] + ',' + new_form[6:9]
    old_form = []
    i = 0
    for line in new_form.split(','):
        line = line.replace("'", '0').replace('v', 'z').replace('b', 'Z')
        if i == 4 and config['chess_type'] == 'luqi':
            old_line = '0'.join(list(line))
        else:
            miss = '0' * int((eval(config['reading_size'])[0]-len(line))/2) #补位
            old_line = miss + line + miss
        old_form.append(old_line)
        i += 1
    return old_form #type:list example:['00000','0Zz00','00000','0ZZZ0','Z0Z0Z']


def get_config(file, chess_type):
    '''输入棋盘种类，读取config.ini返回字典
       chess_type: 棋盘种类
       policy_file: 棋谱文件路径
       board_size: [x, y] 整个棋盘的大小，先宽度再高度,
       reading_size: [x, y] 需要读取写入区域的大小,
       mirror: True or False,
       rotation: [90, 180, -90] 需要旋转的度数'''
    config = {}
    conf = configparser.ConfigParser()
    conf.read(file, encoding="utf-8")
    items = conf.items(chess_type)
    for key,value in items:
        config[key] = value
    return config

def main(code,chess_type):
    config = get_config('config.ini',chess_type)
    policies = read_from_file(config)
    chess_type = config['chess_type']
    if chess_type == 'luqi':
        cleared_board = transfer_to_old_form("','v',b,bbb,bbb",config)
    else:
        cleared_board = transfer_to_old_form("bbb'|'vvv",config)
    cleared_board=transfer_to_board_size(cleared_board,config)
    set_new_board(code, cleared_board)
    last_board = get_the_board(code) #type:list
    while True:
        #人机交互，人调整棋盘，于是board与last_board不同，然后在policies中搜寻解法，搜到就调整棋盘
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
    chess_type=input("please input chess type, 'luqi' or 'zhuobie':")
    code = input("code:")
    try:
        main(code, chess_type)
    except:
        logging.debug(traceback.format_exc())
        raise
    
