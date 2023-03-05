const emailInput = document.querySelector('#email');
const emailError = document.querySelector('#email-duplication-check');
let regex = new RegExp("([!#-'*+/-9=?A-Z^-~-]+(\.[!#-'*+/-9=?A-Z^-~-]+)*|\"\(\[\]!#-[^-~ \t]|(\\[\t -~]))+\")@([!#-'*+/-9=?A-Z^-~-]+(\.[!#-'*+/-9=?A-Z^-~-]+)*|\[[\t -Z^-~]*])");

emailInput.addEventListener('blur', () => {
    const email = emailInput.value;
    fetch(`/signup/check_email_duplication/?email=${email}`)
        .then(response => response.json())
        .then(data => {
            if (data.is_exists) {
                emailError.textContent = '이미 사용중인 이메일입니다.';
            } else {
                if (regex.test(email)) {
                    emailError.textContent = '사용 가능한 이메일입니다.';
                }
                else {
                    emailError.textContent = '올바른 이메일을 입력해주세요.';
                }
            }
        });
    });
