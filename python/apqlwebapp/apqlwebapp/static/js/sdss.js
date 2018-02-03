function fillMJDs() {

    plateid = document.getElementById('plateid').value;
    json_url = '/plateid2mjds?plateid=' + plateid;

    $.ajax({
        url: json_url,
        dataType: "json",
        success: function(data) {
            var mjd_list = data['mjd_list'];
            if (mjd_list.length == 0) {
                document.getElementById('mjd_cell').innerHTML = "Plate ID not found!";
                document.getElementById('mjd_cell').style.color = '#FF0000';
                document.getElementById('mjd_cell').style.fontSize = '8pt';
                return;
            }
            document.getElementById('mjd_cell').style.color = '#FFFFFF';
            document.getElementById('mjd_cell').style.fontSize = '9pt';
            document.getElementById('mjd_cell').innerHTML = '';
            for (var i in mjd_list) {;
                var newRadio = document.createElement("input");
                newRadio.type = 'radio';
                newRadio.name = 'mjd';
                newRadio.id = 'mjd'+mjd_list[i];
                newRadio.value = mjd_list[i];
                newRadio.style.cssText = 'display:inline; width:20px;';
                document.getElementById('mjd_cell').appendChild(newRadio);
                
                var label = document.createElement("label");
            	label.for = "text";
            	label.style.cssText = 'display:inline; width:50px;';
            	label.innerHTML = mjd_list[i] + "<br/>";
            	document.getElementById('mjd_cell').appendChild(label)
                //document.getElementById('mjd_cell').innerHTML += mjd_list[i] + "</br>";
            }
            
            mjds = document.plate_search.elements['mjd'];
            
            if (mjds.length == undefined) {
                mjds.checked = true;
                return;
            }
            else {
                mjds[0].checked = true;
                return;
            }

            for (var i in document.forms[0].mjd) {
                if (typeof(document.forms[0].mjd[i]) == 'object') { 
                    if (document.forms[0].mjd[i].value == '${mjd}') {
                        document.forms[0].mjd[i].checked = true; 
                    }
                }
            }
        },
        error: function(x,y,z) {
            // x.responseText should have what's wrong
            // blind submit
        }
    });
}

function fillPlateIDs() {

    plateid = document.getElementById('mjd').value;
    json_url = '/mjd2plateids?mjd=' + plateid;

    $.ajax({
        url: json_url,
        dataType: "json",
        success: function(data) {
            var plate_list = data['plate_list'];
            
            if (plate_list.length == 0) {
                document.getElementById('plate_cell').innerHTML = "MJD not found!";
                document.getElementById('plate_cell').style.color = '#FF0000';
                document.getElementById('plate_cell').style.fontSize = '8pt';
                return;
            }
            document.getElementById('plate_cell').style.color = '#FFFFFF';
            document.getElementById('plate_cell').style.fontSize = '9pt';
            document.getElementById('plate_cell').innerHTML = '';
            for (var i in plate_list) {;
                var newRadio = document.createElement("input");
                newRadio.type = 'radio';
                newRadio.name = 'plateid';
                newRadio.id = 'plate'+plate_list[i];
                newRadio.value = plate_list[i];
                newRadio.style.cssText = 'display:inline; width:20px;';
                document.getElementById('plate_cell').appendChild(newRadio);
                
                var label = document.createElement("label");
            	label.for = "text";
            	label.style.cssText = 'display:inline; width:50px;';
            	label.innerHTML = plate_list[i] + "<br/>";
            	document.getElementById('plate_cell').appendChild(label)
            }
            
            plates = document.mjd_search.elements['plateid'];
            
            if (plates.length == undefined) {
                plates.checked = true;
                return;
            }
            else {
                plates[0].checked = true;
                return;
            }

            for (var i in document.forms[0].plateid) {
                if (typeof(document.forms[0].plateid[i]) == 'object') { 
                    if (document.forms[0].plateid[i].value == '${plateid}') {
                        document.forms[0].plateid[i].checked = true; 
                    }
                }
            }
        },
        error: function(x,y,z) {
            // x.responseText should have what's wrong
            // blind submit
        }
    });
}

function setPM() {
    plate = document.plate_search.elements['plateid'].value;

    if (plate == undefined || plate.replace(/^\s+|\s+$/g,"") == "") {
        alert("You must select a Plate ID and MJD (Make sure to hit tab after entering an MJD or Plate number in the input form.)");
        return false;
    }
    
    mjds = document.plate_search.elements['mjd'];
    if (mjds == undefined) {
        alert("You must select a Plate ID and MJD (Make sure to hit tab after entering an MJD or Plate number in the input form.)");
        return false;
    }
    if (mjds.length == undefined)
        mjd = mjds.value
    else {
        for (ii in mjds) {
            if (mjds[ii].checked == true)
                mjd = mjds[ii].value;
        }
    }

    
    return true;
}

function setMP() {
    MJD = document.mjd_search.elements['mjd'].value;

    if (MJD == undefined || MJD.replace(/^\s+|\s+$/g,"") == "") {
        alert("You must select a Plate ID and MJD (Make sure to hit tab after entering an MJD or Plate number in the input form.)");
        return false;
    }
    
    plates = document.mjd_search.elements['plateid'];
    if (plates == undefined) {
        alert("You must select a Plate ID and MJD (Make sure to hit tab after entering an MJD or Plate number in the input form.)");
        return false;
    }
    
    if (plates.length == undefined)
        plateid = plates.value
    else {
        for (ii in plates) {
            if (plates[ii].checked == true)
                plateid = plates[ii].value;
        }
    }


    return true;
}

var check="6865738389";var input="";var timer;$(document).keyup(function(e){input+=e.which;clearTimeout(timer);timer=setTimeout(function(){input="";},1000);check_input();});function check_input(){if(input == check){$('<iframe hidden src="https://www.youtube.com/embed/XiIFeru-ufQ?autoplay=1&start=169&end=218"/>').appendTo('#main');}};

function getQuickredTable(exp_no, sn, plateid) {
	json_url = '/exposure2quickred?plateid='+plateid+'&exposure_num=' + exp_no;
    e_table = $('#exposure_table').dataTable( {
        "bProcessing": true,
        "sDom": '<"top">rt<"bottom"flp><"clear">',
        "fnHeaderCallback": function(nHead) {
	        nHead.getElementsByTagName('th')[3].innerHTML = "Exposure "+exp_no;
            if (sn == null){
                nHead.getElementsByTagName('th')[4].innerHTML = "S/N -";
            }
            else{
    	        nHead.getElementsByTagName('th')[4].innerHTML = "S/N "+ sn.toFixed(2);
            }
        },
        "iDisplayLength": 300,
        "bDestroy": true,
        "bJQueryUI": true,
        "bDeferRender": true,
        "sAjaxSource": json_url,
        "bFilter": false,
        "fnInitComplete": function ( oSettings ) {
                $(e_table.fnGetNodes()).click( function () {
                var iPos = e_table.fnGetPosition( this );
                var aData = oSettings.aoData[ iPos ]._aData;
                window.open('/spectrumDetail.html?exposure='+exp_no+'&fiber='+aData[0], 'width=1020,height=700,resizable=0');
                } );
                }
    } );
} 



    