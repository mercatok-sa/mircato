from odoo import fields, models, api, tools, _


class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'
    probation_date_end = fields.Date('Probation Period End')

    @api.model
    def _get_fields(self):
        return ','.join('contract.%s' % name for name, field in self._fields.items()
                        if field.store
                        and field.type not in ['many2many', 'one2many', 'related']
                        and field.name not in ['id', 'contract_id', 'employee_id', 'date_hired', 'is_under_contract',
                                               'active_employee', 'probation_date_end'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Reference contract is the one with the latest start_date.
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
              WITH contract_information AS (
                  SELECT DISTINCT employee_id,
                                  company_id,
                                  FIRST_VALUE(id) OVER w_partition AS id,
                                  MAX(CASE
                                      WHEN state='open' THEN 1
                                      WHEN state='draft' AND kanban_state='done' THEN 1
                                      ELSE 0 END) OVER w_partition AS is_under_contract
                  FROM   hr_contract AS contract
                  WHERE  contract.state <> 'cancel'
                  AND contract.active = true
                  WINDOW w_partition AS (
                      PARTITION BY contract.employee_id
                      ORDER BY
                          CASE
                              WHEN contract.state = 'open' THEN 0
                              WHEN contract.state = 'draft' THEN 1
                              WHEN contract.state = 'close' THEN 2
                              ELSE 3 END,
                          contract.date_start DESC
                      RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                  )
              )
              SELECT     employee.id AS id,
                         employee.id AS employee_id,
                         employee.active AS active_employee,
                         contract.id AS contract_id,
                         contract_information.is_under_contract::bool AS is_under_contract,
                         employee.first_contract_date AS date_hired,
                         employee.probation_date_end AS probation_date_end,
                         %s
              FROM       hr_contract AS contract
              INNER JOIN contract_information ON contract.id = contract_information.id
              RIGHT JOIN hr_employee AS employee
                  ON  contract_information.employee_id = employee.id
                  AND contract.company_id = employee.company_id
              WHERE   employee.employee_type IN ('employee', 'student')
          )""" % (self._table, self._get_fields()))
