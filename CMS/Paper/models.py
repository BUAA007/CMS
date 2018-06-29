from django.db import models
from User.models import *
from Meeting.models import *

# Create your models here.
class Paper(models.Model):
	author_1 = models.CharField(
		max_length = 20,
		null = False,
		)
	author_2 = models.CharField(
		max_length = 20,
		)
	author_3 = models.CharField(
		max_length = 20
		)
	title = models.CharField(
		max_length = 64,
		)
	abstract = models.CharField(
		max_length = 1024,
		)
	keyword = models.CharField(
		max_length = 128,
		)
	content = models.CharField(
		max_length = 64,
		)
	status = models.IntegerField(
		null = False,
		)
	owner = models.ForeignKey(User)
	meeting = models.ForeignKey(Meeting)