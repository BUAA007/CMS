from django.db import models
from Meeting.models import *
from Paper.models import *

# Create your models here.
class User(models.Model):
	username = models.CharField(
		max_length = 32,
		unique = True,
		)
	password = models.CharField(
		max_length = 32,
		)
	email = models.CharField(
		max_length = 32,
		null = True,
		)
	tel = models.CharField(
		max_length = 20,
		null = True,
		)
	favorite = models.ManyToManyField(Meeting, related_name = "User_set",blank = True,)
	participate = models.ManyToManyField(Meeting, related_name = "Attendee_set",blank = True,)

class Join(models.Model):
	receipt = models.FileField(
		upload_to = 'receipt',
		)
	name = models.CharField(
		max_length = 32,
		)
	gender = models.CharField(
		max_length = 10,
		)
	reservation = models.CharField(
		max_length = 8,
		)
	types=models.IntegerField(
		null=True,
		default = 1,
		)
	# papid = models.IntegerField(
	# 	null=True,
	# 	default = 1,
	# 	)
	paper = models.ForeignKey(
		"Paper.Paper",
		on_delete=models.CASCADE,
		default = "",
		)
	meeting = models.ForeignKey(
		"Meeting.Meeting",
		on_delete = models.CASCADE,
		null = True
		)