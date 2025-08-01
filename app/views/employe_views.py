from flask import request, jsonify
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.models import Employe, Experience, Task, Meeting, DocumentUpload, EmployeeBankDetails,Timesheet, TimeSlot, TrainingAndLearning
from app.models import ist_now, IST  # Your IST datetime util
from flask_jwt_extended import create_access_token, create_refresh_token


class EmployeeLoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        mobile = data.get('mobile')
        password = data.get('password')

        if not password or (not email and not mobile):
            return jsonify({'message': 'Email or mobile and password are required.'}), 400

        employee = None
        if email:
            employee = Employe.objects(email=email).first()
        elif mobile:
            employee = Employe.objects(mobile=mobile).first()

        if not employee:
            return jsonify({'message': 'Employee not found.'}), 404

        if not employee.password or employee.password != password:
            return jsonify({'message': 'Invalid password.'}), 401

        # Generate JWT tokens
        access_token = create_access_token(identity=str(employee.id))
        refresh_token = create_refresh_token(identity=str(employee.id))

        return jsonify({
            'message': 'Login successful.',
            'employee_id': employee.employee_id,
            'name': employee.name,
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

from datetime import datetime
from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        raise ValueError("Invalid date format. Expected DD/MM/YYYY.")

class EmployeePersonalDetailsAPI(MethodView):
    @jwt_required()
    def post(self):
        try:
            employee_id = get_jwt_identity()
            employee = Employe.objects(id=employee_id).first()

            if not employee:
                return jsonify({'message': 'Employee not found.'}), 404

            # If already has personal details, reject
            if employee.date_of_birth or employee.phone or employee.gender:
                return jsonify({'message': 'Personal details already exist. Use PUT to update.'}), 400

            data = request.get_json()
            print("Incoming data:", data)

            try:
                dob = parse_date(data.get('date_of_birth'))
            except ValueError as e:
                return jsonify({'message': str(e)}), 400

            # Update fields
            employee.update(
                phone=data.get('phone'),
                date_of_birth=dob,
                gender=data.get('gender'),
                marital_status=data.get('marital_status'),
                nationality=data.get('nationality'),
                aadhar_number=data.get('aadhar_number'),
                pan_number=data.get('pan_number'),
                address_line1=data.get('address_line1'),
                address_line2=data.get('address_line2'),
                city=data.get('city'),
                state=data.get('state'),
                pincode=data.get('pincode'),
                country=data.get('country', 'India'),
                updated_at=ist_now()
            )

            return jsonify({'message': '✅ Personal details saved successfully.'}), 201

        except Exception as e:
            print("❌ Error saving personal details:")
            traceback.print_exc()
            return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500


class EmployeePersonalDetailsUpdateAPI(MethodView):
    @jwt_required()
    def put(self):
        employee_id = get_jwt_identity()
        employee = Employe.objects(id=employee_id).first()

        if not employee:
            return jsonify({'message': 'Employee not found.'}), 404

        data = request.get_json()

        try:
            dob = parse_date(data.get("date_of_birth"))
        except ValueError as e:
            return jsonify({'message': str(e)}), 400

        try:
            employee.update(
                phone=data.get('phone', employee.phone),
                date_of_birth=dob if dob else employee.date_of_birth,
                gender=data.get('gender', employee.gender),
                marital_status=data.get('marital_status', employee.marital_status),
                nationality=data.get('nationality', employee.nationality),
                aadhar_number=data.get('aadhar_number', employee.aadhar_number),
                pan_number=data.get('pan_number', employee.pan_number),
                address_line1=data.get('address_line1', employee.address_line1),
                address_line2=data.get('address_line2', employee.address_line2),
                city=data.get('city', employee.city),
                state=data.get('state', employee.state),
                pincode=data.get('pincode', employee.pincode),
                country=data.get('country', employee.country),
                updated_at=ist_now()
            )
        except Exception as e:
            return jsonify({'message': 'Failed to update details.', 'error': str(e)}), 500

        return jsonify({'message': 'Personal details updated successfully.'}), 200

class GetEmployeeDetails(MethodView):
    @jwt_required()
    def get(self):
        try:
            employee_id = get_jwt_identity()
            employee = Employe.objects(id=employee_id).first()

            if not employee:
                return jsonify({'message': 'Employee not found.'}), 404

            personal_data = {
                "phone": employee.phone,
                "date_of_birth": employee.date_of_birth.strftime("%d-%m-%Y") if employee.date_of_birth else "",
                "gender": employee.gender,
                "marital_status": employee.marital_status,
                "nationality": employee.nationality,
                "aadhar_number": employee.aadhar_number,
                "pan_number": employee.pan_number,
                "address_line1": employee.address_line1,
                "address_line2": employee.address_line2,
                "city": employee.city,
                "state": employee.state,
                "pincode": employee.pincode,
                "country": employee.country,
            }

            return jsonify({"message": "✅ Personal details retrieved successfully.", "data": personal_data}), 200

        except Exception as e:
            return jsonify({
                "message": "An error occurred while retrieving personal details.",
                "error": str(e)
            }), 500

def parse_date_safe(date_str):
    if not date_str:
        return None
    for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError("Invalid date format. Expected DD-MM-YYYY or DD/MM/YYYY.")

class EmployeeProfessionalDetailsAPI(MethodView):
    @jwt_required()
    def post(self):
        try:
            employee_id = get_jwt_identity()
            employee = Employe.objects(id=employee_id).first()

            if not employee:
                return jsonify({"message": "Employee not found."}), 404

            if employee.education or employee.current_job_title:
                return jsonify({"message": "Professional details already exist. Use PUT to update."}), 400

            data = request.get_json()
            employee.update(
                education=data.get("education"),
                specialization=data.get("specialization"),
                college_name=data.get("college_name"),
                year_of_passing=data.get("year_of_passing"),
                certifications=data.get("certifications", []),
                current_job_title=data.get("current_job_title"),
                company_name="Arcap",
                job_description=data.get("job_description"),
                from_date=parse_date_safe(data.get("from_date")),
                to_date=parse_date_safe(data.get("to_date")),
                currently_working=data.get("currently_working", True),
                previous_experiences=[
                    Experience(
                        company_name=exp.get("company_name"),
                        job_title=exp.get("job_title"),
                        employment_type=exp.get("employment_type"),
                        job_description=exp.get("job_description"),
                        from_date=parse_date_safe(exp.get("from_date")),
                        to_date=parse_date_safe(exp.get("to_date")),
                    ) for exp in data.get("previous_experiences", [])
                ],
                skills=data.get("skills", []),
                achievements=data.get("achievements", []),
                languages_known=data.get("languages_known", []),
                linkedin_profile=data.get("linkedin_profile"),
                github_profile=data.get("github_profile"),
                portfolio_website=data.get("portfolio_website"),
                bio=data.get("bio"),
                updated_at=ist_now()
            )
            return jsonify({"message": "✅ Professional details saved successfully."}), 201
        except Exception as e:
            traceback.print_exc()
            return jsonify({"message": "❌ Error saving data", "error": str(e)}), 500

class UpdateEmployeeProfessionalDetails(MethodView):
    @jwt_required()
    def put(self):
        try:
            employee_id = get_jwt_identity()
            employee = Employe.objects(id=employee_id).first()

            if not employee:
                return jsonify({"message": "Employee not found."}), 404

            data = request.get_json()
            employee.update(
                education=data.get("education"),
                specialization=data.get("specialization"),
                college_name=data.get("college_name"),
                year_of_passing=data.get("year_of_passing"),
                certifications=data.get("certifications", []),
                current_job_title=data.get("current_job_title"),
                company_name="Arcap",
                job_description=data.get("job_description"),
                from_date=parse_date_safe(data.get("from_date")),
                to_date=parse_date_safe(data.get("to_date")),
                currently_working=data.get("currently_working", True),
                previous_experiences=[
                    Experience(
                        company_name=exp.get("company_name"),
                        job_title=exp.get("job_title"),
                        employment_type=exp.get("employment_type"),
                        job_description=exp.get("job_description"),
                        from_date=parse_date_safe(exp.get("from_date")),
                        to_date=parse_date_safe(exp.get("to_date")),
                    ) for exp in data.get("previous_experiences", [])
                ],
                skills=data.get("skills", []),
                achievements=data.get("achievements", []),
                languages_known=data.get("languages_known", []),
                linkedin_profile=data.get("linkedin_profile"),
                github_profile=data.get("github_profile"),
                portfolio_website=data.get("portfolio_website"),
                bio=data.get("bio"),
                updated_at=ist_now()
            )
            return jsonify({"message": "✅ Professional details updated successfully."}), 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({"message": "❌ Error updating data", "error": str(e)}), 500

from bson import ObjectId
from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

class GetEmployeeProfessionalDetails(MethodView):
    @jwt_required()
    def get(self):
        try:
            employee_id = get_jwt_identity()
            employee = Employe.objects(id=employee_id).first()

            if not employee:
                return jsonify({"message": "Employee not found."}), 404

            def format_date(dt):
                return dt.strftime("%d-%m-%Y") if dt else ""

            result = {
                "education": employee.education,
                "specialization": employee.specialization,
                "college_name": employee.college_name,
                "year_of_passing": employee.year_of_passing,
                "current_job_title": employee.current_job_title,
                "company_name": employee.company_name,
                "job_description": employee.job_description,
                "from_date": format_date(employee.from_date),
                "to_date": format_date(employee.to_date),
                "currently_working": employee.currently_working,
                "previous_experiences": [
                    {
                        "company_name": exp.company_name,
                        "job_title": exp.job_title,
                        "employment_type": exp.employment_type,
                        "job_description": exp.job_description,
                        "from_date": format_date(exp.from_date),
                        "to_date": format_date(exp.to_date),
                    } for exp in employee.previous_experiences or []
                ],
                "skills": employee.skills or [],
                "languages_known": employee.languages_known or [],
                "linkedin_profile": employee.linkedin_profile,
                "github_profile": employee.github_profile,
                "portfolio_website": employee.portfolio_website,
                "bio": employee.bio,
            }

            return jsonify({
                "data": result,
                "message": "✅ Professional details retrieved."
            }), 200

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                "message": "❌ Error retrieving data",
                "error": str(e)
            }), 500



