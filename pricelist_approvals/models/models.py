from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist', string="Pricelist", compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        tracking=1,
        domain="[('state', '=', 'valid'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pricelist_id = fields.Many2one('product.pricelist', string='Default Pricelist',
                                   domain="[('state', '=', 'valid')]",
                                   help="The pricelist used if no customer is selected or if the customer has no Sale"
                                        " Pricelist configured if any.")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist',
                                   domain="[('state', '=', 'valid')]")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_product_pricelist = fields.Many2one(
        comodel_name='product.pricelist', string="Pricelist",
        compute='_compute_product_pricelist', inverse="_inverse_product_pricelist", company_dependent=False,
        domain=lambda self: [('state', '=', 'valid'), ('company_id', 'in', (self.env.company.id, False))],
        help="This pricelist will be used, instead of the default one, for sales to the current partner")
