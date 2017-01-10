var req;

function reloadData()
{

   reloadGraph();
   reloadData_schedule_text();

//    reloadData_example();
   timeoutID = setTimeout('reloadData()', 2000);

}

function reloadData_schedule_text()
{
   var now = new Date();
   url = 'schedule_status_text?' + now.getTime();

   try {
      req = new XMLHttpRequest();
   } catch (e) {
      try {
         req = new ActiveXObject("Msxml2.XMLHTTP");
      } catch (e) {
         try {
            req = new ActiveXObject("Microsoft.XMLHTTP");
         } catch (oc) {
            alert("No AJAX Support");
            return;
         }
      }
   }

   req.onreadystatechange = processReqChange_schedule_text;
   req.open("GET", url, true);
   req.send(null);
}

function processReqChange_schedule_text()
{
   // If req shows "complete"
   if (req.readyState == 4)
   {
      dataDiv = document.getElementById('schedule_status_text');

      // If "OK"
      if (req.status == 200)
      {
         // Set current data text
         dataDiv.innerHTML = req.responseText;

         // Start new timer (1 min)
        // timeoutID = setTimeout('reloadData()', 2000);
      }
      else
      {
         // Flag error
         dataDiv.innerHTML = '<p>There was a problem retrieving data: ' + req.statusText + '</p>';
      }
   }
}


function reloadData_example()
{
   var now = new Date();
   url = 'liveData?' + now.getTime();

   try {
      req = new XMLHttpRequest();
   } catch (e) {
      try {
         req = new ActiveXObject("Msxml2.XMLHTTP");
      } catch (e) {
         try {
            req = new ActiveXObject("Microsoft.XMLHTTP");
         } catch (oc) {
            alert("No AJAX Support");
            return;
         }
      }
   }

   req.onreadystatechange = processReqChange;
   req.open("GET", url, true);
   req.send(null);
}

function processReqChange()
{
   // If req shows "complete"
   if (req.readyState == 4)
   {
      dataDiv = document.getElementById('currentData');

      // If "OK"
      if (req.status == 200)
      {
         // Set current data text
         dataDiv.innerHTML = req.responseText;

         // Start new timer (1 min)
         //timeoutID = setTimeout('reloadData()', 2000);
      }
      else
      {
         // Flag error
         dataDiv.innerHTML = '<p>There was a problem retrieving data: ' + req.statusText + '</p>';
      }
   }
}

function reloadGraph() {
   var now = new Date();

   document.images['schedule_plot'].src = 'schedule_plot.png?' + now.getTime();

   // Start new timer (1 min)
  //timeoutID = setTimeout('reloadGraph()', 2000);
}
