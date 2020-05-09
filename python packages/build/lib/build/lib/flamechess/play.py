import traceback
import logging
import requests
import time
import os


API_GET = 'http://www.eanson.work/ai/status?code={code}'
API_SET = 'http://www.eanson.work/cb/status?i={content}&code={code}'
nAPI_GET = 'http://flamechess.cn/js/1/22/fcdbrw.php?id={code}'
nAPI_SET = 'http://flamechess.cn/js/1/22/fcdbrw.php?i={content}&id={code}'
DELAY = 0.5

logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ChessBoard:
    def __init__(self, code, get_url=API_GET, set_url=API_SET):
        self.code = code
        self.get_url = get_url
        self.set_url = set_url

    def get(self):
        while True:
            try:
                r = requests.get(self.get_url.format(code=self.code))
            except requests.exceptions:
                print('网络异常')
                logging.debug(traceback.format_exc())
                time.sleep(0.1)
            else:
                break
        return ''.join(filter(lambda x: x in '0zZ', r.content.decode("utf-8")))

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


class Recorder:
    def __init__(self, code, records_dir="records"):
        if not os.path.isdir(records_dir):
            os.mkdir(records_dir)
        self.filename = os.path.join(records_dir, "record-"+time.strftime('%Y_%m_%d=%H=%M=%S_') + code + '.rec')
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write("------\n")

    def record(self, board):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(board+"\n")


def tpe(code):
    if code.isdigit():
        return nAPI_GET, nAPI_SET
    else:
        return API_GET, API_SET


def main(code1, code2):
    board1 = ChessBoard(code1, *tpe(code1))
    board2 = ChessBoard(code2, *tpe(code2))
    recorder = Recorder(code1 + "-" + code2)
    board = board1.get()
    while True:
        time.sleep(DELAY)
        b1 = board1.get()
        if b1 != board:
            board2.set(b1)
            board = b1
            recorder.record(board)
            print('player1 moved')
            continue
        b2 = board2.get()
        if b2 != board:
            board1.set(b2)
            board = b2
            recorder.record(board)
            print('player2 moved')
            continue


if __name__ == '__main__':
    code1 = input("code1:")
    code2 = input("code2:")
    try:
        main(code1, code2)
    except Exception:
        logging.debug(traceback.format_exc())
        raise
