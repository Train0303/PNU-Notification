// navbar click js start
const navbar = document.querySelector('.navbar');

document.querySelector('.navbar-toggler').addEventListener('click', function() {
  if (this.getAttribute('aria-expanded') === 'true') {
    navbar.style.marginBottom = '200px';

  } else {
    navbar.style.marginBottom = '0';
  }
});
// navbar click js end