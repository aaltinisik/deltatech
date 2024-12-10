/** @odoo-module */

import {BusinessProjectSharingFormController} from "./business_project_sharing_form_controller";
import {BusinessProjectSharingFormRenderer} from "./business_project_sharing_form_renderer";
import {formView} from "@web/views/form/form_view";

formView.Controller = BusinessProjectSharingFormController;
formView.Renderer = BusinessProjectSharingFormRenderer;
