let alertType = document.getElementById("alert-type").innerText;
let alertMessage = document.getElementById("alert-message").innerText;
let backgroundColor = alertType == "success" ? "#1f1f1f" : "#ff6464";
let textColor = "#fff"
const Toast = Swal.mixin({
    toast: true,
    position: "top-end",
    showConfirmButton: false,
    timer: 5000000,
    timerProgressBar: true,
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