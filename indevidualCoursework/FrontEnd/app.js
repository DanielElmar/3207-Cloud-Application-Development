'use strict';



//Set up express
const express = require('express');
const app = express();

//Setup socket.io
const server = require('http').Server(app);
const io = require('socket.io')(server);

//Set up fetch
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

// Backend server
const azureCloudUrl = "https://quiplash-dje1g20.azurewebsites.net/api"
const APP_KEY = "RUUCIC39eenl1HInj3IHWoYEmBp-iIPgcJTadEfQA_VZAzFu6Eb_FA=="

//Setup static page handling
app.set('view engine', 'ejs');
app.use('/static', express.static('public'));

//Handle client interface on /
app.get('/', (req, res) => {
  res.render('client');
});
//Handle display interface on /display
app.get('/display', (req, res) => {
  res.render('display');
});

//Start the server
function startServer() {
    const PORT = process.env.PORT || 8080;
    server.listen(PORT, () => {
        console.log(`Server listening on port ${PORT}`);
    });
}

//Server State
// Players = {username, gamesPlayedThisSession, ScoreThisSession, playerGameState, roundScores} OLD
// Players = {username, ScoreThisSession, playerGameState} NEW

// playerGameState 0: notjoined 1: joined Players 2: joined audience
let players = new Map();
let playerNameToSockets = new Map();
let socketsToPlayersName = new Map();
let admin = null;

let audience = new Map();
let audienceNameToSockets = new Map();
let socketsToAudienceName = new Map();

let usersToPasswords = new Map()

let newPromptsCount = 0;
let newPromptsWUser = new Map() // {o1:[p1,p2], o2:[p1,p2]}
let pastPromptsCount = 0;
let pastPromptsWUser = new Map(); // {o1:[p1,p2], o2:[p1,p2]}

let usersAlreadySubmitted = [];
let promptsToAnswers = new Map();
let promptAnswersCount = 0;

let promptsToVotes = new Map(); // {po: {p:{ao: {a:a, v:[u1,u2,u3]}, ao: {a:a, v:[u4,u5,u6]}}}}}
let votesCounted = 0;

let display = null;

let maxPlayers = 8;
let minPlayers = 3;
let appState = {gameState: 0, round: 0, roundState: 0};
//appState 0: waitingToStart, 1: gameInProgress
// roundState 0: notStated 1:promptCollection, 2: answerSubmission, 3: voting, 4: votingResults, 5: totalScores


// Backend Connection Functions

function mapToObj(map){
    const obj = {}
    for (let [k,v] of map)
        obj[k] = v
    return obj
}

function handleRegister(socket, username, password){


    console.log("handling Register Request")

    fetch(azureCloudUrl + "/player/register", {
        method: "POST",
        body: JSON.stringify({"username": username, "password": password}),
        headers: {"content-Type": "application/json", "x-functions-key": APP_KEY}
         })
        .then(res => res.json())
        .then(json => {
            console.log("BackEnd resp: " + JSON.stringify(json))
            socket.emit("loginResp", { "username": username, "msg": json["msg"]})
            addUser(json, socket, username, password)
        })
}

function handleLogin(socket, username, password){

    console.log("handling Login Request for:" + username + ":" + password)

    /*if (username === "Dann" || username === "Adin" || username === "Brad" ){
        socket.emit("loginResp", { "username": username, "msg": "OK"});
        addUser({"result": true, "msg": "OK"}, socket, username, password);
        return;
    }*/

    fetch(azureCloudUrl + "/player/login", {
        method: "POST",
        body: JSON.stringify({"username": username, "password": password}),
        headers: {"content-Type": "application/json", "x-functions-key": APP_KEY}
    })
        .then( res => res.json())
        .then( json => {
            console.log("BackEnd resp: " + JSON.stringify(json));
            socket.emit("loginResp", { "username": username, "msg": json["msg"]});
            addUser(json, socket, username, password);
        })
}

