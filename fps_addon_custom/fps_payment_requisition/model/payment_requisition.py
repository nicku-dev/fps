from odoo import api, fields, models, exceptions, _
import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
# from odoo.addons.terbilang import terbilang
import logging
_logger = logging.getLogger(__name__)



class PaymentRequisition(models.Model):
    _name = 'payment.requisition'
    _description = "Payment Requisition"
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ################################################################
    # Proteksi tidak bisa membuat pengajuan untuk penerima yg sama # 
    # ketika ajuan sebelumnya belum selesai                        #
    ################################################################

    def check_unfinished_submission(self, user_id):
        # import pdb;pdb.set_trace();
        myajuan = self.env['payment.requisition'].search([('responsible_id','=',user_id),
                                            ('cash_advance','=','cash_advance'),
                                            ('id','!=',self.id),
                                            ('state', 'not in', ['refuse','cancel'])],
                                             limit=10, order='id desc')
        if myajuan:
            amount = len(myajuan)
            if amount >= 1:
                for m in myajuan:
                    unfinished = self.env['uudp'].search([('ajuan_id','=',m.id),('type','=','penyelesaian'),('state','=','done')])
                    if not unfinished:
                        raise ValidationError(_("Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum penyelesaian (3)!") % (m.responsible_id.name, m.name))
        return True
    

#
# Belum selesai Lanjutin besok senin
#
    # @api.model
    # def write(self, vals, context=None):
    #     if context !=None:
    #         if 'responsible_id' in context:
    #             user_id = context['responsible_id']
    #             if self.payment_requisition_type =='cash_advance' :
    #                 self.check_unfinished_submission(user_id)
            
    #         action = 'write'
    #         payment_requisition_id = vals[0]
    #         error = False
    #         this_uudp = self.env['payment.requisition'].search([('id','=',payment_requisition_id)])

    #     return super('payment.requisition', self).write(vals)




    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id
    
    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('hr_expense.group_hr_expense_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('hr_expense.group_hr_expense_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('expense_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res

    payreq_summary = fields.Text(string="Request Summary", track_visibility='onchange')
    name = fields.Char(string="Code", default="New", readonly=True)
    fo_number = fields.Many2one(comodel_name='freight.order', string='FO Number')
    employee_id = fields.Many2one('hr.employee', string="Employee", 
                                  required=True, readonly=True, tracking=True, states={'draft': [('readonly', False)]}, 
                                  default=_default_employee_id, check_company=True, domain= lambda self: self.env['hr.expense']._get_employee_id_domain())
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env.company)
    
    currency_id = fields.Many2one('res.currency', string="Currency",
                                related='company_id.currency_id',
                                default=lambda
                                self: self.env.user.company_id.currency_id.id)

    user_id = fields.Many2one("res.users", string="Created By", default=lambda self: self.env.user, store=True, required=True, track_visibility='onchange',)
    department_id = fields.Many2one("hr.department", string="Department", track_visibility='onchange',)
    # company_id = fields.Many2one("res.company", string="Company",default=lambda self: self.env['res.company']._company_default_get(), required=True)
    responsible_id = fields.Many2one("res.users", string="Responsible", track_visibility='onchange')
    payment_requisition_type = fields.Selection([('petty_cash', 'Petty Cash'), 
                             ('cash_advance', 'Cash Advance'), 
                             ('down_payment', 'Down Payment'),
                             ('reimburse', 'Reimburse'),
                             ],string='Type', required=True, track_visibility='onchange',)
    # type = fields.Selection([('pengajuan', 'Pengajuan'), 
    #                          ('penyelesaian', 'Penyelesaian'), 
    #                          ('reimberse', 'Reimberse'),],string='Type', required=True, track_visibility='onchange',)
    
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('waiting_for_approval', 'Waiting for Approval'),
                              ('approved', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refused','Refused')], string='Status', copy=False, index=True, default='draft', readonly=True, store=True, required=True, track_visibility='onchange',)
    
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False, ondelete='set null',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", check_company=True,
        help="Analytic account to which this project, its tasks and its timesheets are linked. \n"
            "Track the costs and revenues of your project by setting this analytic account on your related documents (e.g. sales orders, invoices, purchase orders, vendor bills, expenses etc.).\n"
            "This analytic account can be changed on each task individually if necessary.\n"
            "An analytic account is required in order to use timesheets.")
    analytic_account_balance = fields.Monetary(related="analytic_account_id.balance")
    payment_requisition_ids = fields.One2many("payment.requisition.detail", inverse_name="payment_requisition_id", track_visibility='onchange')
    request_date = fields.Date(string="Request Date", required=True, default=fields.Datetime.now, track_visibility='onchange',)
    expense_date = fields.Date(string="Expense Date", required=True, default=fields.Datetime.now, track_visibility='onchange',)
    bank_id = fields.Many2one("res.bank", string="Bank", track_visibility='onchange',)
    no_rekening = fields.Char(string="Nomor Rekening", track_visibility='onchange',)
    atas_nama = fields.Char(string="Atas Nama", track_visibility='onchange',)
    # total_pencairan = fields.Float(string="Total Pencairan", track_visibility='onchange',)
    total_ajuan = fields.Monetary(string="Total Ajuan", store=True, track_visibility='onchange',)
    
    # total_ajuan = fields.Float(string="Total Ajuan", track_visibility='onchange',)
    notes = fields.Text(string="Notes", track_visibility='onchange')
    # attachment_payreq = fields.Binary(string='Attachment PayReq', track_visibility='onchange')
    attachment_ids = fields.Many2many('ir.attachment', string='Image/PDF')

    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = 'payment.requisition.pengajuan'
        vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)
        return super(PaymentRequisition, self).create(vals)
      
    # @api.multi
    def button_confirm(self):
        if self.payment_requisition_type == 'cash_advance':
            attachment = self.env['ir.attachment'].search([('res_model','=','payment.requisition'),('res_id','=',self.id)])
            if not attachment:
                raise UserError(_('Attachment masih kosong, silahkan lampirkan file / dokumen pendukung untuk melanjutkan.'))

        # self.write_state_line('waiting_for_approval')
        # self.post_mesages_uudp('Waiting for approval')
        return self.write({'state' : 'waiting_for_approval'})
    
    def action_cancel(self):
        """Cancel the record"""
        if self.state == 'draft' and self.state == 'confirm' and self.state == 'waiting_for_approval' and self.state == 'approved' and self.state == 'approved':
            self.state = 'cancel'
        else:
            raise ValidationError("You can't cancel this order")

    def action_waiting_for_approval(self):
        """ waiting_for_approval """
        if self.state == 'waiting_for_approval':
            self.state = 'approved'
        else:
            raise ValidationError("You can't cancel this order")

    def action_button_done(self):
        """ done """
        if self.state == 'approved':
            self.state = 'done'
        else:
            raise ValidationError("You can't cancel this order")
                     

