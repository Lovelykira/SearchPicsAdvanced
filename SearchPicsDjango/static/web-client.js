 var socket = null;
 var isopen = false;

 window.onload = function() {

    socket = new WebSocket("ws://127.0.0.1:9000");

    socket.onopen = function() {
       console.log("Connected!");
       isopen = true;
    }

    socket.onmessage = function(e) {
       if (typeof e.data == "string") {
          data = e.data.slice(1, -1);
          var newLink = $("<a />", {
                        name : "link",
                        href : "/search/"+data,
                        text : data
                        }).appendTo('#tasks');
          tasks2 = document.getElementById("tasks2");
          tasks2_new = tasks2.replace(data, "");
          tasks2.InnerHtml = tasks2_new;

       }
    }

    socket.onclose = function(e) {
       console.log("Connection closed.");
       socket = null;
       isopen = false;
    }
 };
