from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, ReferenceField, ListField, EmbeddedDocument, EmbeddedDocumentField,FloatField
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
def ist_now():
    return datetime.now(IST)

class Admin(Document):
    name = StringField(required=True)
    password = StringField(required=True, max_length=255)
    mobile = StringField(max_length=15, unique=True)
    email = EmailField(required=True, unique=True, max_length=100)
    otp = StringField(max_length=6)
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)
    otp_expiry = DateTimeField(default=lambda: ist_now() + timedelta(minutes=10))
    
from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from datetime import datetime, timedelta, timezone

# Define IST time
IST = timezone(timedelta(hours=5, minutes=30))
def ist_now():
    return datetime.now(IST)

class Experience(EmbeddedDocument):
    company_name = StringField(required=True)
    job_title = StringField()
    employment_type = StringField(choices=["Full-time", "Part-time", "Internship"])
    job_description = StringField()
    from_date = DateTimeField()
    to_date = DateTimeField()

class Employe(Document):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True, max_length=100)
    password = StringField(required=False, max_length=255)
    otp = StringField(max_length=255)
    otp_expiry = DateTimeField(default=lambda: ist_now() + timedelta(minutes=9999))
    is_verified = BooleanField(default=False)
    is_active = BooleanField(default=True)
    employee_id = StringField(required=True, unique=True)
    phone = StringField( max_length=15)
    date_of_birth = DateTimeField()
    gender = StringField(choices=["Male", "Female", "Other"])
    marital_status = StringField(choices=["Single", "Married"])
    nationality = StringField()
    aadhar_number = StringField(max_length=12)
    pan_number = StringField()
    address_line1 = StringField()
    address_line2 = StringField()
    city = StringField()
    state = StringField()
    pincode = StringField()
    country = StringField(default="India")
    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)
    education = StringField(max_length=100)
    specialization = StringField()
    college_name = StringField(max_length=255)
    year_of_passing = StringField(max_length=4)
    certifications = ListField(StringField())
    current_job_title = StringField()
    company_name = StringField(default="Arcap")  # Current company
    job_description = StringField()
    from_date = DateTimeField()
    to_date = DateTimeField()
    currently_working = BooleanField(default=True)
    previous_experiences = ListField(EmbeddedDocumentField(Experience))  # Updated structure
    skills = ListField(StringField())
    achievements = ListField(StringField())
    languages_known = ListField(StringField())
    linkedin_profile = StringField()
    github_profile = StringField()
    portfolio_website = StringField()
    bio = StringField()
    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)

from mongoengine import ListField

class Task(Document):
    task_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    description = StringField()
    project_id = StringField()

    assigned_by = ReferenceField(Admin, required=True)
    assigned_to = ListField(ReferenceField(Employe), required=True)  # ✅ change here

    team_lead_id = StringField()
    approval_status = StringField(default="Pending")
    status = StringField(default="Assigned")

    assigned_date = DateTimeField(default=ist_now)
    due_date = DateTimeField()
    approval_date = DateTimeField()

    meeting_link = StringField()
    meeting_date_time = DateTimeField()
    meeting_agenda = StringField()
    comments = StringField()
    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)




class Project(Document):
    project_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    description = StringField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    status = StringField(default="Ongoing")
    project_manager_id = StringField()
    team_members = StringField()  # store comma-separated or JSON list
    created_at = DateTimeField(default=ist_now)

class Certification(Document):
    employee_id = StringField(required=True)
    title = StringField(required=True)
    issued_by = StringField()
    issue_date = DateTimeField()
    certificate_url = StringField()
    created_at = DateTimeField(default=ist_now)


class Meeting(Document):
    employee = ReferenceField(Employe, required=True)
    meeting_type = StringField(
        choices=["Team Meeting", "Client Meeting", "One-on-One", "Training"],
        required=True
    )
    meeting_id = StringField(required=True, unique=True)  # Changed to StringField
    employee_id = StringField(required=True)
    title = StringField(required=True)
    description = StringField()
    location = StringField()
    date_time = DateTimeField(required=True)
    duration_minutes = StringField()  # Optional time slot
    link = StringField()
    agenda = StringField()
    notes = StringField()
    status = StringField(default="Scheduled", choices=["Scheduled", "Completed", "Cancelled"])
    is_active = BooleanField(default=True)
    created_by = ReferenceField(Admin, required=True)
    created_at = DateTimeField(default=ist_now)
    update_at = DateTimeField(default=ist_now)
    
