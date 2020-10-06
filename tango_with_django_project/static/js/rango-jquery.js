$(document).ready( function() {
    //jQuery Code
    $("#about-btn").click( function(event) {
//        alert("You clicked the button using jQuery!");
        msgstr = $("#msg").html()
        msgstr = msgstr + "ooo"
        $("#msg").html(msgstr)
    });
    $("p").hover( function() {
        $(this).css('color', 'red');
    },
    function() {
        $(this).css('color', 'blue');
    });

});