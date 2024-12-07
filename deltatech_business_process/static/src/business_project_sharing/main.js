/** @odoo-module **/
import {startWebClient} from "@web/start";
import {BusinessProjectSharingWebClient} from "./business_project_sharing";
import {prepareFavoriteMenuRegister} from "./components/favorite_menu_registry";

prepareFavoriteMenuRegister();
startWebClient(BusinessProjectSharingWebClient);