class GetEmployeeTasks(MethodView):
    @jwt_required()
    def get(self):
        try:
            current_user_id = get_jwt_identity()

            # Get employee by ID
            try:
                employee = Employe.objects.get(id=current_user_id)
            except Employe.DoesNotExist:
                return jsonify({"message": "Employee not found."}), 404

            # Fetch all tasks assigned to this employee
            tasks = Task.objects(assigned_to=employee)

            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "approval_status": task.approval_status,
                    "assigned_date": task.assigned_date.strftime("%d-%m-%Y") if task.assigned_date else None,
                    "due_date": task.due_date.strftime("%d-%m-%Y") if task.due_date else None,
                    "assigned_by": {
                        "id": str(task.assigned_by.id) if task.assigned_by else None,
                        "name": getattr(task.assigned_by, "name", "")
                    } if task.assigned_by else None
                })

            return jsonify({"tasks": task_list}), 200

        except Exception as e:
            traceback.print_exc()
            return jsonify({"message": "Error retrieving employee tasks", "error": str(e)}), 500

class UpdateTaskStatus(MethodView):
    @jwt_required()
    def put(self, task_id):
        try:
            current_user_id = get_jwt_identity()

            # Get logged-in employee
            try:
                employee = Employe.objects.get(id=current_user_id)
            except Employe.DoesNotExist:
                return jsonify({"message": "Employee not found."}), 404

            # Get task assigned to this employee
            task = Task.objects(task_id=task_id, assigned_to=employee).first()
            if not task:
                return jsonify({"message": "Task not found or not assigned to you."}), 404

            # Validate status input
            data = request.get_json()
            new_status = data.get("status")
            allowed_statuses = ["Pending", "In Progress", "Completed"]

            if not new_status or new_status not in allowed_statuses:
                return jsonify({
                    "message": f"Invalid or missing status. Valid values: {', '.join(allowed_statuses)}"
                }), 400

            # Update task status
            task.status = new_status
            task.updated_at = ist_now()
            task.save()

            return jsonify({"message": f"✅ Task status updated to '{new_status}'"}), 200

        except Exception as e:
            traceback.print_exc()
            return jsonify({"message": "Error updating task status", "error": str(e)}), 500


