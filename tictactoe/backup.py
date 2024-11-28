"""
Tic Tac Toe Player
"""

import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    espacos_usados = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] != EMPTY:
                espacos_usados = espacos_usados+1

    if espacos_usados%2 == 0:
        return X 
    else:
        return O

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    resultado = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                resultado.add((i,j))

    return resultado


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    copia = deepcopy(board)
    jogada = player(copia)
    X, Y = action
    if copia[X][Y] is not EMPTY or (X < 0 or Y < 0):
        raise ValueError('invalid action')
    else:
        copia[X][Y] = jogada
    
    return copia


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):

        if board[i][0] == X and board[i][1] == X and board[i][2] == X:
            return X
        elif board[i][0] == O and board[i][1] == O and board[i][2] == O:
            return O

        elif board[0][i] == O and board[1][i] == O and board[2][i] == O:
            return O
        elif board[0][i] == X and board[1][i] == X and board[2][i] == X:
            return X
        
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    elif board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X
    else:
        return None
        

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    game = winner(board)
    if game != None:
        return True
    else:
        espacos_usados = 0
        for i in range(3):
            for j in range(3):
                if board[i][j] != EMPTY:
                    espacos_usados = espacos_usados+1
        
        if espacos_usados == 9:
            return True
        else:
            return False
            


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    vencedor = winner(board)

    if vencedor == X:
        return 1
    elif vencedor == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    jogador = player(board)

    if jogador == X:
        jogada = None
        aux = -10
        for action in actions(board):
            maxval = minvalue(result(board,action))
            if maxval > aux:
                aux = maxval
                jogada = action
        
    if jogador == O:
        jogada = None
        aux = 10
        for action in actions(board):
            minval = maxvalue(result(board,action))
            if minval < aux:
                aux = minval
                jogada = action
    
    return jogada


def maxvalue(board):
    if terminal(board):
        return utility(board)
    
    v = -10
    for action in actions(board):
        v = max(v,minvalue(result(board,action)))
    return v

def minvalue(board):
    if terminal(board):
        return utility(board)
    
    v = 10
    for action in actions(board):
        v = min(v,maxvalue(result(board,action)))   
    return v