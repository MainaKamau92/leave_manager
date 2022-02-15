const removeErrorDiv = (divTag) => {
    console.log("Clicked")
    let errorDiv = document.getElementById(divTag);
    if (errorDiv) {
        errorDiv.parentNode.removeChild(errorDiv);
    }

}

function fade_alerts() {
    var alerts = document.querySelector(".alert");
    time = 10000;
    setTimeout(function () {
        $(alerts).fadeOut("slow");
    }, time);
}

// call fade out after DOMContentLoaded
window.addEventListener('DOMContentLoaded', (event) => {
    fade_alerts();
});


var sideBar = document.getElementById("mobile-nav") || null;
var toggler = document.getElementById("mobile-toggler") || null;
if (sideBar !== null) {
    sideBar.style.transform = "translateX(-260px)";
    let moved = true;

    function sidebarHandler() {
        if (moved) {
            sideBar.style.transform = "translateX(0px)";
            moved = false;
        } else {
            sideBar.style.transform = "translateX(-260px)";
            moved = true;
        }
    }

}

var openmodal = document.querySelectorAll('.modal-open')
for (var i = 0; i < openmodal.length; i++) {
    openmodal[i].addEventListener('click', function (event) {
        event.preventDefault()
        toggleModal()
    })
}

const overlay = document.querySelector('.modal-overlay')
if (overlay !== null) {
    overlay.addEventListener('click', toggleModal)

}

var closemodal = document.querySelectorAll('.modal-close')
for (var i = 0; i < closemodal.length; i++) {
    closemodal[i].addEventListener('click', toggleModal)
}

document.onkeydown = function (evt) {
    evt = evt || window.event
    var isEscape = false
    if ("key" in evt) {
        isEscape = (evt.key === "Escape" || evt.key === "Esc")
    } else {
        isEscape = (evt.keyCode === 27)
    }
    if (isEscape && document.body.classList.contains('modal-active')) {
        toggleModal()
    }
};


function toggleModal() {
    const body = document.querySelector('body')
    const modal = document.querySelector('.modal')
    modal.classList.toggle('opacity-0')
    modal.classList.toggle('pointer-events-none')
    body.classList.toggle('modal-active')
}

var sideBar = document.getElementById("mobile-nav");
var toggler = document.getElementById("mobile-toggler");
if (sideBar !== null) {
    sideBar.style.transform = "translateX(-260px)";

}
let moved = true;

function sidebarHandler() {
    if (moved) {
        sideBar.style.transform = "translateX(0px)";
        moved = false;
    } else {
        sideBar.style.transform = "translateX(-260px)";
        moved = true;
    }
}