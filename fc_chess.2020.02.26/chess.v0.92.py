import traceback
import logging


logging.basicConfig(filename='log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


try:
    import requests
    import sys


    URL = 'http://flamechess.cn/js/'
    CODE = input('CODE:')


    def replay(chess, code=CODE):
        last = None
        i = 0
        while True:
            try:
                requests.get('http://flamechess.cn/js/1/22/fcdbrw.php?i=%s&id=%s'%(chess[i][0:209],code))
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
            
            
    def record(url=URL, code=CODE):
        global chess
        chess = []
        last = None
        with open('chess_record.txt', 'a') as f:
            f.write('--------\n')
        while True:
            try:
                txt = requests.get('http://flamechess.cn/js/1/22/fcdbrw.php?id='+code).text
            except:
                print('网络异常')
            if txt != last:
                chess.append(txt)
                last = txt
                with open('chess_record.txt', 'a') as f:
                    f.write(txt[6:216] + '\n')
                print('recorded')
        return chess


    if __name__ == '__main__':
        while True:
            com = input('chooce record or replay:')
            if com == 'record':
                try:
                    record()
                except KeyboardInterrupt:
                    pass
            elif com == 'replay':
                try:
                    print('abc')
                    with open('chess_record.txt', 'r') as f:
                        chess = f.readlines()
                except Exception as e:
                    print(e)
                replay(chess[1:])
except:
    logging.debug(traceback.format_exc())