function addUser(json, socket, username, password){

    if (json["result"]){

        if (admin == null){
            admin = username;
            socket.emit("isAdmin", true);
            if (display != null) {
                display.emit("adminIs", admin)
            }
        }


        // Players = {username, ScoreThisSession, playerGameState}
        // playerState 0: notjoined 1: joined Players 2: joined audience

        // log Player in and add to game
        if (players.size >= maxPlayers || appState.gameState === 1){
            audience.set(username, {username: username, ScoreThisSession: 0, playerGameState: 2})
            audienceNameToSockets.set(username, socket)
            socketsToAudienceName.set(socket, username)
            announce(username + " joined the audience");

            if (appState.gameState === 3){
                for (const promptOwner of promptsToAnswers.keys()){
                    for (const prompt of promptsToAnswers.get(promptOwner).keys()){

                        let answers = promptsToAnswers.get(promptOwner).get(prompt)
                        socket.emit("answerToVoteOn", {prompt:prompt, promptOwner:promptOwner, answers:mapToObj(answers)});
                    }
                }
            }

        }
        else {
            players.set(username, {username: username, ScoreThisSession: 0, playerGameState: 1})
            playerNameToSockets.set(username, socket);
            socketsToPlayersName.set(socket, username);
            announce(username + " joined the players");

        }
        usersToPasswords.set(username, password)
        updateAll();
    }

}

//admin request
function handleAdmin(username, command) {

    console.log("\nADMIN COMMAND: " + command)

    if (username !== admin){
        console.log("Failed admin action from player " + username + " for " + command);
        return;
    }

    if (command === "start" && appState.gameState === 0){
        startGame();
    }else if (command === "nextPhase" && appState.gameState === 1){
        nextPhase();
    }else if (command === "nextRound" && appState.gameState === 1){
        nextRound();
    }else if (command === "endGame" && appState.gameState === 1){
        endGame();
    }else {
        console.log("Unknown admin command: " + command);
    }
}

function startGame() {

    if (players.size >= minPlayers) {


        console.log("Game Starting");
        announce("let the games begin");

        appState.gameState = 1
        appState.round = 1
        appState.roundState = 1

        usersAlreadySubmitted = []

        updateAll()

        if (display != null) {
            display.emit("promptsNumUpdate", {count: 0, target: (players.size + audience.size)})
        }
    }else{
        playerNameToSockets.get(admin).emit("notEnoughPlayerForStart", "")
    }
}

function nextPhase(){

    console.log("Starting Next Phase")

    switch (appState.roundState){
        case 1: appState.roundState++; updateAll(); startAnswerPhase(); break; // prompt collection
        case 2: appState.roundState++; updateAll(); startVotingPhase(); break; // Answer Phase
        case 3: appState.roundState++; updateAll(); startVotingResults(); break; // Voting Phase
        case 4: appState.roundState++; updateAll(); startShowTotalScores(); break; // Voting Results
        case 5: nextRound(); updateAll(); break; // total scores across rounds
    }
}

async function populatePrompts() {


    let targetPromptsNum = -1


    if (newPromptsCount < (players.size / 2) && (players.size % 2 === 0)) {
        // 1 prompt answer pp
        targetPromptsNum = players.size / 2
    } else{
        targetPromptsNum = players.size
    }

    console.log("Populating Prompts target is: " + targetPromptsNum + " newPromptsWUser: " + newPromptsCount + "~")

    pastPromptsWUser.clear()

    while ((newPromptsCount + pastPromptsCount) < targetPromptsNum) {

        console.log("Requesting more Prompts from DB: " + (targetPromptsNum - newPromptsCount - pastPromptsCount))

        await fetch(azureCloudUrl + "/prompts/get", {
            method: "POST",
            body: JSON.stringify({"prompts": (targetPromptsNum - newPromptsCount - pastPromptsCount)}),
            headers: {"content-Type": "application/json", "x-functions-key": APP_KEY}
        })
            .then(res => res.json())
            .then(json => {
                console.log("BackEnd resp: " + JSON.stringify(json));

                for (const prompt of json) {
                    console.log("Considering accepting past prompt: " + JSON.stringify(prompt))


                    let found = false
                    // {o1:[p1,p2], o2:[p1,p2]}
                    if (newPromptsWUser.get(prompt["username"]) !== undefined){
                        if (newPromptsWUser.get(prompt["username"]).includes(prompt["text"])){
                            found = true
                            console.log("Prompt found in newPrompts")
                        }
                    }

                    if (pastPromptsWUser.get(prompt["username"]) !== undefined){
                        if (pastPromptsWUser.get(prompt["username"]).includes(prompt["text"])){
                            found = true
                            console.log("Prompt was found in pastPromts")
                        }
                    }

                    if (!found) {

                        if (pastPromptsWUser.get(prompt["username"]) === undefined){

                            pastPromptsWUser.set(prompt["username"], [prompt["text"]]) ///

                        }else{
                            pastPromptsWUser.get(prompt["username"]).push(prompt["text"])
                        }
                        pastPromptsCount++;
                        console.log("Prompt was added to pastPrompts: " + [...pastPromptsWUser.entries()])

                    }
                }
            })
    }

    console.log("Finished populating Prompts, pastPromptsWUser: " + [...pastPromptsWUser.entries()] + " Count: " + pastPromptsCount)

    return targetPromptsNum
}

