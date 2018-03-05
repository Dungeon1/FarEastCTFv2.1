$(document).ready(function() {
  $('#menu_trigger').click(function() {
   if(!$('#main_navigation').hasClass('open_mobile_main_navigation')){
       $('#main_navigation').addClass('open_mobile_main_navigation');
       $('#sub_menu').removeClass('close_sub_nav');
   }
   else{
       $('#main_navigation').removeClass('open_mobile_main_navigation');
       $('#sub_menu').addClass('close_sub_nav');
   } 
  });//Открытие меню по нажатию на кнопку бургера

  $('#main_navigation li').click(function() {
    $('#main_navigation').removeClass('open_mobile_main_navigation');
  });
    
  $('#about_us').click(function() {
   if(!$('.sub_main_nav').hasClass('sub_main_open_nav')){
       $('.sub_main_nav').addClass('sub_main_open_nav');
   }
   else{
       $('.sub_main_nav').removeClass('sub_main_open_nav');
   }
    if($('#arrow').hasClass('close_arrow')){
        $('#arrow').addClass('open_arrow');
        $('#arrow').removeClass('close_arrow');
    }
    else{
        $('#arrow').removeClass('open_arrow');
        $('#arrow').addClass('close_arrow');
    }
  });

    
  
});//end ready