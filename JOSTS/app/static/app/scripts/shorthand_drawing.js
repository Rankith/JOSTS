
var canvas, ctx, flag = false,
    prevX = 0,
    currX = 0,
    prevY = 0,
    currY = 0,
    dot_flag = false;
var x = "black";
var y = 4;

var clickX = new Array();
var clickY = new Array();
var clickDrag = new Array();
var paint;

function erase() {
    $("#ShorthandTrainingResult").text("");
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, w, h);
    document.getElementById("canvasimg").style.display = "none";
    if (document.getElementById('chkTrace').checked) {
        ctx.globalAlpha = 0.5;
        ctx.drawImage(document.getElementById("ShorthandTrainingImageTrace"), 0, 0, ctx.canvas.width, ctx.canvas.height);
        ctx.globalAlpha = 1;
    }
    clickX = new Array();
    clickY = new Array();
    clickDrag = new Array();
}

function addClick(x, y, dragging) {

    clickX.push(x);
    clickY.push(y);
    clickDrag.push(dragging);
    //txtSkillText.value = "x: " + x + " | y: " + y;
}

function redraw(trace) {
    //console.log("trace: " + trace);
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height); // Clears the canvas
    //if (fill)
    //{
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    if (trace) {
        ctx.globalAlpha = 0.5;
        ctx.drawImage(document.getElementById("ShorthandTrainingImageTrace"), 0, 0, ctx.canvas.width, ctx.canvas.height);
        ctx.globalAlpha = 1;
    }
    //}
    //ctx.strokeStyle = "#df4b26";
    ctx.lineJoin = "round";
    ctx.lineWidth = 5;

    for (var i = 0; i < clickX.length; i++) {
        ctx.beginPath();
        if (clickDrag[i] && i) {
            ctx.moveTo(clickX[i - 1], clickY[i - 1]);
        } else {
            ctx.moveTo(clickX[i] - 1, clickY[i]);
        }
        ctx.lineTo(clickX[i], clickY[i]);
        ctx.closePath();
        ctx.stroke();
    }
}
function point(x, y) {
    ctx.beginPath();
    ctx.arc(x, y, 1, 0, 2 * Math.PI, true);
    ctx.fill();
    console.log("drew circle");
}
function redrawLast(trace) {
    //for(var i=clickX.length-1; i < clickX.length; i++) {
    ctx.lineJoin = "round";
    ctx.lineWidth = 5;
    //check last several back and make bigger
    /* if (clickX[i] == clickX[i-1] == clickX[i-2] == clickX[i-3] == clickX[i-4] == clickX[i-5])
         {
               if (clickY[i] == clickY[i-1] == clickY[i-2] == clickY[i-3] == clickY[i-4] == clickY[i-5])
               {
        //point(clickX[i],clickY[i]);

    }

    }*/

    var i = clickX.length - 1;
    ctx.beginPath();
    if (clickDrag[i] && i) {
        ctx.moveTo(clickX[i - 1], clickY[i - 1]);
    } else {
        ctx.moveTo(clickX[i] - 1, clickY[i]);
    }
    ctx.lineTo(clickX[i], clickY[i]);
    ctx.closePath();
    ctx.stroke();
    //}
}

function ResetWithTrace() {
    //console.log("tracing");
    redraw(document.getElementById('chkTrace').checked);
}

function DrawInit() {
    canvas = document.getElementById('can');
    ctx = canvas.getContext("2d");
    w = canvas.width;
    h = canvas.height;
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, w, h);
    $("#ShorthandTrainingResult").text("");
    if (document.getElementById('chkTrace').checked) {
        console.log("tracing");
        ctx.globalAlpha = 0.5;
        ctx.drawImage(document.getElementById("ShorthandTrainingImageTrace"), 0, 0, ctx.canvas.width, ctx.canvas.height);
        ctx.globalAlpha = 1;
    }
    clickX = new Array();
    clickY = new Array();
    clickDrag = new Array();
    $('#can').mousedown(function (e) {
        var mouseX = e.pageX - canvas.getBoundingClientRect().left - window.scrollX;
        var mouseY = e.pageY - canvas.getBoundingClientRect().top - window.scrollY;

        paint = true;
        addClick(mouseX, mouseY);
        redrawLast(document.getElementById('chkTrace').checked);
    });

    $('#can').mousemove(function (e) {
        if (paint) {
            addClick(e.pageX - canvas.getBoundingClientRect().left - window.scrollX, e.pageY - canvas.getBoundingClientRect().top - window.scrollY, true);
            redrawLast(document.getElementById('chkTrace').checked);
        }
    });

    $('#can').mouseup(function (e) {
        paint = false;
    });

    $('#can').mouseleave(function (e) {
        paint = false;
    });

    /* $('#can').touchend(function(e){
    e.preventDefault();
//paint = false;
//txtSkillText.value = paint.toString();
});*/

    canvas.addEventListener("touchstart", function (e) {
        e.preventDefault();
        paint = true;
        addClick(e.changedTouches[0].pageX - canvas.getBoundingClientRect().left - window.scrollX, e.changedTouches[0].pageY - canvas.getBoundingClientRect().top - window.scrollY);
        redrawLast(document.getElementById('chkTrace').checked);
    }, false);
    canvas.addEventListener("touchmove", function (e) {
        e.preventDefault();
        if (paint) {
            addClick(e.changedTouches[0].pageX - canvas.getBoundingClientRect().left - window.scrollX, e.changedTouches[0].pageY - canvas.getBoundingClientRect().top - window.scrollY, true);
            redrawLast(document.getElementById('chkTrace').checked);
        }
    }, false);
    canvas.addEventListener("touchend", function (e) {
        paint = false;
    }, false);
}

