    
function date2mjd(month,day,year) {


if (month == 1) {
	var yprime = year - 1;
	var mprime = month + 12;
	}
else if (month == 2) {
	var yprime = year - 1;
	var mprime = month + 12;		
}
else {
	var yprime = year;
	var mprime = month;
	}	


if (year > 1582) {
	var A = parseInt(yprime / 100);
	var B = 2 - A + parseInt(A/4.0);
}
else {
	var B = 0;
}

if (yprime < 0) {
	var C = parseInt((365.25 * yprime) - .75);
}
else {
	var C = parseInt(365.25 * yprime);
}

var D = parseInt(30.6001 * (mprime + 1));

//add 1 because observations start at night, by which time we have moved on to next MJD
var total = B+C+D+parseInt(day) + 1720994.5 - 2400000.5 + 1;

return total.toString();

}

