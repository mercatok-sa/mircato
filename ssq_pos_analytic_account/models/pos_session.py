from odoo import models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class PosSession(models.Model):
    _inherit = "pos.session"

    def _create_non_reconciliable_move_lines(self, data):
        # Create account.move.line records for
        #   - sales
        #   - taxes
        #   - stock expense
        #   - non-cash split receivables (not for automatic reconciliation)
        #   - non-cash combine receivables (not for automatic reconciliation)
        taxes = data.get('taxes')
        sales = data.get('sales')
        stock_expense = data.get('stock_expense')
        rounding_difference = data.get('rounding_difference')
        MoveLine = data.get('MoveLine')

        tax_vals = [self._get_tax_vals(key, amounts['amount'], amounts['amount_converted'], amounts['base_amount_converted']) for key, amounts in taxes.items()]
        # Check if all taxes lines have account_id assigned. If not, there are repartition lines of the tax that have no account_id.
        tax_names_no_account = [line['name'] for line in tax_vals if line['account_id'] == False]
        if len(tax_names_no_account) > 0:
            error_message = _(
                'Unable to close and validate the session.\n'
                'Please set corresponding tax account in each repartition line of the following taxes: \n%s'
            ) % ', '.join(tax_names_no_account)
            raise UserError(error_message)
        rounding_vals = []

        if not float_is_zero(rounding_difference['amount'], precision_rounding=self.currency_id.rounding) or not float_is_zero(rounding_difference['amount_converted'], precision_rounding=self.currency_id.rounding):
            rounding_vals = [self._get_rounding_difference_vals(rounding_difference['amount'], rounding_difference['amount_converted'])]

        MoveLine.create(
            tax_vals
            + [self.get_sale_vals(key[0], key[1], key[2], key[3], amounts['amount'], amounts['amount_converted'], amounts['tax_amount']) for key, amounts in sales.items()]
            + [self._get_stock_expense_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in stock_expense.items()]
            + rounding_vals
        )
        return data

    def get_sale_vals(self, account_id, sign, tax_keys, base_tag_ids,  amount, amount_converted, tax_amount):
        # account_id, sign, tax_keys, base_tag_ids = key
        tax_ids = {tax[0] for tax in tax_keys}
        applied_taxes = self.env["account.tax"].browse(tax_ids)
        title = "Sales" if sign == 1 else "Refund"
        name = "%s untaxed" % title
        if applied_taxes:
            name = "{} with {}".format(title, ", ".join([tax.name for tax in applied_taxes]))
        partial_vals = {
            "name": name,
            "account_id": account_id,
            "analytic_account_id": self.config_id.analytic_account_id.id
            if self.config_id.analytic_account_id
            else False,
            "move_id": self.move_id.id,
            "tax_ids": [(6, 0, tax_ids)],
            "tax_tag_ids": [(6, 0, base_tag_ids)],
        }
        return self._credit_amounts(partial_vals, amount, amount_converted)

    # This adds analytic account to COGS account move line in the journal
    # entry created when closing the POS session
    def _get_stock_expense_vals(self, exp_account, amount, amount_converted):
        partial_args = {'account_id': exp_account.id,
                         'move_id': self.move_id.id, 
                         "analytic_account_id": self.config_id.analytic_account_id.id
                                                    if self.config_id.analytic_account_id
                                                    else False,
                        }
        return self._debit_amounts(partial_args, amount, amount_converted, force_company_currency=True)
