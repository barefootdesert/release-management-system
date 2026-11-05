document.addEventListener("DOMContentLoaded", () => {
  const yearNode = document.getElementById("current-year");
  if (yearNode) {
    const year = String(new Date().getFullYear());
    yearNode.textContent = year;
    yearNode.setAttribute("datetime", year);
  }
});
