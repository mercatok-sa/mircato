# -*- coding: utf-8 -*-
####################################################################################
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'HR Custody',
    'version': '14.0.1.0.0',
    'summary': """Manage the company properties when it is in the custody of an employee""",
    'description': 'Manage the company properties when it is in the custody of an employee',
    'category': 'Human Resources  test change',
    'author': 'Test',
    'company': '',
    'website': "https://era.net.sa",
    'depends': ['hr', 'mail', 'hr_employee_updation', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'security/custody_security.xml',
        'views/wizard_reason_view.xml',
        'views/custody_view.xml',
        'views/hr_custody_notification.xml',
        'views/hr_employee_view.xml',
        'views/notification_mail.xml',
        'reports/custody_report.xml'
    ],
    'demo': ['data/demo_data.xml'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
