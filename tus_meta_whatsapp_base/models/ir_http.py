# -*- coding: utf-8 -*-
# ----------------------------------------------------------
# ir_http modular http routing
# ----------------------------------------------------------

from odoo import api, http, models, tools, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError
from odoo.http import request, content_disposition
from odoo.tools import consteq, pycompat



class IrHttpInherit(models.AbstractModel):
    _inherit = 'ir.http'

    def _get_record_and_check(self, xmlid=None, model=None, id=None, field='datas', access_token=None):
        # get object and content
        record = None
        if xmlid:
            record = self._xmlid_to_obj(self.env, xmlid)
        elif id and model in self.env:
            record = self.env[model].sudo().browse(int(id))

        # obj exists
        if not record or field not in record:
            return None, 404

        try:
            if model == 'ir.attachment':
                record_sudo = record.sudo()
                if access_token and not consteq(record_sudo.access_token or '', access_token):
                    return None, 403
                elif (access_token and consteq(record_sudo.access_token or '', access_token)):
                    record = record_sudo
                elif record_sudo.public:
                    record = record_sudo
                elif self.env.user.has_group('base.group_portal'):
                    # Check the read access on the record linked to the attachment
                    # eg: Allow to download an attachment on a task from /my/task/task_id
                    record.check('read')
                    record = record_sudo

            # check read access
            try:
                # We have prefetched some fields of record, among which the field
                # 'write_date' used by '__last_update' below. In order to check
                # access on record, we have to invalidate its cache first.
                if not record.env.su:
                    record._cache.clear()
                record['__last_update']
            except AccessError:
                return None, 403

            return record, 200
        except MissingError:
            return None, 404