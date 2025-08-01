from flask import request, jsonify
from flask.views import MethodView
from ..models import Admin, Employe, ist_now,  Task,Meeting, DocumentUpload , Timesheet, TimeSlot, TrainingAndLearning
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash
from datetime import datetime


class RegisterAdmin(MethodView):
    def post(self):
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        mobile = data.get('mobile')
        is_active = data.get('is_active', True)

        if not all([name, email, password, mobile]):
            return jsonify({'error': 'Name, email, password, and mobile are required.'}), 400

        if Admin.objects(email=email).first():
            return jsonify({'error': 'Email already registered.'}), 409

        if Admin.objects(mobile=mobile).first():
            return jsonify({'error': 'Mobile already registered.'}), 409

        hashed_password = generate_password_hash(password)

        new_admin = Admin(
            name=name,
            email=email,
            password=hashed_password,
            mobile=mobile,
            is_active=is_active
        )
        new_admin.save()

        return jsonify({'message': 'Admin registered successfully.'}), 201


from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import check_password_hash

class AdminLoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        mobile = data.get('mobile')
        password = data.get('password')

        admin = None
        if email:
            admin = Admin.objects(email=email).first()
        elif mobile:
            admin = Admin.objects(mobile=mobile).first()

        if not admin:
            return jsonify({'message': 'Admin not found'}), 404

        if not check_password_hash(admin.password, password):
            return jsonify({'message': 'Invalid password'}), 401

        admin_id = str(admin.id)
        access_token = create_access_token(identity=admin_id)
        refresh_token = create_refresh_token(identity=admin_id)

        return jsonify({
            'message': 'Admin logged in successfully.',
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200


import pandas as pd
from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone


IST = timezone(timedelta(hours=5, minutes=30))
def ist_now(): return datetime.now(IST)




class UploadEmploye(MethodView):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        # Verify admin
        try:
            admin = Admin.objects.get(id=current_user_id)
        except Admin.DoesNotExist:
            return jsonify({'error': 'Admin not found'}), 404

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': f'Invalid Excel file. {str(e)}'}), 400

        added = 0
        for _, row in df.iterrows():
            employee_id = row.get('employee_id')
            name = row.get('name')
            email = row.get('email')
            password = row.get('password')

            if not employee_id or not name or not email or not password:
                continue  # Skip incomplete rows

            if Employe.objects(email=email).first():
                continue  # Skip existing employees by email

            emp = Employe(
                employee_id=employee_id,
                name=name,
                email=email,
                password=password,
                is_verified=True,
                created_at=ist_now(),
                updated_at=ist_now()
            )
            emp.save()
            added += 1

        return jsonify({'message': f'{added} employees added successfully'}), 200


from collections import defaultdict


class UploadTask(MethodView):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        try:
            admin = Admin.objects.get(id=current_user_id)
        except Admin.DoesNotExist:
            return jsonify({'error': 'Admin not found'}), 404

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': f'Invalid Excel file. {str(e)}'}), 400

        required_fields = {'task_id', 'employee_id', 'title', 'description', 'due_date'}
        if not required_fields.issubset(df.columns):
            return jsonify({'error': f'Missing required fields in Excel. Required: {list(required_fields)}'}), 400

        tasks_grouped = defaultdict(list)
        task_meta = {}

        for _, row in df.iterrows():
            task_id = str(row['task_id']).strip()
            employee_id = str(row['employee_id']).strip()

            try:
                employee = Employe.objects.get(employee_id=employee_id)
                tasks_grouped[task_id].append(employee)
            except Employe.DoesNotExist:
                continue

            if task_id not in task_meta:
                due_date = row.get('due_date')
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, "%d-%m-%Y")
                task_meta[task_id] = {
                    'title': str(row['title']).strip(),
                    'description': str(row['description']).strip(),
                    'due_date': due_date,
                }

        added = 0
        errors = []

        for task_id, employees in tasks_grouped.items():
            if Task.objects(task_id=task_id).first():
                errors.append(f"Task {task_id} already exists.")
                continue

            meta = task_meta[task_id]
            task = Task(
                task_id=task_id,
                title=meta['title'],
                description=meta['description'],
                project_id="",
                assigned_by=admin,
                assigned_to=employees,
                approval_status="Pending",
                status="Assigned",
                assigned_date=ist_now(),
                due_date=meta['due_date'],
                created_at=ist_now(),
                updated_at=ist_now()
            )
            task.save()
            added += 1

        return jsonify({
            'message': f'{added} tasks uploaded successfully.',
            'errors': errors
        }), 200


class UpdateTask(MethodView):
    @jwt_required()
    def put(self, task_id):
        current_user_id = get_jwt_identity()

        try:
            admin = Admin.objects.get(id=current_user_id)
        except Admin.DoesNotExist:
            return jsonify({'error': 'Admin not found'}), 404

        task = Task.objects(task_id=task_id).first()
        if not task:
            return jsonify({'error': f'Task {task_id} not found.'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        allowed_fields = {'title', 'description', 'due_date', 'assigned_to', 'approval_status', 'status'}
        updates = {}

        for field in allowed_fields:
            if field in data:
                updates[field] = data[field]

        if 'due_date' in updates:
            try:
                updates['due_date'] = datetime.strptime(updates['due_date'], "%d-%m-%Y")
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Expected DD-MM-YYYY'}), 400

        if 'assigned_to' in updates:
            employee_ids = updates['assigned_to']
            if not isinstance(employee_ids, list):
                return jsonify({'error': 'assigned_to must be a list of employee IDs'}), 400
            employees = []
            for emp_id in employee_ids:
                try:
                    emp = Employe.objects.get(employee_id=emp_id)
                    employees.append(emp)
                except Employe.DoesNotExist:
                    return jsonify({'error': f'Employee {emp_id} not found'}), 400
            updates['assigned_to'] = employees

        for key, value in updates.items():
            setattr(task, key, value)

        task.updated_at = ist_now()
        task.save()

        return jsonify({'message': f'Task {task_id} updated successfully.'}), 200


class GetTask(MethodView):
    @jwt_required()
    def get(self, task_id):
        task = Task.objects(task_id=task_id).first()
        if not task:
            return jsonify({'error': f'Task {task_id} not found.'}), 404

        def employee_to_dict(emp):
            return {
                'employee_id': emp.employee_id,
                'name': emp.name,
                'email': emp.email
            }

        task_data = {
            'task_id': task.task_id,
            'title': task.title,
            'description': task.description,
            'project_id': task.project_id,
            'assigned_by': {
                'id': str(task.assigned_by.id),
                'name': task.assigned_by.name
            } if task.assigned_by else None,
            'assigned_to': [employee_to_dict(emp) for emp in task.assigned_to],
            'approval_status': task.approval_status,
            'status': task.status,
            'assigned_date': task.assigned_date.strftime("%d-%m-%Y") if task.assigned_date else None,
            'due_date': task.due_date.strftime("%d-%m-%Y") if task.due_date else None,
            'created_at': task.created_at.strftime("%d-%m-%Y %H:%M:%S") if task.created_at else None,
            'updated_at': task.updated_at.strftime("%d-%m-%Y %H:%M:%S") if task.updated_at else None,
        }

        return jsonify(task_data), 200



class CreateMeeting(MethodView):
    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()

        try:
            admin = Admin.objects.get(id=current_user_id)
        except Admin.DoesNotExist:
            return jsonify({'error': 'Admin not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        required_fields = {'employee_id', 'meeting_type', 'title', 'date_time', 'link', 'agenda'}
        if not required_fields.issubset(data.keys()):
            return jsonify({'error': f'Missing required fields: {list(required_fields)}'}), 400

        try:
            employee = Employe.objects.get(employee_id=data['employee_id'])
        except Employe.DoesNotExist:
            return jsonify({'error': f'Employee {data["employee_id"]} not found.'}), 404

        try:
            date_time = datetime.strptime(data['date_time'], "%d-%m-%Y %H:%M")
        except ValueError:
            return jsonify({'error': 'Invalid date_time format. Expected DD-MM-YYYY HH:MM'}), 400

        meeting = Meeting(
            meeting_id=data.get('meeting_id', str(ist_now().timestamp())),
            employee=employee,
            employee_id=data['employee_id'],
            meeting_type=data['meeting_type'],
            title=data['title'],
            description=data.get('description'),
            location=data.get('location'),
            date_time=date_time,
            duration_minutes=data.get('duration_minutes'),
            link=data['link'],
            agenda=data['agenda'],
            notes=data.get('notes'),
            status="Scheduled",
            created_by=admin
        )
        meeting.save()

        return jsonify({'message': '✅ Meeting created successfully.', 'meeting_id': meeting.meeting_id}), 201

class UpdateMeeting(MethodView):
    @jwt_required()
    def put(self, meeting_id):
        current_user_id = get_jwt_identity()
        data = request.get_json()

        try:
            admin = Admin.objects.get(id=current_user_id)
        except Admin.DoesNotExist:
            return jsonify({"error": "Admin not found."}), 404

        try:
           
            meeting = Meeting.objects.get(meeting_id=meeting_id)
        except Meeting.DoesNotExist:
            return jsonify({"error": "Meeting not found."}), 404

        if "date_time" in data:
            try:
                data["date_time"] = datetime.strptime(data["date_time"], "%d-%m-%Y %H:%M")
            except ValueError:
                return jsonify({"error": "Invalid date_time format. Expected DD-MM-YYYY HH:MM"}), 400

        data["update_at"] = ist_now()
        meeting.update(**data)

        return jsonify({"message": " Meeting updated successfully."}), 200
    
class GetMeetingByEmployee(MethodView):
    @jwt_required()
    def get(self, employee_id):
        meetings = Meeting.objects(employee_id=employee_id, is_active=True).order_by('-date_time')
        output = []
        for m in meetings:
            output.append({
                "meeting_id": m.meeting_id,
                "title": m.title,
                "meeting_type": m.meeting_type,
                "date_time": m.date_time.strftime("%d-%m-%Y %H:%M"),
                "agenda": m.agenda,
                "link": m.link,
                "status": m.status
            })
        return jsonify({"meetings": output}), 200


class GetAllMeetings(MethodView):
    @jwt_required()
    
    def get(self):
        
        meetings = Meeting.objects(is_active=True).order_by('-date_time')
        result = []
        for m in meetings:
            result.append({
                "meeting_id": m.meeting_id,
                "title": m.title,
                "employee_id": m.employee_id,
                "meeting_type": m.meeting_type,
                "date_time": m.date_time.strftime("%d-%m-%Y %H:%M"),
                "agenda": m.agenda,
                "link": m.link,
                "status": m.status,
            })
        return jsonify({"meetings": result}), 200

import traceback
class UpdateStatusDocumentUpload(MethodView):
    @jwt_required()
    def put(self, document_id):
        current_user_id = get_jwt_identity()

        try:
            admin = Admin.objects.get(id=current_user_id)
        except Admin.DoesNotExist:
            return jsonify({'error': 'Admin not found'}), 404

        try:
            document = DocumentUpload.objects(id=document_id).first()
            if not document:
                return jsonify({'error': f'Document {document_id} not found.'}), 404

            data = request.get_json()
            new_status = data.get("verification_status")
            notes = data.get("verification_notes", "")

            if new_status not in ["Approved", "Rejected"]:
                return jsonify({'error': 'Invalid status. Must be "Approved" or "Rejected".'}), 400

            document.verification_status = new_status
            document.verification_notes = notes
            document.is_verified = True if new_status == "Approved" else False
            document.verified_by = admin
            document.verified_at = ist_now()
            document.save()

            return jsonify({
                'message': f'Document {document_id} has been {new_status.lower()} successfully.'
            }), 200

        except Exception as e:
            traceback.print_exc()
            return jsonify({
                'message': '❌ Failed to update document status.',
                'error': str(e)
            }), 500


class AdminViewSingleTimesheet(MethodView):
    @jwt_required()
    def get(self, timesheet_id):
        admin = Admin.objects(id=get_jwt_identity()).first()
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        timesheet = Timesheet.objects(id=timesheet_id).first()
        if not timesheet:
            return jsonify({"error": "Timesheet not found"}), 404

        timeslot_details = [
            {
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M"),
                "description": slot.description
            }
            for slot in timesheet.time_slots
        ]

        return jsonify({
            "id": str(timesheet.id),
            "employee_id": str(timesheet.employee.id),
            "date": timesheet.date.strftime("%Y-%m-%d"),
            "login_time": timesheet.login_time.strftime("%H:%M") if timesheet.login_time else None,
            "logout_time": timesheet.logout_time.strftime("%H:%M") if timesheet.logout_time else None,
            "total_hours": timesheet.total_hours,
            "status": timesheet.status,
            "remarks": timesheet.remarks,
            "approved_by": str(timesheet.approved_by.id) if timesheet.approved_by else None,
            "rejected_by": str(timesheet.rejected_by.id) if timesheet.rejected_by else None,
            "time_slots": timeslot_details
        }), 200


class AdminUpdateTimesheetStatus(MethodView):
    @jwt_required()
    def put(self, timesheet_id):
        admin = Admin.objects(id=get_jwt_identity()).first()
        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        data = request.get_json()
        status = data.get("status")
        remarks = data.get("remarks", "")

        if status not in ["Approved", "Rejected"]:
            return jsonify({"error": "Invalid status. Must be 'Approved' or 'Rejected'."}), 400

        timesheet = Timesheet.objects(id=timesheet_id).first()
        if not timesheet:
            return jsonify({"error": "Timesheet not found"}), 404

        if timesheet.status in ["Approved", "Rejected"]:
            return jsonify({"error": f"Timesheet already {timesheet.status.lower()}."}), 400

        timesheet.status = status
        timesheet.remarks = remarks
        if status == "Approved":
            timesheet.approved_by = admin
            timesheet.approved_at = datetime.now()
            timesheet.rejected_by = None
            timesheet.rejected_at = None
        else:
            timesheet.rejected_by = admin
            timesheet.rejected_at = datetime.now()
            timesheet.approved_by = None
            timesheet.approved_at = None

        timesheet.updated_at = datetime.now()
        timesheet.save()

        return jsonify({"message": f"Timesheet {status.lower()} successfully."}), 200

       
import os   
import uuid
import boto3
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

admin_views = Blueprint('admin_views', __name__)

# AWS S3 Configuration from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")

def upload_image_to_s3(file_obj, folder="training_images"):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION
        )
        filename = secure_filename(file_obj.filename)
        unique_filename = f"{folder}/{uuid.uuid4().hex}_{filename}"

        # Upload to S3
        s3.upload_fileobj(file_obj, AWS_S3_BUCKET, unique_filename)

        # Return public URL
        url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{unique_filename}"
        return url
    except Exception as e:
        print("Error uploading to S3:", e)
        return None


class AdminCreateTraining(MethodView):
    @jwt_required()
    def post(self):
        admin_id = get_jwt_identity()
        admin = Admin.objects(id=admin_id).first()

        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        # Expect multipart/form-data
        title = request.form.get("title")
        description = request.form.get("description")
        provider = request.form.get("provider")
        no_of_days = request.form.get("no_of_days")
        image = request.files.get("image")

        if not all([title, description, provider, no_of_days, image]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            image_url = upload_image_to_s3(image)
        except Exception as e:
            return jsonify({"error": f"Image upload failed: {str(e)}"}), 500

        training = TrainingAndLearning(
            employee=None,
            training_id=str(uuid.uuid4()),
            title=title,
            description=description,
            image=image_url,
            provider=provider,
            no_of_days=int(no_of_days),
            start_date=None,
            end_date=None,
            status="Enrolled"
        )
        training.save()

        return jsonify({"message": "Training template created successfully", "training_id": training.training_id}), 201

