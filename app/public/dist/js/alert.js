let alertType = document.getElementById("alert-type").innerText;
let alertMessage = document.getElementById("alert-message").innerText;
let backgroundColor = alertType == "success" ? "#1f1f1f" : "#ff3333";
let textColor = "#fff"
let iconColor = alertType == "success" ? " " : "#65141a";
const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 10000,
    timerProgressBar: true,
    iconColor: iconColor,
    background: backgroundColor,
    color: textColor,
    didOpen: (toast) => {
        toast.onmouseenter = Swal.stopTimer;
        toast.onmouseleave = Swal.resumeTimer;
    }
});
Toast.fire({
    icon: alertType,
    title: alertMessage
});