import math
import random
import time
import pickle
import os
import pandas as pd
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import datetime

EMPTY = 0
BLACK = 1
WHITE = -1
VALID = '*'
PLAYER_COLS = {
    BLACK: "BLACK",
    WHITE: "WHITE",
}
VERBOSE = False
MONITOR = False

class Othello():

    def __init__(self, size=6):
        """
        Initialize game board.
        Each game board has
            - size: defined by user
        """
        # (print('\n+++init'))
        self.size = size
        self.state = self.create_board()
        self.player = BLACK
        self.winner = None

    @classmethod
    def playercolor(self, player):

        return "BLACK" if player == 1 else "WHITE"

    # BOARD SHOWING AVAILABLE MOVES
    def boardwithavails(self, board,  human, aimove):  
        print(' ++++boardwithavails')
    
        # print(f'player={player}')
        for cell in self.available_actions( board, human):
            print(f'cell={cell}')
            board[cell[0]][cell[1]] = '*'
        # add ai's last move
        if aimove is not None:
            # print(f'---human= {human}')
            if human == 1:
                board[aimove[0]][aimove[1]] = '-'
            elif human == -1:
                board[aimove[0]][aimove[1]] = '+'
        # print(f"for response board= {board}")
        # self.printboard(board)
        return board
       
    def switchplayer(self, player):
        # print(f'+++switchplayer()')
        # print(f'player={player}')
        # print(f'switchplayer player={player}')
        if player == BLACK:
            # if self.available_actions(board, player):
            return WHITE
        else:
            return BLACK
    @classmethod
    def printboard(self, board, lastmove=None, ):
        RED = '\033[91m'
        ENDC = '\033[0m'        
        symbol_map = {1: 'X', -1: 'O', 0: '.', '*': '*', '+':'X', '-':'O'}
        for i, row in enumerate(board):
            row_str = ''
            for j, cell in enumerate(row):
                if lastmove == (i,j):
                    row_str += RED + f' {symbol_map[cell]} ' + ENDC
                elif cell == '+':
                    row_str += RED + f' {symbol_map[cell]} ' + ENDC
                elif cell == '-':
                    row_str += RED + f' {symbol_map[cell]} ' + ENDC
                else:
                    # print(f'/cell={cell}')
                    row_str += f' {symbol_map[cell]} '
            print(row_str)

    def create_board(self):
        # print('+++create_board')
        board = []
        for i in range (self.size):
            row = []
            for j in range (self.size):
                row.append(0)
            board.append(row)
        center = int((self.size/2)-1)
        board[center][center] = -1
        board[center][center+1] = 1
        board[center+1][center] = 1
        board[center+1][center+1] = -1
        return board

    def move(self, board, action, player):
        """
        `action` must be a tuple `(i,j)`.
        return the updated board.
        !!! CHANGES BOARD VAR !!!
        MAYBE PASS AVAILACTS AS ARGUMENT ???
        """
        copyboard = deepcopy(board)
        # print(f'\n++++move() for {player}, ')
        # self.printboard(board)
        # print(f'action={action}')
        # print(f'player={player}')
        if board is None:
            print("Board is None")
        availactions = self.available_actions(copyboard, player)
        # print(f'>availactions={availactions}')
        # print(f'---action= {action}')
     
        #####      IS ACTION VALID
        if action not in availactions:
            print("\n>>>>Error: Action not in available_actions.")
            return board  # Or handle the error differently
        # else:
            # print(f'Action is valid')

        ####     GET BITS TO FLIP
      
        bitstoflip = availactions[action]
        # print(f'---bitstoflip= {bitstoflip}')
    

        ####  MARK BOARD WITH FLIPPED PIECES
        if bitstoflip:
            for bit in bitstoflip:
                copyboard[bit[0]][bit[1]] = player
        # print(f'board with just  flips')
        
          #####     MARK BOARD WITH ACTUAL MOVE
        copyboard[action[0]][action[1]] = player
        # print(f'board with flips and move')
        # self.printboard(board)

      
        # print('END OF MOVE()')

        return copyboard

    def calcnextcell(self, board, cell, direction):
            #   RETURNS THE NEXT CELL ONLY IF IT IS WITHIN BOUNDS
            # print(f'+++calcnextcell ')
            result = tuple(c + d for c,d in zip(cell, direction)) 
            ####       IS THE NEW CELL ON THE BOARD?
            if result[0] < 0 or result[0] >= self.size or result[1] < 0 or result[1] >= self.size:
                # print(f'OUT OF BOUNDS')
                return None
            # print(f'result={result}')
            return result
    
    def direction_checker(self, board, cell, direction, player):
        """
        Returns a set of captured pieces if possible in that direction, None otherwise.
        """
        #### MAKE PRINTABLE DIRECTIONS
        if direction == (-1, -1):
            compass = 'NW'
        elif direction == (-1, 0):
            compass = 'N'
        elif direction == (-1, 1):  
            compass = 'NE'
        elif direction == (0, -1):
            compass = 'W'
        elif direction == (0, 1):
            compass = 'E'
        elif direction == (1, -1):
            compass = 'SW'
        elif direction == (1, 0):
            compass = 'S'
        elif direction == (1, 1):
            compass = 'SE'

        # print(f'+++++direction_checker().  {compass} from candidate cell{ cell}')
        # self.printboard(board)
        originalcell = cell
        ####       SET UP VARIABLES
        captured = set()
        # nextcell = cell
        opponent = self.switchplayer(player)
        ####   RUN LOOP TO CHECK DIRECTION
        while True:
            # print(f'---START SEARCH LOOP')
            # print(f'---direction={direction}')
            # print(f'opponent={opponent}')

            ####       CALCULATE NEXT CELL
            cell = self.calcnextcell(board, cell, direction)

            # if newcell is not in bounds
            if cell is None:
                # print(f'---cell is None')   
                return None
            # print(f'===new cell= {cell}, original = {originalcell}')

            #### IF THE cell IS EMPTY, RETURN NONE
            if board[cell[0]][cell[1]] == 0:
                # print(f'cell is empty, so returning None')
                return None
            
            
            ####   IF  CELL IS MINE 
            if board[cell[0]][cell[1]]  == player:
                ####    AND  THERE ARE CAPTURED
                if captured:
                    # print(f'{cell} is mine and captured is not empty, so returning = {captured}')
                    return captured
                else:
                    return None

            #### ELSE IF NEXT CELL IS ENEMY, ADD TO CAPTURED
            elif board[cell[0]][cell[1]] == opponent:
                # print(f'opponent at {cell} in direction {compass},')
                captured.add(cell)
                # print(f'captured={captured}')
       
    def available_actions(self, board, player):
        """
        returns a list of tuples,  with all of the available actions `(i, j)` in that state, plus the captued pieces for each move, as a set.
        """
        # print(f'\n+++AVAILABLE_ACTIONS FOR {player}')
        # self.printboard(board)
        actions = {}
        ####       CREATE THE DIRECTIONS
        directions = [(di, dj) for di in [-1, 0, 1] for dj in [-1, 0, 1] if not (di == dj == 0)]
        # print(f'directions={directions}')

        ####        FOR EACH BOARD cell
        # print('---GO THROUGH WHOLE BOARD, LOOKING FOR EMPTY CELLS')
        for i, row in enumerate(board):
            for j, content in enumerate(row):
                cell = (i,j)
                # print(f'content={content}')

                # print(f'\n ---CHECKING CELL = {cell}')
                if (content != 0) :
                    # print(f'content is not 0, so continue')
                    continue
                # print(f'---{cell} is empty, so possibly valid: checking directions')
                # print(f'cell={cell}, type={type(cell[0])}')
                alldirscaptured = set()
                ####       FOR EACH DIRECTION
                for direction in directions:
                    # print(f'---checking direction= {direction}')
                    
                    ####        IF VALID , ADD MOVE TO SET, ADD CAPTURED PIECES TO SET
                    onedircaptured = self.direction_checker(board, cell, direction, player )
                    # print(f'onedir_captured={onedircaptured}')
                    ####    IF THERE IS ANY ADD TO TOAL CAPTURED FOR THIS cell
                    if onedircaptured:
                        # print(f'onedir_captured=true, so adding to alldirscaptured')
                        alldirscaptured.update(onedircaptured)
                    else:
                        continue
                        # print(f'onedirc_aptured=false')
                        
                    # print(f'xxxtotalcaptured={alldirscaptured}') 
                # print(f'alldirs_captured={alldirscaptured}') 
                if alldirscaptured:
                    # print(f'alldirs_captured=true')
                    actions[cell]= alldirscaptured 
                else:
                    continue
                    # print(f'alldirs_captured=false') 
        # print(f'---returning {actions}')
        self.availactions = actions
        # print(f'...end of available_actions()')
        return actions
   
    def scores(self, board):
        """
        Returns a tuple (black_score, white_score) for the current game state.
        """
        # print(f'+++scores()')
    
        black_score = 0
        white_score = 0
        for row in board:
            for cell in row:
                if cell == 1:
                    black_score += 1
                elif cell == -1:
                    white_score += 1
        # print(f'black_score={black_score}')
        # print(f'white_score={white_score}')
        return (black_score, white_score)

    def calc_winner(self, board):
        black_score, white_score = self.scores(board)
        # print(f'+++calc_winner()')
        # print(f'black_score, white_score={black_score}{white_score})')
        if black_score > white_score:
            self.winner = BLACK
            return BLACK
        elif white_score > black_score:
            self.winner = WHITE
            return WHITE
        else:
            return None

    def aimoves(self, board, availactions, player, aiplayer):
        """
        geta the AI move, returns new board and move() 
        """
        if VERBOSE:
            print(f'+++aimoves()')
        # get canonical board and trans
        # canonboard, trans = aiplayer.canonical_board(board)
        # self.printboard(canonboard)
        # trans the availactions

        
        aiboard = board
        # inputmove = input('enter ai move: ')
        # aimove = tuple(int(char) for char in inputmove)
        aimove = aiplayer.choose_q_action(aiboard, availactions)
        if VERBOSE:
            print(f'---q table returns= {aimove}')
        if not aimove:
            '''
            eval act:
            compare all availact outcomes board evaluations,???
            '''
            # print(f'---MAKING RANDOM MOVE')
            aimove = random.choice(list(availactions.items()))

            ####  TODO DISABLED EVALUATION !!!

            # aimove = aiplayer.choose_evaluated_action(aiboard, availactions, self)

            # print(f'---evaluated action= {aimove}') 
        # print(f'---board before ai move ')
        # self.printboard(board)
        #### MAKE AI MOVE
        board = self.move( board, aimove[0], player )
 
        return board, aimove

    def gameover(self, board ):
        """
        Returns True if game is over, False otherwise.
        """
        # print(f'+++gameover()')
        # print(f'---winner= {self.winner}')
        if self.winner is not None:
            print(f'+++gameover: self.winner={self.winner}')
            return True
        ####    CHECK IF BOARD IS FULL
        if not any(cell == 0 for row in board for cell in row):
            # print(f'---board is full')
            return True

        ####   CHECK IF NEITHER PLAYER HAS ANY VALID MOVES
        if (not self.available_actions(  board, -1) and not self.available_actions(board, 1)):
            # print(f'---no valid moves for either player')
            # print(f'----end of gameover()')
            return True
        
        # print(f'----end of gameover()')
        return False
        
    