class GetMeetings(MethodView):
    @jwt_required()
    def get(self):
        try:
            employee_id = get_jwt_identity()
            employee = Employe.objects(id=employee_id).first()

            if not employee:
                return jsonify({"message": "Employee not found."}), 404

            meetings = Meeting.objects(employee=employee).order_by('-date_time')

            meeting_list = []
            for meeting in meetings:
                meeting_list.append({
                    "meeting_id": meeting.meeting_id,
                    "title": meeting.title,
                    "meeting_type": meeting.meeting_type,
                    "description": meeting.description,
                    "location": meeting.location,
                    "date_time": meeting.date_time.strftime("%d-%m-%Y %H:%M") if meeting.date_time else None,
                    "duration_minutes": meeting.duration_minutes,
                    "link": meeting.link,
                    "agenda": meeting.agenda,
                    "notes": meeting.notes,
                    "status": meeting.status,
                    "created_at": meeting.created_at.strftime("%d-%m-%Y %H:%M") if meeting.created_at else None
                })

            return jsonify({
                "meetings": meeting_list,
                "message": f"✅ {len(meeting_list)} meeting(s) retrieved."
            }), 200

        except Exception as e:
            traceback.print_exc()
            return jsonify({
                "message": "❌ Error retrieving meetings",
                "error": str(e)
            }), 500

