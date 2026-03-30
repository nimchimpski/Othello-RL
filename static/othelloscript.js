

class Othellogame {
    constructor() {
        this.human = null;
        this.ai = null;
        this.newgameatrib = false;
        this.message1 = document.getElementById("message1");
        this.message2 = document.getElementById("message2");
        this.boardenabled = true;
        // this.init();
        this.cells = document.querySelectorAll('.cell');
        this.cells.forEach(cell => {
            cell.addEventListener('click', this.cellClickHandler.bind(this));
        });
        // console.log('cells=', this.cells);
        // console.log('cells[0]=', typeof this.cells);
        this.board = []
    }
    //  player = HUMAN or AI
    //  human = BLACK or WHITE
    // playercol = BLACK or WHITE
    cellClickHandler(event) {
   
        // console.log('this=', this);
        if (!this.boardenabled) {
            // console.log('...+++cellClickHandler(), Boardenabled=false, not calling play()');
            return; 
            }
        let cellid=event.target.id;
        // console.log('...+++cellClickHandler(), calling play(cellid) with ', cellid);
        this.play(cellid);
        
    }

    hideElement(element) {
        console.log('...+++hideElement()=', element);
        var x = document.getElementById(element);
        console.log('...+++hideElement(), x=', x);
        if (x) {
            x.style.display = "none";
        } else {
            console.log('...+++hideElement(), x not found');
        }
    }

    showElement(element) {
        console.log('...+++showElement()', element);
        var x = document.getElementById(element);
        if (x) {
            x.style.display = "block";
        } else {
            console.log('...+++showElement(), x not found');
        }
    }

    enableElement(element) {
        if (element) {
            // console.log('...+++enableElement(), element=', element);
            const x = document.getElementById(element);
            x.disabled = false;
        }
        else {
            console.log('...+++enableElement(), element not found');    
        }
    }

    disableElement(element) {
        if (element) {
            // console.log('...+++disableElement(), element=', element);
            const x = document.getElementById(element);
            x.disabled = true;
        }
       
    }
    // Define a function to remove event listeners
    removeEventListeners() {
        console.log('...+++removeEventListeners()');    
        this.cells.forEach(cell => {
            // remove event listener
            cell.removeEventListener('click', event => {
                this.play(event.target.id);
            })
        });
    }

    chooseplayerfunc() {
        console.log('...+++chooseplayerfunc()');
        this.showElement("chooseplayer");
        // this.showElement("board");
        this.message1.innerHTML = "Choose your player";
        this.message2.innerHTML = "Black plays first";
        this.message2.style.border = "None";
    }

    startGame(chosenplayer) {
        console.log('...+++startGame(), human chose', chosenplayer);
        // convert choesnplayer to int
        this.human = Number(chosenplayer);
        // console.log('...human=', this.human);
        this.ai = (chosenplayer === '1') ? Number('-1') : Number('1');
        // console.log('...ai=', this.ai);
        if (chosenplayer === '1'){
            
            // SEND REQUEST FOR BOARD WITH VALID MOVES
            console.log('...requesting initial black avail  board. ');
            this.sendrequest(true, null, this.human, this.human); 
            this.message2.innerHTML = "Your turn " }
            // CALL FUNCTION TO ENABLE VALID MOVES?
            // console.log('...boardenabled=', this.boardenabled)
        else  {
            console.log('...requesting ai move. ');
            this.sendrequest(true, null, this.human, this.ai);
            this.message2.innerHTML = "Computer thinking...";
            }
        let humancolor = null;
        console.log('...humancolor 1 =', humancolor);

        if (this.human === 1) {
            humancolor = "black";
        }
        else {
            humancolor = "white";
        }
        this.message1.innerHTML = "You are playing as " + humancolor;
        this.newgameatrib = false;

        this.hideElement("chooseplayer");
        // ?????????
        // if (this.human === 'O') {
        //     this.play( );
        // }
    }

    winnercheck(winner) {
        // is it a tie?
        if (winner === 'TIE')
           var result = 'FOOLS. You both lost.'
        else {
            var result = (winner === this.human ? "You win!" : "You lose!");}
        return result
    //    this.message1.innerHTML = 'GAME OVER   '+ result;
    //    this.message2.style.border = "1px solid white"
    //    this.message2.innerHTML = "Play again?";
    //   TODO : CALL FUNCTION TO DISABLE BOARD
    //    console.log('...disable board?, boardenabled=', this.boardenabled )
       // this.removeEventListeners();
           
    }  

