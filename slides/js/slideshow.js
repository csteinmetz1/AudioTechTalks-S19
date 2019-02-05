var slideIndex = 1;
var show = 1;
showSlides(slideIndex, show);

function plusSlides(n, show) 
{
	showSlides(slideIndex += n, show);
}

function currentSlide(n, show) 
{
	showSlides(slideIndex = n, show);
}

function showSlides(n, show) {
	var i;
	var slides = document.getElementsByClassName(show + "-mySlides");

	if (n > slides.length) {slideIndex = 1}    
	if (n < 1) {slideIndex = slides.length}
	for (i = 0; i < slides.length; i++) 
	{
		slides[i].style.display = "none";  
	}

	slides[slideIndex-1].style.display = "block";
}
