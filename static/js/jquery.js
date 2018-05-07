$(document).ready(function() {
    $('#signup-username').keyup(function(){
        var name = $('#signup-username').val();
        sql_verify(name);
        });
    });
function sql_verify(name){
    if (name.includes('select') || name.includes('SELECT') || name.includes('--') || name.includes('\'')|| name.includes('\"')){ //вернет true
        $("#cd-error-message-username-signup").text("Мне кажется или ты пытаешься инъекцию запилить?! Брось каку! ");
        $('#cd-error-message-username-signup').addClass('is-visible');
    }
    else{
        $('#cd-error-message-username-signup').removeClass('is-visible');
    }
}
