odoo.define('dev_hr_loan.loan_portal', function (require) {
    "use strict";
    
    var rpc = require('web.rpc')
    
    $(document).ready(function() {
            /* Loans Type selection */
        $(document).on("change", ".loan_type_select", function(){
        	var self = this
        	rpc.query({
        		model : 'employee.loan.type',
        		method: 'search_read',
        		args: [[['id', '=', $(this).val()]], ['id']],
        	})
        	
        });
    });
});
