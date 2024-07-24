from odoo import fields, api, models

class AccountMove(models.Model):
	_inherit = 'account.move'

	@api.multi
	def post(self):
		res = super(AccountMove, self).post()
		for me_id in self :
			for line in me_id.line_ids :
				if line.journal_interco_id :
					line.create_move_interco()
		return res

	@api.multi
	def button_cancel(self):
		res = super(AccountMove, self).button_cancel()
		for me_id in self :
			for line in me_id.line_ids :
				if line.move_interco_id :
					line.move_interco_id.button_cancel()
					line.move_interco_id.unlink()
		return res

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	journal_interco_id = fields.Many2one('account.journal', string='Journal Interco', index=True)
	move_interco_id = fields.Many2one('account.move', string='Journal Entry Interco', index=True, copy=False)

	@api.onchange('account_id','journal_interco_id')
	def account_change(self):
		domain = {}
		if self.account_id :
			journal_interco_ids = self.env['account.journal'].search([
				('interco_journal','=',True),
				('company_id','!=',self.company_id.id),
				'|',
				('account_interco_debit_id.code','=',self.account_id.code),
				('account_interco_credit_id.code','=',self.account_id.code),
			])
			domain['journal_interco_id'] = [('id','in',journal_interco_ids.ids)]
		return {'domain':domain}

	@api.multi
	def create_move_interco(self):
		self.ensure_one()
		move_line_vals = []
		if self.debit > 0 :
			debit_account_id = self.journal_interco_id.default_debit_account_id
			credit_account_id = self.journal_interco_id.account_interco_credit_id
		else :
			debit_account_id = self.journal_interco_id.account_interco_debit_id
			credit_account_id = self.journal_interco_id.default_credit_account_id
		move_line_vals.append((0, 0, {
			'account_id' : debit_account_id.id,
			'partner_id' : self.partner_id.id,
			'analytic_tag_ids' : [(6, 0, [tag.id for tag in self.analytic_tag_ids])],
			'name' : self.name,
			'ref' : self.ref,
			'analytic_account_id' : self.analytic_account_id.id,
			'debit' : self.debit or self.credit,
			'credit': 0,
			'date_maturity' : self.date_maturity,
		}))

		move_line_vals.append((0, 0, {
			'account_id' : credit_account_id.id,
			'partner_id' : self.partner_id.id,
			'analytic_tag_ids' : [(6, 0, [tag.id for tag in self.analytic_tag_ids])],
			'name' : self.name,
			'ref' : self.ref,
			'analytic_account_id' : self.analytic_account_id.id,
			'debit' : 0,
			'credit': self.debit or self.credit,
			'date_maturity' : self.date_maturity,
		}))

		move_id = self.env['account.move'].create({
			"partner_id": self.partner_id.id,
			"journal_id": self.journal_interco_id.id,
			"ref": self.move_id.ref,
			"date": self.date,
			"narration": self.move_id.name,
			"line_ids": move_line_vals,
			})
		move_id.post()
		self.move_interco_id = move_id.id
