var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var chat_socket = new WebSocket('ws://' + window.location.host + "/chat/" + document.getElementById('username').innerText);

chat_socket.onmessage = function(message) {
    var data = JSON.parse(message.data);
    var chat = document.getElementById('chat');
    var content = document.createTextNode('<tr>' 
        + '<td>' + data.created_at + '</td>' 
        + '<td>' + data.username + '</td>'
        + '<td>' + data.message + ' </td>'
    + '</tr>');
    chat.appendChild(content);
};

function OnSubmitForm() {
	var message = {
        username: document.getElementById('username').innerText,
        message: document.getElementById('message').innerText,
    }
    chat_socket.send(JSON.stringify(message));
    return false;
}