async function startAnswerPhase() {

    console.log("\nStarting Answer Phase")


    let targetPromptsNum = await populatePrompts(); // pastPromptsWUser {o1:[p1,p2], o2:[p1,p2]}

    if (display != null) {
        display.emit("answerNumUpdate", {count: 0, target: (pastPromptsCount + newPromptsCount) * 2})
    }

    let playerNamesToPromptList = new Map(); // playerNamesToPromptList {u1: [{p1,o1},{p2,o2}]}

    for (let userName of players.keys()) {
        playerNamesToPromptList.set(userName, [])
    }

    console.log("\nAssigning Prompts To Players")

    //assign newPromptsWUser to players

    let totalPromptsAssined = 0;

    // {o1:[p1,p2], o2:[p1,p2]}
    for (const fPromptOwner of newPromptsWUser.keys()) {
        for (const fPrompt of newPromptsWUser.get(fPromptOwner)) {

            console.log("\n\nAssigning newPrompt: " + fPrompt + " - By " + fPromptOwner)

            let promptAssignCount = 0

            let keysArray = [...players.keys()]
            for (let i = 0; i < players.size; i++) {

                let iOffSet = (i + totalPromptsAssined) % keysArray.length

                const userName = keysArray[iOffSet]
                if (promptAssignCount < 2) {

                    console.log("Considering " + userName + " for prompt. PromptCount: " + promptAssignCount + " TotalPromptAssined: " + totalPromptsAssined)

                    if (playerNamesToPromptList.get(userName).length < 2) {
                        // this player is not above or at the target num of prompts for players
                        console.log("Prompt assigned to: " + userName)
                        promptAssignCount++
                        playerNamesToPromptList.get(userName).push({promptOwner: fPromptOwner, prompt: fPrompt})
                    }
                }
            }
            totalPromptsAssined++
        }
    }

    console.log("New Prompts Assigned: " + [...playerNamesToPromptList.entries()])


    //assign pastPromptsWUser to players

    // {o1:[p1,p2], o2:[p1,p2]}
    for (const fPromptOwner of pastPromptsWUser.keys()) {
        for (const fPrompt of pastPromptsWUser.get(fPromptOwner)) {

            console.log("\n\nAssigning pastPrompt: " + fPrompt + " - By " + fPromptOwner)

            let promptAssignCount = 0

            let keysArray = [...players.keys()]
            for (let i = 0; i < players.size; i++) {

                let iOffSet = (i + totalPromptsAssined) % keysArray.length

                const userName = keysArray[iOffSet]
                if (promptAssignCount < 2) {

                    console.log("Considering " + userName + " for prompt. PromptCount: " + promptAssignCount + " TotalPromptAssined: " + totalPromptsAssined)

                    if (playerNamesToPromptList.get(userName).length < 2) {
                        // this player is not above or at the target num of prompts for players
                        console.log("Prompt assigned to: " + userName)
                        promptAssignCount++
                        playerNamesToPromptList.get(userName).push({promptOwner: fPromptOwner, prompt: fPrompt})
                    }
                }
            }

            totalPromptsAssined++
        }
    }

    console.log("All Prompts Assigned: ")

    for (let array of [...playerNamesToPromptList.entries()]){
        console.log("User: " + array[0])
        for (let prompts of array[1]){
            console.log("prompt: " + prompts.prompt + "  -Prompt Owner: " + prompts.promptOwner)
        }

    }


    console.log("\nSending Prompts to Players")

    // pastPromptsWUser {o1:[p1,p2], o2:[p1,p2]}
    // playerNamesToPromptList = {u1: [{p:p1,o:o1},{p:p2,o:o2}]}
    for (const username of playerNamesToPromptList.keys()) {
        for (const {prompt, promptOwner} of playerNamesToPromptList.get(username)) {

            let socket = playerNameToSockets.get(username)

            socket.emit("promptToAnswer", {prompt:prompt, promptOwner:promptOwner})
        }
    }

    console.log("Finished sending Prompts")



}

