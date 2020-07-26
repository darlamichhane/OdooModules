<label string="Refund" attrs="{'invisible': ['|',('state','in',('draft','proforma','proforma2')), '|', ('type','&lt;&gt;','out_refund'),('has_refund','=',False)]}"/>
<label string="Draft Refund" attrs="{'invisible': ['|',('state','not in',('draft',)),'&amp;', ('type','&lt;&gt;','out_refund'),('has_refund','=',True)]}"/>



for report

<t t-if="o.is_downpayment_receipt == True">
                <t t-call="downpayment_receipt.receipt_report_sale" t-lang="o.partner_id.lang"/>
            </t>
            <t t-if="o.is_downpayment_receipt == False">
                <t t-call="account.report_invoice_document" t-lang="o.partner_id.lang"/>
            </t>