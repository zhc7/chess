def transfer_chessrecord(file):
    """读取原有bv'|型棋盘，返回包含所有list型0Zz棋局的list"""
    with open(file, 'r') as f:
        situations = f.readlines()
    new_situations = []
    for situation in situations:
        if '|' in situation:
            situation = situation.replace('|', '0').replace("'", '0')\
                .replace('v', 'z').replace('b', 'Z').replace('\n', '')
            situation = [situation[i:i + 3] for i in range(len(situation)) if i % 3 == 0]
            new_situations.append(situation)
        else:
            situation = situation.split(',')
            new_situation = []
            for index, line in enumerate(situation):
                if index == 4:
                    line = '0'.join(list(line.replace("'", '0').replace('v', 'z').replace('b', 'Z').replace('\n', '')))
                    new_situation.append(line)
                else:
                    line = line.replace("'", '0').replace('v', 'z').replace('b', 'Z').replace('\n', '')
                    covering = int((5 - len(line)) / 2) * '0'
                    line = covering + line + covering
                    new_situation.append(line)
            new_situations.append(new_situation)
    return new_situations


def transform(state):
    """把棋盘变换，接收reading_size的list棋盘，返回一个list,元素为所有可能变换"""

    def mirror(state):
        """左右翻转"""
        mirrored = []
        for line in state:
            mirrored_line = line[::-1]
            mirrored.append(mirrored_line)
        return mirrored

    def rotate(state):
        """旋转"""
        # 1.上下倒转
        r1 = mirror(state)
        r1.reverse()
        # 2.90度旋转
        r2 = []
        i = 0
        while i < 3:
            for line in state:
                r2.append(line[i])
            i += 1
        r2 = [''.join(r2[n:n + 3]) for n in range(len(r2)) if n % 3 == 0]
        # 3.270度旋转
        r3 = r2
        r3.reverse()
        r3 = mirror(r3)
        ''' 1|2|3      9|8|7       3|6|9       7|4|1
            4|5|6  ->  6|5|4   ->  2|5|8  ->   8|5|2
            7|8|9 上下  3|2|1  90度 1|4|7 270度 9|6|3  '''
        return [r1, r2, r3]

    if len(state) == 5:
        return [state, mirror(state)]
    else:
        return [state, mirror(state), *rotate(state)]


def get_policies(situations):
    """接收所有棋局，进行变换，输出新的所有棋局list"""
    new_situations = []
    if len(situations[0]) == 5:
        for state, index in zip(situations, range(len(situations))):
            if index % 2 == 0:
                condition = state
            else:
                trans_condition = transform(condition)
                trans_state = transform(state)
                for c, p in zip(trans_condition, trans_state):
                    new_situations.append(c)
                    new_situations.append(p)
    else:
        for state, index in zip(situations, range(len(situations))):
            if index == 0:
                condition = state
            else:
                for c, p in zip(transform(condition), transform(state)):
                    new_situations.append(c)
                    new_situations.append(p)
            condition = state
    return new_situations


def write_txt(situations):
    if len(situations[0]) == 5:
        with open('../python包/flamechess/luqi.txt', 'w') as f:
            for s in situations:
                f.write(''.join(s) + '\n')
    else:
        with open('../python包/flamechess/zhuobie.txt', 'w') as f:
            for s in situations:
                f.write(''.join(s) + '\n')


def main(file):
    new_situations = get_policies(transfer_chessrecord(file))
    write_txt(new_situations)


if __name__ == '__main__':
    main('../python包/flamechess/luqi.txt')
    main('../python包/flamechess/zhuobie.txt')
