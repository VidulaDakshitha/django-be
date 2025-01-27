from django.db import models

from common.base_model import BaseModel

BID_CHOICES = [
    ("open", "Open"),
    ("closed", "Closed"),
    ("max_price", "Max Price")
]

JOB_CHOICES = [("remote", "Remote"), ("hybrid", "Hybrid"), ("onsite", "Onsite")]

EXPERIENCE_LEVEL = [("entry", "Entry"), ("intermediate", "Intermediate"), ("expert", "Expert")]

STATUS = [("in_progress", "In Progress"), ("pending", "Pending"), ("completed", "Completed")]

COMMUNICATION_TYPE = [("open", "open"), ("closed", "closed"), ("no", "no")]


class Task(BaseModel):
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=100, blank=True)
    bid_type = models.CharField(max_length=100, choices=BID_CHOICES, blank=True)
    bid_deadline = models.CharField(max_length=100, null=True, blank=True)
    job_type = models.CharField(max_length=100, blank=True, choices=JOB_CHOICES)
    experience_level = models.CharField(max_length=100, blank=True, choices=EXPERIENCE_LEVEL)
    task_deadline = models.CharField(max_length=100, null=True, blank=True)
    acceptance_criteria = models.TextField(blank=True)
    skills = models.ManyToManyField("Skill", related_name='tasks', blank=True)
    is_completed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_worker_accepted = models.BooleanField(default=False)
    is_fully_paid = models.BooleanField(default=False)
    progress = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, blank=True, choices=STATUS)
    is_sub_contractors_only = models.BooleanField(default=False)
    sub_contractors = models.ManyToManyField("user.User", related_name='sub_contractors', blank=True)
    sub_organizations = models.ManyToManyField("user.Organization", related_name='sub_organizations', blank=True)
    # new fields
    task_owner = models.ForeignKey("user.User", related_name="task_owner",
                                   on_delete=models.DO_NOTHING, null=True, blank=True)
    exit_criteria = models.TextField(blank=True)
    communication_deadline = models.CharField(max_length=100, null=True, blank=True)
    communication_type = models.CharField(max_length=100, blank=True, choices=COMMUNICATION_TYPE)
    is_origin_organization = models.BooleanField(default=False)  # If the task is created by an organization
    origin_organization = models.ForeignKey("user.Organization", related_name="origin_organization",
                                            on_delete=models.DO_NOTHING, null=True, blank=True)
    is_post_approved = models.BooleanField(default=False)  # only for organization
    is_post_rejected = models.BooleanField(default=False)  # only for organization
    post_approved_by = models.ForeignKey("user.User", related_name="post_approved_by", on_delete=models.DO_NOTHING,
                                         null=True, blank=True)
    post_approved_on = models.CharField(max_length=100, null=True, blank=True)
    is_worker_organization = models.BooleanField(default=False)  # If the task is managed by an organization
    worker_organization = models.ForeignKey("user.Organization", related_name="worker_organization",
                                            on_delete=models.DO_NOTHING, null=True, blank=True)
    assignee = models.ForeignKey("user.User", related_name="task_assignee", on_delete=models.DO_NOTHING, null=True,
                                 blank=True)
    manager = models.ForeignKey("user.User", related_name="task_manager", on_delete=models.DO_NOTHING, null=True,
                                blank=True)


class SubTask(BaseModel):
    task = models.ForeignKey(Task, related_name="sub_tasks", on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    from_date = models.CharField(max_length=100, null=True, blank=True)
    to_date = models.CharField(max_length=100, null=True, blank=True)
    time_logged = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    revision = models.IntegerField(null=True, blank=True, default=0)
    # Track whether the freelancer has sent an invoice for this sub-task
    is_invoiced = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)


class SubtaskFile(BaseModel):
    subtask = models.ForeignKey(SubTask, related_name="subtask_files", on_delete=models.DO_NOTHING, null=True,
                                blank=True)
    file = models.FileField(upload_to='subtask_files/', null=True, blank=True)
    name = models.TextField(null=True, blank=True)


class Invoice(BaseModel):
    subtask = models.ForeignKey(SubTask, related_name="sub_task_invoice", on_delete=models.CASCADE, null=True,
                                blank=True)
    assignee = models.ForeignKey("user.User", related_name="invoice_assignee", on_delete=models.DO_NOTHING, null=True,
                                 blank=True)
    client = models.ForeignKey("user.User", related_name="invoice_client", on_delete=models.DO_NOTHING, null=True,
                               blank=True)
    file = models.FileField(upload_to='invoice/', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    date_paid = models.CharField(max_length=100, null=True, blank=True)


class Attachment(BaseModel):
    task = models.ForeignKey(Task, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments')
    name = models.TextField(null=True, blank=True)


class Skill(BaseModel):
    skill = models.CharField(max_length=100, blank=True)