function startVotingPhase(){

    console.log("Starting Voting Stage")

    if (display != null) {
        display.emit("votesNumUpdate", {
            count: 0,
            target: (promptAnswersCount / 2) + ((promptAnswersCount / 2) * audience.size)
        })
    }


    // for each prompt Answer

    // {promptOwner: {promptText:{user1: ans1, user2: ans2}}}
    for (const promptOwner of promptsToAnswers.keys()){
        for (const prompt of promptsToAnswers.get(promptOwner).keys()){

            let answers = promptsToAnswers.get(promptOwner).get(prompt)
            //for (const username of promptsToAnswers.get(promptOwner).get(prompt).keys()) {
                // submit prompt answer to all players

            for( let [userName, socket] of playerNameToSockets){
                if (!answers.has(userName)){

                    socket.emit("answerToVoteOn", {prompt:prompt, promptOwner:promptOwner, answers:mapToObj(answers)});
                }
            }

            for( let [userName, socket] of audienceNameToSockets){
                socket.emit("answerToVoteOn", {prompt:prompt, promptOwner:promptOwner, answers:mapToObj(answers)});
            }


        }
    }

    console.log("All Answers Submitted to Players")
}

function startVotingResults(){
    console.log("Starting Voting Scores Phase")

    //     let promptsToVotes = new Map(); // {po: {p:{ao: {a:a, v:[u1,u2,u3]}, ao: {a:a, v:[u4,u5,u6]}}}}}

    let objects = []

    for (const promptOwner of promptsToVotes.keys()) {
        //console.log("key1: " + promptOwner)
        for (const prompt of promptsToVotes.get(promptOwner).keys()){
            //console.log("key2: " + prompt)


            let answerOwners = [];
            let answers = [];
            let voters = [];

            for (const answerOwner of promptsToVotes.get(promptOwner).get(prompt).keys()) {
                //console.log("key3: " + answerOwner)
                //for (const [key, value] of promptsToVotes.get(promptOwner).get(prompt).get(answerOwner)) {
                answerOwners.push(answerOwner)
                answers.push(promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("answer"))
                voters.push(promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("voters"))
                //console.log(answer + " Has a total votes of: " + voters.length)
                //}

                // addscores for this player
                //console.log("Scores for: " + answerOwner + " : " + JSON.stringify(players.get(answerOwner)) + " : To add: " + ( appState.round * 100 * promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("voters").length))
                players.get(answerOwner).ScoreThisSession += ( appState.round * 100 * promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("voters").length )
                console.log("Updated Scores for: " + answerOwner + " : " + JSON.stringify(players.get(answerOwner)))
            }

            objects.push({promptOwner:promptOwner, prompt:prompt, answerOwner1:answerOwners[0], answer1:answers[0], voters1:voters[0], answerOwner2:answerOwners[1], answer2:answers[1], voters2:voters[1]})
        }
    }


    //console.log( JSON.stringify({promptsToVotes: Object.fromEntries(promptsToVotes)}) )

    console.log("Sending Voting Results")
    console.log(JSON.stringify(objects))

    io.emit("votingResults", objects)
}

