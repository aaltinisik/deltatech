# ©  2023 Deltatech
# See README.rst file on addons root folder for license details

from odoo import _, api, fields, models


class BusinessProject(models.Model):
    _name = "business.project"
    _description = "Business project"
    _inherit = ['portal.mixin', "mail.thread", "mail.activity.mixin"]

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=True)
    customer_id = fields.Many2one(string="Customer", comodel_name="res.partner")
    logo = fields.Image()
    state = fields.Selection(
        [
            ("preparation", "Preparation"),
            ("exploration", "Exploration"),
            ("realization", "Realization"),
            ("deployment", "Deployment"),
            ("running", "Running"),
            ("closed", "Closed"),
        ],
        string="State",
        default="preparation",
    )
    date_start = fields.Date(string="Start date")
    date_go_live = fields.Date(string="Go live date")
    process_ids = fields.One2many(string="Processes", comodel_name="business.process", inverse_name="project_id")

    issue_ids = fields.One2many(string="Issues", comodel_name="business.issue", inverse_name="project_id")

    count_processes = fields.Integer(string="Count Processes", compute="_compute_count_processes")
    count_issues = fields.Integer(string="Count Issues", compute="_compute_count_issues")
    count_steps = fields.Integer(string="Steps", compute="_compute_count_steps")
    count_developments = fields.Integer(string="Developments", compute="_compute_count_developments")

    responsible_id = fields.Many2one(
        string="Responsible", domain="[('is_company', '=', False)]", comodel_name="res.partner"
    )
    team_member_ids = fields.Many2many(string="Team members", comodel_name="res.partner")
    total_project_duration = fields.Float(string="Total project duration")
    doc_count = fields.Integer(
        string="Count Documents",
        help="Number of documents attached",
        compute="_compute_attached_docs_count",
    )
    project_manager_id = fields.Many2one(
        string="Project Manager",
        comodel_name="res.partner",
    )
    project_type = fields.Selection([("remote", "Remote"), ("local", "Local")], string="Project Type", default="remote")

    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
        help="Attachments that don't come from a message.")

    @api.model
    def _get_attachments_search_domain(self, model, res_ids):
        return [('res_id', 'in', res_ids), ('res_model', '=', model)]

    def _compute_attachment_ids(self):
        for project in self:
            domain = project._get_attachments_search_domain(project._name, project.ids)
            attachments = self.env['ir.attachment'].search(domain)
            attachments |= project.mapped('message_ids.attachment_ids')
            field_name = [
                "process_ids",
                "process_ids.step_ids",
                "process_ids.test_ids",
                "process_ids.development_ids",
                "process_ids.step_ids.development_ids",
                "process_ids.test_ids.test_step_ids",
                "process_ids.test_ids.test_step_ids.issue_ids"
            ]
            for field in field_name:
                if "attachment_ids" in project.mapped(field):
                    attachments |= project.mapped(field).mapped('attachment_ids')
                if "message_ids" in project.mapped(field):
                    attachments |= project.mapped(field).mapped('message_ids.attachment_ids')
            project.attachment_ids = attachments
            print(project.attachment_ids)

    @api.model
    def create(self, vals):
        if not vals.get("code", False):
            vals["code"] = self.env["ir.sequence"].next_by_code(self._name)
        result = super().create(vals)
        return result

    def name_get(self):
        self.browse(self.ids).read(["name", "code"])
        return [
            (project.id, "{}{}".format(project.code and "[%s] " % project.code or "", project.name)) for project in self
        ]

    def _compute_count_processes(self):
        for project in self:
            project.count_processes = len(project.process_ids)

    def _compute_count_issues(self):
        for project in self:
            project.count_issues = len(project.issue_ids)

    def _compute_count_steps(self):
        for project in self:
            project.count_steps = sum(process.count_steps for process in project.process_ids)

    def _compute_count_developments(self):
        for project in self:
            developments = self.env["business.development"].search([("project_id", "=", self.id)])
            project.count_developments = len(developments)

    def action_view_processes(self):
        domain = [("project_id", "=", self.id)]
        context = {
            "default_project_id": self.id,
            "default_customer_id": self.customer_id.id,
        }
        action = self.env["ir.actions.actions"]._for_xml_id("deltatech_business_process.action_business_process")
        action.update({"domain": domain, "context": context})
        return action

    def get_attachment_domain(self):
        domain = [
            "|",
            "|",
            "&",
            ("res_model", "=", "business.project"),
            ("res_id", "=", self.id),
            "&",
            ("res_model", "=", "business.process"),
            ("res_id", "in", self.process_ids.ids),
            "&",
            ("res_model", "=", "business.process.test"),
            ("res_id", "in", self.process_ids.test_ids.ids),
        ]
        return domain

    def _compute_attached_docs_count(self):
        for order in self:
            domain = order.get_attachment_domain()
            order.doc_count = self.env["ir.attachment"].sudo().search_count(domain)

    def attachment_tree_view(self):
        domain = self.get_attachment_domain()
        return {
            "name": _("Attachments"),
            "domain": domain,
            "res_model": "ir.attachment",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "kanban,tree,form",
            "context": f"{{'default_res_model': '{self._name}','default_res_id': {self.id}}}",
        }

    def action_view_issue(self):
        domain = [("project_id", "=", self.id)]
        context = {
            "default_project_id": self.id,
            "default_customer_id": self.customer_id.id,
        }

        action = self.env["ir.actions.actions"]._for_xml_id("deltatech_business_process.action_business_issue")
        action.update({"domain": domain, "context": context})
        return action

    def action_view_step(self):
        domain = [("process_id", "=", self.process_ids.ids)]
        context = {"default_project_id": self.id}
        action = self.env["ir.actions.actions"]._for_xml_id("deltatech_business_process.action_business_process_step")
        action.update({"domain": domain, "context": context})
        return action

    def action_view_developments(self):
        developments = self.env["business.development"].search([("project_id", "=", self.id)])
        domain = [("id", "=", developments.ids)]
        context = {"default_project_id": self.id}
        action = self.env["ir.actions.actions"]._for_xml_id("deltatech_business_process.action_business_development")
        action.update({"domain": domain, "context": context})
        return action

    def calculate_total_project_duration(self):
        for project in self:
            project.total_project_duration = sum(process.duration_for_completion for process in project.process_ids)
            for development in self.env["business.development"].search(
                [("project_id", "=", project.id), ("approved", "not in", ("draft", "rejected"))]
            ):
                project.total_project_duration += development.development_duration

    # pentru portal
    def action_open_bp(self):
        context = self._context.copy()
        if "binary_field_real_user" in context:
            del context["binary_field_real_user"]
        return {
            "view_mode": "form",
            "res_model": "business.project",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "context": context,
        }

    def action_business_project_sharing_open(self):
        action = self.action_open_bp()

        action["views"] = [
            [
                self.env.ref("deltatech_business_process.view_business_project_form").id,
                "form",
            ]
        ]
        return action