odoo.define('employee_portal_timeoff.portal_timeoff', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.EmpPortalTimeOff = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.new_timeoff_form, .edit_timeoff_form)',
    events: {
        'click .new_timeoff_confirm': '_onNewTimeOffConfirm',
        'click .edit_timeoff_confirm': '_onEditTimeOffConfirm',
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {jQuery} $btn
     * @param {function} callback
     * @returns {Promise}
     */
    _buttonExec: function ($btn, callback) {
        // TODO remove once the automatic system which does this lands in master
        $btn.prop('disabled', true);
        return callback.call(this).guardedCatch(function () {
            $btn.prop('disabled', false);
        });
    },
    /**
     * @private
     * @returns {Promise}
     */
    _createTimeOff: function () {
    	return this._rpc({
            model: 'hr.leave',
            method: 'create_timeoff_portal',
            args: [{
                description: $('.new_timeoff_form .name').val(),
                timeoff_type: $('.new_timeoff_form .holiday_status_id').val(),
                from: $('.new_timeoff_form .request_date_from').val(),
                to: $('.new_timeoff_form .request_date_to').val(),
                half_day: $('.new_timeoff_form .request_unit_half').prop("checked"),
                custom_hours: $('.new_timeoff_form .request_unit_hours').prop("checked"),
                request_hour_from: $('.new_timeoff_form .request_hour_from').val(),
                request_hour_to: $('.new_timeoff_form .request_hour_to').val(),
                request_date_from_period: $('.new_timeoff_form .request_date_from_period').val(),
                delegation_id: $('.new_timeoff_form .delegation_id').val(),
            }],
        }).then(function (response) {
            if (response.errors) {
                $('#new-opp-dialog .alert').remove();
                $('#new-opp-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/timeoff/' + response.id;
            }
        });
    },
    /**
     * @private
     * @returns {Promise}
     */
    _editTimeOffRequest: function () {
        return this._rpc({
            model: 'hr.leave',
            method: 'update_timeoff_portal',
            args: [[parseInt($('.edit_timeoff_form .timeoff_id').val())], {
            	timeoffID: parseInt($('.edit_timeoff_form .timeoff_id').val()),
            	description: $('.edit_timeoff_form .name').val(),
                timeoff_type: $('.edit_timeoff_form .holiday_status_id').val(),
                from: this._parse_date($('.edit_timeoff_form .request_date_from').val()),
                to: this._parse_date($('.edit_timeoff_form .request_date_to').val()),
                half_day: $('.edit_timeoff_form .request_unit_half').prop("checked"),
                custom_hours: $('.edit_timeoff_form .request_unit_hours').prop("checked"),
                request_hour_from: $('.edit_timeoff_form .request_hour_from').val(),
                request_hour_to: $('.edit_timeoff_form .request_hour_to').val(),
                request_date_from_period: $('.edit_timeoff_form .request_date_from_period').val(),
                delegation_id: $('.new_timeoff_form .delegation_id').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onNewTimeOffConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createTimeOff);
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onEditTimeOffConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._editTimeOffRequest);
    },

    _parse_date: function (value) {
        console.log(value);
        var date = moment(value, "YYYY-MM-DD", true);
        if (date.isValid()) {
            return time.date_to_str(date.toDate());
        }
        else {
            return false;
        }
    },
});
});
