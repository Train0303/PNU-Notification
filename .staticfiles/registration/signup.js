const btn_signup_description = document.querySelector('#btn-signup-description');
const btn_resignup = document.querySelector('#btn-resignup');
const description = document.querySelector('#description');
const form_signup = document.querySelector('#form-signup');

btn_signup_description.addEventListener('click', () => {
    description.style.display = 'block';
    form_signup.style.display = 'none';
});

btn_resignup.addEventListener('click', () => {
   description.style.display = 'none';
   form_signup.style.display = 'block';
});