class PaymentRequisitionDetail(models.Model):
    _name = "payment.requisition.detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    payment_requisition_id = fields.Many2one("payment.requisition", string="Nomor Payment Requisition", track_visibility='onchange',)
    product_id = fields.Many2one("product.product", string="Product", track_visibility='onchange',)
    # partner_id = fields.Many2one("res.partner", string="Partner", track_visibility='onchange')
    # store_id = fields.Many2one("res.partner", string="Store", track_visibility='onchange')
    description = fields.Char(string="Description", required=True, track_visibility='onchange',)
    qty = fields.Float(string="Qty", required=True, default=1, track_visibility='onchange',)
    uom = fields.Char(string="UoM", required=True, track_visibility='onchange', default="Pcs")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                related='company_id.currency_id',
                                default=lambda
                                self: self.env.user.company_id.currency_id.id)
    unit_price = fields.Monetary(string="Unit Price", required=True, default=0, track_visibility='onchange',)
    sub_total = fields.Monetary(string="Sub Total", compute="_calc_sub_total", store=True)
    total = fields.Monetary(string="Total", track_visibility='onchange', compute="_compute_total", store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting Department'),
                              ('confirm_department', 'Confirmed Department'),
                              ('confirm_department1', 'Waiting HRD'),
                              ('confirm_hrd', 'Confirmed HRD'),
                              ('pending', 'Pending'),
                              ('confirm_finance', 'Confirmed Finance'),
                              ('confirm_accounting', 'Confirmed Accounting'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled'),
                              ('refuse','Refused')], default='draft', required=True, index=True, track_visibility='onchange',)
    coa_debit = fields.Many2one('account.account', string="Account", track_visibility='onchange')


    @api.onchange('product_id')
    def _get_product_detail(self):
        product = self.product_id
        if product:
            self.description = product.name
            if not self.uom :
                self.uom = product.uom_id.name
            if self.unit_price == 0.0 :
                self.unit_price = product.lst_price
            # if not self.coa_debit :
            self.coa_debit = product.property_account_expense_id.id

    @api.depends('qty','unit_price')
    def _calc_sub_total(self):
        for i in self:
            qty = i.qty
            price = i.unit_price
            sub_total = qty * price
            i.sub_total = sub_total
            i.total = sub_total




    # @api.depends('sub_total')
    # def _compute_total(self):
    #     for rec in self:
    #         rec.total = 2.0 * rec.sub_total

    @api.model
    def create(self, vals):
        #import pdb;pdb.set_trace()
        if vals['qty'] == 0.0 or vals['unit_price'] == 0.0:
            raise ValidationError(_("Unit price tidak boleh di isi 0 !"))
        return super(PaymentRequisitionDetail, self).create(vals)
    
    @api.model
    def _create_analytic_account_from_values(self, values):
        company = self.env['res.company'].browse(values.get('company_id')) if values.get('company_id') else self.env.company
        analytic_account = self.env['account.analytic.account'].create({
            'name': values.get('name', _('Unknown Analytic Account')),
            'company_id': company.id,
            'partner_id': values.get('partner_id'),
            'plan_id': company.analytic_plan_id.id,
        })
        return analytic_account

    def _create_analytic_account(self):
        for project in self:
            analytic_account = self.env['account.analytic.account'].create({
                'name': project.name,
                'company_id': project.company_id.id,
                'partner_id': project.partner_id.id,
                'plan_id': project.company_id.analytic_plan_id.id,
                'active': True,
            })
            project.write({'analytic_account_id': analytic_account.id})