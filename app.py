from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from flask_session import Session
from tempfile import mkdtemp
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import sys
import time
import json
import uuid
import os
import pickle
import time
import othello as othello
import threading
# hello me
####  OPTION TO CHANGE STATIC LOCATION!
# Keep Othello static assets self-contained and namespaced to avoid collisions with other apps.
app = Flask(__name__)
app.secret_key = "supermofustrongpword"

qtable = 'masterq'

# aiplayer = othello.OthelloAI(epsilon = 0)
aiplayer = None
_ai_lock = threading.Lock()
# print(f'---loaded q table = {aiplayer.q}')

def get_aiplayer():
    global aiplayer
    if aiplayer is None:
        with _ai_lock:
            if aiplayer is None:
                ai = othello.OthelloAI(epsilon=0)
                print(f"---aiplayer.epsilon= {ai.epsilon}")
                ai.q = ai.load_data(qtable)
                aiplayer = ai
    return aiplayer


####      CONFIGURE PROXYFIX WITH THE CORRECT PARAMETERS
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

####      CONFIG DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_ECHO'] = True

####      SET THE APP TO DEBUG MODE
environment = os.environ.get('FLASK_ENV', 'production')
app.config['ENV'] = environment
if environment == 'development':
    app.config['DEBUG'] = True
else:
    app.config['DEBUG'] = False
# app.debug = False

####      GAMEDB IS ACTUALLY A ROW IN THE DATABASE ? TODO CHANGE NAME
class Gamedb(db.Model):
    dbid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dbsessionid = db.Column(db.String, nullable=False)
    boardstate = db.Column(db.String, nullable=False)
    player = db.Column(db.String, nullable=False)
    human = db.Column(db.String, nullable=False)

    def saveboard(self, sessionid, board, player, human):
        # print(f'+++SAVEBOARD---')
        self.dbsessionid = sessionid
        self.boardstate = json.dumps(board)  ####      STORE BOARD AS A STRING
        self.player = json.dumps(player)
        self.human = json.dumps(human)
        ####      COMMIT THE CHANGES TO THE DATABASE
        db.session.commit()
        # print(f'---db_row saved= {self}')
        return board


    def getboard(self, sessionid):
        # print(f'+++GETBOARD---')
        db_row = Gamedb.query.filter_by(dbsessionid=sessionid).first()
        if db_row:
            # print(f'---db_row found= {db_row}')
            return json.loads(db_row.boardstate)
        else:
            # print('+++getboard: no db_row in db---')
            return None

    def __repr__(self):

        return f"<Gamedb(dbid={self.dbid}, dbsessionid={self.dbsessionid}, boardstate={self.boardstate}, player={self.player}, human={self.human})>"

with app.app_context():
    db.create_all()

def checkfordbrow(sessionid):
    db_row = Gamedb.query.filter_by(dbsessionid=sessionid).first()
    if db_row:
        # print(f'+++db_row found= {db_row}')
        return True
    else:
        print('+++checkfordbrow: no db_row in db---')
        return False

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


    ######  ROUTES  ######

@app.route('/', methods=['GET'])
def index():
    print('>>>INDEX ROUTE GET')
    ####       IF NO SESSIONID, CREATE ONE
    sessionid = session.get('sessionid')
    if not sessionid:
        print('---no sessionid in session---')
        session['sessionid'] = str(uuid.uuid4())
        sessionid = session['sessionid']
    # print(f'---sessionid={sessionid}')
    game = othello.Othello(size=6)
    size = game.size
    # render page with size of board variable
    return render_template('index.html', size=size)

