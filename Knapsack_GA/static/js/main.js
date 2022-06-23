$(document).ready(function(){
    $('#submit').click(function(){
        items   = document.getElementById('items').value;
        values  = document.getElementById('values').value;
        weights = document.getElementById('weights').value;
        limW    = document.getElementById('limW').value;
        
        $.ajax(
            {
                url: '',
                type: 'get',
                data: {
                    'items':items,
                    'values':values,
                    'weights':weights,
                    'limW':limW,
                },
                success: function(response) {
                    $('#result').empty().append(response.result);
                }
            }
        )
    });

});