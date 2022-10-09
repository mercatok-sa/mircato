# -*- coding: utf-8 -*-
#################################################################################
# Author      : Zero For Information Systems (<www.erpzero.com>)
# Copyright(c): 2016-Zero For Information Systems
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockLocation(models.Model):
    _inherit = 'stock.location'

    location_acc_valuation = fields.Many2one(
        'account.account', 'Stock Valuation Account', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0]), ('deprecated', '=', False)]", check_company=True,
        help="""When automated inventory valuation is enabled on a product, this account will hold the current value of the products.""",)
    location_stock_journal = fields.Many2one(
        'account.journal', 'Stock Journal', company_dependent=True,
        domain="[('company_id', '=', allowed_company_ids[0])]", check_company=True,
        help="When doing automated inventory valuation, this is the Accounting Journal in which entries will be automatically posted when stock moves are processed.")

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_accounting_data_for_valuation(self):
        res = super(StockMove, self)._get_accounting_data_for_valuation()
        if self.company_id.activat_internal_trans and self.picking_type_id.code != 'internal':
            self.ensure_one()
            self = self.with_context(force_company=self.company_id.id)
            accounts_data = self.product_id.product_tmpl_id.get_product_accounts()

            if self.location_id.valuation_out_account_id:
                acc_src = self.location_id.valuation_out_account_id.id
            else:
                acc_src = accounts_data['stock_input'].id

            if self.location_dest_id.valuation_in_account_id:
                acc_dest = self.location_dest_id.valuation_in_account_id.id
            else:
                acc_dest = accounts_data['stock_output'].id

            acc_valuation = self.location_id.location_acc_valuation or self.location_dest_id.location_acc_valuation or accounts_data.get('stock_valuation', False)
            if acc_valuation:
                acc_valuation = acc_valuation.id
            if not accounts_data.get('stock_journal', False):
                raise UserError(_('You don\'t have any stock journal defined on your product category, check if you have installed a chart of accounts.'))
            if not acc_src:
                raise UserError(_('Cannot find a stock input account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
            if not acc_dest:
                raise UserError(_('Cannot find a stock output account for the product %s. You must define one on the product category, or on the location, before processing this operation.') % (self.product_id.display_name))
            if not acc_valuation:
                raise UserError(_('You don\'t have any stock valuation account defined on your product category. You must define one before processing this operation.'))

            journal_id = self.location_id.location_stock_journal.id or self.location_dest_id.location_stock_journal.id or accounts_data['stock_journal'].id
            return journal_id, acc_src, acc_dest, acc_valuation

        return res

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder)
        for move in self:
            if self.company_id.activat_internal_trans:
                if self.picking_type_id.code == 'internal' and not self.company_id.inter_locations_clearing_account_id:
                    raise UserError(_("please Define Inter-locations clearing account in Company Info"))
                if self.picking_type_id.code == 'internal' and self.company_id.inter_locations_clearing_account_id:
                    if not self.picking_type_id.code == "internal":
                        return True
                    if move.picking_type_id.code == "internal":
                        if move.product_id.valuation == "real_time" and move.product_id.type == "product":
                            if (move.location_id.company_id
                                and move.location_id.company_id == move.location_dest_id.company_id
                                and move.location_id != move.location_dest_id):
                                (
                                    journal_id,
                                    acc_src,
                                    acc_dest,
                                    acc_valuation,
                                ) = move._get_accounting_data_for_valuation()
                                move_total_value = (move.product_id.standard_price)*(move.product_qty)
                                if move_total_value >0:
                                    location_acc_valuation_from = move.location_id.location_acc_valuation.id or acc_valuation
                                    journal_id_from = move.location_id.location_stock_journal.id or journal_id
                                    journal_id_to = move.location_dest_id.location_stock_journal.id or journal_id
                                    location_acc_valuation_to = move.location_dest_id.location_acc_valuation.id or acc_valuation
                                    inter_locations_clearing_account_id = self.company_id.inter_locations_clearing_account_id.id
                                    ref_name = '%s- %s' % (move.picking_id.name,move.product_id.display_name)
                                    move_lines_to = move._prepare_account_move_line(
                                        move.product_qty,
                                        move_total_value,
                                        location_acc_valuation_from,
                                        inter_locations_clearing_account_id,
                                        ref_name,
                                    )
                                    move_lines_from = move._prepare_account_move_line(
                                        move.product_qty,
                                        move_total_value,
                                        inter_locations_clearing_account_id,
                                        location_acc_valuation_to,
                                        ref_name,
                                    )
                                    AccountMove = self.env["account.move"].with_context(
                                                force_company=move.location_id.company_id.id,
                                                company_id=move.company_id.id,)
                                    if move_lines_to and move_lines_from and move_total_value !=0:
                                        all_lines = move_lines_from + move_lines_from
                                        date = self._context.get('force_period_date', fields.Date.context_today(self))
                                        new_account_move = AccountMove.sudo().create(
                                                {
                                                    "journal_id": journal_id_from,
                                                    "line_ids": move_lines_to,
                                                    "company_id": move.company_id.id,
                                                    'date': date,
                                                    "ref": move.picking_id and move.picking_id.name,
                                                    "stock_move_id": move.id,
                                                    "move_type": 'entry',
                                                }
                                            )
                                        new_account_move.post()
                                        new_account_move2 = AccountMove.sudo().create(
                                                {
                                                    "journal_id": journal_id_to,
                                                    "line_ids": move_lines_from,
                                                    "company_id": move.company_id.id,
                                                    'date': date,
                                                    "ref": move.picking_id and move.picking_id.name,
                                                    "stock_move_id": move.id,
                                                    "move_type": 'entry',
                                                }
                                            )
                                        new_account_move2.post()
                                    
        return res
 
