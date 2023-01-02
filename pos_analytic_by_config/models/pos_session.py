# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"





    def _debit_amounts(self, partial_move_line_vals, amount, amount_converted, force_company_currency=False):
        """ `partial_move_line_vals` is completed by `debit`ing the given amounts.

        See _credit_amounts docs for more details.
        """
        account_analytic_id = self.env.context.get("account_analytic_id")
        if account_analytic_id:
            partial_move_line_vals.update({"analytic_account_id": account_analytic_id})
        return super()._debit_amounts(
            partial_move_line_vals, amount, amount_converted, force_company_currency
        )

    def _credit_amounts(
        self,
        partial_move_line_vals,
        amount,
        amount_converted,
        force_company_currency=False,
    ):
        """We only want the analyitic account set in the sales items from the account
        move. This is called from `_get_sale_vals` but from other credit methods
        as well. To ensure that only sales items get the analytic account we flag
        the context from the former method with the proper analytic account id.
        """
        account_analytic_id = self.env.context.get("account_analytic_id")
        print("")
        if account_analytic_id:
            partial_move_line_vals.update({"analytic_account_id": account_analytic_id})
        return super()._credit_amounts(
            partial_move_line_vals, amount, amount_converted, force_company_currency
        )
    def _get_tax_vals(self, key, amount, amount_converted, base_amount_converted):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,
                         self.with_context(account_analytic_id=account_analytic_id.id), )._get_tax_vals(key, amount, amount_converted, base_amount_converted)
        return super()._get_tax_vals(key, amount, amount_converted, base_amount_converted)

    # def _prepare_balancing_line_vals(self, imbalance_amount, move):
    #     account_analytic_id = self.config_id.account_analytic_id
    #     if account_analytic_id:
    #         return super(PosSession,
    #                      self.with_context(account_analytic_id=account_analytic_id.id), )._prepare_balancing_line_vals(
    #             imbalance_amount, move)
    #     return super()._prepare_balancing_line_vals( imbalance_amount, move)

    def _get_stock_output_vals(self, out_account, amount, amount_converted):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,self.with_context(account_analytic_id=account_analytic_id.id), )._get_stock_output_vals(out_account, amount, amount_converted)
        return super()._get_stock_output_vals(out_account, amount, amount_converted)

    def _get_invoice_receivable_vals(self, account_id, amount, amount_converted, **kwargs):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,self.with_context(account_analytic_id=account_analytic_id.id), )._get_invoice_receivable_vals(account_id, amount, amount_converted, **kwargs)
        return super()._get_invoice_receivable_vals(account_id, amount, amount_converted, **kwargs)

    def _get_rounding_difference_vals(self, amount, amount_converted):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,self.with_context(account_analytic_id=account_analytic_id.id), )._get_rounding_difference_vals(amount, amount_converted)
        return super()._get_rounding_difference_vals(amount, amount_converted)

    def _get_combine_receivable_vals(self, payment_method, amount, amount_converted):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,self.with_context(account_analytic_id=account_analytic_id.id), )._get_combine_receivable_vals(payment_method, amount, amount_converted)
        return super()._get_combine_receivable_vals(payment_method, amount, amount_converted)
    def _get_stock_expense_vals(self, exp_account, amount, amount_converted):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,self.with_context(account_analytic_id=account_analytic_id.id), )._get_stock_expense_vals(exp_account, amount, amount_converted)
        return super()._get_stock_expense_vals( exp_account, amount, amount_converted)

    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(PosSession,self.with_context(account_analytic_id=account_analytic_id.id), )._get_split_receivable_vals(payment, amount, amount_converted)
        return  super()._get_split_receivable_vals( payment, amount, amount_converted)

    def _get_sale_vals(self, key, amount, amount_converted):
        """The method that allowed to add the analytic account to the sales items
        has been dropped in v13, so we have to add it in the moment the sales
        items values are prepared.
        """
        account_analytic_id = self.config_id.account_analytic_id
        if account_analytic_id:
            return super(
                PosSession,
                self.with_context(account_analytic_id=account_analytic_id.id),
            )._get_sale_vals(key, amount, amount_converted)
        return super()._get_sale_vals(key, amount, amount_converted)



