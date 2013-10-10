Huxleyview = {
  version: '1.0',
};

//event register
Huxleyview.Run = function(components){
  var components = components;
  var count = components.length;
  for(var i=0;i<count;i++){
    var page = components[i];
    var id = page.id;
    var e_array = page.event.split(',');
    for(var j=0; j <e_array.length;j++){
      var e = e_array[j];
      if($.trim(e).length == 0)
        continue;
      if(id==="document" && e==="ready"){
        Huxleyview.Controllers[id][e]();
      }
      else{
        $(document).delegate(id, e, {}, Huxleyview.Controllers[id][e]);
      }
    }
  }
};

//Common Utils
Huxleyview.Utils = {
  IsEmpty:function(obj){
    for(var name in obj){
      if(obj.hasOwnProperty(name)){
        return false;
      }
    }
    return true;
  },
};

//Control center
Huxleyview.Controllers = {};

//Storage
Huxleyview.Storage = {
  'timelineDataList':{},
  'tcaseDataList':{},

  GetLatestTimestamp:function(){
    if(!Huxleyview.Utils.IsEmpty(this['timelineDataList']) && this['timelineDataList'][0]['times'].length>0){
      times = this['timelineDataList'][0]['times'];
      return times[times.length-1][0];
    }
    return null;
  },

  GetTimeScore:function(){
  //return [starting_time, ending_time]
    var starting_time = 2381251667010;
    var ending_time = 0;

    if(Huxleyview.Utils.IsEmpty(this.timelineDataList)){
      return [moment().unix()-3600*24, moment().unix()];
    }
    for(var i=0; i<this.timelineDataList.length; i++){
      for(var j=0; j<this.timelineDataList[i].times.length; j++){
        if(this.timelineDataList[i].times[j]['starting_time'] < starting_time){
          starting_time = this.timelineDataList[i].times[j]['starting_time'];
        }
        if(this.timelineDataList[i].times[j]['ending_time'] > ending_time){
          ending_time = this.timelineDataList[i].times[j]['ending_time'];
        }
      }
    }

    return [Math.floor(starting_time/1000), Math.floor(ending_time/1000)];
  },
};

//Request utils
Huxleyview.Request = {
  GetAllTcaseRunTimes:function(){
   $.post("huxley/ajax/get_all_testcase_run_times",
        {},
        function(resp){
          var timelineDataList = [];
          var timelineData = JSON.parse(resp);
          succTimelineData = {result:"succ", times:[]};
          failTimelineData = {result:"fail", times:[]};

          $.each(timelineData, function(index, value){
            timestamp = moment(value[0], "YYYYMMDDHHmmss").unix() * 1000;
            if(value[1] == 'ok'){
              succTimelineData.times.push({"starting_time":timestamp, "ending_time":timestamp+10});
            }
            else{
              failTimelineData.times.push({"starting_time":timestamp, "ending_time":timestamp+10});
            }
          });
          if(succTimelineData['times'].length > 0){
              timelineDataList.push(succTimelineData);
          }
          if(failTimelineData['times'].length > 0){
              timelineDataList.push(failTimelineData);
          }
          Huxleyview.Storage['timelineDataList'] = timelineDataList;
          $('#tcase-timeline').trigger('refreshTimeline');
        }
    );
  },

  GetAllTcase:function(value){
    timestamp = moment.unix(value).format("YYYYMMDDHHmmss");
    $.post("huxley/ajax/get_all_testcase",
        {'timestamp':timestamp},
        function(resp){
          var tcaseDataList = JSON.parse(resp);
          Huxleyview.Storage['tcaseDataList'] = tcaseDataList;
          $.each(Huxleyview.Storage['tcaseDataList'], function(index, value){
            value.push(timestamp);
            }
          );
          $('#tcase-list').trigger('refreshTcaseList');
        }
    );
  },

  GetLatestTcase:function(){
   $.post("huxley/ajax/get_latest_testcase",
        {},
        function(resp){
          var tcaseDataList = JSON.parse(resp)['data'];
          var timestamp = JSON.parse(resp)['timestamp'];

          Huxleyview.Storage['tcaseDataList'] = tcaseDataList;
          $.each(Huxleyview.Storage['tcaseDataList'], function(index, value){
            value.push(timestamp);
            }
          );
          $('#tcase-list').trigger('refreshTcaseList');
        }
    );
  }

}

//UI utils
Huxleyview.UI = {
  RefreshTcaseList:function(){
    var tcaseDataList = Huxleyview.Storage["tcaseDataList"];
    runTime = moment(Huxleyview.Storage["tcaseDataList"][0][2], "YYYYMMDDHHmmss").format('MMMM Do YYYY, h:mm:ss a');
    $("div.runtime p").text(runTime);
    $("#tcase-list ul").fadeOut().empty();
    $.each(tcaseDataList, function(index, value){
      if(value[1]==='ok'){
        $("#tcase-list ul").append($('<li class="succ"><a href=/huxley/'+value[0]+"/"+value[2]+"/"+value[2]+">"+value[0]+"</a></li>"));
      }
      else{
        $("#tcase-list ul").append($('<li class="fail"><a href=/huxley/'+value[0]+"/"+value[2]+"/"+value[2]+">"+value[0]+"</a></li>"));
      }
    });
    $("#tcase-list ul").fadeIn();
  },

  RefreshTimeline:function(){
    var timelineDataList = Huxleyview.Storage['timelineDataList'];
    var width = $("#tcase-timeline").width();
    var colorScale = d3.scale.ordinal().range(['#1f77b4','#ff0000'])
                       .domain(['succ','fail']);
    var timeScore = Huxleyview.Storage.GetTimeScore();
    var timeIntervalNum = Math.ceil((timeScore[1]-timeScore[0])/(3600*24*7));

    var chart = d3.timeline()
                  .width(width*timeIntervalNum)
                  .stack()
                  .tickFormat( //
                      {format: d3.time.format("%Y-%m-%d %H:%M"),
                       tickTime: d3.time.hours,
                       tickNumber: 24,
                       tickSize: 40})
                  .margin({left:30, right:30, top:10, bottom:20})
                  .hover(function (d, i, datum) {
                  // d is the current rendering object
                  // i is the index during d3 rendering
                  // datum is the id object
                  })
                  .click(function (d, i, datum) {
                       Huxleyview.Request.GetAllTcase(d['starting_time']/1000);
                  })
                  .scroll(function (x, scale) {
                    $("#scrolled_date").text(scale.invert(x) + " to " + scale.invert(x+width));
                  })

                  .display("circle") // toggle between rectangles and circles
                  .colors(colorScale)
                  .colorProperty('result');

    var svg = d3.select("#tcase-timeline")
                .append("svg")
                .attr("width", width)
                .datum(timelineDataList).call(chart);
  },
};
