# ©  2023 Deltatech
# See README.rst file on addons root folder for license details

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BusinessProcessTest(models.Model):
    _name = "business.process.test"
    _description = "Business process Test"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", required=True, readonly=False, states={"done": [("readonly", True)]})
    process_id = fields.Many2one(
        string="Process", comodel_name="business.process", required=True, states={"done": [("readonly", True)]}
    )
    area_id = fields.Many2one(string="Area", comodel_name="business.area", related="process_id.area_id", store=True)
    tester_id = fields.Many2one(
        string="Tester",
        comodel_name="res.partner",
        domain="[('is_company', '=', False)]",
        states={"done": [("readonly", True)]},
    )
    date_start = fields.Date(string="Date start", states={"done": [("readonly", True)]}, default=fields.Date.today)
    date_end = fields.Date(string="Date end", states={"done": [("readonly", True)]})
    state = fields.Selection(
        [("draft", "Draft"), ("run", "Run"), ("wait", "Waiting"), ("done", "Done")],
        string="State",
        tracking=True,
        default="draft",
        copy=False,
        index=True,
    )
    scope = fields.Selection(
        [
            ("internal", "Internal"),
            ("integration", "Integration"),
            ("user_acceptance", "User Acceptance"),
            ("regression", "Regression"),
            ("other", "Other"),
        ],
        string="Scope",
        required=True,
        default="other",
    )
    count_steps = fields.Integer(string="Steps", compute="_compute_count_steps")
    completion_test = fields.Float(
        help="Completion test", group_operator="avg", compute="_compute_completion_test", store=True, digits=(16, 2)
    )
    doc_count = fields.Integer(string="Number of documents attached", compute="_compute_attached_docs_count")

    test_step_ids = fields.One2many(
        string="Test steps",
        comodel_name="business.process.step.test",
        inverse_name="process_test_id",
        copy=True,
    )

    @api.depends("test_step_ids.result")
    def _compute_completion_test(self):
        for test in self:
            if test.test_step_ids:
                completion_test_steps = test.test_step_ids.filtered(lambda x: x.result == "passed")
                test.completion_test = round(len(completion_test_steps) / len(test.test_step_ids) * 100, 2)
            else:
                test.completion_test = 0.0

    def _compute_count_steps(self):
        for test in self:
            test.count_steps = len(test.test_step_ids)

    def action_view_test_steps(self):
        domain = [("process_test_id", "=", self.id)]
        context = {"default_process_test_id": self.id}
        action = self.env["ir.actions.actions"]._for_xml_id(
            "deltatech_business_process.action_business_process_step_test"
        )
        action.update({"domain": domain, "context": context})
        return action

    def get_attachment_domain(self):
        domain = [("res_model", "=", self._name), ("res_id", "=", self.id)]
        return domain

    def _compute_attached_docs_count(self):
        for order in self:
            domain = order.get_attachment_domain()
            order.doc_count = self.env["ir.attachment"].search_count(domain)

    def attachment_tree_view(self):
        domain = self.get_attachment_domain()
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "ir.attachment",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "kanban,tree,form",
            "context": "{{'default_res_model': '{}','default_res_id': {}}}".format(self._name, self.id),
        }

    @api.onchange("process_id")
    def _onchange_process_id(self):
        if self.process_id:
            if not self.name:
                self.name = _("Testing %s") % self.process_id.name
            self.test_step_ids = [(5, 0, 0)]
            for step in self.process_id.step_ids:
                self.test_step_ids = [
                    (
                        0,
                        0,
                        {
                            "step_id": step.id,
                            "responsible_id": step.responsible_id.id,
                        },
                    )
                ]

    @api.onchange("state")
    def _onchange_state(self):
        today_date = datetime.now().date()
        if self.state == "run":
            self.date_start = today_date
        if self.state == "done":
            self.date_end = today_date

    def action_run(self):
        self.ensure_one()
        self.sudo().with_user(self.env.user).write({"state": "run"})
        self.sudo()._add_followers()
        for test in self:
            process = test.process_id.sudo()
            if not test.date_start:
                test.date_start = fields.Date.today()
            if not test.test_step_ids:
                date_start = fields.Date.today()
            else:
                for step in test.test_step_ids:
                    if not step.date_start:
                        step.date_start = fields.Date.today()
                date_start = min(test.test_step_ids.mapped("date_start") or fields.Date.today())

            date_start = min(date_start, test.date_start or fields.Date.today())
            test_step_ids = test.test_step_ids.filtered(lambda x: not x.date_start)
            test_step_ids.write({"date_start": date_start})
            test.write({"date_start": date_start})
            if test.scope == "internal":
                process.write({"status_internal_test": "in_progress"})
            elif test.scope == "integration":
                process.write({"status_integration_test": "in_progress"})
            elif test.scope == "user_acceptance":
                process.write({"status_user_acceptance_test": "in_progress"})
            if not self.tester_id:
                self.tester_id = self.env.user.partner_id
            for step in self.test_step_ids:
                if not step.responsible_id:
                    step.responsible_id = self.tester_id
            for steps in self.test_step_ids:
                steps.write({"test_started": True})

    def action_wait(self):
        self.ensure_one()
        self.sudo().with_user(self.env.user).write({"state": "wait"})

    def action_done(self):
        self.ensure_one()
        self.sudo().with_user(self.env.user).write({"state": "done"})
        for test in self:
            process = test.process_id.sudo()
            # verifica daca toate testele sunt completate
            # altfel da eroare cad vrea sa calculeze date_end
            if test.test_step_ids.filtered(lambda x: x.result == "draft"):
                raise UserError(_("All test steps must be completed."))
            if test.test_step_ids.filtered(lambda x: x.result == "failed"):
                test.write({"state": "wait"})
                continue
            if not test.date_end:
                test.date_start = fields.Date.today()
            if not test.test_step_ids:
                date_end = fields.Date.today()
            else:
                date_end = max(test.test_step_ids.mapped("date_end")) or fields.Date.today()
            date_end = max(date_end, test.date_end or fields.Date.today())

            test.write({"date_end": date_end})
            if test.scope == "internal":
                process.write({"status_internal_test": "done"})
            elif test.scope == "integration":
                process.write({"status_integration_test": "done"})
            elif test.scope == "user_acceptance":
                process.write({"status_user_acceptance_test": "done"})

        # verifica daca toate testele sunt done
        for process in self.mapped("process_id"):
            process = process.sudo()
            if (
                process.status_internal_test == "done"
                and process.status_integration_test == "done"
                and process.status_user_acceptance_test == "done"
            ):
                process.write({"state": "ready"})
            else:
                tests = process.test_ids.filtered(lambda x: x.state != "done")
                if not tests:
                    process.write({"state": "ready"})

    def action_draft(self):
        self.ensure_one()
        self.sudo().with_user(self.env.user).write({"state": "draft"})
        # reset test steps to draft
        self.test_step_ids.reset_draft()

    def _add_followers(self):
        for process in self:
            followers = self.env["res.partner"]
            if process.tester_id not in process.message_partner_ids:
                followers |= process.tester_id
            for step in process.test_step_ids:
                if step.responsible_id not in process.message_partner_ids:
                    followers |= step.responsible_id
            process.message_subscribe(followers.ids)

    @api.onchange("completion_test")
    def _onchange_completion_test(self):
        if self.completion_test == 100.0:
            self.action_done()

    def action_assign_to_me(self):
        self.tester_id = self.env.user.partner_id
        self.test_step_ids.responsible_id = self.env.user.partner_id

    def action_unassign_me(self):
        self.tester_id = False
        self.test_step_ids.responsible_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            name = False
            if not vals.get("name", False) and vals.get("process_id", False):
                name = self.env["business.process"].browse(vals["process_id"]).name
            if not name and self._context.get("default_process_id", False):
                name = self.env["business.process"].browse(self._context["default_process_id"]).name
            if name:
                vals["name"] = name
        result = super().create(vals_list)
        return result
