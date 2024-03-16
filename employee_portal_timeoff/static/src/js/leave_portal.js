odoo.define('employee_portal_timeoff.leave_portal', function (require) { 
    "use strict";
    
    var rpc = require('web.rpc')
    
    $(document).ready(function() {
    	
    	/* Half Day Checkbox */
    	function check_from_duration($this){
            var $challenges_details = $('#from_period_div');
            var $challenges_input = $challenges_details.find('#select_from_period');
            if ($this.prop('checked'))
            {
            	$challenges_details.show();
            	$challenges_input.attr('required','required');
            }
            else
            {
            	$challenges_details.hide();
            	$challenges_input.removeAttr('required');
            	$challenges_input.val('')
            }
        }
        $('#half_day_input_id').each(function(){
        	check_from_duration($(this));
        });
        
        $(document).on("change","#half_day_input_id", function(){
        	$("#unit_hours_input_id"). prop("checked", false);
        	$('.custom_hour_divs').hide()
        	$('.select_period_select').removeAttr('required');
        	$('.select_period_select').val('')
        	
        	check_from_duration($(this));
        });
        
        /* Custom Hours Checkbox */
        function check_custom_hours($this){
            var $challenges_details = $('.custom_hour_divs');
            var $challenges_input = $challenges_details.find('.select_period_select');
            if ($this.prop('checked'))
            {
            	$challenges_details.show();
            	$challenges_input.attr('required','required');
            }
            else
            {
            	$challenges_details.hide();
            	$challenges_input.removeAttr('required');
            	$challenges_input.val('')
            }
        }
        $('#unit_hours_input_id').each(function(){
        	check_custom_hours($(this));
        });
        
        $(document).on("change","#unit_hours_input_id", function(){
        	$("#half_day_input_id"). prop("checked", false);
        	$('#from_period_div').hide()
        	$('#select_from_period').removeAttr('required');
        	$('#select_from_period').val('')
        	
        	check_custom_hours($(this));
        });
        
        /* Time off Type selection */
        $(document).on("change", ".time_off_type_select", function(){
        	var self = this
        	rpc.query({
        		model : 'hr.leave.type',
        		method: 'search_read',
        		args: [[['id', '=', $(this).val()]], ['id', 'request_unit']],
        	}).then(function(rec){
        		if (rec && rec[0]){
        			if (rec[0].request_unit == 'hour'){
        				$('.half_day_option').show()
        				$('.custom_hrs_option').show()
        			}
        			else if (rec[0].request_unit == 'half_day'){
        				$('.half_day_option').show()
        				$('.custom_hrs_option').hide()
        			}
        			else{
        				$('.half_day_option').hide()
        				$('.custom_hrs_option').hide()
        			}
        		} 
        		
        	})
        	
        });

        /* Time off delegation selection */
        $(document).on("change", ".time_off_delegation_select", function(){
        	var self = this
        	rpc.query({
        		model : 'hr.employee',
        		method: 'search_read',
        		args: [[['id', '=', $(this).val()]], ['id']],
        	})
        });
    });
});
