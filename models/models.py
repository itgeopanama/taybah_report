# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class taybah_report(models.Model):
#     _name = 'taybah_report.taybah_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError





# Journal Transaction Report
class account_journalcartreport(models.TransientModel):

    _name = 'account.journalcartreport'
    _description = 'Account Aged Trial balance Report'

    date_from = fields.Date(string="start date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    date_end = fields.Date(string="end date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    account_move=fields.Many2one('account.journal',"account journal")
    nid=fields.Integer(related="account_move.id")
    name=fields.Char(related="account_move.display_name")
    @api.multi
    @api.onchange('account_move')
    def product_id_change(self):
        self.nid=self.account_move.id
        self.name=self.account_move.display_name
    def print_report(self, data,context=None):
        data['form']=self.read(['nid','name','date_from','date_end'])[0]
        return self.env['report'].with_context(landscape=True).get_action(self, 'taybah_report.report_journalcartreport', data=data)

class journalcartreport(models.AbstractModel):

    _name = 'report.taybah_report.report_journalcartreport'

    def _get_partner_move_lines(self,nid, date_from, date_end,target_move):
        res = []
        totalinval = 0.0
        totaloutval = 0.0
        netval=0.0
        cr = self.env.cr

        #select records before date_from
        cr.execute("select \
                    CASE \
                      WHEN AM.payment_type='inbound'   THEN Am.Amount   ELSE 0  END  AS InVal, \
                    CASE \
                      WHEN AM.payment_type='outbound'  THEN Am.Amount  ELSE 0   END as OutVal"
                   "  FROM account_payment AM        where state ='posted' and journal_id=%s and payment_date < %s;",
                   (str(nid), date_from))
        # ,(str(nid),date_from,date_end)
        beforeleads = cr.dictfetchall()
        beforetotalinval=0.0
        beforetotaloutval=0.0
        for ld in beforeleads:
            beforetotalinval += float(ld['inval'])
            beforetotaloutval += float(ld['outval'])

        beforenetval=beforetotalinval-beforetotaloutval



        #select all record between tow date
        cr.execute("select \
             AM.payment_date,AM.payment_type,AM.Name, \
             CASE \
               WHEN AM.payment_type='inbound'   THEN Am.Amount   ELSE 0  END  AS InVal, \
             CASE \
               WHEN AM.payment_type='outbound'  THEN Am.Amount  ELSE 0   END as OutVal"
                   "  FROM account_payment AM        where state ='posted' and journal_id=%s and payment_date between %s and %s;",(str(nid),date_from,date_end))
        #,(str(nid),date_from,date_end)
        leads = cr.dictfetchall()
        for ld in leads:
            value= { }
            value['payment_date'] = ld['payment_date']
            value['payment_type'] = ld['payment_type']
            value['name'] = ld['name']
            value['inval'] = ld['inval']
            value['outval'] = ld['outval']

            totalinval += float(ld['inval'])
            totaloutval += float(ld['outval'])
            value['netval']=beforenetval+ totalinval-totaloutval
            res.append(value)

        return res,totalinval,totaloutval,beforenetval
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        date_end = data['form'].get('date_end', time.strftime('%Y-%m-%d'))
        nid = data['form'].get('nid')
        movelines,totalinval,totaloutval,beforenetval = self._get_partner_move_lines(nid, date_from, date_end,target_move)
        docargs = {
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'get_lead_lines': movelines,
            'totalinval':totalinval,
            'totaloutval':totaloutval,
            'totalnetval':beforenetval+totalinval-totaloutval,
            'beforenetval':beforenetval,
        }
        return self.env['report'].render('taybah_report.report_journalcartreport', docargs)

# Customer Tnasaction Report
class account_CutomerTransactionreport(models.TransientModel):

    _name = 'account.cutomertransactionreport'
    _description = 'Account Aged Trial balance Report'

    date_from = fields.Date(string="start date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    date_end = fields.Date(string="end date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    account_Customer=fields.Many2one('res.partner',"Customer")
    nid=fields.Integer(related="account_Customer.id")
    name=fields.Char(related="account_Customer.name")
    @api.multi
    @api.onchange('account_Customer')
    def product_id_change(self):
        self.nid=self.account_Customer.id
        self.name=self.account_Customer.name
    def print_report(self, data,context=None):
        data['form']=self.read(['nid','name','date_from','date_end'])[0]
        return self.env['report'].with_context(landscape=True).get_action(self, 'taybah_report.report_cutomertransactionreport', data=data)

class CutomerTransactionreport(models.AbstractModel):

    _name = 'report.taybah_report.report_cutomertransactionreport'

    def _get_partner_move_lines(self,nid, date_from, date_end,target_move):
        res = []
        TotInvoice = 0.0
        PaymentTo = 0.0
        PaymentFrom = 0.0
        FirstBal = 0.0
        totaldebit = 0.0
        totalcredit = 0.0
        cr = self.env.cr

        #calc FirstBal before date_from
        cr.execute("select amount_total as TotInvoice \
                    from  account_invoice \
                    where \
                     partner_id = %s and \
                     date_invoice  < %s",
                   (str(nid), date_from))
        # ,(str(nid),date_from,date_end)
        beforeleads1 = cr.dictfetchall()
        for ld in beforeleads1:
            TotInvoice += float(  (ld['totinvoice']))

        cr.execute("select amount as PaymentTo \
                    from account_payment \
                    where \
                     partner_id = %s and \
                     payment_date < %s and \
                     state = 'posted' and \
                     payment_type = 'inbound';",
                   (str(nid), date_from))
        # ,(str(nid),date_from,date_end)
        beforeleads2 = cr.dictfetchall()
        for ld in beforeleads2:
            PaymentTo += float(ld['paymentto'])

        cr.execute("select amount as PaymentFrom \
                    from account_payment \
                    where \
                     partner_id = %s and \
                     payment_date < %s and \
                     state = 'posted' and \
                     payment_type = 'outbound';",
                   (str(nid), date_from))
        # ,(str(nid),date_from,date_end)
        beforeleads3 = cr.dictfetchall()
        for ld in beforeleads3:
            PaymentFrom += float(ld['paymentfrom'])

        FirstBal = TotInvoice - PaymentTo + PaymentFrom



        #select all record between tow date
        cr.execute("select Q_Trans.* from \
                    (select \
                      date_invoice as TransDate, \
                      create_date as TransDateTime, 'Invoice' as TransType, \
                      number as TransNumber, \
                      amount_total as Debit, \
                      0 as Credit, \
                      0 as NetBal, \
                      '' as Desciption \
                    from \
                     account_invoice \
                    where \
                     partner_id = %s and \
                     date_invoice between %s and %s \
                    union \
                    select \
                      AP.payment_date as TransDate, \
                      Ap.create_date as TransDateTime, \
                      'Payment' as TransType, \
                      AP.name as TransNumber, \
                      0 as Debit, \
                      AP.amount as Credit, \
                      0 as NetBal, \
                      'Payed to ' || AJ.name as Description \
                    from \
                    account_payment AP \
                      INNER JOIN account_Journal AJ ON AJ.id = AP.journal_id \
                    where \
                     partner_id = %s and \
                     payment_date between %s and %s and \
                     state = 'posted' and \
                     payment_type = 'inbound' \
                    union \
                     select \
                      AP.payment_date as TransDate, \
                      Ap.create_date as TransDateTime, \
                      'Payment' as TransType, \
                      AP.name as TransNumber, \
                      AP.amount as Debit, \
                      0 as Credit, \
                      0 as NetBal, \
                      'Payed from ' || AJ.name as Description \
                    from \
                    account_payment AP \
                      INNER JOIN account_Journal AJ ON AJ.id = AP.journal_id \
                    where \
                     partner_id = %s and \
                     payment_date between %s and %s and \
                     state = 'posted' and \
                     payment_type = 'outbound' \
                     ) \
                 as Q_Trans \
                 Order by TransDateTime;",(str(nid),date_from,date_end,str(nid),date_from,date_end,str(nid),date_from,date_end))
        #,(str(nid),date_from,date_end)
        leads = cr.dictfetchall()
        for ld in leads:
            value= { }
            value['transdate'] = ld['transdate']
            value['transdatetime'] = ld['transdatetime']
            value['transtype'] = ld['transtype']
            value['transnumber'] = ld['transnumber']
            value['debit'] = ld['debit']
            value['credit'] = ld['credit']

            totaldebit += float(ld['debit'])
            totalcredit += float(ld['credit'])
            value['netbal']=FirstBal+ totaldebit-totalcredit
            res.append(value)

        return res,totaldebit,totalcredit,FirstBal
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        date_end = data['form'].get('date_end', time.strftime('%Y-%m-%d'))
        nid = data['form'].get('nid')
        movelines,totaldebit,totalcredit,FirstBal = self._get_partner_move_lines(nid, date_from, date_end,target_move)
        docargs = {
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'get_lead_lines': movelines,
            'totaldebit':totaldebit,
            'totalcredit':totalcredit,
            'totalnetbal':FirstBal+totaldebit-totalcredit,
            'FirstBal':FirstBal,
        }
        return self.env['report'].render('taybah_report.report_cutomertransactionreport', docargs)




class account_customerbalancereport(models.TransientModel):

    _name = 'account.customerbalancereport'
    _description = 'customer balance Report'

    date_from = fields.Date(string="select start date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    date_end = fields.Date(string="select end date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    def print_report(self, data,context=None):
        data['form']=self.read(['date_from','date_end'])[0]
        return self.env['report'].with_context(landscape=True).get_action(self, 'taybah_report.report_cbr', data=data)

class customerbalancereport(models.AbstractModel):

    _name = 'report.taybah_report.report_cbr'

    def _get_partner_move_lines(self,nid, date_from, date_end,target_move):
        res = []
        netval=0.0
        cr = self.env.cr

        #select all record between tow date
        cr.execute("select id, name, \
                                 (COALESCE(dbt_first_invoice, 0) + COALESCE(dbt_payment_first, 0) - COALESCE(crd_payment_first, 0)) first_bal, \
                                 (COALESCE(dbt_invoice, 0) + COALESCE(dbt_payment, 0)) dbt, \
                                 (COALESCE(crd_Payment, 0)) crd, \
                                 (COALESCE(dbt_first_invoice, 0) + COALESCE(dbt_payment_first, 0) - COALESCE(crd_payment_first, 0) + COALESCE(dbt_invoice, 0) + COALESCE(dbt_payment, 0)  - COALESCE(crd_Payment, 0)) Net \
                                  from \
                                ( \
                                select RP.id, RP.name, (select sum(amount_total) from account_invoice AI \
                                  where AI.partner_id = RP.id \
                                  and AI.date_invoice < %s \
                                  and state <> 'draft') as dbt_first_invoice, \
                                 (select sum(amount) from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date < %s and payment_type = 'outbound' and state = 'posted') as dbt_Payment_first, (select sum(amount)  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date < %s and payment_type = 'inbound' and state = 'posted') as crd_Payment_first, \
                                 (select sum(amount_total) \
                                  from account_invoice AI \
                                  where AI.partner_id = RP.id \
                                  and AI.date_invoice between %s and %s and state <> 'draft') as dbt_invoice, \
                                  (select sum(amount) \
                                  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date between %s and %s and payment_type = 'outbound' and state = 'posted') as dbt_Payment, \
                                  (select sum(amount) \
                                  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date between %s and %s and payment_type = 'inbound' \
                                  and state = 'posted') as crd_Payment \
                                 from res_partner RP \
                                 where customer = true \
                                 and active = true \
                                 )as Q_Bal \
                                 order by id;"
                            ,(date_from,date_from,date_from,date_from,date_end,date_from,date_end,date_from,date_end))
        #,(str(nid),date_from,date_end)
        leads = cr.dictfetchall()
        for ld in leads:
            value= { }
            value['id'] = ld['id']
            value['name'] = ld['name']
            value['first_bal'] = ld['first_bal']
            value['dbt'] = ld['dbt']
            value['crd'] = ld['crd']
            value['net'] = ld['net']
            netval += float(ld['net'])
            res.append(value)

        return res,netval
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        date_end = data['form'].get('date_end', time.strftime('%Y-%m-%d'))
        nid = data['form'].get('nid')
        movelines,netval = self._get_partner_move_lines(nid, date_from, date_end,target_move)
        docargs = {
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'get_lead_lines': movelines,
            'netval':netval,
        }
        return self.env['report'].render('taybah_report.report_cbr', docargs)

#vendor balance report
class account_vendorbalancereport(models.TransientModel):

    _name = 'account.vendorbalancereport'
    _description = 'vendor balance Report'

    date_from = fields.Date(string="select start date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    date_end = fields.Date(string="select end date", required=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    def print_report(self, data,context=None):
        data['form']=self.read(['date_from','date_end'])[0]
        return self.env['report'].with_context(landscape=True).get_action(self, 'taybah_report.report_vbr', data=data)

class vendorbalancereport(models.AbstractModel):

    _name = 'report.taybah_report.report_vbr'

    def _get_partner_move_lines(self,nid, date_from, date_end,target_move):
        res = []
        netval=0.0
        cr = self.env.cr

        #select all record between tow date
        cr.execute("select id, name, \
                                 (COALESCE(crd_first_invoice, 0) + COALESCE(crd_payment_first, 0) - COALESCE(dbt_payment_first, 0)) first_bal, \
                                 (COALESCE(dbt_Payment, 0)) dbt, \
                                 (COALESCE(crd_invoice, 0) + COALESCE(crd_payment, 0)) crd, \
                                 (COALESCE(crd_first_invoice, 0) + COALESCE(crd_payment_first, 0) - COALESCE(dbt_payment_first, 0) + COALESCE(crd_invoice, 0) + COALESCE(crd_payment, 0)  - COALESCE(dbt_Payment, 0)) Net \
                                  from ( select RP.id, RP.name, (select sum(amount_total) from account_invoice AI \
                                  where AI.partner_id = RP.id \
                                  and AI.date_invoice < %s \
                                  and state <> 'draft') as crd_first_invoice, \
                                 (select sum(amount) \
                                  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date < %s and payment_type = 'outbound' \
                                  and state = 'posted') as dbt_Payment_first, \
                                  (select sum(amount) \
                                  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date < %s and payment_type = 'inbound' and state = 'posted') as crd_Payment_first, \
                                 (select sum(amount_total) \
                                  from account_invoice AI \
                                  where AI.partner_id = RP.id \
                                  and AI.date_invoice between %s and %s and state <> 'draft') as crd_invoice, \
                                  (select sum(amount) \
                                  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date between %s and %s and payment_type = 'outbound' and state = 'posted') as dbt_Payment, \
                                  (select sum(amount) \
                                  from account_payment AP \
                                  where AP.partner_id = RP.id \
                                  and AP.payment_date between %s and %s and payment_type = 'inbound' and state = 'posted') as crd_Payment \
                                 from res_partner RP \
                                 where supplier = true \
                                 and active = true \
                                 )as Q_Bal \
                                 order by id;"
                            ,(date_from,date_from,date_from,date_from,date_end,date_from,date_end,date_from,date_end))
        #,(str(nid),date_from,date_end)
        leads = cr.dictfetchall()
        for ld in leads:
            value= { }
            value['id'] = ld['id']
            value['name'] = ld['name']
            value['first_bal'] = ld['first_bal']
            value['dbt'] = ld['dbt']
            value['crd'] = ld['crd']
            value['net'] = ld['net']
            netval += float(ld['net'])
            res.append(value)

        return res,netval
    def render_html(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        total = []
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        target_move = data['form'].get('target_move', 'all')
        date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        date_end = data['form'].get('date_end', time.strftime('%Y-%m-%d'))
        nid = data['form'].get('nid')
        movelines,netval = self._get_partner_move_lines(nid, date_from, date_end,target_move)
        docargs = {
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'get_lead_lines': movelines,
            'netval':netval,
        }
        return self.env['report'].render('taybah_report.report_vbr', docargs)

