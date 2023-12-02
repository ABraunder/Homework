board = list(range(1,10))

def draw_board(board):
    for i in range(3):
        print (board[0+i*3],board[1+i*3],board[2+i*3])

def take_input(player_point):
    valid = False
    while not valid:
        player_answer = input("Куда поставим " + player_point+"? ")
        try:
            player_answer = int(player_answer)
        except:
            print ("Некорректный ввод. Вы уверены, что ввели число?")
            continue
        if player_answer >= 1 and player_answer <= 9:
            if (str(board[player_answer-1]) not in "XO"):
                board[player_answer-1] = player_point
                valid = True
            else:
                print ("Клетка занята")
        else:
            print ("Некоректный выбор клетки. Выбери от 1 до 9 из свободных клеток.")

def check_win(board):
    win_coordinate = ((0,1,2),
                      (3,4,5),
                      (6,7,8),
                      (0,3,6),
                      (1,4,7),
                      (2,5,8),
                      (0,4,8),
                      (2,4,6))
    for each in win_coordinate:
        if board[each[0]] == board[each[1]] == board[each[2]]:
            return board[each[0]]
    return False

def main(board):
    counter = 0
    win = False
    while not win:
        draw_board(board)
        if counter % 2 == 0:
            take_input("✖")
        else:
            take_input("○")
        counter += 1
        if counter > 4:
            player = check_win(board)
            if player:
                print('-' * 19)
                print ('Игрок',player, "победил!")
                print('-' * 19)
                win = True
                break
        if counter == 9:
            print('-' * 19)
            print ("Ничья!")
            print('-' * 19)
            break
    draw_board(board)

main(board)