class OthelloAI():
    ### AI CAN USE CLASS ATTRIBUTES AS IT WILL NOT BE SERVED/SUBJECT TO REQUESTS

    def __init__(self, alpha=0.5, epsilon=0):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - `action` is a tuple `(i, j)` for an action
        """
        self.q = dict() # VALUE CAN BE NONE FOR UNEXPLORED STATES
        self.alpha = alpha
        self.epsilon = epsilon
        self.minratio = float('inf')
        self.maxratio = -float('inf')
        self.numqupdates = 0
        self.sumdeltaqs = 0
        self.deltaqaverage = 0
        self.qs_used = 0
        self.color = None
        

    def update(self, old_state, action, new_state, reward, game_instance):
        """
        Update Q-learning model, given an old state, an action taken
        in that state, a new resulting state, and the reward received
        from taking that action.
        """
        if VERBOSE:
            print(f"+++update")
            # print(f"--- action={action}, new_state={new_state}, reward={reward}")
            print(f"---STATE ACTION SAVED in Qtable:")
            Othello.printboard(old_state, action)
            # print(f"---NEW STATE")
            # Othello.printboard(new_state)
            # print(f'---getting old q value ')
        old = self.get_q_value( old_state, action)
        best_future = self.best_future_reward(new_state, game_instance)
        self.update_q_value( old_state, action, old, reward, best_future)
        if VERBOSE:
            print(f"---old q value= {old}")
            print(f"---best_future_reward=  {best_future}")
            print(f"---updated q value= {self.get_q_value(old_state, action)}")

    def get_q_value(self, state, action):
        """
        Return the Q-value for the state `state` and the action `action`.
        If no Q-value exists yet in `self.q`, return NONE.
        """
        # if VERBOSE:
        #     print(f"+++get_q_value")
        #     print(f'---action= {action}. RECIEVED:::')
        #     Othello.printboard(state)
        # print
        if not state or not action:
            print(f"---state or action is None")
            return None  
        # print(f"---state type= {type(state)}")
        # print(f"---state= {state}")
        statetuple = self.statetotuple(state)
        # print(f"---statetuple type= {type(statetuple)}")
        # print(f"---statetuple= {statetuple}")
        # print(f"---action type= {type(action)}")

        # print(f'---self.q= {self.q}')  
        # print(f'---type(self.q) = {type(self.q)}') 
     
        q =  self.q.get((statetuple, action))
        if q != None and q != 0:
                if MONITOR == True:
                    print(f"---Q accessed = {q}")
                self.qs_used += 1
        # print(f'---get_q_value returning= {q}')
        return q 

    def statetotuple(self, state):
        return tuple(tuple(row) for row in state)

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Q(state, action) = Q(state, action) + α * (reward + γ * max_a Q(next_state, a) - Q(state, action))

        where `old value estimate` is the previous Q-value,
        `alpha` is the learning rate, and `new value estimate`
        is the sum of the current reward and estimated future rewards.
        # """
        # print(f"+++update_q_value") 
        # print(f"---state={state}, action={action}, old_q={old_q}, reward={reward}, future_rewards={future_rewards}")
        if state is None or action is None:
          # print(f"---!!!!!state or action is None")
            return

        if old_q is None:
            old_q = 0
   
        statetuple = self.statetotuple(state)
        gamma = 0.9
        newvalest = reward + (gamma * future_rewards)
        # print(f"---newvalest={newvalest}")
        ####     IF WINNER = PLAYER, REWARD = 1

        result = old_q + (self.alpha * (newvalest - old_q))
        self.q[statetuple, action] = result
        # Calculate update magnitude
        self.sumdeltaqs += abs(result - old_q)
        # if MONITOR:
        #     print(f'---reward= {reward}, future_rewards={future_rewards}')
        #     print(f'--oldq= {old_q}')   
        #     print(f'--newq= {result}')
        #     print(f"---sumdeltaqs={self.sumdeltaqs}")
        self.numqupdates += 1
        

        # print(f"---updated with action {action} self.q = {self.q[statetuple, action]}")
        
    def terminalupdate(self, state, action, reward):
        statetuple = self.statetotuple(state)

        old_q = self.get_q_value( state, action)
        if old_q is None:
            old_q = 0

        self.q[statetuple, action] = reward
        # Calculate update magnitude
        self.sumdeltaqs += abs(reward - old_q)
        # print(f"---sumdeltaqs={self.sumdeltaqs}")
        self.numqupdates += 1
    
    def best_future_reward(self, state, game_instance):
        """
        Given a state `state`, consider all possible `(state, action)`
        pairs available in that state and return the maximum of all
        of their Q-values.

        Use 0 as the Q-value if a `(state, action)` pair has no
        Q-value in `self.q`. If there are no available actions in
        `state`, return 0.

        =epsilon is the exploration rate (probability of taking a random action))]
        ='Q-table' is a dictionary mapping state-action pairs to Q-values
        """
        actions =  game_instance.available_actions(state, game_instance.player)
        # print(f"+++best_future: actions={actions} len={len(actions)})") 
        if not actions:
            # print(f"---no actions")
            return 0
        # get q value for actions
        qlist = []
        for action in actions:
            # print(f"---action={action}")
            # print(f"---q = {self.get_q_value(state, action)})")
            n = self.get_q_value(state, action)
            if n is None:
                n = 0
            qlist.append(n)
        # print(f"---qlist={qlist} len={len(qlist)}")
        best = max(qlist)
        # print(f"---best={best}")
        ####   GAMMA=1 MEANS FUTURE REWARDS ARE PRIORITIZED
        gamma = 1 
        result =  gamma * best
        # print(f"---result={result}")
        # print(f">>>best={best}")
        return result
        
    

        # get max of the q values

    def choose_q_action(self, state, availactions):
        """
        Given a state `state`, return an action `(i, j)` to take.
        If `epsilon` is `False`, then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).
        If `epsilon` is `True`, return None.
        """
        global VERBOSE
        if VERBOSE: 
            print(f"+++choose-Q-action")
        
        # print(f"---availactions={availactions}")
        if not availactions:
            print(f"---no actions")
            return None
        action = None
        ####  IF ONLY ONE ACTION RETURN IT
        if len(availactions) == 1:
            # print(f"---only one action, so returning it")
            key = next(iter(availactions))
            action = key
            # print(f'---action 1  = {action}')

        # WITH EPSILON >0 : CHOOSE RANDOM ACTION WITH EPSILON PROB
        
       
        # print(f"---CHOOSING EPSILON HERE = {epsilon}")
        x = random.random()
        # print(f"---random x = {x}")
        # print(f'---epsilon={self.epsilon}')
        if x < self.epsilon:
            # print(f'---EXPLORATION')
            action = random.choice(list(availactions))
            # print(f">>>EPs=True : random action= {action}")
        else:
            ...
                # print(f'---a random action was not chosen, so use the q table to choose the best action')

        ### EPSILON FALSE: CHOOSE ACTION WITH HIGHEST Q VALUE

        # IF RAMDOM ACTION WAS NOT CHOSEN, USE Q TABLE 
        if not action:
            maxq = -float('inf')
            bestaction_q = None
            bestactions = []
            # print(f'---CHOOING Q ACTION HERE:')
            # print(f'---actions={actions}')

            for action in availactions:
                assert action is not None
                q = self.get_q_value( state, action)
                
                if q != None:
                    if q > maxq:
                        maxq = q
                        bestactions = [action]
                    elif q == maxq:
                        bestactions.append(action)
            if bestactions:
                # print(f"---bestactions= {bestactions}")
                bestaction_q = random.choice(bestactions)
                # print(f"---bestcaction_q= {bestaction_q}")
                action = bestaction_q
            else:
                # print(f"---choose_q_action from get_q so returning None")
                return None
        # print(f"---action 3  = {action}")
        # get the captured pieces
        captured = availactions[action]
        # print(f"---choose_q_action returning= {action}, {captured}")
        # print(f'+--end of choose_q_action()')
        return action, captured
    
    def choose_evaluated_action(self, state, availactions, game_instance):
        """
        returns action and captures
        """
        # print(f"+++choose_evaluated_action()")
        # print(f"---avail actions={availactions}")
        besteval = -float('inf')
        bestaction = None
        for action in availactions:
            # print(f"---action={action}")
            # print(f'---availactions[action]={availactions[action]}')
            eval = self.evaluate_action(state, action,game_instance)
            # print(f"---{action} eval={eval}")
            if eval > besteval:
                besteval = eval
                bestaction = action
            # print(f"---action={action}, besteval={besteval}")
        # print(f"---bestaction={bestaction}")
        return bestaction, availactions[bestaction]
        
    def is_edge(self,move, last_index):
        return move[0] == 0 or move[0] == last_index or move[1] == 0 or move[1] == last_index

    def is_corner_adjacent(self, move, last_index):
        corner_adjacent_positions = [
            (0, 1), (1, 0), (1, 1),  # Top-left corner adjacent positions
            (last_index, last_index-1), (last_index-1, last_index), (last_index-1, last_index-1),  # Bottom-right corner adjacent positions
            (0, last_index-1), (1, last_index), (1, last_index-1),  # Top-right corner adjacent positions
            (last_index, 1), (last_index-1, 0), (last_index-1, 1)  # Bottom-left corner adjacent positions
            ]
        return move in corner_adjacent_positions

    def is_edge_adjacent(self, board, move, last_index):
        # print(f'--move= {move}')
        # Check adjacent to vertical edges and not at corners
        if move[0] in [1, last_index-1] and move[1] not in [0, last_index]:
            if move[0] == 1 and board[0][move[1]] == EMPTY:  # Check upper edge if move is on the second row
                return True
            elif move[0] == last_index-1 and board[last_index-1][move[1]] == EMPTY:  # Corrected index for lower edge check
                return True

        # Check adjacent to horizontal edges and not at corners
        if move[1] in [1, last_index-1] and move[0] not in [0, last_index]:
            if move[1] == 1 and board[move[0]][0] == EMPTY:  # Check left edge if move is in the second column
                return True
            elif move[1] == last_index-1 and board[move[0]][last_index-1] == EMPTY:  # Corrected index for right edge check
                return True

        return False

    def is_corner(self,move, last_index):
        return move in [(0, 0), (0, last_index), (last_index, 0), (last_index, last_index)]
    
    def connects_to_corner(self, move, board):
        # Determine if a move is directly connected to a player-occupied corner with a path consisting only of player's pieces
        last_index = len(board) - 1
        corners = [(0, 0), (0, last_index), (last_index, 0), (last_index, last_index)]

        def check_path(start, end):
            # Check if the path between start and end is clear or consists only of player's pieces
            # This function assumes start and end are in a straight line (horizontal, vertical, or diagonal)
            dx = 1 if end[0] > start[0] else -1 if end[0] < start[0] else 0
            dy = 1 if end[1] > start[1] else -1 if end[1] < start[1] else 0

            x, y = start
            while (x, y) != end:
                x += dx
                y += dy
                if (x, y) != end and board[x][y] != BLACK:  # Skip checking the end point itself
                    return False
            return True
    
        for corner in corners:
            if board[corner[0]][corner[1]] == BLACK:
                # Directly connected if on the same row, column, or diagonal
                if corner[0] == move[0] or corner[1] == move[1] or abs(corner[0] - move[0]) == abs(corner[1] - move[1]):
                    # Check the path between the move and the corner
                    if check_path(move, corner):
                        return True
        return False

        # Determine if a move is directly connected to a player-occupied corner with an uninterrupted path
        last_index = len(board) - 1
        corners = [(0, 0), (0, last_index), (last_index, 0), (last_index, last_index)]

        def check_path(corner, move):
            # Check horizontal or vertical paths
            if corner[0] == move[0]:  # Same row
                for col in range(min(corner[1], move[1]) + 1, max(corner[1], move[1])):
                    if board[move[0]][col] != player:
                        return False
            elif corner[1] == move[1]:  # Same column
                for row in range(min(corner[0], move[0]) + 1, max(corner[0], move[0])):
                    if board[row][move[1]] != player:
                        return False
            else:
                # Check diagonal paths
                row_step = 1 if move[0] < corner[0] else -1
                col_step = 1 if move[1] < corner[1] else -1
                row_range = range(move[0] + row_step, corner[0], row_step)
                col_range = range(move[1] + col_step, corner[1], col_step)
                for row, col in zip(row_range, col_range):
                    if board[row][col] != player:
                        return False
            return True

        for corner in corners:
            if board[corner[0]][corner[1]] == player:
                if corner[0] == move[0] or corner[1] == move[1] or abs(corner[0] - move[0]) == abs(corner[1] - move[1]):
                    if check_path(corner, move):
                        return True
        return False

    def evaluate_mobility_and_ratio(self,board, move, player, captured_pieces):
        # This is a placeholder for mobility and disc ratio evaluation
        # Implement your own logic here based on the current state after the move is made and captured pieces are flipped
        mobility_diff = 0.1  # Placeholder value
        disc_ratio = 0.1  # Placeholder value
        return mobility_diff, disc_ratio

        # Example of making a move and evaluating it
        move = (0, 0)  # A corner move
        player = 1  # Assuming 1 is black
        captured_pieces = [(0, 1), (1, 0), (1, 1)]  # Example captured pieces for this move
        # You need to implement the logic for updating the board with the move and captured pieces
        # new_board = make_move(board, move, player, captured_pieces)

        # val = evaluate_move(new_board, move, player, captured_pieces)
        # print(f"Move value: {val}")

    def evaluate_board(self, board, instance):
        # print(f"+++evaluate_board_2()") 
        val = 0
        size = len(board) - 1
        player_pieces = 0
        opponent_pieces = 0
        player_frontier = 0
        opponent_frontier = 0
        player_mobility = 0
        opponent_mobility = 0
        empties = 0

        directions = [(di, dj) for di in [-1, 0, 1] for dj in [-1, 0, 1] if not (di == dj == 0)]

        ####    EDGES AND CORNER PIECES
        for i in range(len(board)):
            for j in range(len(board)):
                cell = (i, j)
                if board[i][j] == BLACK:
                    # count pieces
                    player_pieces += 1
                    val += self.evaluate_action(board, cell, instance)
                    # print(f"---BLACK val={val}")
                    
                elif board[i][j] == WHITE:
                    # print(f"opponent_pieces += 1")
                    opponent_pieces += 1
                elif board[i][j] == 0:
                    empties += 1

                ####    FRONTIER PIECES
                # if a position is filled
                if board[i][j] != 0:
                    for di, dj in directions:
                        ni, nj = i + di, j + dj
                        # look for an empty position next to it = frontier
                        if 0 <= ni <= size and 0 <= nj <= size and board[ni][nj] == 0:
                            if board[i][j] == BLACK:
                                # print(f"player_frontier += 1")
                                player_frontier += 1
                            else:
                                # print(f"opponent_frontier += 1")
                                opponent_frontier += 1
                            break
        ####   CALCULATE GAME PHASE
        if empties > 20:
            phase = 1
        elif empties <= 20 and empties > 10:
            phase = 2
        else:
            phase = 3
        # print(f"phase= {phase}")

        #####      MOBILITY AND POTENTIAL MOBILITY
        player_mobility = len(instance.available_actions(board,  BLACK))
        opponent_mobility = len(instance.available_actions(board, WHITE))
        
        # Piece ratio
        # print(f"player_pieces={player_pieces}, opponent_pieces={opponent_pieces}")
        ratio = (player_pieces - opponent_pieces) / (player_pieces + opponent_pieces) 

        # Assuming player_pieces and opponent_pieces are already calculated
        def adjusted_sigmoid(x):
            return 2 / (1 + math.exp(-x)) - 1


        total_pieces = player_pieces + opponent_pieces
        if total_pieces == 0:
            ratio = 0  # Avoid division by zero in an empty or initial board state
        else:
            ratio = (player_pieces - opponent_pieces) / total_pieces
        ratio *= 8
        sigratio = adjusted_sigmoid(ratio)
        # multiply by bias
        
        # print(f'---sigratio= {sigratio}')

        if sigratio < self.minratio:
            self.minratio = sigratio
        if sigratio > self.maxratio:
            self.maxratio = sigratio
        # print(f'--ratio= {round(ratio,2)}\n')
        if phase == 3:
            val += ratio
    
        # Minimize frontier pieces
        val -= (player_frontier - opponent_frontier) / (player_frontier + opponent_frontier + 1) 
        # Mobility 
        val += (player_mobility - opponent_mobility) / (player_mobility + opponent_mobility + 1)  
        # print(f"val={val}")
        val = adjusted_sigmoid(val)
        # print(f"sigmoid val={val}")
        return val
    
    def evaluate_action(self, state, action, game_instance):
        '''

        '''
        # print(f"+++evaluate_action()")
        val = 0
        last_index = game_instance.size - 1
        # IF CORNER
        if self.is_corner(action, last_index):
            # print(f"---action in corner")
            val = 0.9
        # IF NEXT TO CORNER
        elif self.is_corner_adjacent(action, last_index):
            if not self.connects_to_corner(action, game_instance.state):
                # print(f"--- action next to corner ")
                val = -0.9
            elif self.connects_to_corner(action, game_instance.state):
                # print(f"--- action connects to corner ")
                val = 0.6

        
        # IF ON EDGE BUT NOT CORNER ADJACENT AND NOT CONNECTED TO CORNER
        elif self.is_edge(action, last_index):
            if  self.is_corner_adjacent(action, last_index) and not self.connects_to_corner(action, game_instance.state,  ):
                print(f"---{action} doesnt connet to corner???")
                # print(f"---action on edge")
                val = 0.3
            # IF ON EDGE AND CONNECTED TO CORNER 
            elif  self.connects_to_corner(action, game_instance.state,  ):
                # print(f"---action connected to corner")
                val = 0.5
            elif self.is_corner_adjacent(action, last_index):
                # print(f"---action corner adjacent")
                val = -0.5
        # IF EDGE ADJACENT
        elif self.is_edge_adjacent(state, action, last_index) and not self.is_corner_adjacent(action, last_index):
            # print(f"---action edge adjacent")
            val = -0.3
        return val

        # calculate if player has more available moves than opponent
        playeravails = game_instance.available_actions(state, player)
        opponent = game_instance.switchplayer(player)
        oppavails = game_instance.available_actions(state, opponent)
        if len(playeravails) > len(oppavails):
            print(f"---player has more available moves")
            val += 0.5
        elif len(playeravails) < len(oppavails):
            print(f"---opponent has more available moves")
            val -= 0.5
        # val += min(1, len(avails)/10)

        return val

    def invertboard(self, board):
        copyboard = deepcopy(board)
        for i in range(len(copyboard)):
            for j in range(len(copyboard)):
                if copyboard[i][j] == 1:
                    copyboard[i][j] = -1
                elif copyboard[i][j] == -1:
                    copyboard[i][j] = 1
        return copyboard
    
    def save_data(self, filename):
        with open(f'qtables/{filename}.pickle', 'wb') as f:
            # print(f"+++saving qtable: {self.q}")
            pickle.dump(self.q, f)

    @classmethod
    def load_data(self, filename ):
        # print(f"+++load_data  with {filename}")
        with open(f'qtables/{filename}.pickle', 'rb') as f:
            q = pickle.load(f)
            return q
 
    def evalweights(self, board):
        print(f"+++evalweights()")
        board = np.array(board)
        weights = np.array([
            [1, -0.25, 0.1,  0.1, -0.25, 1],
            [-0.25, -0.25, 0.01, 0.01, -0.25, -0.25],
            [0.1, 0.01, 0.05, 0.05, 0.01, 0.1],
            [0.1, 0.01, 0.05, 0.05, 0.01, 0.1],
            [-0.25, -0.25, 0.01, 0.01, -0.25, -0.25],
            [1, -0.25, 0.1,  0.1, -0.25, 1]
        ])

        # Element-wise multiplication followed by sum
        result = np.sum(board * weights)
        return result

    def generate_2_tuples(self, board_size):
        tuples_list = []
        for k in range (1,10):
            for i in range(board_size):
                for j in range(board_size):
                    if j < board_size - 1:  # Horizontal tuples
                        tuples_list.append(((i, j), (i, j + 1),k))
                    if i < board_size - 1:  # Vertical tuples
                        tuples_list.append(((i, j), (i + 1, j),k))
                    if i < board_size - 1 and j < board_size - 1:  # Diagonal right-down
                        tuples_list.append(((i, j), (i + 1, j + 1),k))
                    if i < board_size - 1 and j > 0:  # Diagonal left-down
                        tuples_list.append(((i, j), (i + 1, j - 1),k))
        # print(f"---tuples_list={tuples_list}")
        return tuples_list


    ### CANONICAL BOARD REPRESENTATION

    def rotate_board(self,board):
        """Rotate the board 90 degrees clockwise."""
        return [list(row) for row in zip(*board[::-1])]

    def reflect_board(self,board):
        """Reflect the board horizontally."""
        return [row[::-1] for row in board]

    def symmetries_with_xforms(self, board):
        # Initial board with no transformations
        rotations = [(board, ["none"])]

        # Generate rotations
        for i in range(1, 4):
            new_rotation = self.rotate_board(rotations[-1][0])
            rotations.append((new_rotation, [f"rotate {90 * i}"]))

        reflections = []
        # Generate reflections for original and each rotation
        for rot, trans in rotations:
            new_reflection = self.reflect_board(rot)

            # Determine correct reflection label based on rotation before reflection
            if "rotate 90" in trans or "rotate 270" in trans:
                # A "horizontal" reflection becomes vertical after a 90 or 270-degree rotation
                reflection_label = "reflect vertically"
            else:
                # Otherwise, it's a horizontal reflection
                reflection_label = "reflect horizontally"

            # If initial transformation was "none", just use the determined reflection label
            if trans == ["none"]:
                reflections.append((new_reflection, [reflection_label]))
            else:
                reflections.append((new_reflection, trans + [reflection_label]))

        return rotations + reflections

    def determine_actual_reflection(trans):
        """
        This function would be used if we were dynamically determining the reflection type
        based on the transformations list. It's integrated into the solution above with an
        if-else construct.
        """
        pass

    
    def canonical_board(self,board):
        symmetries = self.symmetries_with_xforms(board)
        # print(f"---symmetries= {symmetries}")
        # Flatten boards for comparison and keep transformations
        flatsyms = [([element for row in sym[0] for element in row], sym[1]) for sym in symmetries]

        # Find the lexicographically smallest board and its transformation history
        lexicographically_smallest, transformations = min(flatsyms, key=lambda x: x[0])

        # Reconstruct the 2D list from the flattened version
        board_size = len(board)
        result = [lexicographically_smallest[i:i + board_size] for i in range(0, len(lexicographically_smallest), board_size)]
        # if transformations is none return None
        if transformations == ["none"]:
            transformations = None
        return result, transformations

    def canonical_move(self, xform, move, size):
        """
        Translate the move to the canonical board position
        """
        # print(f"+++rcanonical_move()")
        # print(f'---original move= {move}')
        # print(f'---xform= {xform}')
        # print(f'---size= {size}')
        if not xform:
                return move
        for xs in xform:
            # print(f'\n---move b4 xform= {move}') 
            # print(f'---this xform= {xs}')  
            
            if xs == "reflect horizontally":
                move = (move[0], size - 1 - move[1])
                # print(f'---xform= reflect horizontally= {move}')
            elif xs == "rotate 90":
                # move = (size - 1 - move[1], move[0])
                move = (move[1], size - 1 - move[0])

                # print(f'---xform= rotate 90 = {move}')
            elif xs == "rotate 180":
                move = (size - 1 - move[0], size - 1 - move[1])
                # print(f'---xform= 180 = {move}')
            elif xs == "rotate 270":
                move = ( size - 1 - move[1], move[0])
                

                # print(f'---xform= 270= {move}')
            elif xs == "reflect vertically":   
                move = (move[0],size - 1 - move[1],)
                # print(f'---xform= reflect vertically= {move}')
            
        # print(f'---canonical move= {move}')
        return move
    
    def retranslate_move(self, xform, move, size):
        """
        Retranslate the move to the original board position
        """
        print(f"+++retranslate_move()")
        print(f'---original move= {move}')
        print(f'---xform= {xform}')
        # print(f'---size= {size}')
        if not xform:
                return move
        for xs in reversed(xform):
            print(f'\n---move b4 xform= {move}') 
            print(f'---this xform= {xs}')  
            
            if xs == "reflect horizontally":
                move = (move[0], size - 1 - move[1])
                print(f'---xform= reflect horizontally= {move}')
            elif xs == "rotate 90":
                move = (size - 1 - move[1], move[0])
                print(f'---xform= rotate 90 = {move}')
            elif xs == "rotate 180":
                move = (size - 1 - move[0], size - 1 - move[1])
                print(f'---xform= 180 = {move}')
            elif xs == "rotate 270":
                move = ( size - 1 - move[0], move[1])
                print(f'---xform= 270= {move}')
            
        print(f'---retranslated move= {move}')
        return move

    # function ot turn canonical board back to original
    def retranslate_board(self, xform, board):
        """
        Retranslate the board to the original board position
        """
        if xform == "none":
            return board
        elif xform == "reflect horizontally":
            return self.reflect_board(board)
        elif xform == "rotate 90":
            return self.rotate_board(self.rotate_board(self.rotate_board(board)))
        elif xform == "rotate 180":
            return self.rotate_board(self.rotate_board(board))
        elif xform == "rotate 270":
            return self.rotate_board(board)

