import traceback
import logging
import requests
import sys
import time
import os
import time


URL = 'http://www.eanson.work/ai/'
BASE_DIR = './'
FILENAME = 'record-'
CODE = input('code:')


logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def record(code=CODE, url=URL, filename=BASE_DIR+FILENAME):
    global chess
    global file
    chess = []
    file = filename + time.strftime('%Y_%m_%d-%H-%M-%S') + '.rec'
    last = None
    with open(file, 'w', encoding='utf-8') as f:
        f.write('--------\n')
    while True:
        try:
            txt = requests.get(url + 'status?code='+code).text
        except Exception:
            print('网络异常')
            time.sleep(0.1)
        except KeyboardInterrupt:
            raise
        if txt != last:
            chess.append(txt)
            last = txt
            with open(file, 'a') as f:
                f.write(txt + '\n')
            print('recorded')
    return chess


def replay(chess, code=CODE):
    last = None
    i = 0
    print('totally %d steps'%len(chess))
    while True:
        try:
            requests.get('http://www.eanson.work/cb/status?i=%s&code=%s'%(chess[i],code))
        except IndexError:
            print('到头了')
            i = len(chess)
        com = input().lower()
        if com == 'a':
            i -= 1
        elif com == 'd':
            i += 1
        elif com == 'quit':
            return
        else:
            i = int(com)
        print(i)


def main():
    file = None
    while True:
        time.sleep(0.5)
        com = input('choose record or replay:')
        if com == 'record':
            try:
                record()
            except KeyboardInterrupt:
                pass
        elif com == 'replay':
            if not file:
                index = 0
                files = [i for i in os.listdir(BASE_DIR) if i[-4:] == '.rec']
                for i in files:
                    index += 1
                    print(str(index), i)
                file = files[int(input('which one would you like to replay?'))-1]
            print(file)
            with open(file, 'r') as f:
                chess = f.readlines()
            replay(chess[1:])


if __name__ == '__main__':
    try:
        main()
    except:
        logging.debug(traceback.format_exc())
        raise
