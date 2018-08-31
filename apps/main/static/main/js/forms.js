// Models
$('#myModal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
});
$('#myModal').modal({backdrop: 'static', keyboard: false}) 

$(document).on('click', '#send_email', function(e){
    e.preventDefault() // prevent form from submitting

    var emailFormat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    var emailVal = $('#email_input').val();
    if(emailVal == ""){
        $('#email_input').css('border', '1px solid red')
    }else if(emailVal.match(emailFormat)) {
        // Send the form now using ajax
        $.ajax({
            url: $('#form_forgot').attr('action'),
            method: 'POST',
            data: $('#form_forgot').serialize(),
            success: function(serverResponse){
                console.log(serverResponse)
            }
        })
        // let the user know that we send a pin number
        $('.message').removeClass('text-danger');
        $('.message').addClass('text-success')
        $('.modal-body').html(
            `<p class="message text-success">We've emailed you a temporary pin number, if an account exists with the email you entered. You should received them shortly</p>
            <input type="text" id="pin_input" name="pin" class="form-control" placeholder="Enter your Pin" autofocus>
            <button type="button" class="btn btn-primary btn-lg" id="check_pin">Check Pin</button>`
        )

        // removed the model footer 
        $('.modal-footer').hide()
        
    } else{
        $('.message').removeClass('text-success');
        $('.message').addClass('text-danger')
        $('.message').text("Invalid email")
    }
});


$(document).on('click', '#check_pin', function(){
    var pin = $('#pin_input').val()
    if (pin == ""){
        $('#pin_input').css('border', '1px solid red');
    }
    else if(isNaN(pin)){
        $('.message').removeClass('text-success');
        $('.message').addClass('text-danger')
        $('.message').text("Please enter numbers only")
        $('#pin_input').css('border', '1px solid red');
    }
    else{
        // send a ajax request to the server to check pin number
        $.ajax({
            url: "/check_pin/"+pin,
            success: function(serverResponse){
                // check if this was a json response
                if (typeof(serverResponse) == "object"){
                    if("status" in serverResponse && serverResponse.status == 'wrong'){
                        $('.modal-body').html(
                            `<div class="modal-body">
                                <p class="message text-danger">Wrong Pin number, Please try again.</p>
                                <input type="text" id="pin_input" name="pin" class="form-control" placeholder="Enter your Pin" autofocus>
                                <button type="button" class="btn btn-primary" id="check_pin">Check Pin</button>
                            </div>`
                        );
                    }
                    else if("status" in serverResponse && serverResponse.status == 'startover'){
                        $('.modal-body').html(
                            `<div class="modal-body">
                                <p class="message text-danger">No more tries left, Please request a new pin.</p>
                                <input type="email" name="email" class="form-control" placeholder="Email address" id="email_input" autofocus>
                            </div>`
                        );
                        $('.modal-footer').show();
                    }
                }
                else{
                    $('.message').removeClass('text-danger');
                    $('.message').addClass('text-success')
                    $('.message').text("Your Pin is correct. You are now being redirect to reset your password")
                    $('#check_pin').html(`<i class='fa loader'></i> Redirecting Now`);
                    
                    setTimeout(() => {
                        $('#check_pin').html('Check Pin');
                        window.location.href = "/reset_password";
                    }, 3000);
                } // end else
            }
        }); // ajax end here
    }
})