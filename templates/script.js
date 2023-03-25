const menuIcon = document.querySelector(".menu li.icon");
const menuItems = document.querySelector(".menu");

menuIcon.addEventListener("click", () => {
  menuItems.classList.toggle("active");
});
