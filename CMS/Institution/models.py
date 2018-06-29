from django.db import models
from Meeting.models import meeting 
from Paper.models import paper
# Create your models here.
class Institution(models.Model):
	id=models.AutoField(
		max_length = 256,
		primary_key = True,
		)
	name=models.CharField(
		max_length=128,
		null=True,
		)
	corporate_id=models.CharField(
		max_length=256,
		null=True,
		)
	establish_date=models.CharField(
		null=True,
		)
	place=models.CharField(
		max_length=256,
		null=True,
		)
	legal_person=models.CharField(
		max_length=256,
		null=True,
		)
	type=models.CharField(
		max_length=16,
		null=True,
		)
	status=models.CharField(
		max_length=16,
		null=True,
		)
	meeting=models.ForeignKey(
		'Meeting.meeting'
		on_delete=models.CASCADE,
		default = "",
		)
	paper=models.ForeignKey(
		'Paper.paper'
		on_delete=models.CASCADE,
		default = "",
		)