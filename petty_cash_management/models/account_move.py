import time
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp
from lxml import etree


class AccountMove(models.Model):
    _inherit = "account.move"

    petty_move_id = fields.Many2one('petty.cash','Petty Cash')

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"


    petty_id=fields.Many2one('petty.cash','Petty Cash')
