var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chat_socket = new WebSocket('ws://' + window.location.host + "/chat/" + document.getElementById('username').innerText);

chat_socket.onmessage = function(message) {
    var data = JSON.parse(message.data);
    var chat = document.getElementById('chat');
    chat.innerHTML += ' -------- ' + data.created_at + ' -------- ' + '<br>'
    chat.innerHTML += data.username + ' >>>  ' + data.message + '<br>'
};

function OnSubmitForm() {
	var message = {
        username: document.getElementById('username').innerText,
        message: document.getElementById('message').value,
    }
    chat_socket.send(JSON.stringify(message));
    return false;
}