function toggleHelp() {
	var helpDivs = document.getElementsByClassName('help');
	
	for (var i in helpDivs) {
		if (helpDivs[i].style.display == 'block') {
			helpDivs[i].style.display = 'none';
			document.getElementById('helpToggle').innerHTML = 'Show Help';
		}
		else if (helpDivs[i].style.display == 'none') {
			helpDivs[i].style.display = 'block';
			document.getElementById('helpToggle').innerHTML = 'Hide Help';
		}
	}
}

function bitMaskOptions(id) {
	var chkDiv = document.getElementById(id+'_div');

	if (chkDiv.style.display == 'none') {
		// Show corresponding checkboxes
		ShowPop(id+'_div');
		document.getElementById(id+'_rightArrow').style.display = 'none';
		document.getElementById(id+'_downArrow').style.display = 'inline';
	}
	else if (chkDiv.style.display == 'inline' || chkDiv.style.display == 'block') {
		// Hide corresponding Select object
		HidePop(id+'_div');
		document.getElementById(id+'_rightArrow').style.display = 'inline';
		document.getElementById(id+'_downArrow').style.display = 'none';
	}
}

function fitsFilters(id) {
	var chkDiv = document.getElementById(id);

	if (chkDiv.style.display == 'none') {
		// Show corresponding checkboxes
		ShowPop(id);
		document.getElementById('rightArrow').style.display = 'none';
		document.getElementById('downArrow').style.display = 'inline';
	}
	else if (chkDiv.style.display == 'inline' || chkDiv.style.display == 'block') {
		// Hide corresponding Select object
		HidePop(id);
		document.getElementById('rightArrow').style.display = 'inline';
		document.getElementById('downArrow').style.display = 'none';
	}
}

function toggleBand(band) {
	cell = document.getElementById(band);
	
	/*if (document.getElementById(band).className == 'off') {
			document.getElementById(band).style.backgroundColor = band_on_highlight;
		}
	else
		document.getElementById(band).style.backgroundColor = band_off_highlight;
	*/
	if (cell.className == 'on') {
		cell.className = 'off';
	}
	else
		cell.className = 'on';
}

function setSearch() {
	// reload the page, change search= to searchType
	rads = document.formSelect.elements['formSelect'];
	for (i in rads) {
		if (rads[i].checked == true)
			window.location.search = "?search=" + rads[i].value;
	}
}

function setBands(select) {
    bands = "";
	if (document.getElementById(select+'u').className == 'on') bands = bands + 'u'
    if (document.getElementById(select+'g').className == 'on') bands = bands + 'g'
    if (document.getElementById(select+'r').className == 'on') bands = bands + 'r'
    if (document.getElementById(select+'i').className == 'on') bands = bands + 'i'
    if (document.getElementById(select+'z').className == 'on') bands = bands + 'z'
    document.getElementById(select+'bands').value = bands;
	
	return true;
}

//--------------------------------------------------------

function checkAllFiltered(table) {
    var inputs = table.getElementsByTagName('input');
    for (i in inputs) {
        if (inputs[i].name == "platemjdfiber" && inputs[i].parentNode.parentNode.style.getPropertyValue('display') != "none") {
            inputs[i].checked = true;}
        else if (inputs[i].name == "tmassid" && inputs[i].parentNode.parentNode.style.getPropertyValue('display') != "none") {
            inputs[i].checked = true;
        }
    }
}



function unCheckAllFiltered(table) {
	var inputs = table.getElementsByTagName('input');
		for (i in inputs){
			inputs[i].checked = false;
		}
	
	
}

/*
function unCheckAllFiltered(chk) {
	if (chk.length > 1) {
		for (i = 0; i < chk.length; i++)
			chk[i].checked = false ;
	}
	else {
		chk.checked = false ;
	}
}
*/

function inverseFiltered(table) {
    var inputs = table.getElementsByTagName('input');
    for (i in inputs) {
        if (inputs[i].name == "platemjdfiber" && inputs[i].parentNode.parentNode.style.getPropertyValue('display') != "none") {
            if (inputs[i].checked == false)
                inputs[i].checked = true;
            else if (inputs[i].checked == true)
                inputs[i].checked = false}
        if (inputs[i].name == "tmassid" && inputs[i].parentNode.parentNode.style.getPropertyValue('display') != "none") {
            if (inputs[i].checked == false)
                inputs[i].checked = true;
            else if (inputs[i].checked == true)
                inputs[i].checked = false
        }
    }
}

