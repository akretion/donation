# Copyright 2014-2021 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_donation = fields.Boolean(
        string="Is a donation",
        tracking=True,
        readonly=False,
        store=True,
        help="Specify if the product is a donation",
    )
    in_kind = fields.Boolean(
        string="Is an in-kind donation",
        tracking=True,
        compute="_compute_is_inkind",
        readonly=False,
        store=True,
        precompute=True,
        help="Specify if the donation item is of type in-kind (a good or a service rather than a monetary donation)"
    )
    tax_receipt_ok = fields.Boolean(
        string="Is Eligible for a Tax Receipt",
        tracking=True,
        compute="_compute_tax_receipt_ok",
        readonly=False,
        store=True,
        precompute=True,
        help="Specify if the donation item is eligible for a tax receipt",
    )

    @api.depends("is_donation")
    def _compute_is_inkind(self):
        for product in self:
            if not product.is_donation:
                product.in_kind = False
            elif product.type in ["consu", "combo"]:
                product.in_kind = True

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
                product.sale_ok = False
                if "can_be_expensed" in product._fields:
                    product.can_be_expensed = False
                    
    @api.constrains("type", "in_kind")
    def inkind_check(self):
        for product in self:
            if product.type in ["consu", "combo"] and product.in_kind == False:
                raise ValidationError(
                    _(
                        "A donation product of type '%s' "
                        "is always an in-kind donation"
                    )
                    % product.type
                )
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
                product.sale_ok = False
                if "can_be_expensed" in product._fields:
                    product.can_be_expensed = False