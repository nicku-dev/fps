from odoo import api, fields, models, exceptions, _
from datetime import datetime
from odoo.exceptions import UserError, AccessError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class UUDP(models.Model):
    _inherit = "uudp"

    @api.multi
    def calculate_total_pencairan(self):
        for rec in self :
            total_pencairan = 0.0
            if rec.child_ids :
                for det in rec.child_ids :
                    if det.state == 'done' :
                        total_pencairan += det.total_pencairan
            else :
                if rec.pencairan_id :
                    total_pencairan = rec.total_ajuan
            rec.total_pencairan = total_pencairan
            
    @api.model
    def create(self, vals):
        res = super(UUDP, self).create(vals)
        if 'uudp_parent_id' in vals :
            child_exist = self.env['uudp'].sudo().search([('uudp_parent_id','=',vals['uudp_parent_id'])])
            if child_exist :
                seq = len(child_exist)
            else :
                seq = 1
            res.name = child_exist[0].uudp_parent_id.name +'-'+ str(seq) 
        return res

    uudp_parent_id = fields.Many2one("uudp", string="Parent")
    child_ids = fields.One2many('uudp','uudp_parent_id',string = 'Child', compute="get_child_ids")

    def check_unfinished_submission(self, user_id):
        #res = super(UUDP, self).check_unfinished_submission(user_id)
        myajuan = self.env['uudp'].sudo().search([('responsible_id','=',user_id),
                                            ('type','=','pengajuan'),
                                            ('id','!=',self.id),
                                            ('state', 'not in', ['refuse','cancel']),
                                            ('uudp_parent_id','=',False)],
                                             limit=10, order='id desc')
        if myajuan:
            for m in myajuan:
                if self.uudp_parent_id and self.uudp_parent_id == m.id:
                    continue
                unfinished = self.env['uudp'].sudo().search([('ajuan_id','=',m.id),('type','=','penyelesaian'),('state','=','done')])
                if not unfinished:
                    raise ValidationError(_("Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum penyelesaian (1)!") % (m.responsible_id.name, m.name))

        user = self.env['res.users']
        myajuan2 = self.env['uudp'].sudo().search([('responsible_id', '=', user_id),
                                            ('type', '=', 'pengajuan'),
                                            ('id', '!=', self.id),
                                            ('state', '=', 'done'),
                                            ('penyelesaian_id', '=', False),
                                            ('uudp_parent_id','=',False)],
                                           limit=1, order='id desc')
        if myajuan2:
            if myajuan2.penyelesaian_id :
                raise ValidationError(_(
                    "Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum penyelesaian !") % (
                                      user.browse(user_id).name, myajuan2.name))
            elif myajuan2.penyelesaian_id.state != 'done':
                raise ValidationError(_(
                    "Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan (%s) penyelesaiannya (%s) belum berstatus 'Done' (2)!") % (
                                      user.browse(user_id).name, myajuan2.name, myajuan2.penyelesaian_id.name))

        return True


    @api.depends('uudp_ids','uudp_parent_id')
    def get_child_ids(self):
        for rec in self:
            child_exist = self.env['uudp'].sudo().search([('uudp_parent_id','=',rec.id)])
            if child_exist :
                rec.child_ids = child_exist.ids

    @api.multi
    def button_done_finance(self):
        res = super(UUDP, self).button_done_finance() 
        if self.type == 'penyelesaian' and self.ajuan_id.child_ids:
            for ch in self.ajuan_id.child_ids :
                ch.write_state_line('done')
                ch.write({'selesai':True, 'penyelesaian_id' : self.id, 'tgl_penyelesaian' : self.date})
                ch.post_mesages_uudp('Done')


    @api.multi
    def button_set_to_draft(self):
        res = super(UUDP, self).button_set_to_draft() 
        if self.type == 'pengajuan' :
            myajuan = self.env['uudp'].sudo().search([('responsible_id','=',self.responsible_id.id),
                                                ('type','=','pengajuan'),
                                                ('id','!=',self.id),
                                                ('uudp_parent_id','=',False),
                                                ('state', 'not in', ['refuse','cancel','done'])],
                                                 limit=10, order='id desc')
            if myajuan:
                amount = len(myajuan)
                if amount >= 1:
                    for m in myajuan:
                        unfinished = self.env['uudp'].sudo().search([('ajuan_id','=',m.id),('type','=','penyelesaian'),('uudp_parent_id','=',False)])
                        if not unfinished:
                            raise ValidationError(_("Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum penyelesaian !") % (m.responsible_id.name, m.name))
        return res

    @api.multi
    def button_confirm(self):
        res = super(UUDP, self).button_confirm()
        if self.type == 'pengajuan':
            myajuan = self.env['uudp'].sudo().search([('responsible_id', '=', self.responsible_id.id),
                                               ('type', '=', 'pengajuan'),
                                               ('id', '!=', self.id),
                                               ('uudp_parent_id', '=', False),
                                               ('state', 'not in', ['refuse', 'cancel','done'])],
                                              limit=1, order='id desc')
            if myajuan:
                raise ValidationError(_(
                    "Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum diproses !") % (
                                      self.responsible_id.name, myajuan.name))

            myajuan_done = self.env['uudp'].sudo().search([('responsible_id', '=', self.responsible_id.id),
                                               ('type', '=', 'pengajuan'),
                                               ('id', '!=', self.id),
                                               ('uudp_parent_id', '=', False),
                                               ('state', '=', 'done'),
                                                ('penyelesaian_id', '=', False)],
                                              limit=1, order='id desc')
            if myajuan_done:

                raise ValidationError(_(
                    "Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) belum penyelesaian !") % (
                                      self.responsible_id.name, myajuan_done.name))

            myajuan_done2 = self.env['uudp'].sudo().search([('responsible_id', '=', self.responsible_id.id),
                                                    ('type', '=', 'pengajuan'),
                                                    ('id', '!=', self.id),
                                                    ('uudp_parent_id', '=', False),
                                                    ('state', '=', 'done'),
                                                    ('penyelesaian_id', '!=', False),
                                                     ('penyelesaian_id.state', '!=', 'done')],
                                                   limit=1, order='id desc')
            if myajuan_done2:
                if myajuan_done2.penyelesaian_id.state != 'done':
                    raise ValidationError(_(
                        "Anda tidak bisa membuat pengajuan untuk penerima yg sama (%s), ketika ajuan sebelumnya (%s) sudah penyelesaian (%s) tetapi penyelesaian tersebut belum di proses !") % (
                                      self.responsible_id.name,myajuan_done2.name, myajuan_done2.penyelesaian_id.name))

            return res


    @api.multi
    def alert_uudp_penyelesaian(self, *args):
        res = super(UUDP, self).alert_uudp_penyelesaian()
        uudp = self.env['uudp']
        now = datetime.datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        uudp_pending = uudp.sudo().search([('type','=','pengajuan'),
                                    ('penyelesaian_id','=',False),
                                    ('end_date','<',today_date),
                                    ('state','=','done'),
                                    ('uudp_parent_id','=',False)])
        for ajuan in uudp_pending :
            body_html = '<p>Assalamualaikum '+str(ajuan.user_id.name)+',</p> \n'+'<p>Ajuan '+ajuan.name+' belum ada penyelesaian, silahkan segera buat penyelesaian dengan klik tombol dibawah</p>'+'<br><a href="https://shaferp.shafco.co.id/web?#view_type=form&amp;model=uudp&amp;menu_id=537&amp;action=641" class="btn btn-primary" target="_blank" data-original-title="" title="">Saya ingin buat penyelesaian</a>&nbsp;<p></p>'         
            # create notifikasi ke email
            mail        = self.env['mail.mail']
            notif_mail  = mail.create({'subject'    : 'Ajuan '+str(ajuan.name)+' Belum Penyelesaian',
                                    'email_from'    : ajuan.company_id.email,
                                    'email_to'      : ajuan.user_id.partner_id.email,
                                    #'email_cc'      : ajuan.responsible_id.partner_id.email,
                                    'auto_delete'   : True,
                                    'message_type'  : 'notification',
                                    'recipient_ids' : [(6, 0, [ajuan.user_id.partner_id.id,ajuan.responsible_id.partner_id.id])],
                                    'notification'  : True,
                                    'body_html'     : body_html,
                                    })
            _logger.info("created ajuan penyelesaian alert to %s" % (ajuan.user_id.partner_id.email) )
        return res

    @api.multi
    def button_validate(self):
        if self.state != 'confirm_accounting' or not self.pencairan_id:
            raise AccessError(_('Ajuan %s belum confirm accounting atau belum dijadwalkan pencairan!') % (self.name))
        if self.pencairan_id :
            self.write({'total_pencairan' : self.total_ajuan})
        if self.type == 'pengajuan' :
            myajuan = self.env['uudp'].sudo().search([('responsible_id','=',self.responsible_id.id),
                                                ('type','=','pengajuan'),
                                                ('id','!=',self.id),
                                                ('uudp_parent_id','=',False),
                                                ('state', 'not in', ['refuse','cancel','done'])],
                                                order='id desc')
            if myajuan:
                amount = len(myajuan)
                if amount >= 1:
                    for m in myajuan:
                        if m.uudp_parent_id :
                            raise UserError(_('Ajuan sebelumnya (%s) belum ada pencairan !') % (m.name))
                        if self.uudp_parent_id :
                            if m.id == self.uudp_parent_id.id :
                                continue
                        m.button_cancel()
                        m.sudo().message_post(body=_('Cancel otomatis dari sistem karena terindikasi melalukan pengajuan ketika ajuan sebelumnya (%s) belum penyelesaian.') % (self.name,))
        return super(UUDP, self).button_validate()

    @api.multi
    def button_clearing_link_pencairan(self):
        # warning = {
        #     'title': (_('Information')),
        #     'message': (_('Clearing failed...'))
        # }
        self.ensure_one()
        if not self.pencairan_id.uudp_ids.filtered(lambda cl:cl.id == self.id) :
            self.write({'state':'confirm_finance',
                        'pencairan_id': False,
                        'tgl_Pencairan': False,
                        'type_pencairan': False})
            # warning ga muncul
            # warning = {
            #     'title': (_('Information')),
            #     'message': (_('Clearing success...'))
            # }
            # return {'warning': warning}
            self._cr.commit()
            raise ValidationError(_('Remove link pencairan success.....'))
        else :
            raise ValidationError(_('Remove link pencairan failed.....'))

