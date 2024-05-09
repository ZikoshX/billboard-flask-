//jQuery time
var current_fs, next_fs, previous_fs; //fieldsets
var current_fs, next_fs, previous_fs; //fieldsets
var animating; //flag to prevent quick multi-click glitches
$(document).ready(function() {
  $(".next").click(function(){
      if(animating) return false;
      animating = true;

      var companyName = $("#company-name").val();  // Get the value of the company name input
      console.log("Company Name:", companyName); // Debug: Check what value is being captured
      
      if (!companyName.trim()) {  // Check if the company name is empty
          console.log("Validation failed: Company Name is required."); // Debug: Log a message if validation fails
          animating = false;  // Reset the animating flag to allow future interactions
          return false;  // Stop the function here if the company name is empty
      }
      var desc = $("#billboard-info").val();  // Get the value of the company name input
      console.log("What about billboard:", desc); // Debug: Check what value is being captured
      
      if (!desc.trim()) {  // Check if the company name is empty
          console.log("Validation failed: Description is required."); // Debug: Log a message if validation fails
          animating = false;  // Reset the animating flag to allow future interactions
          return false;  // Stop the function here if the company name is empty
      }

      var Start = $("#Start").val();  // Get the value of the company name input
      console.log("Start-date:", Start); // Debug: Check what value is being captured
      
      if (!Start.trim()) {  // Check if the company name is empty
          console.log("Validation failed: Start date is required."); // Debug: Log a message if validation fails
          animating = false;  // Reset the animating flag to allow future interactions
          return false;  // Stop the function here if the company name is empty
      }
      var end = $("#End").val();  // Get the value of the company name input
    
      if (!end.trim()) {  // Check if the company name is empty
          animating = false;  // Reset the animating flag to allow future interactions
          return false;  // Stop the function here if the company name is empty
      }
      
      
     

      current_fs = $(this).parent();
      next_fs = current_fs.next();

      // Activate next step on progressbar
      $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

      // Show the next fieldset
      next_fs.show(); 
      $("#msform").css('overflow', 'hidden');

      // Hide the current fieldset with style
      current_fs.animate({opacity: 0}, {
          step: function(now, mx) {
              var scale = 1 - (1 - now) * 0.2;
              var left = (now * 50) + "%";
              var opacity = 1 - now;
              current_fs.css({
                  'transform': 'scale('+scale+')',
                  'position': 'absolute'
              });
              next_fs.css({'left': left, 'opacity': opacity});
          }, 
          duration: 800, 
          complete: function(){
              current_fs.hide();
              current_fs.css({'position': '', 'transform': '', 'opacity': ''});
              next_fs.css({'left': '', 'opacity': ''});
              $("#msform").css('overflow', '');
              animating = false;
          }, 
      });
  });
});

$(".previous").click(function(){
    if(animating) return false;
    animating = true;
    
    current_fs = $(this).parent();
    previous_fs = current_fs.prev();

    //de-activate current step on progressbar
    $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

    //show the previous fieldset
    previous_fs.show(); 
    $("#msform").css('overflow', 'hidden');

    //hide the current fieldset with style
    current_fs.animate({opacity: 0}, {
        step: function(now, mx) {
            scale = 0.8 + (1 - now) * 0.2;
            left = ((1-now) * 50) + "%";
            opacity = 1 - now;
            current_fs.css({'left': left});
            previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
        }, 
        duration: 800, 
        complete: function(){
            current_fs.hide();
            current_fs.css({'position': '', 'left': '', 'opacity': ''});
            previous_fs.css({'transform': '', 'opacity': ''});
            $("#msform").css('overflow', '');
            animating = false;
        }, 
    });
});

function updateImageDisplay(checkbox, imageName) {
    var image = document.getElementById(imageName);
    if (checkbox.checked) {
        image.style.display = 'block';
    } else {
        image.style.display = 'none';
    }
}
const radioGroups = document.querySelectorAll('.radio-group') || []
radioGroups.forEach(radioGroup => {
  let bullet = document.createElement("div");
  bullet.classList.add("bullet");
  radioGroup.prepend(bullet);
  let checked = radioGroup.querySelector('input:checked + label');
  bullet.style.top = checked.offsetTop + 'px';
  let options = radioGroup.querySelectorAll('label');
  options.forEach(option =>{
    option.addEventListener('click', (e)=>{
      bullet.style.top = e.target.offsetTop + 'px';
    })
  })
})
$(".custom-select").each(function() {
    var classes = $(this).attr("class"),
      id = $(this).attr("id"),
      name = $(this).attr("name");
    var template = '<div class="' + classes + '">';
    template +=
      '<span class="custom-select-trigger">' +
      $(this).attr("placeholder") +
      "</span>";
    template += '<div class="custom-options">';
    $(this).find("option").each(function() {
      template +=
        '<span class="custom-option ' +
        $(this).attr("class") +
        '" data-value="' +
        $(this).attr("value") +
        '">' +
        $(this).html() +
        "</span>";
    });
    template += "</div></div>";
  
    $(this).wrap('<div class="custom-select-wrapper"></div>');
    $(this).hide();
    $(this).after(template);
  });
  $(".custom-option:first-of-type").hover(
    function() {
      $(this).parents(".custom-options").addClass("option-hover");
    },
    function() {
      $(this).parents(".custom-options").removeClass("option-hover");
    }
  );
  $(".custom-select-trigger").on("click", function() {
    $(".custom-select").not($(this).parents(".custom-select")).removeClass("opened");
    $("html").one("click", function() {
      $(".custom-select").removeClass("opened");
    });
    $(this).parents(".custom-select").toggleClass("opened");
    event.stopPropagation();
  });
  $(".custom-option").on("click", function() {
    $(this)
      .parents(".custom-select-wrapper")
      .find("select")
      .val($(this).data("value"));
    $(this)
      .parents(".custom-options")
      .find(".custom-option")
      .removeClass("selection");
    $(this).addClass("selection");
    $(this).parents(".custom-select").removeClass("opened");
    $(this)
      .parents(".custom-select")
      .find(".custom-select-trigger")
      .text($(this).text());
  });
  
  
  $(".custom-select-trigger").on("click", function() {  
  
    if($('#potencial').next().hasClass( "opened" ))
      {        
  
       if($('#potencial1').next().hasClass( "opened" )) 
         {         
           console.log('trying to close drop 2');
           $('#potencial1').next().removeClass('opened');
           
           if($('#potencial').next().hasClass( "opened" ))
             {
             $('#potencial').next().removeClass('opened');
  
             }        
           
         }
         
       
      }
    else
      
      {
        console.log('does not has class');
            console.log($('#potencial1').next().attr('class')); 
        
            
      }
  });
  
  $(".custom-option").on("click", function() {
    var value = $(this).data("value");
    var select = $(this).closest(".custom-select-wrapper").find("select");
    var trigger = $(this).closest(".custom-select").find(".custom-select-trigger");
    
    select.val(value).trigger('change');
    trigger.text($(this).text());
    $(this).closest(".custom-select").removeClass("opened");
});
  // Existing logic for .next and .previous buttons
// ...

// Additional logic to calculate and display the order summary and total pric
  
