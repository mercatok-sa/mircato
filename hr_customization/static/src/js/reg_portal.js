odoo.define('hr_customization.reg_portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.EmpPortalLoans = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.new_reg_form)',
    events: {
        'click .new_reg_confirm': '_onNewRegConfirm',
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
    _createReg: function () {
    	return this._rpc({
            model: 'hr.resignation.request',
            method: 'create_regfrom_rtal',
            args: [{
                employee_id: $('.new_reg_form .employee_id').val(),
                last_date: $('.new_reg_form .last_date').val(),
                request_notes: $('.new_reg_form .request_notes').val(),

            }],
        }).then(function (response) {
            if (response.errors) {
                $('#new-opp-dialog .alert').remove();
                $('#new-opp-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/resignation/' + response.id;
            }
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    _onNewRegConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createReg);
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
