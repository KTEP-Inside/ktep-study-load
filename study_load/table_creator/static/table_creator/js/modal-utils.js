let modal = document.getElementById("myModal");
let modContent = document.getElementById('modal-content');

function openModal(text, status=null) {
    
    let msg = document.createElement('p')
    msg.textContent = text;
    msg.classList.add('text-modal');
    modContent.appendChild(msg);
    if (status == 'warning') {
        modContent.classList.add('warning-modal');
    }
    modal.style.display = "block";
  }

function closeModal() {
    modal.style.display = "none";
    let paragraphs = modContent.querySelectorAll('p');
    paragraphs.forEach(paragraph => {
        modContent.removeChild(paragraph);
    });
}

export {openModal, closeModal};