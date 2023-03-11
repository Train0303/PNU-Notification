const deleteBtn = document.getElementById('delete-btn');
const cancelBtn = document.getElementById('cancel-delete-btn');
const confirmDiv = document.getElementById('delete-confirm');

deleteBtn.addEventListener('click', function() {
    confirmDiv.style.display = 'block';
});

cancelBtn.addEventListener('click', function() {
    confirmDiv.style.display = 'none';
});