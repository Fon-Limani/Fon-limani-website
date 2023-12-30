function scrollPage() {
  second_section = document.getElementById("second");

  second_section.scrollIntoView({
      behavior: 'smooth',
      block: 'nearest',
  });
  
}

// Add a click event listener to the button
document.getElementById('scrollButton').addEventListener('click', scrollPage);
