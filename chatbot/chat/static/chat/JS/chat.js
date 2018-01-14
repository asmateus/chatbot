var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chat_socket = new WebSocket('ws://' + window.location.host + "/chat/" + document.getElementById('username').innerText);

chat_socket.onmessage = function(message) {
    var data = JSON.parse(message.data);
    var chat = document.getElementById('chat');
    var new_data = '';
    new_data += ' -------- ' + data.created_at + ' -------- ' + '<br>';
    new_data += data.username + ' >>>  ' + data.message + '<br>';
    chat.innerHTML = new_data + chat.innerHTML;
};

function OnSubmitForm() {
	var message = {
        username: document.getElementById('username').innerText,
        message: document.getElementById('message').value,
    }
    chat_socket.send(JSON.stringify(message));
    return false;
}