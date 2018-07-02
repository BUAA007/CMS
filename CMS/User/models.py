from django.db import models
from Meeting.models import *

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
	#participate = models.ManyToManyField(Meeting,through="type_participate",related_name = "Attendee_set",blank = True,)

class type_participate(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	meeting=models.ForeignKey(Meeting,on_delete=models.CASCADE)
	type=models.CharField(
		max_length=20,)
	paper_id=models.CharField(max_length=256,null=True,)
	people_name=models.CharField(max_length=256,)
	people_sex=models.CharField(max_length=20,null=True,)
	isbook=models.CharField(max_length=20,)
	register_pay=models.FileField(upload_to='register_pay/',)