    sendrequest(newgame = false, humanmove = null, human = null, player = null) {
        console.log('...request sent with: newgame=', newgame, 'humanmove=', humanmove, 'human=', human, 'player=', player);
        this.message2.disabled = true;
        fetch('othello/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'newgame': newgame, 'humanmove': humanmove, 'human': human, 'player': player}),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('response for aimove request was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('response data:', data, typeof data);
            let player=data.player;
            
            console.log('...this.human=', this.human);
            console.log('...player = human?', player == this.human);
            console.log('...gameover =', data.gameover);

            // update board
            this.updateboard(data.board);


            if (data.gameover == null) { 
                // check if newgame - human still has to choose player
                if (data.newgame == true) {
                    if (player == null) {
                        this.chooseplayerfunc();
                        
                    }}
                    // IF PLAYER = HUMAN
                    // RESPONSE WAS HUMAN AVAIL MOVES
                else if (player == this.human) {
                        console.log('...player == human', player == this.human)
                        console.log('...RECIEVED BOARD AI MOVE and NEW VALID MOVES - NOW UPDATE BOARD, + REQUEST AI MOVE');
                                            // change message
                        this.message2.innerHTML = "Your turn - come on";
                        // this.boardenabled = true;
                        // TODO : CALL FUNCTION TO ENABLE BOARD
                    }
                    // IF PLAYER = AI
                    // RESPONSE WAS BOARD WITH CAPTURED PIECES
                else if (player == this.ai) {
                        console.log('...player = ai?', player == this.ai)
                        console.log('...RECIEVED BOARD WITH CAPTURED PIECES - NOW UPDATE BOARD');
                        // change message
                        this.message2.innerHTML = "Computer thinking...";
                        // NOW SEND REQUEST FOR AI MOVE
                        this.sendrequest(false, null, this.human, this.ai);
                    }
            
                }
            else {
                console.log('...RESPONSE = GAMEOVER: NOT NULL', data.gameover);
                const result = this.winnercheck(data.gameover);
                this.message1.innerHTML = 'GAME OVER   '+ result;
                this.message2.style.border = "1px solid white"
                this.message2.innerHTML = "Play again?";
                console.log('message2 type =', typeof this.message2)
                this.message2.disabled = false;

                // FUNCTION TO DISABLE BOARD
            } 
                
            
    })
        .catch((error) => {
            console.error('...response Error :', error);
        });
    }

    play(humanmove) {
        console.log('...+++play(),');
        // console.log('...+++play(), newgameatrib=' , this.newgameatrib,  'human=', this.human, 'ai=', this.ai, );

        // send request 1 for board the human move
        console.log("...sending request for board  with flips after human move")
        let player = this.human;
        // console.log('...player=', player)

        this.sendrequest(this.newgameatrib, humanmove, this.human, player)
        
        this.message2.innerHTML = "Computer thinking...";
        console.log('+--end of play())')
    }

    updateboard(board) {
        // UPDATE HTML BOARD
        console.log('...+++updateboard(), board=', board);
        for (var i = 0; i < board.length; i++) {
            for (var j = 0; j < board.length; j++){
                var cell = document.getElementById(i.toString() + j.toString());
                // console.log('...cell=', cell);
                if (board[i][j] === 1) {
                    cell.className = "disk blackdisk";
                    this.disableElement(cell.id);
                }
                else if (board[i][j] === -1) {
                    cell.className = "disk whitedisk";
                    this.disableElement(cell.id);
                }
                else if (board[i][j] === "*") {
                    cell.className = "disk validmove";
                    // eneble the cell
                    this.enableElement(cell.id);
                    }
                else if (board[i][j] === 0) {
                    cell.className = "disk";
                    this.disableElement(cell.id);
                }
                else if (board[i][j] === '+') {
                    cell.className = "disk blackdisk last"
                }
                else if (board[i][j] === '-') {
                    cell.className = "disk whitedisk last"
                }
                else {
                    cell.classList.remove("validmove");
                    this.disableElement(cell.id);
                }
                }
            }
        }



}




window.onload = () => {

    game= new Othellogame();
    // reuqest a new game
    console.log('...+++ONLOAD(). requesting initial board.')
    game.sendrequest(true);
    
    
};
