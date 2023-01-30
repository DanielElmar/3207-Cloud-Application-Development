var socket = null;

//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        connected: false,
        loggedIn: false,
        username: null,
        isAdmin: false,
        allowPromptSubmit: false,
        promptsToAnswerQueue: [], // Current prompt is 1st in queue
        answersToVoteQueue: [], // Current prompt is 1st in queue
        messages: [],
        chatmessage: '',
        appState: {gameState: 0, round: 1, roundState: 0},
        // roundState 0: waitingGameStart, 1:promptCollection, 2: answerSubmission, 3: voting, 4: votingResults, 5: totalScores}
        me: null,
        // Players = {username, ScoreThisSession, playerGameState}
        players: null,
        audience: null,
        amAudience: false,
        waitingForNextPhase: false,
        waitingForPromptsToAnswer: true,
        waitingForAnswersToVote: true,
        answerOrder: [],
        voteResults: null,
        testing: null,

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
        handleLoginResp(message){

            console.log("Handling Login Resp: " + JSON.stringify(message))

            document.getElementById('logInError').innerHTML = message["msg"];

            switch (message["msg"]){
                case "OK": app.loggedIn = true; app.username = message["username"]; break;
                case "Password less than 8 characters or more than 24 characters": document.getElementById('loginPassword').value = ""; break;
                case "Username less than 4 characters or more than 16 characters": document.getElementById('loginUsername').value = ""; break;
                case "Username already exists": document.getElementById('loginUsername').value = ""; break;
                case "Username or password incorrect": document.getElementById('loginUsername').value = ""; document.getElementById('loginPassword').value = ""; break;
            }
            document.getElementById('loginPassword').value = "";

        },
        handlePromptResp(message){

            console.log("Handling prompt Resp: " + JSON.stringify(message))

            document.getElementById('promptSubmitError').innerHTML = message["msg"];

            if (message["msg"] === "OK"){
                app.allowPromptSubmit = false
            }
        },
        handlePromptToAnswer(prompt, promptOwner){
            if (app.appState.gameState === 1 && app.appState.roundState === 2){
                console.log("New Prompt to answer: " + JSON.stringify(prompt))

                app.waitingForPromptsToAnswer = false

                if (app.promptsToAnswerQueue.length === 0){

                    document.getElementById("prompt").innerHTML = "Prompt: " + prompt;
                    document.getElementById("promptOwner").innerHTML = "Created By - " + promptOwner;


                    console.log("Prompt loaded on screen")
                }else{
                    console.log("Prompt put in queue")
                }

                app.promptsToAnswerQueue.push({prompt:prompt, promptOwner:promptOwner});

            }else{
                console.log("Client Not Ready to receive prompts to answer: " + app.appState.roundState)
                throw Error
            }
        },
        handleAnswerToVoteOn(prompt, promptOwner, answersObj) {
            // answers {user1: ans1, user2: ans2}

            app.waitingForAnswersToVote = false;

            if (app.appState.gameState === 1 && app.appState.roundState === 3) {

                console.log("New Answers to Vote on")

                const answers = new Map(Object.entries(answersObj));
                console.log("As Map: " + answers)

                if (app.answersToVoteQueue.length === 0) {

                    app.answerOrder = []

                    for (const userName of answers.keys()) { //Object.keys(answers)
                        console.log("Map Key: " + userName)
                        app.answerOrder.push(userName);
                    }

                    console.log("As Map2: " + answers)
                    console.log(app.answerOrder)
                    console.log(app.answerOrder[0])

                    let ans1 = app.answerOrder[0]

                    console.log(answers.get(ans1))
                    document.getElementById('promptToVote').innerHTML = "prompt: " + prompt
                    document.getElementById('promptToVoteOwner').innerHTML = "By - " + promptOwner
                    document.getElementById('leftPromptAnswer').innerHTML = answers.get(app.answerOrder[0])
                    document.getElementById('rightPromptAnswer').innerHTML = answers.get(app.answerOrder[1])


                    console.log("Answers loaded on screen")
                } else {
                    console.log("Prompt put in queue")
                }

                app.answersToVoteQueue.push({prompt: prompt, promptOwner: promptOwner, answersObj: answersObj});

                console.log("Answer Queue1: " + JSON.stringify(app.answersToVoteQueue))


            } else {
                console.log("Client Not Ready to vote on answers: " + app.appState.roundState)
                throw Error
            }

        },
        handleVoteResults(promptsToVotesObj){

            console.log("Votes to displays recieved:")

            const promptsToVotesMap = new Map(Object.entries(promptsToVotesObj));
            app.voteResults = promptsToVotesMap

            for (const [key, obj] of promptsToVotesMap) {
                console.log(obj.promptOwner + ":" + obj.prompt + ":" + obj.answerOwner1 + ":" + obj.answer1 + ":" + obj.voters1)
                console.log(obj.promptOwner + ":" + obj.prompt + ":" + obj.answerOwner2 + ":" + obj.answer2 + ":" + obj.voters2)
            }

            console.log("Votes Displayed")

        },
        handleTotalScores(){
            //handed by update and ejs

            if (app.appState.round === 3 && app.appState.roundState === 5){
                document.getElementById("lastRoundPrompt").innerHTML = "Thanks for playing, your scores will be added to your account at the end of the game :)"
            }

        },
        chat() {
            console.log("Sending Chat Message: " + this.chatmessage)
            socket.emit('chat', this.username + ": " + this.chatmessage);
            this.chatmessage = '';
        },
        register() {
            let userName = document.getElementById('loginUsername').value
            let password = document.getElementById('loginPassword').value

            console.log("Submitting Register Request for: " + userName + " : " + password)

            socket.emit( "register", userName + " " + password);
        },
        login() {
            let userName = document.getElementById('loginUsername').value
            let password = document.getElementById('loginPassword').value

            console.log("Submitting Login Request for: " + userName + " : " + password)

            socket.emit( "login", userName + " " + password);
        },
        startGame(){
            document.getElementById("adminErrorPrompt").innerHTML = "";
            socket.emit("admin", "start");
        },
        nextPhase(){
            console.log("Next Phase Request Submitted")
            socket.emit("admin","nextPhase")
        },
        nextRound(){
            socket.emit("admin","nextRound")
        },
        endGame(){
            socket.emit("admin","endGame")
        },
        submitPrompt(){
            if (app.allowPromptSubmit) {
                let prompt = document.getElementById('promptSubmit').value;

                console.log("Submitting Prompt: " + prompt)
                socket.emit("prompt", prompt)

                document.getElementById("promptSubmit").value = "";
                document.getElementById("promptSubmitError").innerHTML = "";
            }else{
                document.getElementById('promptSubmitError').innerHTML = "Sorry You Cant Submit Anymore Prompts This Round";
            }
        },
        submitAnswer() {

            const answerQueueObj = app.promptsToAnswerQueue.shift();

            if (!app.waitingForPromptsToAnswer) {

                if (answerQueueObj !== undefined) {


                    const answer = document.getElementById("answerSubmit").value
                    const prompt = answerQueueObj.prompt;
                    const promptOwner = answerQueueObj.promptOwner;

                    console.log("Submitting answer: " + answer + " For prompt: " + prompt + " -By: " + promptOwner)

                    socket.emit("promptAnswer", {prompt: prompt, promptOwner: promptOwner, answer: answer})
                }

                if (app.promptsToAnswerQueue.length !== 0) {
                    console.log("Displaying prompt from queue")

                    document.getElementById("prompt").innerHTML = app.promptsToAnswerQueue[0].prompt;
                    document.getElementById("promptOwner").innerHTML = "Created By - " + app.promptsToAnswerQueue[0].promptOwner;


                } else {
                    console.log("No More Prompts Left To Answer")
                    document.getElementById("prompt").innerHTML = ""
                    document.getElementById("promptOwner").innerHTML = "";

                    app.waitingForNextPhase = true

                }
                document.getElementById("answerSubmit").value = "";
                document.getElementById("answerSubmitError").innerHTML = "";

            }

        },
        submitVote(){

            let leftVote = document.getElementById('leftVote').checked
            let rightVote = document.getElementById('rightVote').checked
            //let voteSelected = false;
            let selectedVote = null;
            // 0-left, 1-right

            if (!leftVote && !rightVote) {
                document.getElementById('voteSubmitError').innerHTML = "You must select the prompt answer you like best"
                return;
            } else if (rightVote) {
                //voteSelected = true
                selectedVote = 1;

            }else{
                //voteSelected = true
                selectedVote = 0;

            }

            //if (voteSelected) {

                const voteQueueObj = app.answersToVoteQueue.shift();

                if (voteQueueObj !== undefined) {
                    console.log("From Queue as Obj: " + voteQueueObj)
                    // {prompt:prompt, promptOwner:promptOwner, answers:{user1: ans1, user2: ans2}}

                    const answers = new Map(Object.entries(voteQueueObj.answersObj));
                    console.log("From Queue as Map: " + answers)
                    let prompt = voteQueueObj.prompt
                    let promptOwner = voteQueueObj.promptOwner
                    let answerJSON = {username:app.answerOrder[selectedVote], answer: answers.get(app.answerOrder[selectedVote])}

                    console.log("Submitting Vote: " + answerJSON.answer + " -By: " + answerJSON.username + " For prompt: " + prompt + " -By: " + promptOwner)
                    // {prompt:prompt, promptOwner:promptOwner, answer:{username:username, answer:ans2}}
                    socket.emit("answerVote", {prompt: prompt, promptOwner: promptOwner, answer: answerJSON})

                }else{
                    console.log("ERROR85920")
                }



                if (app.answersToVoteQueue.length !== 0) {
                    console.log("Displaying answer from queue")
                    // set answer on screen
                    const voteObj = app.answersToVoteQueue[0]
                    console.log(voteObj)
                    const answers = new Map(Object.entries(voteObj.answersObj));

                    app.answerOrder = []
                    for (const userName of answers.keys()) {
                        console.log("Found U: " + userName)
                        app.answerOrder.push(userName);
                    }

                    document.getElementById('promptToVote').innerHTML = "prompt: " + voteObj.prompt
                    document.getElementById('promptToVoteOwner').innerHTML = "By - " + voteObj.promptOwner
                    document.getElementById('leftPromptAnswer').innerHTML = answers.get(app.answerOrder[0])
                    document.getElementById('rightPromptAnswer').innerHTML = answers.get(app.answerOrder[1])

                } else {
                    console.log("No More answers Left To vote on")

                    app.waitingForNextPhase = true
                }
            //}
        }

    }
});

