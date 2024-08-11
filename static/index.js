function validatePassword() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const submitButton = document.getElementById('submit');
    const criteria = document.getElementById('criteria');

    // Show the criteria list
    criteria.style.display = 'block';

    // Password strength criteria
    const minLength = 8;
    const uppercaseRegex = /[A-Z]/;
    const lowercaseRegex = /[a-z]/;
    const numberRegex = /[0-9]/;
    const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;

    let isValid = true;

    // Validate each criterion
    if (password.length >= minLength) {
        document.getElementById('length').classList.add('valid');
        document.getElementById('length').classList.remove('invalid');
    } else {
        document.getElementById('length').classList.add('invalid');
        document.getElementById('length').classList.remove('valid');
        isValid = false;
    }

    if (uppercaseRegex.test(password)) {
        document.getElementById('uppercase').classList.add('valid');
        document.getElementById('uppercase').classList.remove('invalid');
    } else {
        document.getElementById('uppercase').classList.add('invalid');
        document.getElementById('uppercase').classList.remove('valid');
        isValid = false;
    }

    if (lowercaseRegex.test(password)) {
        document.getElementById('lowercase').classList.add('valid');
        document.getElementById('lowercase').classList.remove('invalid');
    } else {
        document.getElementById('lowercase').classList.add('invalid');
        document.getElementById('lowercase').classList.remove('valid');
        isValid = false;
    }

    if (numberRegex.test(password)) {
        document.getElementById('number').classList.add('valid');
        document.getElementById('number').classList.remove('invalid');
    } else {
        document.getElementById('number').classList.add('invalid');
        document.getElementById('number').classList.remove('valid');
        isValid = false;
    }

    if (specialCharRegex.test(password)) {
        document.getElementById('special').classList.add('valid');
        document.getElementById('special').classList.remove('invalid');
    } else {
        document.getElementById('special').classList.add('invalid');
        document.getElementById('special').classList.remove('valid');
        isValid = false;
    }

    if (password === confirmPassword && confirmPassword !== '') {
        document.getElementById('match').classList.add('valid');
        document.getElementById('match').classList.remove('invalid');
    } else {
        document.getElementById('match').classList.add('invalid');
        document.getElementById('match').classList.remove('valid');
        isValid = false;
    }

    submitButton.disabled = !isValid;
    return isValid;
}

function validateMatchPassword() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const submitButton = document.getElementById('submit');
    const criteria = document.getElementById('match_criteria');

    // Show the criteria list
    criteria.style.display = 'block';

    let isValid = true;

    // Validate each criterion
    if (password === confirmPassword && confirmPassword !== '') {
        document.getElementById('match').classList.add('valid');
        document.getElementById('match').classList.remove('invalid');
    } else {
        document.getElementById('match').classList.add('invalid');
        document.getElementById('match').classList.remove('valid');
        isValid = false;
    }

    submitButton.disabled = !isValid;
    return isValid;
}

document.getElementById('movie-search').addEventListener('input', function() {
    let query = this.value;
    if (query.length > 2) {
        fetch('/search_suggestions?query=' + query)
            .then(response => response.json())
            .then(data => {
                let resultsDiv = document.getElementById('search-results');
                resultsDiv.innerHTML = '';
                if (data.length > 0) {
                    resultsDiv.style.display = 'block';
                    data.forEach(movie => {
                        let link = document.createElement('a');
                        link.href = '/movie/' + movie.id;
                        link.textContent = movie.title;
                        resultsDiv.appendChild(link);
                    });
                } else {
                    resultsDiv.style.display = 'none';
                }
            });
    } else {
        document.getElementById('search-results').style.display = 'none';
    }
});
