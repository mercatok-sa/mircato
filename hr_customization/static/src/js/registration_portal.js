odoo.define('hr_customization.registration_portal', function (require) {
    "use strict";
    var rpc = require('web.rpc')
    $(document).ready(function() {
        /* regis off Type selection */
        $(document).on("change", ".employee_select", function(){
        	var self = this
        	rpc.query({
        		model : 'hr.employee',
        		method: 'search_read',
        		args: [[['id', '=', $(this).val()]], ['id']],
        	})
        });
    });
});
