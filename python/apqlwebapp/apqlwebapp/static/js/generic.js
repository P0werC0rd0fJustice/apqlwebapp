function checkAll(chk) {
	if (chk.length > 1) {
		for (i = 0; i < chk.length; i++)
			chk[i].checked = true;
	}
	else {
		chk.checked = true;
	}
}

function unCheckAll(chk) {
	if (chk.length > 1) {
		for (i = 0; i < chk.length; i++)
			chk[i].checked = false ;
	}
	else {
		chk.checked = false ;
	}
}

function inverse(chk) {
	if (chk.length > 1) {
		for (i = 0; i < chk.length; i++) {
			if (chk[i].checked == false)
				chk[i].checked = true;
			else if (chk[i].checked == true)
				chk[i].checked = false;
		}
	}
	else {
		if (chk.checked == false)
			chk.checked = true;
		else if (chk.checked == true)
			chk.checked = false;
	}
}

//------------------------------------------------------------
// Are these used???
function checkUncheckAll(thisChk, chk) {
	var boxes = document.advSearch.elements[chk];
	var thisChkBox = document.getElementById(thisChk);

	for (var box in boxes) {
		if (thisChkBox.checked == true) {
			boxes[box].checked = true;
		}
		else {
			boxes[box].checked = false;
		}
	}
}

function checkUncheck(chk) {
	var box = document.getElementById(chk);
	if (box.checked == true) {
		box.checked = false;
	}
	else {
		box.checked = true;
	}
}
//------------------------------------------------------------

function getElementsByClassName(class_name)
      {
        var all_obj,ret_obj=new Array(),j=0,teststr;

        if(document.all)all_obj=document.all;
        else if(document.getElementsByTagName && !document.all)
          all_obj=document.getElementsByTagName("*");

        for(i=0;i<all_obj.length;i++)
        {
          if(all_obj[i].className.indexOf(class_name)!=-1)
          {
            teststr=","+all_obj[i].className.split(" ").join(",")+",";
            if(teststr.indexOf(","+class_name+",")!=-1)
            {
              ret_obj[j]=all_obj[i];
              j++;
            }
          }
        }
        return ret_obj;
}

function ShowPop(id) {
	document.getElementById(id).style.display = "block";
}

function HidePop(id) {
	document.getElementById(id).style.display = "none";
}

function ShowTable(id) {
	document.getElementById(id).style.display = "table";
}

function HideTable(id) {
	document.getElementById(id).style.display = "none";
}

function goToURL(theUrl) {
	/*if (document.location.pathname + document.location.search != '/' + theUrl) {
		document.location.href = theUrl;
	}*/
	window.open(theUrl);
}

var getKeys = function(obj){
   var keys = [];
   for(var key in obj){
      keys.push(key);
   }
   return keys;
}

function validateDL(form) {
	for (j=0; j < form.platemjdfiber.length; j++) {
		if (form.platemjdfiber[j].checked) {
			var oneChecked = true;
		}
	}
	
	if (!oneChecked) {
		alert("Please select at least one row.");
		return false;
	}
	
	return true;
}

function showLoader() { 
	var ldgif = document.getElementById("loading").style;
	var jpg = document.getElementById("jpg").style;
	ldgif.display = 'inline';
	jpg.display = 'none';
}

function hideLoader() { 
	var ldgif = document.getElementById("loading").style;
	var jpg = document.getElementById("jpg").style;
	ldgif.display = 'none';
	jpg.display = 'inline';
}

var tooltip=function(){
 var id = 'tt';
 var top = 3;
 var left = 3;
 var maxw = 300;
 var speed = 10;
 var timer = 20;
 var endalpha = 95;
 var alpha = 0;
 var tt,t,c,b,h;
 var ie = document.all ? true : false;
 return{
  show:function(v,w){
   if(tt == null){
    tt = document.createElement('div');
    tt.setAttribute('id',id);
    t = document.createElement('div');
    t.setAttribute('id',id + 'top');
    c = document.createElement('div');
    c.setAttribute('id',id + 'cont');
    b = document.createElement('div');
    b.setAttribute('id',id + 'bot');
    tt.appendChild(t);
    tt.appendChild(c);
    tt.appendChild(b);
    document.body.appendChild(tt);
    tt.style.opacity = 0;
    tt.style.filter = 'alpha(opacity=0)';
    document.onmousemove = this.pos;
   }
   tt.style.display = 'block';
   c.innerHTML = v;
   tt.style.width = 'auto';
   if(!w && ie){
    t.style.display = 'none';
    b.style.display = 'none';
    tt.style.width = tt.offsetWidth;
    t.style.display = 'block';
    b.style.display = 'block';
   }
  if(tt.offsetWidth > maxw){tt.style.width = maxw + 'px'}
  h = parseInt(tt.offsetHeight) + top;
  clearInterval(tt.timer);
  tt.timer = setInterval(function(){tooltip.fade(1)},timer);
  },
  pos:function(e){
   var u = ie ? event.clientY + document.documentElement.scrollTop : e.pageY;
   var l = ie ? event.clientX + document.documentElement.scrollLeft : e.pageX;
   tt.style.top = (u - h) + 'px';
   tt.style.left = (l + left) + 'px';
  },
  fade:function(d){
   var a = alpha;
   if((a != endalpha && d == 1) || (a != 0 && d == -1)){
    var i = speed;
   if(endalpha - a < speed && d == 1){
    i = endalpha - a;
   }else if(alpha < speed && d == -1){
     i = a;
   }
   alpha = a + (i * d);
   tt.style.opacity = alpha * .01;
   tt.style.filter = 'alpha(opacity=' + alpha + ')';
  }else{
    clearInterval(tt.timer);
     if(d == -1){tt.style.display = 'none'}
  }
 },
 hide:function(){
  clearInterval(tt.timer);
   tt.timer = setInterval(function(){tooltip.fade(-1)},timer);
  }
 };
}();
