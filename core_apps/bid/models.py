from django.db import models

from common.base_model import BaseModel
from core_apps.task.models import Task

STATUS = [("in_progress", "In Progress"), ("pending", "Pending"), ("completed", "Completed")]


class Bid(BaseModel):
    bidder = models.ForeignKey("user.User", related_name="bidder_bid", on_delete=models.DO_NOTHING, null=True, blank=True)
    employer = models.ForeignKey("user.User", related_name="employer_bid", on_delete=models.DO_NOTHING, null=True, blank=True)
    task = models.ForeignKey(Task, related_name="task", on_delete=models.DO_NOTHING, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    revision = models.IntegerField(null=True, blank=True)
    cover_letter = models.TextField(null=True, blank=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    status = models.CharField(max_length=100, blank=True, choices=STATUS)
    bid_updated_on = models.CharField(max_length=100, null=True, blank=True)
    bid_updated_by = models.ForeignKey("user.User", related_name='bid_updated_by', on_delete=models.DO_NOTHING,
                                       null=True,
                                       blank=True)


class AdditionalCost(BaseModel):
    bid = models.ForeignKey(Bid, related_name="additional_costs", on_delete=models.DO_NOTHING, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
