import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, RedirectWarning, UserError
import xlsxwriter, base64, pytz, string, re
from cStringIO import StringIO
from datetime import date, datetime, time, timedelta
from pytz import timezone
from string import ascii_uppercase
import itertools
import xlwt


class VitUUDPReport(models.TransientModel):
    _name = "vit.uudp.report"
    _description = "UUDP Report"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
    
    @api.onchange('department_ids','company_ids')
    def onchange_department_ids(self):
        return {'domain':{'department_ids':[('company_id','in',self.company_ids.ids)]}}

    state_x = fields.Selection([('choose','choose'),('get','get')], default='choose')
    data_x = fields.Binary('File', readonly=True)
    name = fields.Char('Filename', readonly=True)
    start_date = fields.Date('Date Start',
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    end_date = fields.Date('End Date', default=fields.Datetime.now())
    company_ids = fields.Many2many("res.company", string="Company", default=lambda self: self.env['res.company']._company_default_get(), required=True)
    department_ids = fields.Many2many("hr.department", string="Department")
    responsible_ids = fields.Many2many("res.users", string="Responsible")
    employee_ids = fields.Many2many("res.users", string="Employee")


    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
            'grey': '#808080',
            'silver': '#C0C0C0',
        }

        wbf = {}

        wbf['header1'] = workbook.add_format({'bold': 1,'align': 'center','font_color': '#000000'})
        wbf['header1'].set_border()
        wbf['header1'].set_align('vcenter')

        wbf['header2'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#C0C0C0', 'font_color': '#000000'})
        wbf['header2'].set_border()

        wbf['header_no'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')

        wbf['footer'] = workbook.add_format({'align': 'left'})

        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()

        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()

        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()

        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()

        wbf['company'] = workbook.add_format({'align': 'left'})
        wbf['company'].set_font_size(11)

        wbf['total_float'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'right', 'num_format': '#,##0.00'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()

        wbf['total'] = workbook.add_format({'bold': 1, 'bg_color': colors['white_orange'], 'align': 'left'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_yellow'] = workbook.add_format({'bold': 1, 'bg_color': colors['yellow'], 'align': 'center'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2','num_format': '#,##0.00'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()
        return wbf, workbook
  

    def print_excel_report(self):
        uudp = self.env['uudp']
        start_date = self.start_date
        end_date = self.end_date
        company_ids = self.company_ids
        department_ids = self.department_ids
        responsible_ids = self.responsible_ids
        employee_ids = self.employee_ids

        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)
        datetime_string = self.get_default_date_model().strftime("%Y-%m-%d %H:%M:%S")
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        if start_date :
            date_string = start_date+' to '+date_string
        filename = 'UUDP Report (%s).xlsx' % (date_string)
        sheet_names = []

        sheet_name = 'UUDP %s'%(type)

        sheet_names.append(sheet_name)
        #WKS 1
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.set_column('A1:A1', 5)
        worksheet.set_column('B1:B1', 20)
        worksheet.set_column('C1:C1', 20)
        worksheet.set_column('D1:D1', 20)
        worksheet.set_column('E1:E1', 20)
        worksheet.set_column('F1:F1', 20)
        worksheet.set_column('G1:G1', 20)
        worksheet.set_column('H1:H1', 60)
        worksheet.set_column('I1:I1', 20)
        worksheet.set_column('J1:J1', 20)
        worksheet.set_column('K1:K1', 20)
        worksheet.set_column('L1:L1', 20)
        worksheet.set_column('M1:M1', 20)
        worksheet.set_column('N1:N1', 20)
        worksheet.set_column('O1:O1', 20)
        worksheet.set_column('P1:P1', 20)
        worksheet.set_column('Q1:Q1', 20)

        #WKS 1
        worksheet.merge_range('A1:Q1', 'SHAFIRA CORPORATION', wbf['header1'])
        worksheet.merge_range('A2:Q2', 'LAPORAN UUPD', wbf['header1'])
        if start_date :
            periode = start_date+' to '+ end_date
        else :
            periode = end_date
        worksheet.merge_range('A3:Q3', 'Per %s'%(periode), wbf['header1'])

        row=5

        worksheet.write('A%s' %(row), 'No', wbf['header2'])
        worksheet.write('B%s' %(row), 'No Ajuan', wbf['header2'])
        worksheet.write('C%s' %(row), 'Pengaju', wbf['header2'])
        worksheet.write('D%s' %(row), 'Responsible', wbf['header2'])
        worksheet.write('E%s' %(row), 'Department', wbf['header2'])
        worksheet.write('F%s' %(row), 'Company', wbf['header2'])
        worksheet.write('G%s' %(row), 'Keterangan', wbf['header2'])
        worksheet.write('H%s' %(row), 'Start Date', wbf['header2'])
        worksheet.write('I%s' %(row), 'End Date', wbf['header2'])
        worksheet.write('J%s' %(row), 'Total Ajuan', wbf['header2'])
        worksheet.write('K%s' %(row), 'Total Pencairan', wbf['header2'])
        worksheet.write('L%s' %(row), 'Tanggal Pencairan', wbf['header2'])
        worksheet.write('M%s' %(row), 'No Pencairan', wbf['header2'])
        worksheet.write('N%s' %(row), 'No Laporan UUDP', wbf['header2'])
        worksheet.write('O%s' %(row), 'Tanggal Laporan', wbf['header2'])
        worksheet.write('P%s' %(row), 'Total Realisasi', wbf['header2'])
        worksheet.write('Q%s' %(row), 'Sisa UUDP', wbf['header2'])

        dtstart = datetime.strptime(end_date,'%Y-%m-%d')
        where_dept_exist = """ """
        if department_ids :
            where_dept_exist= """
                and department_id in %s
            """ % (str(tuple(department_ids.ids)).replace(',)', ')'))

        where_resp_exist = """ """
        if responsible_ids :
            where_resp_exist= """
                and responsible_id in %s 
            """ % (str(tuple(responsible_ids.ids)).replace(',)', ')'))

        where_emp_exist = """ """
        if employee_ids :
            where_emp_exist= """
                and user_id in %s  
            """ % (str(tuple(employee_ids.ids)).replace(',)', ')'))

        sql = """
                select id from uudp
                where state = 'done' and type = 'pengajuan' and company_id in %s
                and date between '%s' and '%s' 
            """ % ((str(tuple(company_ids.ids)).replace(',)', ')')),start_date,end_date,)
        orderby = """ order by date  """  
        sql_statement = sql+where_dept_exist+where_resp_exist+where_resp_exist+orderby
        self._cr.execute(sql_statement)
        result = self._cr.fetchall()
        if result :
            no = 0
            for u in result:
                row+=1
                no+=1
                uudp_id = uudp.browse(u[0])
                worksheet.write('A%s' % row, no, wbf['content'])
                worksheet.write('B%s' % row, uudp_id.name, wbf['content'])
                worksheet.write('C%s' % row, uudp_id.user_id.name, wbf['content'])
                worksheet.write('D%s' % row, uudp_id.responsible_id.name, wbf['content'])
                worksheet.write('E%s' % row, uudp_id.department_id.name, wbf['content'])
                worksheet.write('F%s' % row, uudp_id.company_id.name, wbf['content_float'])
                worksheet.write('G%s' % row, uudp_id.notes, wbf['content_float'])
                worksheet.write('H%s' % row, uudp_id.date, wbf['content'])
                worksheet.write('I%s' % row, uudp_id.end_date, wbf['content'])
                worksheet.write('J%s' % row, uudp_id.total_ajuan, wbf['content_float'])
                worksheet.write('K%s' % row, uudp_id.total_pencairan, wbf['content_float'])
                worksheet.write('L%s' % row, uudp_id.tgl_pencairan, wbf['content'])
                worksheet.write('M%s' % row, uudp_id.pencairan_id.name, wbf['content'])
                worksheet.write('N%s' % row, uudp_id.penyelesaian_id.name, wbf['content'])
                worksheet.write('O%s' % row, uudp_id.tgl_penyelesaian, wbf['content'])
                worksheet.write('P%s' % row, uudp_id.total_pencairan, wbf['content_float'])
                worksheet.write('Q%s' % row, sum(uudp_id.uudp_ids.mapped('sub_total'))-uudp_id.total_pencairan, wbf['content_float'])


        #worksheet.merge_range('A%s:F%s' % (row,row), '', wbf['header_detail'])
        #worksheet.write_formula('G%s'%(row), '{=subtotal(9,G%s:G%s)}' % (first_row_payment, row-1), wbf['header_detail'])

        worksheet.write('A%s'%(row+2), '%s %s'%(datetime_string, self.env.user.name), wbf['footer'])

        workbook.close()
        out=base64.encodestring(fp.getvalue())
        self.write({'state_x':'get', 'data_x':out, 'name':filename})
        fp.close()
        
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference('vit_uudp_report', 'vit_uudp_report_form_view')
        
        form_id = form_res and form_res[1] or False
        return {
            'name': 'Download .xlsx',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'vit.uudp.report',
            'res_id': self.id,
            'view_id': False,
            'views': [(form_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
        
VitUUDPReport()