function startShowTotalScores(){
    console.log("Starting Total Scores Phase")
    io.emit("totalScores", "")
}

function nextRound(){
    console.log("Starting New Round!!")
    appState.round++
    appState.roundState = 1

    clearRoundData();

    updateAll();

    if (display != null) {
        display.emit("promptsNumUpdate", {count: 0, target: (players.size + audience.size)})
    }
}

function clearRoundData(){
    pastPromptsWUser.clear()
    pastPromptsCount = 0

    newPromptsWUser.clear()
    newPromptsCount = 0

    usersAlreadySubmitted = []
    promptAnswersCount = 0
    promptsToAnswers.clear()

    promptsToVotes.clear()
    votesCounted = 0
}

function endGame(){ // more of a end round
    console.log("In End Game Func")
    appState.gameState = 0;
    appState.roundState = 0;

    clearRoundData();

    // Update BackEnd
    for (const [username, obj] of players) { //new Map(Object.entries(

        console.log("Updating scores and games for: " + username + " Adding Score: " + obj.ScoreThisSession)
        fetch(azureCloudUrl + "/player/update", {
            method: "POST",
            body: JSON.stringify({"username": username, "password": usersToPasswords.get(username), "add_to_score": obj.ScoreThisSession, "add_to_games_played": 1}),
            headers: {"content-Type": "application/json", "x-functions-key": APP_KEY}
        })
            .then( res => res.json())
            .then( json => {
                console.log("BackEnd resp: " + JSON.stringify(json));
            })

    }
    updateAll()
}

//Chat message
function handleChat(message) {
    console.log('Handling chat: ' + message); 
    io.emit('chat',message);
}

//handle announcements
function announce(message){
    console.log("Announcement: " + message);
    io.emit("chat", message);
}

function updateAll(){
    updatePlayers()
    updateAudiences()
    updateDisplay()
}

function updateDisplay(){

    if (display != null) {
        console.log("Updating Display")
        const data = {appState: appState, players: Object.fromEntries(players), audience: Object.fromEntries(audience)};
        display.emit("state", data)
        display.emit("adminIs", admin)
    }else{
        console.log("No Display to update")
    }
}

//Update all players
function updatePlayers(){
    console.log("Updating all players");
    for( let [userName, socket] of playerNameToSockets){
        updatePlayer(socket);
    }
}

//Update ALL audience

function updateAudiences(){
    console.log("Updating all Audiences");
    for( let [userName, socket] of audienceNameToSockets){
        updateAudience(socket);
    }
}

//Update audience
function updateAudience(socket=null){
    const userName = socketsToAudienceName.get(socket)
    const thePlayer = audience.get(userName);
    const data = { appState: appState, me: thePlayer, players: Object.fromEntries(players), audience: Object.fromEntries(audience)};
    socket.emit("state", data);
}

//update Player
function updatePlayer(socket=null){

    const userName = socketsToPlayersName.get(socket)
    const thePlayer = players.get(userName);
    const data = { appState: appState, me: thePlayer, players: Object.fromEntries(players), audience: Object.fromEntries(audience)};
    socket.emit("state", data);
    //throw Error();
}

//handle PromptSubmit
function handlePrompt(socket, username, prompt){
    console.log("Handling Submitted Prompt: " + prompt + ": From: " + username)

    // one prompt per user per round
    if (usersAlreadySubmitted.indexOf(username) === -1){

        fetch(azureCloudUrl + "/prompt/create", {
            method: "POST",
            body: JSON.stringify({"username": username, "password": usersToPasswords.get(username), "text": prompt}),
            headers: {"content-Type": "application/json", "x-functions-key": APP_KEY}
        })
        .then( res => res.json())
        .then( json => {
            console.log("BackEnd resp: " + JSON.stringify(json));
            socket.emit("promptResp", { "username": username, "msg": json["msg"]});

            if (json["result"]){

                if (newPromptsWUser.get(username) === undefined){

                    newPromptsWUser.set(username, [prompt]) //
                }else{
                    newPromptsWUser.get(username).push(prompt)
                }
                newPromptsCount++;
                usersAlreadySubmitted.push(username);

                // auto next phase if all prompts have been collected

                if (display != null) {
                    display.emit("promptsNumUpdate", {count: newPromptsCount, target: (players.size + audience.size)})
                }
                if (newPromptsCount === (players.size + audience.size)){
                    nextPhase();
                }
            }
        })
    }}

