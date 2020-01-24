
    var VideoPlayer = document.getElementById("VideoPlayer");
    var VidJSPlayer = videojs("VideoPlayer");
var FrameStepTimer;
var CurFrame = 0;
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
        VideoPlayer.currentTime=now+amountIn/30;
        FrameStepTimer=setTimeout("VideoStep(" + amountIn + ")",250);
    }

    function VideoStepEnd() {
        clearTimeout(FrameStepTimer);
    }
   

    function ShowVideo(idIn, fileIn) {
        VidJSPlayer.pause();
        var vidurl = SourceBase + fileIn;
        VidJSPlayer.src({
            "type": "video/mp4",
            "src": vidurl
        });
        VidJSPlayer.play();
        $.get('/video_notes/?video=' + idIn, function (data) {
            $("#divNotesArea").empty();
            $("#divNotesArea").append(data);
        });
}

var FrameCountIntervalID = setInterval("UpdateFrame()", 100);

function UpdateFrame() {
    CurFrame = Math.round(VidJSPlayer.currentTime() * 30);
    $("#VidFrameDisplay").html(CurFrame);  
    HighlightNote(CurFrame);
}

function ShowVideoFrames() {
    $("#VidSpeedArea").removeClass("col-md-8").addClass("col-md-5");
    $("#VidFramesArea").addClass("col-md-3").addClass("d-flex");
    $("#VidFramesArea").show();
}

function TextFrameJump(e) {
    if (e.keyCode == 13) {
        if (isNaN($("#txtFrameJump").val()))
            $("#txtFrameJump").val("");
        else
            VideoFrameJump($("#txtFrameJump").val());
    }
}

function VideoFrameJump(position) {
    VidJSPlayer.pause();
    VidJSPlayer.currentTime(position / 30);
   
    //alert("paused");
    //var t=setTimeout("VideoPlay()",1500);
}



