const emailInput = document.querySelector('#email');
const emailError = document.querySelector('#email-duplication-check');

emailInput.addEventListener('blur', () => {
    const email = emailInput.value;
    if (email === '') {
        emailError.textContent = '이메일을 입력해주세요.';
    }
    fetch(`/signup/check_email_duplication/?email=${email}`)
        .then(response => response.json())
        .then(data => {
            if (data.is_exists) {
                emailError.textContent = '이미 사용중인 이메일입니다.';
            } else {
                emailError.textContent = '사용 가능한 이메일입니다.';
            }
        });
    });