// incoming messages from server
function connect() {
    //Prepare web socket
    socket = io();

    //Connect
    socket.on('connect', function() {
        //Set connected state to true
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

    //Handle register response message
    socket.on('loginResp', function(message) {
        app.handleLoginResp(message);
    });

    //Handle prompt response message
    socket.on('promptResp', function(message) {
        //socket.emit("promptResp", { "username": username, "msg": json["msg"]});
        app.handlePromptResp(message);
    });

    //Handle promptToAnswer message
    socket.on('promptToAnswer', function(message) {

        app.handlePromptToAnswer(message.prompt, message.promptOwner);
    });

    //Handle answerToVoteOn message
    socket.on('answerToVoteOn', function(json) {
        //{prompt:prompt, promptOwner:promptOwner, answers:{user1: ans1, user2: ans2}}
        app.waitingForAnswersToVote = false;
        app.handleAnswerToVoteOn(json.prompt, json.promptOwner, json.answers);
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

    //Handle game state update message
    socket.on('gameState', function(message) {
        console.log("Updating game state to: " + JSON.stringify(message))
        app.appState = message;
    });

    //Handle admin message
    socket.on('isAdmin', function(message) {
        app.isAdmin = message;
    });

    //Handle admin message
    socket.on('state', function(data) {
        //data = { appState: gameState, me: thePlayer, players: Object.fromEntries(players), audience: Object.fromEntries(audience)};
        console.log("Updating State: " + JSON.stringify(data))

        if (app.isAdmin) {
            document.getElementById("adminErrorPrompt").innerHTML = "";
        }

        if (data.appState.roundState !== app.appState.roundState){
            app.waitingForNextPhase = false;

            try {
                document.getElementById('promptSubmit').innerHTML = "";
                document.getElementById('promptSubmitError').innerHTML = "";
            }catch (e) { }

            try {
                document.getElementById('answerSubmit').innerHTML = "";
                document.getElementById('answerSubmitError').innerHTML = "";
            }catch (e) { }
        }

        if (data.me.playerGameState === 2){app.amAudience = true}

        app.appState = data.appState;
        app.me = data.me
        app.players = data.players
        app.audience = data.audience

        if (data.appState.gameState === 1 && data.appState.roundState === 1) {
            app.allowPromptSubmit = true;
        }
    });

    //Handle admin message
    socket.on('notEnoughPlayerForStart', function() {
        console.log("notEnoughPlayerForStart")
        if (app.isAdmin) {
            document.getElementById("adminErrorPrompt").innerHTML = "Not Enough Players To Start"
        }

    });




}
