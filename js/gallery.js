$(document).ready(function() {
  var counter=1;
  $('#img_box_1').mouseenter(function() {
      $(".img_box_1").css('background-image', 'url(img/area1/' + counter + '.jpg)');
      counter = counter+1;
      if(counter>3){
          counter = 1 
      }
      
  }); 
    $('#img_box_2').mouseenter(function() {
      $(".img_box_2").css('background-image', 'url(img/area2/' + counter + '.jpg)');
      counter = counter+1;
      if(counter>3){
          counter = 1 
      }
      
  });
    $('#img_box_3').mouseenter(function() {
      $(".img_box_3").css('background-image', 'url(img/area3/' + counter + '.jpg)');
      counter = counter+1;
      if(counter>3){
          counter = 1 
      }
      
  });
    $('#img_box_4').mouseenter(function() {
      $(".img_box_4").css('background-image', 'url(img/area4/' + counter + '.jpg)');
      counter = counter+1;
      if(counter>3){
          counter = 1 
      }
      
  });
    $('#img_box_5').mouseenter(function() {
      $(".img_box_5").css('background-image', 'url(img/area5/' + counter + '.jpg)');
      counter = counter+1;
      if(counter>3){
          counter = 1 
      }
      
  });
});