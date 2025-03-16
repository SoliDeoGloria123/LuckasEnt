let index = 0;
const track = document.querySelector('.carousel-track');
const dots = document.querySelectorAll('.dot');
const totalSlides = document.querySelectorAll('.partner').length;

function moveSlide(step) {
    index += step;
    if (index < 0) index = totalSlides - 1;
    if (index >= totalSlides) index = 0;
    
    updateCarousel();
}

function goToSlide(n) {
    index = n;
    updateCarousel();
}

function updateCarousel() {
    const offset = -index * 100;
    track.style.transform = `translateX(${offset}%)`;
    
    dots.forEach(dot => dot.classList.remove('active'));
    dots[index].classList.add('active');
}

// Deslizar automáticamente cada 3 segundos
setInterval(() => moveSlide(1), 3000);
