var socket = null;

//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        connected: false,//
        username: "display",//
        // roundState 0: waitingGameStart, 1:promptCollection, 2: answerSubmission, 3: voting, 4: votingResults, 5: totalScores}
        appState: {gameState: 0, round: 1, roundState: 0},//
        messages: [],//


        promptsToAnswerQueue: [], // Current prompt is 1st in queue
        answersToVoteQueue: [], // Current prompt is 1st in queue
        chatmessage: '',

        // Players = {username, ScoreThisSession, playerGameState}
        players: null,//
        audience: null,//

        adminIs: "No One 0.o",

        amAudience: false,
        waitingForNextPhase: false,
        waitingForPromptsToAnswer: true,
        waitingForAnswersToVote: true,
        answerOrder: [],
        voteResults: null //////////

    },
    mounted: function() {
        connect();
    },
    methods: {
        handleChat(message) {
            if(this.messages.length + 1 > 10) {
                this.messages.pop();
            }
            this.messages.unshift(message);
        },
        handleVoteResults(promptsToVotesObj){
            //

            console.log("Votes to displays recieved:")



            //const promptsToVotes = new Map(Object.entries(promptsToVotesObj.promptsToVotes));

            const promptsToVotesMap = new Map(Object.entries(promptsToVotesObj));
            app.voteResults = promptsToVotesMap

            for (const [key, obj] of promptsToVotesMap) {
                console.log(obj.promptOwner + ":" + obj.prompt + ":" + obj.answerOwner1 + ":" + obj.answer1 + ":" + obj.voters1)
                console.log(obj.promptOwner + ":" + obj.prompt + ":" + obj.answerOwner2 + ":" + obj.answer2 + ":" + obj.voters2)
            }


            /*for (const promptOwner of promptsToVotes.keys()) {
                console.log("key1: " + promptOwner)
                for (const prompt of promptsToVotes.get(promptOwner).keys()){
                    console.log("key2: " + prompt)
                    for (const answerOwner of promptsToVotes.get(promptOwner).get(prompt).keys()) {
                        console.log("key3: " + answerOwner)
                        for (const [answer, voters] of promptsToVotes.get(promptOwner).get(prompt).get(answerOwner)) {
                            console.log(answer + " Has a total votes of: " + voters.length)
                        }
                    }
                }
            }*/

            console.log("Votes Displayed")

        },
        handleTotalScores(){
            //handed by update and ejs

            if (app.appState.round === 3 && app.appState.roundState === 5){
                document.getElementById("lastRoundPrompt").innerHTML = "Thanks for playing, your scores will be added to your account at the end of the game :)"
            }

        },
        handlePromptsNumUpdate(count, target){
            document.getElementById("promptNumUpdate").innerHTML = (count + " prompts collected out of " + target)
        },
        handleAnswerNumUpdate(count, target){
            document.getElementById("answerNumUpdate").innerHTML = (count + " answers collected out of " + target)
        },
        handleVotesNumUpdate(count, target){
            document.getElementById("votesNumUpdate").innerHTML = (count + " votes collected out of " + target)
        },
    }
});

// incoming messages from server
function connect() {
    //Prepare web socket
    socket = io();

    //Connect
    socket.on('connect', function() {
        //Set connected state to true
        console.log("In Connect Func")
        socket.emit( "display", "");
        app.connected = true;
    });

    //Handle connection error
    socket.on('connect_error', function(message) {
        alert('Unable to connect: ' + message);
    });

    //Handle disconnection
    socket.on('disconnect', function() {
        alert('Disconnected');
        app.connected = false;
    });

    //Handle incoming chat message
    socket.on('chat', function(message) {
        app.handleChat(message);
    });



    //Handle promptsNumUpdate
    socket.on('promptsNumUpdate', function(json) {
        app.handlePromptsNumUpdate(json.count, json.target);
    });

    //Handle answerNumUpdate
    socket.on('answerNumUpdate', function(json) {
        app.handleAnswerNumUpdate(json.count, json.target);
    });

    //Handle votesNumUpdate
    socket.on('votesNumUpdate', function(json) {
        app.handleVotesNumUpdate(json.count, json.target);
    });

    //Handle votingResults message
    socket.on('votingResults', function(json) {
        // {po: {p:{ao: {a:a, v:[u1,u2,u3]}, ao: {a:a, v:[u4,u5,u6]}}}}}

        app.handleVoteResults(json);
    });

    //Handle votingResults message
    socket.on('totalScores', function() {
        app.handleTotalScores();
    });

    //Handle admin message
    socket.on('state', function(data) {
        //data = { appState: gameState, me: thePlayer, players: Object.fromEntries(players), audience: Object.fromEntries(audience)};
        console.log("Updating State: " + JSON.stringify(data))

        app.appState = data.appState;
        app.players = data.players
        app.audience = data.audience

    });


    //Handle adminIs message
    socket.on('adminIs', function(admin) {
        app.adminIs = admin
    });




}
