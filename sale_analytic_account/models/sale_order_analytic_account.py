# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderanalyticAccount(models.Model):
    _inherit = "sale.order"


    def action_confirm(self):
        """ On SO confirmation, analytic account will be created automatically. """
        result = super(SaleOrderanalyticAccount, self).action_confirm()
        # if the SO not already linked to analytic account, create a new analytic account and set to so analytic account.
        if not self.analytic_account_id:
            self._analytic_account_generation()
        return result

    def _saleorder_create_analytic_account_prepare_values(self):
        """
         Prepare values to create analytic account
        :return: list of values
        """
        return {
            'name': '%s' % self.name,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
        }


    def _analytic_account_generation(self):
        """ Generate analytic account for the so , and link it.
            :return a mapping with the so id and its linked analytic account
            :rtype dict
        """
        result = {}
        values = self._saleorder_create_analytic_account_prepare_values()
        analytic_account = self.env['account.analytic.account'].sudo().create(values)
        self.write({'analytic_account_id': analytic_account.id})
        result[self.id] = analytic_account
        return result