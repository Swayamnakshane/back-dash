from flask import Blueprint
from ..views import admin_views

admin_bp = Blueprint('admin_bp', __name__) # Removed url_prefix here, it's in app.register_blueprint




admin_bp.add_url_rule(
    "/register",
    view_func=admin_views.RegisterAdmin.as_view("register_admin_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/adminlogin",
    view_func=admin_views.AdminLoginAPI.as_view("admin_login_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/upload-employe",
    view_func=admin_views.UploadEmploye.as_view("upload_employe_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/upload-task",
    view_func=admin_views.UploadTask.as_view("upload_task_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/update-task/<task_id>",
    view_func=admin_views.UpdateTask.as_view("upload_project_api"),
    methods=["PUT"]
)

admin_bp.add_url_rule(
    "/get-task/<task_id>",
    view_func=admin_views.GetTask.as_view("get_task_api"),
    methods=["GET"]
)

admin_bp.add_url_rule(
    "/create-meeting",
    view_func=admin_views.CreateMeeting.as_view("create_meeting_api"),
    methods=["POST"]
)

admin_bp.add_url_rule(
    "/update-meeting/<meeting_id>",
    view_func=admin_views.UpdateMeeting.as_view("update_meeting_api"),
    methods=["PUT"]
)

admin_bp.add_url_rule(
    "/UpdateStatusDocumentUpload/<document_id>",
    view_func=admin_views.UpdateStatusDocumentUpload.as_view("update_status_document_upload_api"),
    methods=["PUT"]
)


admin_bp.add_url_rule(
    "/timesheet/<timesheet_id>",
    view_func=admin_views.AdminViewSingleTimesheet.as_view("timesheet_api "),
    methods=["GET"]
)

admin_bp.add_url_rule(
    "/update-timesheet-status/<timesheet_id>",
    view_func=admin_views.AdminUpdateTimesheetStatus.as_view("update_timesheet_status_api"),
    methods=["PUT"]
)

admin_bp.add_url_rule(
    "/create-training",
    view_func=admin_views.AdminCreateTraining.as_view("create_training_api"),
    methods=["POST"]
)