@app.route('/othello/play', methods=['POST', 'GET'])
def play():
    # print('>>>PLAY ROUTE GET')

    EMPTY = 0
    BLACK = 1
    WHITE = -1
    winner = None
    # print(f'winner= {winner}')

    ####      GET SESSION ID
    sessionid = session.get('sessionid')
    # print(f'---sessionid={sessionid}')

    ####      CREATE GAME INSTANCE
    game = othello.Othello(size=6)
    
    ####      GET THE DB ROW
    db_row = Gamedb.query.filter_by(dbsessionid=sessionid).first()
    if not db_row:
        print('---no db_row in db---')
       
    #########      POST     #########
    if request.method == 'POST':
        print('>>>PLAY ROUTE POST')

        ####    PRINT ALL JSON
        print(f"\n--- request.json= {request.json} ---") 

        ####    GET VARIABLES FROM JSON
        player = request.json.get('player')
        if player:
            player = int(player)
        human = request.json.get('human')
        if human:
            human = int(human)
        humanmove = request.json.get('humanmove')
        if human == 1:
            ai= -1
        else:
            ai= 1
        # print(f"---human= {human}, ai= {ai}---")

        ####     CHECK IF NEW GAME + INITIALISE
        if request.json.get('newgame') == True:
            assert request.json.get('humanmove') != True

            ####   RESET BOARD
            board = game.create_board()
            # Server controls the opening turn: black always starts.
            # If human is white (-1), AI (black) should take the first move.
            if human == WHITE:
                player = BLACK
            else:
                player = human
            # print(f'---board initialised--{board}-')
            # print(f'---player= {human}---')
            # print(f'\n*******player= {player}---')

            ####    CREATE NEW ROW INSTANCE
            if not db_row:
                # print('---making new db_row--- ')
                db_row = Gamedb(
                        dbsessionid=sessionid,
                        boardstate=json.dumps(board),
                        player=json.dumps(player),
                        human=json.dumps(human)
                    )
                db.session.add(db_row)

            ####    SAVE INIT BOARD TO DB
            # print(f'---board to be saved= {board}')
            db_row.saveboard(sessionid, board, player, human)
            # print(f'---new db_row saved= {db_row}')

            ####  IF HUMAN IS BLACK RETURN VALID MOVES
            # print(f'---human= {human}, type= {type(human)}---')
            # print(f'---human == 1? {human == 1}---')
            if human == 1:
                print(f'---HUMAN IS BLACK SO GET AVAIL BOARD:',{human})
                board = game.boardwithavails(board, human, None)
                # print(f'---response board board={board}')
                player = 1 # DELET THIS?
        
            if human != -1:
            #### IF HUMAN IS NULL JUST SEND INITIAL BOARD
                responsevars = {'newgame': True, 'player': player, 'board': board}
                # print(f'---First responsevars= {responsevars}')
                return jsonify({'newgame': True,'board': board, 'player': player})

        #    NOT A NEW GAME

        # print('||| AFTER NEWGAME CONDITION')
        #### GET BOARD FROM DB
        board = db_row.getboard(sessionid)
        print(f"board retrieved1 = {board}")
    
        humanmove = request.json.get('humanmove')
        
        if humanmove: # ONLY SENT ONCE AFTER MOVE TO GET UPDATED BOARD
            # print(f'\n---" HUMANMOVE"---\n')
            #### MEANS WE ONLY WANT BOARD WITH FLIPS
            humanmovetuple = tuple(int(char) for char in humanmove)

            ####    UPDATE BOARD WITH HUMAN MOVE
            board = game.move(board, humanmovetuple,  player)
            
            print(f"--- board with human move flips = {board} ")
            #### NOW JUST SEND THE BOARD - GOTO RESPONSE
            player = game.switchplayer(player)
        
        else :
            ####             AI MOVE

            print(f'\n----GET AI MOVE. NO HUMANMOVE...HUMANMOVE WAS SAVED IN LAST REQUEST---\n')
            print(f"---player= {player} ai= -")
            ####  CHECK FOR MOVES AVAILABLE FOR AI
            availactions = game.available_actions(board, player)
            if  availactions:
                print(f'---ai avail actions= {availactions}')  

                ####     START THE TIMER
                start_time = time.time()

                ####     GET AI MOVE AND UPDATE BOARD
                ai = get_aiplayer()
                board, aimove = game.aimoves(board, availactions, player, ai)

                ####  SAVE BOARD    
                print(f'---board + ai move TO SAVE---')
                game.printboard(board)
                db_row.saveboard(sessionid, board, player, human)

                ####  CHECK TIME TAKEN AND DELAY IF LESS THAN 2 SECONDS
                ai_time = time.time() - start_time
                if ai_time < 2.5:
                    delay = 2.5 - ai_time
                    time.sleep(delay)

            else:
                print(f'---NO VALID MOVES FOR AI, SO CHECK HUMAN---')
                player = human
                board = game.boardwithavails(board, human, None)
                # CHECK HUMAN HAS MOVES - IF NOT GAME OVER 
                humanavails = game.available_actions(board, player)
                print(f'---avail moves hum={humanavails}')  
                if not  humanavails:
                    print(f'no human avails?={humanavails}. GAMEOVER')
                    winner = game.calc_winner(board)
                print(f'---response vars no ai moves: gameover={winner},player={player}, board={board}')
                return jsonify({'gameover':winner, 'player': player, 'board': board})
            # print(f'---board after ai move {board}---')
            #### NOW ITS HUMANS TURN: SWITCH PLAYER
            player = human

            ####    CHECK IF GAME OVER
            
            if game.gameover(board):
                print('---GAME OVER---')
                winner = game.calc_winner(board) 
                print(f'---winner= {winner}')
        
        print(f'---player to be returned= {player}')

        ###   SAVE BOARD

        print(f'---board to be saved= {board}')
        db_row.saveboard(sessionid, board, player, human)

        if player == human:
            print(f'---player= {player}, human= {human}')    
            print(f'---ai move {aimove}')
            aimove = aimove[0]
            ####   ADD VALID MOVES

            # Ai HAS MOVED - CHECK IF HUMAN CAN MOVE.
            print(f'----{player} avail moves={game.available_actions(board, player)}')

            if not game.available_actions(board, player):
                print(f'---NO VALID MOVES FOR HUMAN---')
                # IF NOT, PLAYER = AI
                player = ai
            else:
                print(f'---adding valid moves to board')
                
                board = game.boardwithavails(board, human, aimove)
        # if winner:
            # print(f'---q table = {aiplayer.q}')
        ####  PREPARE RESPONSE
        # responsedict = {'gameover': winner, 'player': player, 'board': board}
        print(f'---respnse gameover={winner}')
        print(f'---respnse player= {player}')
        print(f'---board to be returned= {board}')  
        game.printboard(board)
        # print(f'---respnse aimove= {aimove}')
        # print(f'---response normal  {responsedict}')
        # return json with board
        return jsonify({'gameover': winner, 'player': player, 'board': board})
    
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)