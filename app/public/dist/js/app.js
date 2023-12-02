const dropdownBtn = document.querySelectorAll(".dropdown-btn");
const dropdown = document.querySelectorAll(".dropdown");
const hamburgerBtn = document.getElementById("hamburger");
const navMenu = document.querySelector(".menu");
const links = document.querySelectorAll(".dropdown a");

function setAriaExpandedFalse() {
  dropdownBtn.forEach((btn) => btn.setAttribute("aria-expanded", "false"));
}

function closeDropdownMenu() {
  dropdown.forEach((drop) => {
    drop.classList.remove("active");
    drop.addEventListener("click", (e) => e.stopPropagation());
  });
}

function toggleHamburger() {
  navMenu.classList.toggle("show");
  // change hamburger to close icon
  if (navMenu.classList.contains("show")) {
    hamburgerBtn.innerHTML = `<i class="bx bx-x" aria-hidden="true"></i>`;
    // hide overflow when the hamburger menu is open
    document.documentElement.style.overflow = "hidden";
  } else {
    hamburgerBtn.innerHTML = `<i class="bx bx-menu" aria-hidden="true"></i>`;
    // show overflow when the hamburger menu is closed
    document.documentElement.style.overflow = "visible";
  }
}

dropdownBtn.forEach((btn) => {
  btn.addEventListener("click", function (e) {
    const dropdownIndex = e.currentTarget.dataset.dropdown;
    const dropdownElement = document.getElementById(dropdownIndex);

    dropdownElement.classList.toggle("active");
    dropdown.forEach((drop) => {
      if (drop.id !== btn.dataset["dropdown"]) {
        drop.classList.remove("active");
      }
    });
    e.stopPropagation();
    btn.setAttribute(
      "aria-expanded",
      btn.getAttribute("aria-expanded") === "false" ? "true" : "false"
    );
  });
});

// close dropdown menu when the dropdown links are clicked
links.forEach((link) =>
  link.addEventListener("click", () => {
    closeDropdownMenu();
    setAriaExpandedFalse();
    toggleHamburger();
  })
);

// close dropdown menu when you click on the document body
document.documentElement.addEventListener("click", () => {
  closeDropdownMenu();
  setAriaExpandedFalse();
});

// close dropdown when the escape key is pressed
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeDropdownMenu();
    setAriaExpandedFalse();
  }
});

// toggle hamburger menu
hamburgerBtn.addEventListener("click", toggleHamburger);

function getCookie(name) {
  const cookies = document.cookie.split("; ");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].split("=");
    if (cookie[0] === name) {
      return cookie[1];
    }
  }
  return null;
}

function getCookieExpiration(name) {
  const cookie = decodeURIComponent(document.cookie);
  const cookieParts = cookie.split('; ');
  const jwtPart = cookieParts.find(part => part.startsWith(`${name}=`));
  if (jwtPart) {
    const jwtToken = jwtPart.split('=')[1];
    const [, payload] = jwtToken.split('.');
    const decodedPayload = atob(payload);
    const expiration = JSON.parse(decodedPayload).exp;
    if (expiration) {
      const expirationDate = new Date(expiration * 1000);
      return expirationDate;
    }
  }
  return null;
}

setInterval(() => {
  const myCookie = getCookie("c_user");
  if (myCookie) {
    const expiration = getCookieExpiration("c_user");
    if (expiration) {
      // Obtener hora actual
      const now = new Date();

      // Obtener hora de expiración de la cookie
      const expirationTime = new Date(expiration);

      // Calcular la diferencia en milisegundos entre la hora actual y la hora de expiración
      const timeDiff = expirationTime - now;

      // Convertir la diferencia a minutos
      const minutesUntilExpiration = Math.round(timeDiff / (1000 * 60));

      // Verificar si está a menos de ciertos minutos de la expiración
      const alertThreshold = 15;
      if (minutesUntilExpiration <= alertThreshold) {
        const timerDuration = 300000; // Duración del temporizador en milisegundos

        const swalOptions = {
          title: "Tu sesión está a punto de expirar",
          confirmButtonText: "Renovar",
          showCancelButton: true,
          cancelButtonText: "Cerrar sesión",
          icon: "warning",
          timer: timerDuration,
          timerProgressBar: true,
          allowEscapeKey: false,
          allowOutsideClick: false,
        };
        
        const swalAlert = Swal.fire(swalOptions);
        swalAlert.then((result) => {
          if (result.isConfirmed) {
            window.location.href = "/renew/token";
          }
          if (result.isDismissed) {
            window.location.href = "/logout";
          }
        });
        
        setTimeout(() => {
          swalAlert.then((result) => {
          if (result.dismiss === Swal.DismissReason.timer) {
              window.location.href = "/logout";
            }
          });
        }, timerDuration);
        
      }
      console.log("Checking session");
      console.log("Cookie: " + myCookie);
      console.log("Expiration: " + expirationTime);
      console.log("Minutes until expiration: " + minutesUntilExpiration);
      console.log("---------------------------");
    }
  }
}, 150000);

let loader = document.getElementById("loader");
window.addEventListener("load", function () {
  this.setTimeout(() => {
    loader.style.display = "none";
  }, 1000);
});
let pruebasBtn = document.getElementById("pruebasBtn");
let pruebas = document.getElementById("pruebas");
pruebasBtn.addEventListener("click", function () {
  console.log("click boton pruebas");
  if (pruebas.classList.contains("hidden")) {
    console.log("se quita hidden");
    pruebas.classList.remove("hidden");
  } else {
    console.log("se agrega hidden");
    pruebas.classList.add("hidden");
  }
});