UUDP()


class UUDPPencairan(models.Model):
    _inherit = "uudp.pencairan"

    @api.multi
    def button_force_cancel(self):
        res = super(UUDPPencairan, self).button_force_cancel()
        for ch in self.child_ids.filtered(lambda x : x.state == 'cancel') :
            ch.write({'state':'confirm_parsial'})
            for j in ch.uudp_ids.filtered(lambda i : i.state == 'cancel') :
                j.write({'state':'confirm_accounting'})
        return res

    pencairan_id = fields.Many2one("uudp.pencairan", string="Parent")
    total_pencairan = fields.Float(string="Total Pencairan", compute="get_total_pencairan")
    child_ids = fields.One2many('uudp.pencairan','pencairan_id',string = 'Child', compute="get_total_pencairan")

    @api.model
    def create(self, vals):
        res = super(UUDPPencairan, self).create(vals)
        if 'pencairan_id' in vals :
            child_exist = self.env['uudp.pencairan'].sudo().search([('pencairan_id','=',vals['pencairan_id'])])
            if child_exist :
                seq = len(child_exist)
            else :
                seq = 1
            res.name = child_exist[0].pencairan_id.name +'-'+ str(seq) 
        return res

    @api.depends('uudp_ids.state','journal_entry_ids.state')
    def get_total_pencairan(self):
        for rec in self:
            total = 0
            # for u in rec.journal_entry_ids:
            #     for l in u.line_ids:
            #         total += l.credit           
            if rec.type == 'once':
                for u in rec.uudp_ids:
                    total += u.total_ajuan
            #     rec.total_pencairan = total
            # elif rec.type == 'parsial':
            #     uudp_obj = self.env['uudp.pencairan']
            #     uudps = uudp_obj.search([('pencairan_id','=',rec.id),('state','not in',('cancel','refuse'))])
            #     for uu in uudps : 
            #         total += sum(uu.ajuan_id.uudp_ids.mapped('sub_total'))
            else :
                child_exist = self.env['uudp.pencairan'].sudo().search([('pencairan_id','=',rec.id)])
                if child_exist :
                    rec.child_ids = child_exist.ids
                    for x in child_exist :
                        if x.state == 'done' :
                            total += x.total_pencairan
            rec.total_pencairan = total
            if rec.ajuan_id :
                rec.ajuan_id.total_pencairan = total

            # utk data/konsep lama
            if total == 0.0 :
                if rec.journal_entry_ids:
                    for u in rec.journal_entry_ids:
                        for l in u.line_ids:
                            total += l.credit
                    rec.total_pencairan = total


    @api.multi
    def button_done_once(self):
        res = super(UUDPPencairan, self).button_done_once()
        uudp_obj = self.env['uudp.pencairan']
        for rec in self:
            if rec.pencairan_id.state == 'confirm_parsial' :
                if rec.pencairan_id.total_pencairan > rec.pencairan_id.nominal_ajuan :
                    raise UserError(_('Total pencairan ini melebihi total pencairan parsial induknya (%s) !')%(rec.pencairan_id.name))
                elif rec.pencairan_id.total_pencairan == rec.pencairan_id.nominal_ajuan :
                    rec.pencairan_id.write({'state':'done'})
                    rec.pencairan_id.ajuan_id.write({'state':'done'})

    @api.multi
    def button_done_parsial(self):
        for rec in self :
            if rec.child_ids :
                total_pencairan = 0.0
                #import pdb;pdb.set_trace()
                for det in rec.child_ids :
                    if det.state == 'confirm_once' :
                        det.button_done_once()
                        total_pencairan += det.total_pencairan
                    elif det.state == 'done' :
                        for aj in det.uudp_ids :
                            if aj.uudp_parent_id and aj.uudp_parent_id.id == rec.ajuan_id.id:
                                total_pencairan += aj.total_pencairan

                rec.ajuan_id.total_pencairan = total_pencairan
        return super(UUDPPencairan, self).button_done_parsial()

UUDPPencairan()