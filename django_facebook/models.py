from django.db import models
from django.core.urlresolvers import reverse
from django.core import exceptions
from django.conf import settings
from django.db.models import fields
from django.utils.translation import ugettext as _

class BigIntegerField(fields.IntegerField):
    '''Class to be used for the facebook_id fields, that need BigInt, which is
       not natively supported by django 1.0 (see ticket #399)
    '''
    
    def db_type(self):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE[:8] == 'postgres':
            return "bigint"
        else:
            raise NotImplemented
    
    def get_internal_type(self):
        return "BigIntegerField"
    
    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class FacebookProfileModel(models.Model):
    '''
    Abstract class to add to your profile model.
    NOTE: If you don't use this this abstract class, make sure you copy/paste
    the fields in.
    '''
    about_me = models.TextField(blank=True)
    facebook_id = BigIntegerField(blank=True, unique=True, null=True)
    access_token = models.TextField(
        blank=True, help_text='Facebook token for offline access')
    facebook_name = models.CharField(max_length=255, blank=True)
    facebook_profile_url = models.TextField(blank=True)
    website_url = models.TextField(blank=True)
    blog_url = models.TextField(blank=True)
    image = models.ImageField(blank=True, null=True,
        upload_to='profile_images', max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(('m', 'Male'), ('f', 'Female')), blank=True, null=True)
    raw_data = models.TextField(blank=True)

    def __unicode__(self):
        return self.user.__unicode__()

    class Meta:
        abstract = True

    def post_facebook_registration(self, request):
        '''
        Behaviour after registering with facebook
        '''
        from django_facebook.utils import next_redirect
        default_url = reverse('facebook_connect')
        response = next_redirect(request, default=default_url,
                                 next_key='register_next')
        response.set_cookie('fresh_registration', self.user_id)

        return response

    def get_offline_graph(self):
        '''
        Returns a open facebook graph client based on the access token stored
        in the user's profile
        '''
        from open_facebook.api import OpenFacebook
        if self.access_token:
            graph = OpenFacebook(access_token=self.access_token)
            graph.current_user_id = self.facebook_id
            return graph


class FacebookUser(models.Model):
    '''
    Model for storing a users friends
    '''
    # in order to be able to easily move these to an another db,
    # use a user_id and no foreign key
    user_id = models.IntegerField()
    facebook_id = BigIntegerField()
    name = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user_id', 'facebook_id']


class FacebookLike(models.Model):
    '''
    Model for storing all of a users fb likes
    '''
    # in order to be able to easily move these to an another db,
    # use a user_id and no foreign key
    user_id = models.IntegerField()
    facebook_id = BigIntegerField()
    name = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['user_id', 'facebook_id']