//handle prompt Answer submit
function handlePromptAnswer(socket, username, prompt, promptOwner, answer){
    // {promptOwner: {promptText:{user1: ans1, user2: ans2}}}
    console.log("\nPrompt Answer Received: " + answer + " From Player: " + username + " For prompt: " + prompt)


    if (promptsToAnswers.has(promptOwner) && promptsToAnswers.get(promptOwner).has(prompt)){
        console.log("Case 1")
        promptsToAnswers.get(promptOwner).get(prompt).set(username, answer)
    }else if (promptsToAnswers.has(promptOwner) && !promptsToAnswers.get(promptOwner).has(prompt)){
        console.log("Case 2")
        promptsToAnswers.get(promptOwner).set(prompt, new Map())
        promptsToAnswers.get(promptOwner).get(prompt).set(username, answer)
    }else {
        console.log("Case 3")
        promptsToAnswers.set(promptOwner, new Map())
        promptsToAnswers.get(promptOwner).set(prompt, new Map())
        promptsToAnswers.get(promptOwner).get(prompt).set(username, answer)
    }
    promptAnswersCount++
    let answerCountTarget = (pastPromptsCount + newPromptsCount) * 2;

    console.log("Check Answer stored correctly: " + promptsToAnswers.get(promptOwner).get(prompt).get(username))

    console.log("Current received answer is: " + promptAnswersCount + " Target is: " + answerCountTarget)

    //setting votes to 0 for this answer
    //new code
    let answerOwner = username;
    if (promptsToVotes.has(promptOwner)){
        if ( promptsToVotes.get(promptOwner).has(prompt)) {
            if (promptsToVotes.get(promptOwner).get(prompt).has(answerOwner)) {
                console.log("Case 1")
            }else{
                console.log("Case 2")
                promptsToVotes.get(promptOwner).get(prompt).set(answerOwner, new Map)
            }
        }else{
            console.log("Case 3")
            promptsToVotes.get(promptOwner).set(prompt, new Map)
            promptsToVotes.get(promptOwner).get(prompt).set(answerOwner, new Map)
        }
    }else{
        console.log("Case 4")
        promptsToVotes.set(promptOwner, new Map)
        promptsToVotes.get(promptOwner).set(prompt, new Map)
        promptsToVotes.get(promptOwner).get(prompt).set(answerOwner, new Map)
    }

    promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).set("answer", answer)
    promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).set("voters", [])


    if (display != null) {
        display.emit("answerNumUpdate", {count: promptAnswersCount, target: (pastPromptsCount + newPromptsCount) * 2})
    }
    if (promptAnswersCount === answerCountTarget){
        nextPhase();
    }
}

// handle answer Vote submit
// answer = {username:username, answer:ans}}
function handleAnswerVote(socket, voterUsername, prompt, promptOwner, answer){
    const answerOwner = answer.username;
    const answerText = answer.answer;

    console.log("Vote received from player: " + voterUsername + " For answer: " + answerText + " From: " + answerOwner)

    if (promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("answer") === answerText) {
        promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("voters").push(voterUsername)
    }else{
        throw Error
    }

    console.log("Check Vote Stored Properly: " + promptsToVotes.get(promptOwner).get(prompt).get(answerOwner).get("voters") )

    votesCounted++
    let votesTarget = (promptAnswersCount / 2) + ( (promptAnswersCount / 2) * audience.size)
    console.log("Collected collected: " + votesCounted + " Target is: " + votesTarget)

    if (display != null) {
        display.emit("votesNumUpdate", {count: votesCounted, target: votesTarget})
    }
    if (votesCounted === votesTarget ){
        nextPhase();
    }


}


