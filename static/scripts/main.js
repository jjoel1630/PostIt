// Get the container element
var btnContainer = document.getElementById("profile-nav");

// Get all buttons with class="btn" inside the container
var btns = btnContainer.getElementsByClassName("button");

// Loop through the buttons and add the active class to the current/clicked button
for (var i = 0; i < btns.length; i++) {
  btns[i].addEventListener("click", function() {
    var current = document.getElementsByClassName("pro-active");
    current[0].className = current[0].className.replace(" pro-active", "");
    this.className += " pro-active";
  });
}