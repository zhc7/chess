import configparser
import logging
import time
import traceback
from .play import ChessBoard, tpe

API_GET = 'http://www.eanson.work/ai/status?code={code}'
API_SET = 'http://www.eanson.work/cb/status?i={content}&code={code}'
nAPI_GET = 'http://flamechess.cn/js/1/31/fcdbrw.php?id={code}'
nAPI_SET = 'http://flamechess.cn/js/1/31/fcdbrw.php?i={content}&id={code}'
DELAY = 0.5


class Board(ChessBoard):
    def __init__(self, config, chess_type, code):
        super().__init__(code, *tpe(code))
        self.config = self.get_config(config, chess_type)
        self.code = code

    @staticmethod
    def get_config(file, chess_type):
        """输入棋盘种类，读取config.ini返回字典
           chess_type: 棋盘种类
           policy_file: 棋谱文件路径
           board_size: [x, y] 整个棋盘的大小，先宽度再高度,
           reading_size: [x, y] 需要读取写入区域的大小,
           mirror: True or False,
           rotation: [90, 180, -90] 需要旋转的度数"""
        config = {}
        conf = configparser.ConfigParser()
        conf.read(file, encoding="utf-8")
        items = conf.items(chess_type)
        for key, value in items:
            config[key] = value
        return config

    def transform(self, state):
        """把棋盘变换，接收reading_size的list棋盘，返回一个list,元素为所有可能变换"""
        return_list = [state]
        if self.config['mirror'] == 'True':
            return_list.append(state.mirror())
        if self.config['rotation'] == 'True':
            return_list += state.rotate()
        return return_list

    def read_from_file(self):
        """读取现有棋谱，返回一个哈希表，每个键为上一局面，每个值为键的下一个局面"""
        with open(self.config['policy_file'], 'r') as f:
            content = f.readlines()
        policies = {}
        condition = None
        for index, state in enumerate(content):
            state = State(state, self.config["reading_size"], self.config["board_size"])
            if index % 2 == 0:
                condition = state
            else:
                policies[''.join(condition)] = state
        return policies  # type:dict  # key:str value:list
        # example:{'00z000000000Z000ZZZ0Z0Z0Z':['00z00','00Z00','00000','0ZZZ0','Z0Z0Z']}

    def get_the_board(self):
        """获取列表0Zz形式的现有棋盘"""
        board = self.get()
        cut_board = []
        x, y = self.config["board_size"]
        for i in range(5):
            cut_board.append(board[x * i:x * (i + 1)])
        return cut_board  # type:list  # example:['00000','00z00','00Z00','0ZZZ0','Z0Z0Z']

    def set_new_board(self, board):
        """根据输入的列表0Zz形board_size棋盘，转换为str后重设网上棋盘"""
        str_board = ''.join(board)
        return self..set(str_board)  # 重设网上棋盘

    def transfer_to_old_form(self, new_form):
        """将字符串b'v棋盘形式，转换为列表0Zz形式的棋盘(size是reading_size) v->z,b->Z"""
        if '|' in new_form:
            new_form = new_form.replace('|', "'")
            new_form = new_form[0:3] + ',' + new_form[3:6] + ',' + new_form[6:9]
        old_form = []
        i = 0
        for line in new_form.split(','):
            line = line.replace("'", '0').replace('v', 'z').replace('b', 'Z')
            if i == 4 and self.config['chess_type'] == 'luqi':
                old_line = '0'.join(list(line))
            else:
                miss = '0' * int((eval(self.config['reading_size'])[0] - len(line)) / 2)  # 补位
                old_line = miss + line + miss
            old_form.append(old_line)
            i += 1
        return State(old_form, self.config["reading_size"], self.config["board-size"])
        # type:list  # example:['00000','0Zz00','00000','0ZZZ0','Z0Z0Z']

    def main(self):
        config = self.config
        policies = self.read_from_file(config)
        chess_type = config['chess_type']
        if chess_type == 'luqi':
            cleared_board = transfer_to_old_form("','v',b,bbb,bbb", config)
        else:
            cleared_board = transfer_to_old_form("bbb'|'vvv", config)
        self.set_new_board(cleared_board)
        last_board = self.get_the_board()  # type:list
        while True:
            # 人机交互，人调整棋盘，于是board与last_board不同，然后在policies中搜寻解法，搜到就调整棋盘
            board = self.get_the_board()
            if board == last_board:
                continue
            txt_board = ''.join(board)  # convert to str
            if txt_board in policies.keys():
                policy = policies[txt_board]
            else:
                print('no match policy')
                policy = board
            self.set_new_board(policy)
            last_board = policy
            time.sleep(DELAY)


