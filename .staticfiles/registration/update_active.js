$('.toggle-event').change(function(){
    const csrftoken = getCookie('csrftoken');
    let id = $(this).data('value');
    let check = $(this).prop('checked');
    const data = {
        state: check
    }
    fetch(`/subscribe/update/active/${id}`,{
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then((response) => response.json())
    .then((result) => {
        console.log("success: ", result);
    })
    .catch((error) => {
        console.log("error: ", error);
    })
});

$('.toggle-event-hakjisi').change(function(){
    const csrftoken = getCookie('csrftoken');
    let id = $(this).data('value');
    let check = $(this).prop('checked');
    const data = {
        state: check
    }
    fetch(`/subscribe/update/active/hakjisi/${id}`,{
        method: "POST",
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then((response) => response.json())
    .then((result) => {
        console.log("success: ", result);
    })
    .catch((error) => {
        console.log("error: ", error);
    })
});



function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}