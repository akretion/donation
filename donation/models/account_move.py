# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = ["account.move"]

    donation_ids = fields.One2many(
        "donation.donation",
        "move_id",
        string="Donations",
        store=True,
    )

    @api.constrains('state')
    def _check_with_tax_receipt(self):
        moves_with_tax_receipt = []
        for move in self.filtered(lambda m: m.state in ['cancel', 'draft']):
            donations_with_receipt = move.donation_ids.filtered(lambda d: d.tax_receipt_id)
            if donations_with_receipt:
                moves_with_tax_receipt.append({
                    'move_name': move.name,
                    'donations': donations_with_receipt
                })
        if moves_with_tax_receipt:
            message_lines = []
            for item in moves_with_tax_receipt:
                move_name = item['move_name']
                donations = item['donations']
                donation_lines = "\n".join(
                    f"- {d.number} ({d.tax_receipt_id.display_name})"
                    for d in donations
                )
                message_lines.append(_(f"Move '{move_name}' has donations with tax receipts:\n{donation_lines}"))
            raise UserError("\n\n".join(message_lines))