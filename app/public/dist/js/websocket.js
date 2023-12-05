console.log("websocket.js loaded");
var client_id = Date.now()
//document.querySelector("#ws-id").textContent = client_id;
console.log("client_id: ", client_id);
var ws = new WebSocket(`wss://3173-191-156-47-159.ngrok-free.app/ws/${client_id}`);
ws.onopen = function () {
  console.log(nameClient);
  console.log(lastNameClient);
  console.log(rolClient);
  if (rolClient == "Rol.Secretaria") {
    ws.send(nameClient + " ha iniciado sesión.");
  }
};
window.onbeforeunload = function () {
  document.getElementById("logout").addEventListener("click", function () {
    console.log("logout");
    if (rolClient == "Rol.Secretaria") {
      ws.send(nameClient + " ha cerrado sesión.");
    }
  });
}
ws.onmessage = function (event) {
  console.log("message received: ", event.data);
  var time = new Date().toLocaleTimeString()
  console.log("Hora del mensaje: ", time);
  var messages = document.getElementById('messages')
  var message = document.createElement('li')
  var data = event.data

  // Add classes to the message element
  message.classList.add('message', 'flex', 'items-center', 'justify-center')

  var timeContainer = document.createElement('div')
  timeContainer.classList.add('flex-initial', 'w-16')

  var time = document.createElement('p')
  time.classList.add('text-sm')
  time.textContent = time
  // Add the time to the message
  timeContainer.appendChild(time)
  message.appendChild(timeContainer)

  var iconContainer = document.createElement('div')
  iconContainer.classList.add('mx-5')
  var icon = document.createElement('p')
  //check the type of message and set the color 
  icon.classList.add('p-1', 'rounded-xl', 'border-green-600', 'border-2')
  // Add the icon to the message
  iconContainer.appendChild(icon)
  message.appendChild(iconContainer)

  var content = document.createElement('div')
  content.classList.add('flex-initial', 'w-64')
  var messageContent = document.createElement('p');
  content.style.maxWidth = "250px";
  messageContent.classList.add('text-sm', 'break-words')
  messageContent.textContent = data

  // Add the content to the message
  content.appendChild(messageContent)
  message.appendChild(content)

  // Add the message to the list of messages
  messages.appendChild(message)
};