class State:
    def __init__(self, state, reading_size, board_size):
        self.reading_size = reading_size
        self.board_size = board_size
        if type(state) == str:
            state = self.preprocess(state)
            state = self.transfer_to_board_size(state)
        self.state = state

    def __iter__(self):
        return self.state

    def preprocess(self, state: str) -> list:
        x, y = self.reading_size
        state = state.strip()
        new_state = []
        for i in range(0, len(state), x):
            line = state[i:i+x]
            new_state.append(line)
        return new_state

    def transfer_to_board_size(self, state):
        """接收0Zz型reading_size的list棋盘，转换为0Zz型board_size的list棋盘"""
        filled_board = ''
        board_x, board_y = self.board_size
        x, y = len(state[0]), len(state)
        y_fill = int((board_y - y) / 2)  # 纵向需要填充的行数
        x_fill = int((board_x - x) / 2)  # 横向需要填充的空格数
        filled_board += y_fill * board_x * '0'  # 填充空行
        for line in state:
            filled_line = x_fill * '0' + line  # 前面填充
            filled_line += (board_x - len(filled_line)) * '0'  # 后面补齐
            filled_board += filled_line  # filled_board:str example:'000000Zz00000000ZZZ0Z0Z0Z'
        filled_board += (board_x * board_y - len(filled_board)) * '0'  # 补齐整个棋盘
        new_state = [filled_board[i:i + board_x] for i in range(0, len(filled_board), board_x)]
        return new_state

    def mirror(self, state=None):
        if not state:
            state = self.state
        """左右翻转"""
        mirrored = []
        for line in state:
            mirrored_line = line[::-1]
            mirrored.append(mirrored_line)
        return mirrored

    def rotate(self):
        """旋转"""
        # 1.上下倒转
        r1 = self.mirror()
        r1.reverse()
        # 2.90度旋转
        r2 = []
        i = 0
        while i < 3:
            for line in self.state:
                r2.append(line[i])
            i += 1
        r2 = [''.join(r2[n:n + 3]) for n in range(len(r2)) if n % 3 == 0]
        # 3.270度旋转
        r3 = r2
        r3.reverse()
        r3 = self.mirror(r3)
        ''' 1|2|3      9|8|7       3|6|9       7|4|1
            4|5|6  ->  6|5|4   ->  2|5|8  ->   8|5|2
            7|8|9 上下  3|2|1  90度 1|4|7 270度 9|6|3  '''
        return [r1, r2, r3]


def transfer_to_new_form(old_form):
    new_form = []
    new_form[0] = old_form[0][2]
    new_form[1] = old_form[1][1:4]
    new_form[2] = old_form[2][2]
    new_form[3] = old_form[0][1:4]
    new_form[4] = [old_form[0][0], old_form[0][3], old_form[0][5]]
    new_form = [i.replace('0', "'") for i in new_form]
    return ','.join(new_form)


if __name__ == '__main__':
    input_chess_type = input("please input chess type, 'luqi' or 'zhuobie':")
    input_code = input("code:")
    try:
    board = Board("config.ini", input_chess_type, input_code)
        board.main()
    except Exception:
        logging.debug(traceback.format_exc())
        raise
