$(document).ready(function() {
    $(".dropdown-trigger").dropdown();

    // highlight the language select
    var listItems = $('#nav-mobile').children()
    var listItems2 = $('#dropdown1').children()

    if(lang == ""){
        $(listItems[0]).siblings().removeClass('red');
        $(listItems[0]).addClass('red');
    }
    var check = false;
    for(var i = 0; i < listItems.length; i++){
        var aText = $(listItems[i]).children('a').text().toLowerCase()
        if(aText == lang){
            $(listItems[i]).siblings().removeClass('red')
            $(listItems[i]).addClass('red');
            check = true;
        }
    }
    if (check == false){
        for(var i = 0; i < listItems2.length; i++){
            var aText = $(listItems2[i]).children('a').text().toLowerCase()
            if(aText == lang){
                $(listItems[0]).siblings().removeClass('red');
                $(listItems2[i]).siblings().removeClass('red')
                $(listItems2[i]).addClass('red');
            }
        }
    }
});

// comment reply button
$(document).on('click', '#reply-btn', function() {
    $('#comment_box').show()
});

$('.slider').slider({
    full_width: true,
    interval: 2000,
    transition: 800,
    duration: 2000,
    height: 500
});

$(document).on('click', '.dropdown-trigger', function(){
    // Highlight the selected header
    $(this).parent().siblings().removeClass('red');
    $(this).parent().addClass('red');
});

// Ajax for search bar
$('.ajax_form').submit(function(e){
    e.preventDefault()
});
$('#search-title').keyup(function(){
    $.ajax({
        url: '/search',
        method: 'POST',
        data: $(this).parent().serialize(),
        success: function(serverResponse){
            $('#search-results').html(serverResponse)
        }
    })
});