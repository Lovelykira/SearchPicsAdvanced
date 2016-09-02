$(document).ready(function(){
        //update();
        //setTimeout(function(){
        //    update();
        //}, 5000);
       });




function update() {
          $.get('/tasks/', function(result){
                //console.log(showObjectjQuery(result));
                $( "#tasks" ).empty();
                var value;
                var newContainer = $("<div />",{
                    class : "row div-container"
                    }).appendTo('#tasks');
                for(var key in result){
                    value = result[key];

                    var newLink = $("<a />", {
                        name : "link",
                        href : "/search/"+key,
                        text : key
                        }).appendTo('.div-container');

                    var newDivProgress = $("<div />", {
                        class : "progress"
                    }).appendTo('.div-container');

                    var style = ""
                    if(value == "FINISHED"){
                        style = "width:100%";
                    }
                    else{
                        len = value.split(" ").length;
                        style = "width:"+100/len+"%"
                    }
                    var newDivProgressBar = $("<div />", {
                        class : "progress-bar",
                        role : "progressbar",
                        'aria-valuemin' : "0",
                        'aria-valuemax' : "100",
                        style : style,
                        text : style
                    }).appendTo('.progress');

                }
           });
}

function showObjectjQuery(obj) {
  var result = "";
  $.each(obj, function(k, v) {
    result += k + ", " + v + "\n";
  });
  return result;
}