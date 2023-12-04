console.log("websocket.js loaded");
var client_id = Date.now()
//document.querySelector("#ws-id").textContent = client_id;
console.log("client_id: ", client_id);
var ws = new WebSocket(`wss://6935-191-156-47-50.ngrok-free.app/ws/${client_id}`);
ws.onopen = function() {
    console.log(nameClient);
    console.log(last_name);
    console.log(rolClient);
    if (rolClient == Rol.Secretaria) {
      ws.send("connected");
    }
};

ws.onmessage = function(event) {
    console.log("message received: ", event.data);
/*     var messages = document.getElementById('messages')
    var message = document.createElement('li')
    var content = document.createTextNode(event.data)
    message.appendChild(content)
    messages.appendChild(message) */
};

function sendMessage(message) {
    ws.send(message)
}

