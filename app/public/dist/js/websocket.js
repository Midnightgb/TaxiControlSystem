console.log("websocket.js loaded");
console.log("idClient: " + idClient);
var host = window.location.host;
var protocol = window.location.protocol;
var wsProtocol = protocol === "https:" ? "wss://" : "ws://";
var ws = new WebSocket(`${wsProtocol}${host}/ws/${nameClient}/${idClient}`);

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
};

ws.onmessage = function (event) {
  console.log("message received: ", event.data);
  // get the current time
  var time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  // split time at the colons
  var formattedTime = time.split(':');
  // get hours
  var hours = parseInt(formattedTime[0]);
  // get AM/PM value
  var suffix = hours >= 12 ? ' pm' : ' am';
  //only -12 from hours if it is greater than 12 (if not back at mid night)
  hours = hours % 12 || 12;
  // convert hours to string
  formattedTime = hours + ':' + formattedTime[1] + suffix;
  // get the list of messages
  var messages = document.getElementById('messages')
  var message = document.createElement('li')
  var data = event.data

  // Add classes to the message element
  message.classList.add('message', 'flex', 'items-center', 'justify-center')

  var timeContainer = document.createElement('div')
  timeContainer.classList.add('flex-initial', 'w-16')

  var time = document.createElement('p')
  time.classList.add('text-sm')
  time.textContent = formattedTime
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
  content.style.maxWidth = "256px";
  messageContent.classList.add('text-sm', 'break-words')
  messageContent.textContent = data

  // Add the content to the message
  content.appendChild(messageContent)
  message.appendChild(content)

  //Add the vertical line to the message
  var verticalLineContainer = document.createElement('li')
  verticalLineContainer.classList.add('flex', 'items-center', 'justify-center')
  var verticalLineSpacerStart = document.createElement('div')
  verticalLineSpacerStart.classList.add('flex-initial', 'w-16')
  var verticalLine = document.createElement('div')
  verticalLine.classList.add('text-gray-500')
  verticalLine.textContent = "|"
  var verticalLineSpacerEnd = document.createElement('div')
  verticalLineSpacerEnd.classList.add('flex-initial', 'w-64')

  //group the vertical line elements
  verticalLineContainer.appendChild(verticalLineSpacerStart)
  verticalLineContainer.appendChild(verticalLine)
  verticalLineContainer.appendChild(verticalLineSpacerEnd)

  // Add the vertical line to the message
  messages.prepend(verticalLineContainer)

  // Add the message to the beginning of the list of messages
  messages.prepend(message)
  //scroll to the top of the messages
  messages.scrollTop = 0
};