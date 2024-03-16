odoo.define('dev_hr_loan.portal_loans', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.EmpPortalLoans = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.new_loans_form, .edit_loan_form)',
    events: {
        'click .new_loan_confirm': '_onNewLoanConfirm',
//        'click .edit_loan_confirm': '_onEditTimeOffConfirm',
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
    _createLoans: function () {
    	return this._rpc({
            model: 'employee.loan',
            method: 'create_loan_portal',
            args: [{
                description: $('.new_loans_form .name').val(),
                loan_type: $('.new_loans_form .loan_type_id').val(),
                date: $('.new_loans_form .request_date').val(),
                request_loan_amount: $('.new_loans_form .request_loan_amount').val(),
                request_term: $('.new_loans_form .request_term').val(),
                request_notes: $('.new_loans_form .request_notes').val(),

            }],
        }).then(function (response) {
            if (response.errors) {
                $('#new-opp-dialog .alert').remove();
                $('#new-opp-dialog div:first').prepend('<div class="alert alert-danger">' + response.errors + '</div>');
                return Promise.reject(response);
            } else {
                window.location = '/my/loans/' + response.id;
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
    _onNewLoanConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._createLoans);
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
