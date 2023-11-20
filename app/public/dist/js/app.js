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
  console.log("jwtPart:", jwtPart);
  if (jwtPart) {
    const jwtToken = jwtPart.split('=')[1];
    console.log("jwtToken:", jwtToken);
    const [, payload] = jwtToken.split('.');
    console.log("payload:", payload);
    const decodedPayload = atob(payload);
    console.log("decodedPayload:", decodedPayload);
    const expiration = JSON.parse(decodedPayload).exp;
    console.log("expiration:", expiration);

    if (expiration) {
      const expirationDate = new Date(expiration * 1000); // Multiplica por 1000 para convertir de segundos a milisegundos
      return expirationDate;
    }
  }
  return null;
}



console.log("Cookies:", document.cookie);
const myCookie = getCookie("c_user");
if (myCookie) {
  console.log("Valor de la cookie:", myCookie);
  const expiration = getCookieExpiration("c_user");
  if (expiration) {
    console.log("Tiempo de expiración:", expiration);
  } else {
    console.log("La cookie no tiene tiempo de expiración");
  }
} else {
  console.log("La cookie no existe");
}
