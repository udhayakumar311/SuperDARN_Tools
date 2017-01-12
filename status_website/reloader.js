var req;

function reloadData()
{

   reloadGraph();
   reloadData_schedule_text();

//    reloadData_example();
   timeoutID = setTimeout('reloadData()', 10000);

}



function reload_rom_kodiakAux()
{
   var now = new Date();
   url = 'liveData/agent_summary_kod-aux?' + now.getTime();

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

   req.onreadystatechange = processReqChange_rom_kod_aux;
   req.open("GET", url, true);
   req.send(null);

   timeoutID = setTimeout('reload_rom_kodiakAux()', 10000);
}



function processReqChange_rom_kod_aux()
{
   // If req shows "complete"
   if (req.readyState == 4)
   {
      dataDiv = document.getElementById('agent_log_kodiak_aux');

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


function update_RT_geo_power()
{
   var plotName = "geo_power"
   var now = new Date();
   var baseURL = 'http://superdarn.gi.alaska.edu/java/images/gui/'
   var siteArray = ["ade", "kodc", "mcma", "ksr", "adw", "kodd", "mcmb", "sps"];

   for (let site of siteArray) {
   	document.images[site].src = baseURL + site + '/' + plotName + '.png?' + now.getTime();
   	document.getElementById(site + "_href").href = baseURL + site + '/' + plotName + '.png' ;
}


   // Start new timer (in ms)
  timeoutID = setTimeout('update_RT_geo_power()', 5000);

}

function update_RT_fan_power()
{
   var plotName = "fan_power"
   var now = new Date();
   var baseURL = 'http://superdarn.gi.alaska.edu/java/images/gui/'
   var siteArray = ["ade", "kodc", "mcma", "ksr", "adw", "kodd", "mcmb", "sps"];

   for (let site of siteArray) {
   	document.images[site].src = baseURL + site + '/' + plotName + '.png?' + now.getTime();
   	document.getElementById(site + "_href").href = baseURL + site + '/' + plotName + '.png' ;
}


   // Start new timer (in ms)
  timeoutID = setTimeout('update_RT_fan_power()', 5000);

}


function reloadData_schedule_text()
{
   var now = new Date();
   url = 'liveData/schedule_status_text?' + now.getTime();

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

   document.images['schedule_plot'].src = 'liveData/schedule_plot.png?' + now.getTime();

   // Start new timer (1 min)
  //timeoutID = setTimeout('reloadGraph()', 2000);
}