//Handle new connection
io.on('connection', socket => { 
  console.log('New connection');

    //Handle on chat message received
    socket.on('chat', message => {
    handleChat(message);
    });

    //Handle on register message received
    socket.on('register', message => {
        let userName = message.substring(0, message.indexOf(" "));
        let password = message.substring(message.indexOf(" ") + 1);
        handleRegister(socket, userName, password);
    });

    //Handle on login message received
    socket.on('login', message => {
        let userName = message.substring(0, message.indexOf(" "));
        let password = message.substring(message.indexOf(" ") + 1);
        handleLogin(socket, userName, password);
    });

    socket.on("display", message => {
        display = socket;
        console.log("Display connected -> Undating")
        updateDisplay()
    });

    //Handle admin message received
    socket.on('admin', command => {
        if (!socketsToPlayersName.has(socket)) return;
        handleAdmin(socketsToPlayersName.get(socket), command);
    });

    //Handle admin message received

    //Handle prompt message received
    socket.on('prompt', prompt => {
        if (socketsToPlayersName.has(socket) && appState.gameState === 1 && appState.roundState === 1) {
            handlePrompt(socket, socketsToPlayersName.get(socket), prompt);

        }else if ( socketsToAudienceName.has(socket) && appState.gameState === 1 && appState.roundState === 1) {
            handlePrompt(socket, socketsToAudienceName.get(socket), prompt);
        }
    });


    //Handle prompt answer message received
    // From Client: socket.emit("promptAnswer", {prompt:prompt, promptOwner:promptOwner, answer:answer} )
    socket.on('promptAnswer', json => {
        //socket.emit("promptAnswer", {prompt: prompt, promptOwner: promptOwner, answer: answer})
        if (socketsToPlayersName.has(socket) && appState.gameState === 1 && appState.roundState === 2) {
            handlePromptAnswer(socket, socketsToPlayersName.get(socket), json.prompt, json.promptOwner, json.answer);

            // function handlePromptAnswer(socket, username, prompt, answer){
        }else{
            console.log("ERROR6830")
        }
    });

    //Handle answer vote message received
    // From Client: socket.emit("answerVote", {prompt: prompt, promptOwner: promptOwner, answer: answerJSON})
    // {prompt:prompt, promptOwner:promptOwner, answer:{username:username, answer:ans2}}
    socket.on('answerVote', json => {
        if (socketsToPlayersName.has(socket) && appState.gameState === 1 && appState.roundState === 3) {
            handleAnswerVote(socket, socketsToPlayersName.get(socket), json.prompt, json.promptOwner, json.answer);

            // function handlePromptAnswer(socket, username, prompt, answer){
        }else if(socketsToAudienceName.has(socket) && appState.gameState === 1 && appState.roundState === 3){
            handleAnswerVote(socket, socketsToAudienceName.get(socket), json.prompt, json.promptOwner, json.answer);
        }
    });


    //Handle answer message received
    socket.on('next', message => {
        if (socketsToPlayersName.has(socket)) {
            if (socketsToPlayersName.get(socket).username === admin) {
                handleAnswer(socketsToPlayersName.get(socket), ans);
            }
        }
    });

    //Handle disconnection
    socket.on('disconnect', () => {

        let username = null;

        if (socketsToPlayersName.has(socket)) {
            username = socketsToPlayersName.get(socket)

            players.delete(username)
            playerNameToSockets.delete(username)
            socketsToPlayersName.delete(socket)

            if (admin === username) {
                admin = players.keys()[0];
                console.log("Assigning new Admin to: " + admin)

                if ( admin === undefined){
                    // No more players end game
                    endGame()
                }else {
                    playerNameToSockets.get(admin).emit("isAdmin", true);

                    if (display != null) {
                        display.emit("adminIs", admin)
                    }
                }
            }
        }else if (socketsToAudienceName.has(socket)) {
            username = socketsToAudienceName.get(socket)

            audience.delete(username)
            audienceNameToSockets.delete(username)
            socketsToAudienceName.delete(socket)
        }


    console.log(username + ' dropped connection');
    });
});

//Start server
if (module === require.main) {
  startServer();
}

module.exports = server;
