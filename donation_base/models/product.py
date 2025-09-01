# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_donation = fields.Selection(
        selection=[
            ("donation", "Donation"),
            ("donation_in_kind_service", "In-Kind Donation Service"),
        ],
        string="Is a donation",
        readonly=False,
        help="Specify if the product is a donation",
    )
    tax_receipt_ok = fields.Boolean(
        string="Is Eligible for a Tax Receipt",
        tracking=True,
        compute="_compute_tax_receipt_ok",
        readonly=False,
        store=True,
        precompute=True,
        help="Specify if the product is eligible for a tax receipt",
    )

    @api.depends("is_donation")
    def _compute_tax_receipt_ok(self):
        for product in self:
            if not product.is_donation:
                product.tax_receipt_ok = False

    @api.onchange("is_donation")
    def _donation_change(self):
        for product in self:
            if product.is_donation:
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False

    @api.constrains("is_donation", "taxes_id")
    def donation_check(self):
        for product in self:
            # The check below is to make sure that we don't forget to remove
            # the default sale VAT tax on the donation product, particularly
            # for users of donation_sale. If there are countries that have
            # sale tax on donations (!), please tell us and we can remove this
            # constraint
            if product.is_donation and product.taxes_id:
                raise ValidationError(
                    _(
                        "There shouldn't have any Customer Taxes on the "
                        "donation product '%s'."
                    )
                    % product.display_name
                )


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.onchange("is_donation")
    def _donation_change(self):
        for product in self:
            if product.is_donation:
                product.taxes_id = False
                product.supplier_taxes_id = False
                product.purchase_ok = False
