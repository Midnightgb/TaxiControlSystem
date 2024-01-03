console.log("websocket.js loaded");
console.log("idClient: " + idClient);
console.log("nameClient: " + nameClient);
console.log("rolClient: " + rolClient);

var host = window.location.host;
var protocol = window.location.protocol;
var wsProtocol = protocol === "https:" ? "wss://" : "ws://";
var ws = new WebSocket(`${wsProtocol}${host}/ws/${nameClient}/${idClient}`);

ws.onopen = function () {
  var loggedIn = localStorage.getItem("hasLoggedIn")
  console.log("hasLoggedIn? " + localStorage.getItem("hasLoggedIn"));
  if (loggedIn == 1) {
    console.log("I'm logged in");
    console.log("hasLoggedIn? " + localStorage.getItem("hasLoggedIn"));
  } else {
    console.log("I'm not logged in");
    console.log(nameClient);
    console.log(rolClient);
    
    // get the current time
    formattedTime = getTime();
    localStorage.setItem("hasLoggedIn", 1);
    if (rolClient == "Secretaria") {
      ws.send(nameClient + " ha iniciado sesión. / " + formattedTime);
    }
  }
};

window.onload = function () {
  let logout = document.getElementById("logout");
  logout.addEventListener("click", function () {
    localStorage.setItem("hasLoggedIn", 0);

    formattedTime = getTime();
    ws.send(nameClient + " ha cerrado sesión." + " / " + formattedTime);
  });
}

ws.onmessage = function (event) {
  console.log("message received: ", event.data);
  // get the list of messages
  var messages = document.getElementById('messages')
  var message = document.createElement('li')
  var data = event.data
  var messageTxt = data.split(' / ')[0]

  // get the current time
  var timeSplitted = event.data.split('/');
  timeSplitted = timeSplitted[1];
  console.log(timeSplitted);
  // Add classes to the message element
  message.classList.add('message', 'flex', 'items-center', 'justify-center')

  var timeContainer = document.createElement('div')
  timeContainer.classList.add('flex-initial', 'w-16')

  var time = document.createElement('p')
  time.classList.add('text-sm')
  time.textContent = timeSplitted
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
  messageContent.textContent = messageTxt

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

function getTime() {
  var time = new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
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
  return formattedTime;
}