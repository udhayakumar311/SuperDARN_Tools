var images = new Array(7);  
    images[0] = "liveData/schedule_plot_0.png";
    images[1] = "liveData/schedule_plot_1.png";
    images[2] = "liveData/schedule_plot_2.png";
    images[3] = "liveData/schedule_plot_3.png";
    images[4] = "liveData/schedule_plot_4.png";
    images[5] = "liveData/schedule_plot_5.png";
    images[6] = "liveData/schedule_plot_6.png";
    

    var nImages = 6;
    var iImage = 0;

  function  go_back() {
    var im=document.getElementById("schedule_plot5");
    if(iImage>0)
   {
    im.src = images[iImage-1];
    iImage = iImage - 1;
   }else{
    alert("This is the first image");
   }


}

function go_fwd(){
var im=document.getElementById("schedule_plot5");
    if(iImage < nImages){
    im.src = images[iImage+1];
    iImage = iImage + 1;
   }else{
      alert("This is the last image");
      var next=document.getElementById("next");
      next.setEnabled(false);
      }
   if(iImage > nImages-1){
     var next=document.getElementById("next");
      next.setEnabled(false);
    }




}
