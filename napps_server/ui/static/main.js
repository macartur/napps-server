function convert_form_to_json(form){
    var array = jQuery(form).serializeArray();
    var json = {};

    jQuery.each(array, function() {
        json[this.name] = this.value || '';
    });

    return json;
}

function set_message(notice_type, strong_text, message){
  $('#notice')[0].className = notice_type
  $('#notice strong')[0].textContent =strong_text;
  $('#notice .message')[0].textContent = message;
}

function valid_password(){
   password = $('#user_form input[name=password]')[0].value
   confirm_password = $('#user_form input[name=confirm_password]')[0].value
   console.log(password)
   console.log(confirm_password)
   if(password != confirm_password){
     set_message('alert', 'Warning', "The password and confirm password must be the same.")
     return false;
   }
   set_message('invisible', '', '')
   return true;
}

function handle_result(data){
  if(data.statusText == "CREATED"){
      set_message('success', 'Success', 'The user has been created, verify the email confirmation.')
      $('#user_form input[type=reset]').click()
  }else if(data.statusText == "UNAUTHORIZED"){
    if(data.responseJSON.error){
      set_message('error', 'Error', 'data.responseJSON.error')
    }
  }
}

function register_user(url,json){
    options= {
              type: 'POST',
              url: url,
              data: JSON.stringify(json),
              dataType: 'json',
              contentType: "application/json"
             }
    result = $.ajax(options).always(handle_result)
}

main = function(){
  $("input[name=confirm_password]").blur(valid_password);
  $('form#user_form').bind('submit', function(event){
    event.preventDefault();

    var $form = this;
    var $json = convert_form_to_json($form)
    var url = "/users/"
    set_message('invisible', '', '')
    if(valid_password()){
      register_user(url, $json)
    }
  });
};

$(document).ready(main)
