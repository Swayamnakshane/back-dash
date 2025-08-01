from flask import Blueprint
from ..views import employe_views

employee_bp = Blueprint('employe_bp', __name__) # Removed url_prefix here, it's in app.register_blueprint

employee_bp.add_url_rule(
    "/login",
    view_func=employe_views.EmployeeLoginAPI.as_view("LoginAPI"),
    methods=["POST"]
)


employee_bp.add_url_rule(
    "/personal-details",
    view_func=employe_views.EmployeePersonalDetailsAPI.as_view("personal_details_api"),
    
    methods=["POST"]
)

employee_bp.add_url_rule(
    "/personal-details/update",
    view_func=employe_views.EmployeePersonalDetailsUpdateAPI.as_view("personal_details_update_api"),
    methods=["PUT"]
)

employee_bp.add_url_rule(
    "/get-details",
    view_func=employe_views.GetEmployeeDetails.as_view("get_employee_details_api"),
    methods=["GET"]
)

employee_bp.add_url_rule(
    "/ProfessionalDetails",
    view_func=employe_views.EmployeeProfessionalDetailsAPI.as_view("professional_details_api"),
    methods=["POST"]
)

employee_bp.add_url_rule(
    "/ProfessionalDetails/update",
    view_func=employe_views.UpdateEmployeeProfessionalDetails.as_view("update_professional_details_api"),
    methods=["PUT"]
)

employee_bp.add_url_rule(
    "/get-professional-details",
    view_func=employe_views.GetEmployeeProfessionalDetails.as_view("get_professional_details_api"),
    methods=["GET"]
)

employee_bp.add_url_rule(
    "/get-tasks",
    view_func=employe_views.GetEmployeeTasks.as_view("get_employee_tasks_api"),
    methods=["GET"]
)


employee_bp.add_url_rule(
    "/update-task-status/<task_id>",
    view_func=employe_views.UpdateTaskStatus.as_view("update_task_status_api"),
    methods=["PUT"]
)


employee_bp.add_url_rule(
    "/get-meetings",
    view_func=employe_views.GetMeetings.as_view("get_meetings_api"),
    methods=["GET"]
)

employee_bp.add_url_rule(
    "/upload-document",
    view_func=employe_views.UploadDocumentAPI.as_view("upload_document_api"),
    methods=["POST"]
)

employee_bp.add_url_rule(
    "/get-documents",
    view_func=employe_views.GetDocumentsAPI.as_view("get_documents_api"),
    methods=["GET"]
)

employee_bp.add_url_rule(
    "/delete-document/<doc_id>",
    view_func=employe_views.DeleteDocumentAPI.as_view("delete_document_api"),
    methods=["DELETE"]
)

employee_bp.add_url_rule(
    "/upload-bank-details",
    view_func=employe_views.UploadBankDetailsAPI.as_view("upload_bank_details_api"),
    methods=["POST"]
)

employee_bp.add_url_rule(
    "/update/BankDetails",
    view_func=employe_views.UpdateBankDetailsAPI.as_view("update_bank_details_api"),
    methods=["PUT"]
)


employee_bp.add_url_rule(
    "/get-bank-details",
    view_func=employe_views.GetBankDetailsAPI.as_view("get_bank_details_api"),
    methods=["GET"]
)

employee_bp.add_url_rule(
    "/add-timesheet",
    view_func=employe_views.AddTimesheet.as_view("add_timesheet_api"),
    methods=["POST"]
)

employee_bp.add_url_rule(
    "/update-timesheet",
    view_func=employe_views.UpdateTimesheet.as_view("update_timesheet_api"),
    methods=["PUT"] )

employee_bp.add_url_rule(
    "/daily/get-timesheet",
    view_func=employe_views.DailyTimesheet.as_view("daily_timesheet_api"),
    methods=["GET"]
)

employee_bp.add_url_rule(
    "/summary/get-timesheet",
    view_func=employe_views.SummaryTimesheet.as_view("summary_timesheet_api"),
    methods=["GET"]
)
employee_bp.add_url_rule(
    '/training/available', 
    view_func=employe_views.GetAvailableTrainings.as_view('get_available_trainings'),
     methods=["GET"]
    )

employee_bp.add_url_rule(
    '/training/enroll/<training_id>',
    view_func=employe_views.EnrollTraining.as_view('enroll_training'),
    methods=["POST"])

employee_bp.add_url_rule(
    '/training/my-trainings',
    view_func=employe_views.GetMyTrainings.as_view('get_my_trainings')
    , methods=["GET"])