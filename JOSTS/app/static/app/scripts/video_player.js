try {
    VidJSPlayer.dispose();
    clearInterval(FrameCountIntervalID);
}
catch(err)
{

}
var VideoPlayer = document.getElementById("VideoPlayer");
    var VidJSPlayer = videojs("VideoPlayer");
var FrameStepTimer;
var CurFrame = 0;
var VidFPS = 25;
var EJump = 0;
    //level slider
    var SpeedSlider = document.getElementById("SpeedSlider");

    noUiSlider.create(SpeedSlider, {
        start: 1,
        connect: [true,false],
        range: {
            'min': 0,
            'max': 1.25
        },
        step: 0.25,

    });


    SpeedSlider.noUiSlider.on('update', function (values, handle) {
        var SpeedDisplay = 0
        if (values[0] == "0.00")
            SpeedDisplay = "Stopped";
        else if (values[0] == "0.25")
            SpeedDisplay = "25%";
        else if (values[0] == "0.50")
            SpeedDisplay = "50%";
        else if (values[0] == "0.75")
            SpeedDisplay = "75%";
        else if (values[0] == "1.00")
            SpeedDisplay = "100%";
        else if (values[0] == "1.25")
            SpeedDisplay = "125%";
        $("#divsSpeedSliderValues").html(SpeedDisplay);
        VideoPlayer.playbackRate = values[0];

    });


     $(document).keydown(function(event) { 
        var key = (event.keyCode ? event.keyCode : event.which); 
        if (key==187)//+
		{
			VideoStep(1);
			VideoStepEnd();
		}
		else if(key==189)//-
		{
			VideoStep(-1);
			VideoStep();
		}
     }); 

     VidJSPlayer.on('touchstart', function (e) {
        if (e.target.nodeName === 'VIDEO') {
            if (VidJSPlayer.paused()) {
                this.play();
            } else {
                this.pause();
            }
        }
    });

    function VideoStep(amountIn) {
        VideoPlayer.pause();
        var now=VideoPlayer.currentTime;
        VideoPlayer.currentTime = now + amountIn / VidFPS;
        FrameStepTimer=setTimeout("VideoStep(" + amountIn + ")",250);
    }

    function VideoStepEnd() {
        clearTimeout(FrameStepTimer);
    }
   

    function ShowVideo(idIn, fileIn, FPSIn = 25, oldID, elementJump = -1, extrapath='', hide='') {
        VidJSPlayer.pause();
        var vidurl;
        console.log(extrapath);
        if (oldID != '' && oldID != 'None') {
            if (extrapath == '')
                vidurl = "https://web-sts.com/" + DiscP + "/VideoFiles/" + EventP + "/" + fileIn;
            else
                vidurl = "https://web-sts.com/" + DiscP + "/VideoFiles/" + extrapath + "/" + fileIn;
        }
        else
            vidurl = SourceBase + fileIn;
        VidFPS = FPSIn;
        VidJSPlayer.src({
            "type": "video/mp4",
            "src": vidurl
        });
        VidJSPlayer.play();
        $("#divHud").remove();
        $.get('/video_notes/?video=' + idIn + '&element=' + elementJump, function (data) {
            $("#divNotesArea").empty();
            $("#divNotesArea").append(data);
            $("#divHud").detach().appendTo("#VidHudArea");
            if (hide != '') {
                $("#NotesTitle" + hide).hide();
                $("#Notes" + hide).hide();
                if (hide == "D")
                    $("#NotesE").css("max-height", $("#divVideoContainer").height() + 150).css("overflow", "auto");
                else
                    $("#NotesD").css("max-height", $("#divVideoContainer").height() + 150).css("overflow", "auto");
            }
            else {
                $("#NotesE").css("max-height", ($("#divVideoContainer").height() + 150) / 2).css("overflow", "auto");
                $("#NotesD").css("max-height", ($("#divVideoContainer").height() + 150) / 2).css("overflow", "auto");
            }
        });

        $("#divVidFramesSeconds").html("1 sec = " + VidFPS + "");
}

function JumpToElement() {
    if (ElementJump != -1)
        VideoFrameJump(ElementJump);
}

var FrameCountIntervalID = setInterval("UpdateFrame()", 100);

function UpdateFrame() {
    CurFrame = Math.round(VidJSPlayer.currentTime() * VidFPS);
    $("#VidFrameDisplay").html(CurFrame);  
    HighlightNote(CurFrame);
}

function ShowVideoFrames() {
    $("#VidFramesArea").css("display", "inline");
    //$("#VidSpeedArea").removeClass("col-md-8").addClass("col-md-5");
    //$("#VidFramesArea").addClass("col-md-3").addClass("d-flex");
    //$("#VidFramesArea").show();
}

function TextFrameJump(e) {
    if (e.keyCode == 13) {
        if (isNaN($("#txtFrameJump").val()))
            $("#txtFrameJump").val("");
        else
            VideoFrameJumpPause($("#txtFrameJump").val());
    }
}

function VideoPlay() {
    VidJSPlayer.play();
}

function VideoFrameJump(position) {
    VidJSPlayer.pause();
    VidJSPlayer.currentTime(position / VidFPS);
   
    //alert("paused");
    var t=setTimeout("VideoPlay()",1500);
}

function VideoFrameJumpPause(position) {
    VidJSPlayer.pause();
    VidJSPlayer.currentTime(position / VidFPS);
}