def plot(data):
    filetime=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    iteration = data['Iteration']
    alpha = data['Alpha']
    epsilon = data['Epsilon']
    deltaq = data['Deltaq']

    # Creating the plot
    fig, ax1 = plt.subplots()

    # Plotting epsilon and alpha on the primary y-axis
    ax1.set_xlabel('games')
    ax1.set_ylabel('Epsilon orange.  Alpha blue', color='tab:blue')
    ax1.plot(iteration, epsilon, label='Epsilon orange', color='tab:orange')
    ax1.plot(iteration, alpha, label='Alpha blue', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Creating a secondary y-axis for delta Q
    ax2 = ax1.twinx()
    ax2.set_ylabel('Delta Q Av/100 Games - green', color='tab:green')
    ax2.plot(iteration, deltaq, label='Delta Q, green', color='tab:green')
    ax2.tick_params(axis='y', labelcolor='tab:green')

    chartname = f"{filetime}.png"
    if not os.path.exists('plots'):
        os.makedirs('plots')
    chartnamepath = os.path.join('plots', chartname)
    plt.savefig(chartnamepath)
    plt.show()
    return chartnamepath

def print_q_table(q_table):
    for key, value in q_table.items():
        state, action = key  # Unpack the key
        # Convert state to a readable format
        state_str = '\n'.join(' '.join('X' if cell == 1 else 'O' if cell == -1 else '.' for cell in row) for row in state)
        
        # Determine player's color for printing
        
        # Format and print the information
        if value not in [0, 1, -1]:
        # if True:
            print(f"State:\n{state_str}")
            print(f"Action: {action}")
            print(f"Q-value: {value}")
            print("-" * 40)  # Separator for readability

def train(n,  filename='testing', verbose=False, monitor=True, makeplot=True):
    ai = OthelloAI(epsilon=0.0, alpha=0.3)
    
    maxeval = -float('inf') 
    mineval = float('inf')
    global VERBOSE
    global MONITOR
    if verbose:
        VERBOSE = True
    else:
        VERBOSE = False
    if monitor:
        MONITOR = True
    else:
        MONITOR = False

    def epsilon_decay(iteration, total_iterations, initial_epsilon=0.3, min_epsilon=0.05):
        decay_rate = math.log(2)/total_iterations
        epsilon = min_epsilon + (initial_epsilon - min_epsilon) * math.exp(- decay_rate * iteration)
        return epsilon

    def alpha_decay(iteration, total_iterations, initial_alpha=0.5, min_alpha=0.2):
        decay_rate = math.log(2)/total_iterations
        expo = - decay_rate * iteration
        alpha = min_alpha + (initial_alpha - min_alpha) * math.exp(expo)
        return alpha

    # if file isnt 'testing', check if it exists
    if filename != 'testing':
        if os.path.exists(f'qtables/{filename}.pickle'):
          # print(f"Loading qtable from {filename}")
            #### LOAD IT
            ai.q = ai.load_data(filename)

    # ai0wins = 0
    completed = 0
    trainingdata = []
    ####      PLAY N GAMES
    for i in range(n):
        if i % 100 == 0:
            ai.deltaqaverage = ai.deltaqaverage/100
            print(f"\n>>>>>>>>>>Playing training game {i}")
            print(f'---ai.epsilon= {ai.epsilon:.5f}')
            print(f'---ai.alpha= {ai.alpha:.5f}')

            
            print(f'---deltaq average/100 games= {ai.deltaqaverage:.5f}')
            trainingdata.append({
            "Iteration": i,
            "Epsilon": ai.epsilon,
            "Alpha": ai.alpha,
            "Deltaq": ai.deltaqaverage,
        })
            ai.deltaqaverage = 0
        # ai.epsilon = epsilon_decay(i, n)
        ai.epsilon = epsilon_decay(i, n)
        ai.alpha = alpha_decay(i, n)
        # print(f"\n>>>>>>>>>>Playing training game {i + 1}")
        game = Othello()
        
        ####      Keep track of last move made by either player
        last = {
            BLACK: {"state": None, "action": None},
            WHITE: {"state": None, "action": None}
        }
      
        moves = 0
        ####      GAME LOOP PLAYS 1 GAME
        while True:
            moves += 1
            opponent = game.switchplayer(game.player)
            if VERBOSE:
                print(f'\n>>>MOVE FOR {game.playercolor(game.player)}')
                print(f'---SAVED BOARD:')
                game.printboard(game.state)
    
            board = game.state
            ####  IF AI IS WHITE, INVERT
            if game.player == WHITE:
                board = ai.invertboard(game.state)
                if VERBOSE:
                        print(f"---inverted+canon board for white player")
                        game.printboard(board)

            ####      MAKE MOVE
            availactions = game.available_actions(board, BLACK)
            # game.printboard(game.state)
            # print(f"...availactions={availactions}")
            if availactions:
                # SAVE AS LAST THE ORIGINAL, CANONICAL BUT UNINVERTED BOARD FOR WHITE
                if game.player == WHITE:
                    last[game.player]["state"] = ai.invertboard(board)
                else:
                    last[game.player]["state"] = board
                # if VERBOSE:
                    # print(f'---AVAILS. BOARD FOR BOTH COLOURS:')
                    # game.printboard(board)
                    # print(f'---LAST STATE SAVED FOR {game.playercolor(game.player)}:')
                    # game.printboard(last[game.player]["state"])
                    # print(f'---LAST STATE SAVED FOR {game.playercolor(opponent)}:')
                    # if last[opponent]["state"]:
                        # game.printboard(last[opponent]["state"])
                # MAKE MOVE
                new_state, action_caps = game.aimoves(board, availactions, BLACK, ai)
                action = action_caps[0]

                # SAVE THIS  AS LAST ACTION
                last[game.player]["action"] = action

                # CANON BOARD AND ACTION AFTER MOVE
                canonboard, xform = ai.canonical_board(board)
                canonaction = ai.canonical_move(xform, action, game.size)
         
                #  UPDATE Q (WITH INVERTED BOARD IF WHITE)
                ai.update(canonboard, canonaction, new_state, 0, game)
                
                # MAKE NEW STATE CANONICAL
                new_state, xform = ai.canonical_board(new_state)  
                if VERBOSE:
                    print(f'---xform= {xform}')
                    print(f'---action= {action}')
                canonaction = ai.canonical_move(xform, action, game.size)
                if VERBOSE:
                    print(f'---xform= {xform}')
                    print(f'---canonedaction= {action}') 
                

                if not game.gameover(new_state):

                    action = canonaction
                    
    
                    # IF AI IS WHITE, RE-INVERT BOARD
                    if game.player == WHITE:
                        new_state = ai.invertboard(new_state)
                        if VERBOSE:
                            print(f"---RE-inverted board for white player")
                            game.printboard(new_state, action)
                        # CANONIZE NEW STATE AND ACTION
                        new_state, xform = ai.canonical_board(new_state)
                        action = ai.canonical_move(xform, action, game.size)
                        if VERBOSE:
                            print(f'---canonical reinverted board:')
                            game.printboard(new_state, action)
                    if VERBOSE:    
                        print(f'---BOARD AFTER MOVE')
                        game.printboard(new_state, action)
                        # print(f"---last[game.player]['state']={last[game.player]['state']}")
                        # print(f"---last[game.player]['action']={last[game.player]['action']}")
                        game.printboard(last[game.player]["state"], last[game.player]["action"])
                     ####      SAVE THE NEW STATE
                    game.state = new_state

                    

                    # if moves == 10:
                    #     break
                    # print(f"---moves= {moves}")

                    ####      IF GAME OVER UPDATE Q VALUES WITH FINAL REWARDS
                elif game.gameover(new_state):
                    game.winner = game.calc_winner(new_state)

                    ####     PLAYER WON
                    if game.player == game.winner:
                        # print(f"...winning move for {game.playercolor(game.player)}={last[game.player]['action']}")
                        # print(f"...last[game.player]={last[game.player]}")
                        # game.printboard(last[game.player]['state'])

                        ai.terminalupdate( last[game.player]["state"],  last[game.player]["action"],  1)

                        ai.terminalupdate( last[opponent]["state"],  last[opponent]["action"], -1)

                    #####     PLAYER LOST
                    elif game.winner is not game.player:
                        assert game.winner != game.player
                        # print(f"...last[game.player]={last[game.player]}")
                        ai.terminalupdate( last[game.player]["state"], last[game.player]["action"], -1)

                        ai.terminalupdate( last[opponent]["state"],  last[opponent]["action"], 1)

                    ####     IT WAS A TIE
                    else:
                        assert game.winner == None
                        ai.terminalupdate(last[BLACK]["state"], last[BLACK]["action"], 0) 
                        ai.terminalupdate( last[WHITE]["state"], last[WHITE]["action"],0)


                    ai.deltaqaverage = ai.deltaqaverage + (ai.sumdeltaqs/ai.numqupdates)
                    # print(f"---end game deltaqaverage={ai.deltaqaverage}")
                    ai.sumdeltaqs = 0
                    ai.numqupdates = 0
                    break
            ####      SWITCH PLAYERS . 
            game.player = game.switchplayer( game.player)
                
        completed += 1
        # if completed % 100 == 0:
        #     print(f"played games = {completed}")
            

    data = pd.DataFrame(trainingdata)   
    print(f"Done training {completed} games")
    print(f'--qtable: {filename} len= {len(ai.q)}')
    print(f'--qs used= {ai.qs_used}')
    x = ai.qs_used/n
    print(f'--qs used/n= {x:.5f}')
    # print(f'---trainingdata= {trainingdata}')

    ai.save_data(filename)

    if makeplot:
        plot(data)

    ####      RETURN THE TRAINED AI
    return ai



def evaluate(n, qtable, benchmarkq=None, verbose=False, monitor=False):
    """
    Evaluate the performance of `ai` against `benchmarkai` by playing `n` games.
    """
    global VERBOSE
    global MONITOR
    if verbose == True:
        VERBOSE = True
    if monitor == True:
        MONITOR = True
    
        
    testai = OthelloAI(epsilon=0, alpha=0)  

    testai.q = testai.load_data(qtable)
    benchmarkai = OthelloAI()
    if benchmarkq:
        benchmarkai.q = benchmarkai.load_data(benchmarkq)
    benchmarkai.color = WHITE  

    wins = 0
    losses = 0
    ties = 0

    ####     CALC EVERY OTHER GAME
    for i in range(n):
        # print(f"\nPLAYING EVALUATION GAME {i+1}")
        

        game = Othello()
        # every other game, switch starter:
        if i % 2 == 0:
            # print(f'...i= {i} is even')
            testai.color = BLACK
            benchmarkai.color = WHITE
        else:
            # print(f'...i= {i} is odd')
            testai.color = WHITE
            benchmarkai.color = BLACK
        # print(f'---testai.color= {game.playercolor(testai.color)}')
        
        while not game.gameover(game.state):
            if game.player == testai.color:
                actor = 'testai'
            else:
                actor = 'benchmarkai'
            if VERBOSE:
                if game.player == testai.color:
                    print(f"\n==={game.playercolor(game.player)} to MOVE as {actor} ")
                    print(f'--retrieved game.state')
                    game.printboard(game.state)
            
            # MAKE CANONICAL BOARD
            canonboard, xform = testai.canonical_board(game.state)
            # if VERBOSE:
            #     print(f'---canonboard:')
            #     game.printboard(canonboard)
            #     print(f'---xform={xform}')

            ####    IF AI TO MOVE
            if game.player == testai.color:
                # print(f'--- AI to play as {game.playercolor(game.player)}')
                ####   IF AI IS WHITE, INVERT BOARD
                if game.player == WHITE == testai.color:
                    # print(f'---game.player=WHITE=testai.color= {game.player == WHITE == testai.color}')
                    canonboard = testai.invertboard(canonboard)
                    if VERBOSE:
                        print(f'---inverted board for white player')
                        game.printboard(canonboard)
                        # CACONICALIZE
                    canonboard, xform = testai.canonical_board(canonboard)
                    if VERBOSE:
                        print(f'---xform={xform}. canonboard=:')
                        game.printboard(canonboard)
                    # AVAILS FOR INVERTED BOARD
                    availactions = game.available_actions(canonboard, BLACK)
                    if VERBOSE:
                        print(f"---availactions={availactions}")
                    # CHECK IF THERE ARE ANY ACTIONS
                    if not availactions:
                        # print(f"---no actions available for testai")
                        game.player = game.switchplayer(game.player)
                        continue
                    # MAKE MOVE
                    newboard, aimove = game.aimoves(canonboard, availactions, BLACK, testai)
                    if VERBOSE:
                        print(f'---new board with move')
                        game.printboard(newboard, lastmove=aimove[0])
                    # RE-INVERT BOARD
                    newboard = testai.invertboard(newboard)
                    lastmove = aimove[0]
                    # print(f"---aimove as WHITE= {lastmove}")
                    # RE-CANONICALIZE
                    newboard, xform = testai.canonical_board(newboard)
                    # print(f'---xform={xform}')
                    
                    # CANONICALIZE MOVE
                    lastmove = testai.canonical_move(xform, lastmove, game.size)
                    if VERBOSE:
                        print(f'---lastmove after canonicalize= {lastmove}')
                        print(f'---newboard  after move REINVERTED+canonize')
                        game.printboard(newboard, lastmove=lastmove)
                elif game.player == BLACK == testai.color:
                    # print(f'---game.player=BLACK=testai.color= {game.player == BLACK == testai.color}')
                    availactions = game.available_actions(canonboard, game.player)
                    # CHECK IF THERE ARE ANY ACTIONS
                    if not availactions:
                        # print(f"---no actions available for testai")
                        game.player = game.switchplayer(game.player)
                        continue
                    # MAKE MOVE
                    newboard, aimove = game.aimoves(canonboard, availactions, game.player, testai)
                    if VERBOSE:
                        print(f"---aimove as BLACK= {aimove}")
                        print(f"---newboard after move")
                        game.printboard(newboard, lastmove=aimove[0])
                    lastmove = aimove[0]

            #### BENCHMARK TO MOVE
            elif game.player == benchmarkai.color:
                # print(f'---benchmarkai is {game.playercolor(benchmarkai.color)}, to play as {game.playercolor(game.player)}')
                availactions = game.available_actions(canonboard, game.player)

                # CHECK IF THERE ARE ANY ACTIONS
                if not availactions:
                    # print(f"---no actions available for benchmarkai")
                    game.player = game.switchplayer(game.player)
                    continue
                # print(f"---availactions={availactions}")

                # CHOOSE RANDOM ACTION
                random_key = random.choice(list(availactions.keys()))
                benchmove = availactions[random_key]

                benchmove = random.choice(list(availactions.items()))
                # print(f"---benchmove={benchmove}")
                
                # MAKE MOVE
                newboard = game.move(canonboard, benchmove[0], game.player)
                lastmove = benchmove[0]
            
            ####     SAVE THE NEW STATE

            # RE-CANONICALIZE
            # print(f'---end board b4 canonicalize')
            # game.printboard(newboard, lastmove=lastmove)
            newboard, xform = testai.canonical_board(newboard)
            # print(f'---applied xform= {xform}')

            # CANONICALIZE MOVE

            if xform:
                # print(f'---xform is true')
                lastmove = testai.canonical_move(xform, lastmove, game.size)
            # SAVE
            # print(f'---board to save after canonicalize')
            # game.printboard(newboard, lastmove=lastmove)
            game.state = newboard
            
            game.player = game.switchplayer(game.player)
            # break

        ####   EXITED WHILE LOOP BECAUSE GAME OVER

        # print(f"===game over")
        game.calc_winner(game.state)
        # game.printboard(game.state)
        # print(f"...game.winner= {game.winner}")
        # print(f"...testai.color= {testai.color}")
        if game.winner == testai.color:
            wins += 1
            # print(f"...END OF GAME {i+1}, \nTESTAI WINS. \n")
        elif game.winner == benchmarkai.color:
            losses += 1
            # print(f"...END OF GAME {i+1}. BENCHMARKAI WINS. \nlosses = {losses}||||||||||||\n")
        elif game.winner == None:
            ties += 1
            # print(f"...END OF GAME {i+1} \nTIE. ties={ties}||||||||||||\n")
        if i % 50 == 0:
            print(f"PLAYED {i} GAMES")
    
    # win/loss ratio
    if losses == 0:
        winlossratio = 1
    else:
        winlossratio= wins/losses
    winrate = (wins / n)*100
    lossrate = (losses / n)*100  
        
    print(f'---q records retrieved= {testai.qs_used}')
    print(f"wins: {wins}, losses: {losses}, ties: {ties}")
    
    print(f"winrate= {winrate}")
    print(f"lossrate= {lossrate}")
    print(f"win/loss ratio= {round(winlossratio, 2)}:1")
    ### print the q table used
    print(f"Qtable= {qtable} len={len(testai.q)}")


if __name__ == "__main__":
    app.run(debug=True)