function findxytouch(res, e) {
    e.preventDefault();
    findxy(res, e.changedTouches[0].pageX, e.changedTouches[0].pageY);
}

function findxymouse(res, e) {
    findxy(res, e.clientX, e.clientY);
}

function draw() {
    ctx.beginPath();
    ctx.moveTo(prevX, prevY);
    ctx.lineTo(currX, currY);
    //console.log("path: " + prevX + " " + currX + " " + prevY + " " + currY);
    ctx.strokeStyle = x;
    ctx.lineWidth = y;
    ctx.stroke();
    ctx.closePath();
}

function findxy(res, cx, cy) {
    //console.log(res);
    ctx.lineJoin = "round";
    if (res == 'down') {
        prevX = currX;
        prevY = currY;
        currX = cx - canvas.getBoundingClientRect().left;
        currY = cy - canvas.getBoundingClientRect().top;

        flag = true;
        dot_flag = true;
        if (dot_flag) {
            //console.log ("drawing " + x);
            ctx.beginPath();
            ctx.fillStyle = x;
            ctx.fillRect(currX, currY, 2, 2);
            ctx.closePath();
            dot_flag = false;
        }
    }
    if (res == 'up' || res == "out") {
        flag = false;
    }
    if (res == 'move') {
        if (flag) {
            prevX = currX;
            prevY = currY;
            currX = cx - canvas.getBoundingClientRect().left;
            currY = cy - canvas.getBoundingClientRect().top;
            draw();
        }
    }
}
function CheckImage() {
    redraw(false);

    var dataImage = canvas.toDataURL();
    SaveRecordImageNoData(dataImage);
    var fd = new FormData();
    var eventrespond;
    if (typeof (Event) == "function")
        eventrespond = EventForDraw;
    else
        eventrespond = Event;
    fd.append('image', dataImage);
    fd.append('discevent', drawing_prefix + Disc + eventrespond);
    console.log(drawing_prefix + Disc + eventrespond);
    //AddToListYou(dataImage);
    $.ajax({
        'url': "https://symbolsdl.jdogzennodes.club:5000/predict",
        'type': 'POST',
        processData: false,
        contentType: false,
        'data': fd,
        'success': function (data) {
            //$("#btnDone").removeClass('ui-disabled');
            console.log(data);
            //console.log(data.probabilityMost);
            //console.log(data[ShorthandTrainingOnImage.toLowerCase()]);

            //$("#ShorthandTrainingResult").text(data.predicted.toLowerCase());
            //$("#ShorthandTrainingResult").css("color","green");
            SetResult(data.predicted.toLowerCase());//this must be a function on other page

        },
        'beforeSend': function () {
            CheckImageBefore(dataImage);
        },
        'error': function (data) {
            CheckImageError(data);
            /*	$("#btnDoneL").removeClass('ui-disabled');
            $("#btnDoneR").removeClass('ui-disabled');
            $("#btnDoneConnectionL").removeClass('ui-disabled');
            $("#btnDoneConnectionR").removeClass('ui-disabled');*/
        }
    });
}

function SaveRecordImageNoData(image) {
    if (document.getElementById('chkSave').checked) {
        var date = new Date();
        //var label = ShorthandTrainingOnImage.toLowerCase();
        //if (ShorthandTranslate[ShorthandTrainingOnImage] != undefined)
        //	label = ShorthandTranslate[ShorthandTrainingOnImage].toLowerCase();
        //generate unique string
        var name = date.toLocaleString().replace(/\//g, "").replace(/ /g, "").replace(",", "").replace(/:/g, "") + date.getMilliseconds();
        name = $("#hdnName").val() + name;
        var eventrespond;
        if (typeof (Event) == "function")
            eventrespond = EventForDraw;
        else
            eventrespond = Event;
        $.ajax({
            url: '/save_record_image/',
            type: 'POST',
            data: {
                data: image,
                name: name,
                event: eventrespond.toLowerCase(),
                disc: Disc.toLowerCase(),
                label: $("#hdnName").val(),
                csrfmiddlewaretoken: window.CSRF_TOKEN
            },
            success: function (data) {
                $("#divTempCount").html(data);
            }
        });

    }
};