from mongoengine import (
    Document, StringField, BooleanField,
    DateTimeField, ReferenceField, IntField
)


class DocumentUpload(Document):
    employee_id = StringField(required=True)
    document_type = StringField(
        required=True,
        choices=[
            "PAN Card", "Aadhaar Card", "Resume", "Certificate","Bank Details",
            "Criminal Conduct Certificate", "Digital Responsibility Certificate", "Other"
        ]
    )
    document_name = StringField(required=True)
    document_url = StringField(required=True)
    file_size_kb = IntField(required=True)
    file_extension = StringField(required=True)  # e.g., .pdf, .jpg, .png

    uploaded_by = ReferenceField(Employe, required=True)
    uploaded_at = DateTimeField(default=ist_now)

    verification_status = StringField(
        choices=["Pending", "Approved", "Rejected"], default="Pending"
    )
    verification_notes = StringField()
    verified_by = ReferenceField(Admin, null=True)
    verified_at = DateTimeField()

    is_active = BooleanField(default=True)

    meta = {
        "indexes": [
            "employee_id",
            "document_type",
            "verification_status",
            "is_active"
        ],
        "ordering": ["-uploaded_at"]
    }



class EmployeeBankDetails(Document):
    employee = ReferenceField(Employe, required=True, unique=True)
    employee_id = StringField(required=True)
    bank_name = StringField(required=True)
    account_number = StringField(required=True)
    ifsc_code = StringField(required=True)
    pf_number = StringField()
    uan_number = StringField()

    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)

    meta = {
        "indexes": ["employee_id", "ifsc_code", "uan_number"],
        "ordering": ["-updated_at"]
    }




class OnboardingChecklist(Document):
    employee_id = StringField(required=True)
    step_1_profile = BooleanField(default=False)
    step_2_bank_details = BooleanField(default=False)
    step_3_document_uploads = BooleanField(default=False)
    step_4_bgv = StringField(default="Pending")
    step_5_training_level_1 = StringField(default="Pending")
    step_5_training_level_2 = StringField(default="Pending")
    step_5_training_level_3 = StringField(default="Pending")
    step_5_training_level_4 = StringField(default="Pending")
    step_5_training_level_5 = StringField(default="Pending")
    step_6_policy_ack = BooleanField(default=False)
    step_7_hr_review = BooleanField(default=False)
    advisor_id = StringField()
    ccc_provider = StringField()
    cdr_provider = StringField()
    overall_status = StringField(default="Pending")  # Pending, In Progress, Completed
    created_at = DateTimeField(default=ist_now)


class TimeSlot(EmbeddedDocument):
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    description = StringField(required=True)  # E.g., "Client Meeting"

class Timesheet(Document):
    employee = ReferenceField('Employe', required=True)
    date = DateTimeField(required=True)
    login_time = DateTimeField()
    logout_time = DateTimeField()
    status = StringField(choices=['Pending', 'Approved', 'Rejected'], default='Pending')
    remarks = StringField()
    approved_by = ReferenceField(Admin)
    rejected_by = ReferenceField(Admin)
    approved_at = DateTimeField()
    rejected_at = DateTimeField()
    time_slots = ListField(EmbeddedDocumentField(TimeSlot))  # Tasks with time range
    total_hours = FloatField(default=0)  # Auto-calculated
    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)

    meta = {
        "indexes": ["employee", "date"],
        "ordering": ["-date"]
    }


class TrainingAndLearning(Document):
    employee = ReferenceField(Employe, required=False, null=True)

    training_id = StringField(required=True,)
    title = StringField(required=True)
    description = StringField()
    image= StringField()  # URL to training image
    provider = StringField()
    no_of_days = IntField(required=True)
    start_date = DateTimeField()
    end_date = DateTimeField()
    status = StringField(choices=["Enrolled", "In Progress", "Completed"], default="Enrolled")
    created_at = DateTimeField(default=ist_now)
    updated_at = DateTimeField(default=ist_now)

    meta = {
        "indexes": ["employee", "training_id"],
        "ordering": ["-start_date"]
    }