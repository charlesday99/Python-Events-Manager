//Site-wide resizing
function mobileWidthCheck() {
	//Width of the orange left border
	const BAR_WIDTH = 6;
	
	//Checks whether the window is less then 900 pixels
	if (window.innerWidth < 900) {
		
		//Checks whether the scroll bar is visible
		if (scrollbarVisible(document.body)) {
			document.getElementById("main").style.setProperty('width', (document.body.clientWidth - BAR_WIDTH) + "px");
		} else {
			document.getElementById("main").style.setProperty('width', (window.innerWidth - BAR_WIDTH) + "px");
		}
		
	} else {
		document.getElementById("main").style.setProperty('width', "70%");
	}
}

//Returns boolean for whether the scroll bar is visible
function scrollbarVisible(element) {
	return element.scrollHeight > element.clientHeight;
}