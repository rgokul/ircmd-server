

function clear_alert(obj) {
  'use strict';
  $(obj).removeClass();
  $(obj).empty();
};

function create_alert(obj, status, title, text) {
  'use strict';
  if (status == 'success') {
    $(obj).addClass('alert alert-success in');
  }
  else {
    $(obj).addClass('alert alert-error in');
  }
  $(obj).append('<button type="button" class="close">&times;</button><h4>' + title + '</h4><p>' + text + '</p>');
  
};

function get_server_status() {
  'use strict';
  $.ajax({url:"/getStatus", 
    success: function(data, textStatus, jqXHR) {
      //alert(textStatus);
      create_alert('#le-alert', 'success', 'Connected', 'You can use the commands below')
    }, 
    error: function(jqXHR, textStatus, errorThrown) {
      //alert(textStatus);
      create_alert('#le-alert', 'error', 'Error', 'Check connectivity ' + errorThrown);
     }
  });
};

$(window).load(function() {
  $('#btn-alert').click(function () {
    'use strict';

    clear_alert('#le-alert');
    get_server_status();
    });
  });    

$(document).on('click', '.close', function() {
  'use strict';
  clear_alert($(this).parent());
  });
