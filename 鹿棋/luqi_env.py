from os import environ

from luqi import *

if __name__ == '__main__':
    chess_type = environ.get("CHESS_TYPE")
    code = environ.get("CHESS_CODE")

    if chess_type is None or code is None:
        raise ValueError("Please define CHESS_TYPE and CHESS_CODE.")
    else:
        main(code, chess_type)
