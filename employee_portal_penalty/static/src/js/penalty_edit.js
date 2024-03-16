odoo.define('employee_portal_penalty.penalty_edit', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.EmpPenaltyPortal = publicWidget.Widget.extend({
    selector: '#wrapwrap:has(.edit_penalty_form)',
    events: {
        'click .edit_penalty_confirm': '_onEditPenaltyConfirm',
    },

    _buttonExec: function ($btn, callback) {
        // TODO remove once the automatic system which does this lands in master
        $btn.prop('disabled', true);
        return callback.call(this).guardedCatch(function () {
            $btn.prop('disabled', false);
        });
    },

    _editPenaltyRequest: function () {
        return this._rpc({
            model: 'penalty.request',
            method: 'update_penalty_portal',
            args: [[parseInt($('.edit_penalty_form .penalty_id').val())], {
            	PenaltyID: parseInt($('.edit_penalty_form .penalty_id').val()),
                emp_manager_opinion: $('.edit_penalty_form .emp_manager_opinion').val(),
                emp_manager_feedback: $('.edit_penalty_form .emp_manager_feedback').val(),
                employee_cause_of_penalty: $('.edit_penalty_form .employee_cause_of_penalty').val(),
                employee_approve_of_cause: $('.edit_penalty_form .employee_approve_of_cause').val(),
                employee_other_approve: $('.edit_penalty_form .employee_other_approve').val(),
                hr_manager_feedback: $('.edit_penalty_form .hr_manager_feedback').val(),
            }],
        }).then(function () {
            window.location.reload();
        });
    },

    _onEditPenaltyConfirm: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        this._buttonExec($(ev.currentTarget), this._editPenaltyRequest);
    },


});
});