# class UploadDocumentAPI(MethodView):
#     @jwt_required()
#     def post(self):
#         user_id = get_jwt_identity()
#         employee = Employe.objects(id=user_id).first()
#         if not employee:
#             return jsonify({"error": "Employee not found"}), 404

#         if 'file' not in request.files:
#             return jsonify({"error": "No file uploaded"}), 400

#         file = request.files['file']
#         data = request.form.to_dict()

#         if not all(k in data for k in ("document_type", "document_name")):
#             return jsonify({"error": "Missing required fields"}), 400

#         extension = file.filename.split('.')[-1]
#         file_size_kb = len(file.read()) // 1024
#         file.seek(0)

#         # Assume you uploaded the file and got URL (pseudo logic)
#         file_url = f"https://your-bucket.s3.amazonaws.com/{file.filename}"

#         doc = DocumentUpload(
#             employee_id=employee.employee_id,
#             document_type=data['document_type'],
#             document_name=data['document_name'],
#             document_url=file_url,
#             file_size_kb=file_size_kb,
#             file_extension=f".{extension}",
#             uploaded_by=employee
#         )
#         doc.save()

#         return jsonify({"message": "✅ Document uploaded successfully."}), 201
    
# class GetDocumentsAPI(MethodView):
#     @jwt_required()
#     def get(self):
#         employee_id = get_jwt_identity()
#         employee = Employe.objects(id=employee_id).first()
#         if not employee:
#             return jsonify({"error": "Employee not found"}), 404

#         docs = DocumentUpload.objects(employee_id=employee.employee_id, is_active=True)
#         result = [{
#             "document_id": str(d.id),
#             "document_type": d.document_type,
#             "document_name": d.document_name,
#             "document_url": d.document_url,
#             "file_size_kb": d.file_size_kb,
#             "file_extension": d.file_extension,
#             "verification_status": d.verification_status,
#             "uploaded_at": d.uploaded_at.strftime("%d-%m-%Y %H:%M")
#         } for d in docs]

#         return jsonify({"documents": result}), 200

# class DeleteDocumentAPI(MethodView):
#     @jwt_required()
#     def delete(self, doc_id):
#         user_id = get_jwt_identity()
#         employee = Employe.objects(id=user_id).first()
#         if not employee:
#             return jsonify({"error": "Employee not found"}), 404

#         doc = DocumentUpload.objects(id=doc_id, uploaded_by=employee).first()
#         if not doc:
#             return jsonify({"error": "Document not found"}), 404

