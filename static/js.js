window.addEventListener("load", function () {
  let date = document.getElementById("date");
  let parsedDate = new Date(date.textContent);
  date.textContent = parsedDate.toLocaleString("es-ES");
});