#         doc.is_active = False
#         doc.save()

#         return jsonify({"message": "🗑️ Document removed successfully."}), 200

class UploadDocumentAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        data = request.form.to_dict()

        required_fields = ("document_type", "document_name", "google_drive_url")
        if not all(field in data and data[field].strip() for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Extract filename from the Google Drive URL (or set default)
        filename = data['document_name']
        extension = ".pdf" if filename.endswith(".pdf") else ".docx"  # example, infer as needed
        file_size_kb = 0  # Google Drive file size isn't known here unless fetched from Drive API

        doc = DocumentUpload(
            employee_id=employee.employee_id,
            document_type=data['document_type'],
            document_name=data['document_name'],
            document_url=data['google_drive_url'],
            file_size_kb=file_size_kb,
            file_extension=extension,
            uploaded_by=employee
        )
        doc.save()

        return jsonify({"message": "✅ Document uploaded successfully."}), 201

class GetDocumentsAPI(MethodView):
    @jwt_required()
    def get(self):
        employee_id = get_jwt_identity()
        employee = Employe.objects(id=employee_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        documents = DocumentUpload.objects(employee_id=employee.employee_id, is_active=True)

        result = [{
            "document_id": str(doc.id),
            "document_type": doc.document_type,
            "document_name": doc.document_name,
            "document_url": doc.document_url,
            "file_size_kb": doc.file_size_kb,
            "file_extension": doc.file_extension,
            "verification_status": doc.verification_status,
            "uploaded_at": doc.uploaded_at.strftime("%d-%m-%Y %H:%M")
        } for doc in documents]

        return jsonify({"documents": result}), 200

class DeleteDocumentAPI(MethodView):
    @jwt_required()
    def delete(self, doc_id):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        doc = DocumentUpload.objects(id=doc_id, uploaded_by=employee).first()
        if not doc:
            return jsonify({"error": "Document not found"}), 404

        doc.is_active = False
        doc.save()

        return jsonify({"message": "🗑️ Document removed successfully."}), 200

class UploadBankDetailsAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        data = request.get_json()
        required = {"bank_name", "account_number", "ifsc_code"}
        missing = required - data.keys()

        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        existing_bank = EmployeeBankDetails.objects(employee=employee).first()
        if existing_bank:
            return jsonify({"error": "Bank details already exist"}), 400

        bank = EmployeeBankDetails(
            employee=employee,
            bank_name=data["bank_name"],
            account_number=data["account_number"],
            ifsc_code=data["ifsc_code"],
            pf_number=data.get("pf_number"),
            uan_number=data.get("uan_number"),
            employee_id=employee.employee_id,
            created_at=ist_now(),
            updated_at=ist_now()
        )
        bank.save()

        return jsonify({"message": "✅ Bank details uploaded successfully."}), 201


class UpdateBankDetailsAPI(MethodView):
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()

        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        data = request.get_json()

        required = {"bank_name", "account_number", "ifsc_code"}
        if not required.issubset(data.keys()):
            return jsonify({"error": f"Missing fields: {required - data.keys()}"}), 400

        bank = EmployeeBankDetails.objects(employee=employee).first()

        if not bank:
            bank = EmployeeBankDetails(employee=employee, employee_id=employee.employee_id)

        bank.bank_name = data.get("bank_name")
        bank.account_number = data.get("account_number")
        bank.ifsc_code = data.get("ifsc_code")
        bank.pf_number = data.get("pf_number")
        bank.uan_number = data.get("uan_number")
        bank.updated_at = ist_now()

        bank.save()
        return jsonify({"message": "✅ Bank details updated successfully."}), 200

class GetBankDetailsAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        bank = EmployeeBankDetails.objects(employee=employee).first()
        if not bank:
            return jsonify({"message": "No bank details found."}), 404

        return jsonify({
            "data": {
                "bank_name": bank.bank_name,
                "account_number": bank.account_number,
                "ifsc_code": bank.ifsc_code,
                "pf_number": bank.pf_number,
                "uan_number": bank.uan_number
            },
            "message": "✅ Bank details retrieved."
        }), 200

from datetime import datetime, timedelta


class AddTimesheet(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        data = request.get_json()
        required_fields = {"login_time", "logout_time", "time_slots"}

        if not required_fields.issubset(data):
            return jsonify({"error": f"Missing fields: {', '.join(required_fields - data.keys())}"}), 400

        try:
            login_time = datetime.fromisoformat(data["login_time"])
            logout_time = datetime.fromisoformat(data["logout_time"])
            if logout_time <= login_time:
                return jsonify({"error": "Logout time must be after login time."}), 400
        except ValueError:
            return jsonify({"error": "Invalid datetime format. Use ISO format."}), 400

        time_slots = []
        total_seconds = 0

        for slot in data["time_slots"]:
            try:
                start = datetime.fromisoformat(slot["start_time"])
                end = datetime.fromisoformat(slot["end_time"])
                description = slot["description"]

                if end <= start:
                    return jsonify({"error": "Time slot end time must be after start time."}), 400

                time_slots.append(TimeSlot(start_time=start, end_time=end, description=description))
                total_seconds += (end - start).total_seconds()
            except (KeyError, ValueError):
                return jsonify({"error": "Each time slot must include valid start_time, end_time, and description."}), 400

        total_hours = round(total_seconds / 3600, 2)

        existing = Timesheet.objects(employee=employee, date=login_time.date()).first()
        if existing:
            return jsonify({"error": "Timesheet for this date already exists. Please update instead."}), 400

        timesheet = Timesheet(
            employee=employee,
            date=login_time.date(),
            login_time=login_time,
            logout_time=logout_time,
            time_slots=time_slots,
            total_hours=total_hours
        )
        timesheet.save()

        return jsonify({"message": "✅ Timesheet added successfully", "total_hours": total_hours}), 201


class UpdateTimesheet(MethodView):
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        data = request.get_json()
        required_fields = {"date", "login_time", "logout_time", "time_slots"}
        if not required_fields.issubset(data):
            return jsonify({"error": f"Missing fields: {', '.join(required_fields - data.keys())}"}), 400

        try:
            date = datetime.strptime(data["date"], "%Y-%m-%d").date()
            login_time = datetime.fromisoformat(data["login_time"])
            logout_time = datetime.fromisoformat(data["logout_time"])
        except ValueError:
            return jsonify({"error": "Invalid datetime format."}), 400

        timesheet = Timesheet.objects(employee=employee, date=date).first()
        if not timesheet:
            return jsonify({"error": "Timesheet not found for the given date."}), 404

        if timesheet.status in ["Approved", "Rejected"]:
            return jsonify({"error": f"Cannot update a {timesheet.status.lower()} timesheet."}), 400

        time_slots = []
        total_seconds = 0

        for slot in data["time_slots"]:
            try:
                start = datetime.fromisoformat(slot["start_time"])
                end = datetime.fromisoformat(slot["end_time"])
                description = slot["description"]

                if end <= start:
                    return jsonify({"error": "Time slot end time must be after start time."}), 400

                time_slots.append(TimeSlot(start_time=start, end_time=end, description=description))
                total_seconds += (end - start).total_seconds()
            except (KeyError, ValueError):
                return jsonify({"error": "Invalid or missing time slot fields."}), 400

        timesheet.login_time = login_time
        timesheet.logout_time = logout_time
        timesheet.time_slots = time_slots
        timesheet.total_hours = round(total_seconds / 3600, 2)
        timesheet.status = "Pending"
        timesheet.updated_at = datetime.now()
        timesheet.save()

        return jsonify({"message": "✅ Timesheet updated successfully", "total_hours": timesheet.total_hours}), 200


class DailyTimesheet(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        date_str = request.args.get("date")
        if not date_str:
            date_obj = datetime.now().date()
        else:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        timesheet = Timesheet.objects(employee=employee, date=date_obj).first()
        if not timesheet:
            return jsonify({"message": "No timesheet entry found for this day."}), 404

        tasks = [
            {
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "description": slot.description
            }
            for slot in timesheet.time_slots
        ]

        return jsonify({
            "date": date_obj.strftime("%Y-%m-%d"),
            "login_time": timesheet.login_time.strftime("%H:%M") if timesheet.login_time else None,
            "logout_time": timesheet.logout_time.strftime("%H:%M") if timesheet.logout_time else None,
            "total_hours": timesheet.total_hours,
            "status": timesheet.status,
            "tasks": tasks
        }), 200


class SummaryTimesheet(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        today = datetime.now()
        start_of_week = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        start_of_month = datetime.combine(today.replace(day=1), datetime.min.time())

        weekly_sheets = Timesheet.objects(employee=employee, date__gte=start_of_week)
        monthly_sheets = Timesheet.objects(employee=employee, date__gte=start_of_month)

        weekly_hours = sum(ts.total_hours for ts in weekly_sheets)
        monthly_hours = sum(ts.total_hours for ts in monthly_sheets)

        avg_weekly = round(weekly_hours / 7, 2)
        avg_monthly = round(monthly_hours / today.day, 2)

        return jsonify({
            "weekly_total": round(weekly_hours, 2),
            "weekly_avg": avg_weekly,
            "monthly_total": round(monthly_hours, 2),
            "monthly_avg": avg_monthly
        }), 200

class GetAvailableTrainings(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()

        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Fetch training templates not yet enrolled by this employee
        enrolled_ids = TrainingAndLearning.objects(employee=employee).distinct("training_id")
        trainings = TrainingAndLearning.objects(employee=None, training_id__nin=enrolled_ids)

        result = [{
            "training_id": tr.training_id,
            "title": tr.title,
            "description": tr.description,
            "provider": tr.provider,
            "image": tr.image,
            "no_of_days": tr.no_of_days,
        } for tr in trainings]

        return jsonify(result), 200

class EnrollTraining(MethodView):
    @jwt_required()
    def post(self, training_id):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Check if the user has already enrolled
        exists = TrainingAndLearning.objects(employee=employee, training_id=training_id).first()
        if exists:
            return jsonify({"message": "Already enrolled"}), 400

        # Get the training template (should be global with employee=None)
        template = TrainingAndLearning.objects(training_id=training_id, employee=None).first()
        if not template:
            return jsonify({"error": "Training template not found"}), 404

        now = ist_now()

        # Create a new enrollment
        enrolled = TrainingAndLearning(
            employee=employee,
            training_id=training_id,
            title=template.title,
            description=template.description,
            image=template.image,
            provider=template.provider,
            no_of_days=template.no_of_days,
            start_date=now,
            end_date=now + timedelta(days=template.no_of_days),
            status="Enrolled"
        )
        enrolled.save()
        return jsonify({"message": "Training enrolled successfully."}), 201


from datetime import timezone
import pytz

# Your timezone function (assuming India Standard Time)
def ist_now():
    return datetime.now(pytz.timezone("Asia/Kolkata"))

class GetMyTrainings(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        employee = Employe.objects(id=user_id).first()
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        trainings = TrainingAndLearning.objects(employee=employee)
        now = ist_now()
        result = []

        for tr in trainings:
            if tr.start_date and tr.end_date:
                # Ensure both start_date and end_date are timezone-aware
                start_date = tr.start_date.astimezone(pytz.timezone("Asia/Kolkata"))
                end_date = tr.end_date.astimezone(pytz.timezone("Asia/Kolkata"))

                # Training status logic
                if now < start_date:
                    status = "Enrolled"
                elif start_date <= now <= end_date:
                    status = "In Progress"
                else:
                    status = "Completed"

                if tr.status != status:
                    tr.status = status
                    tr.save()
            else:
                status = tr.status or "Unknown"

            result.append({
                "training_id": tr.training_id,
                "title": tr.title,
                "description": tr.description,
                "image": tr.image,
                "provider": tr.provider,
                "start_date": tr.start_date.strftime("%Y-%m-%d") if tr.start_date else None,
                "end_date": tr.end_date.strftime("%Y-%m-%d") if tr.end_date else None,
                "no_of_days": tr.no_of_days,
                "status": status
            })

        return jsonify(result), 200
