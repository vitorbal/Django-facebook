from __future__ import with_statement
from django.contrib.auth.models import AnonymousUser
from django_facebook import exceptions as facebook_exceptions
from django_facebook.api import get_facebook_graph
from django_facebook.connect import connect_user, CONNECT_ACTIONS
from django_facebook.official_sdk import GraphAPIError
from django_facebook.tests.base import FacebookTest
import logging
import unittest



logger = logging.getLogger(__name__)

    
    
class UserConnectTest(FacebookTest):
    '''
    Tests the connect user functionality
    
    
    '''
    fixtures = ['users.json']
    
    def test_invalid_token(self):
        self.assertRaises(AssertionError, connect_user, self.request, access_token='invalid')

    def test_no_email_registration(self):
        self.assertRaises(facebook_exceptions.IncompleteProfileError, connect_user, self.request, access_token='no_email')
    
    def test_current_user(self):
        facebook = get_facebook_graph(access_token='tschellenbach', persistent_token=False)
        action, user = connect_user(self.request, facebook_graph=facebook)
        assert action == CONNECT_ACTIONS.LOGIN
    
    def test_new_user(self):
        facebook = get_facebook_graph(access_token='new_user', persistent_token=False)
        action, user = connect_user(self.request, facebook_graph=facebook)
    
    def test_short_username(self):
        facebook = get_facebook_graph(access_token='short_username', persistent_token=False)
        action, user = connect_user(self.request, facebook_graph=facebook)
        assert len(user.username) > 4
        assert action == CONNECT_ACTIONS.REGISTER
    
    def test_double_username(self):
        '''
        This used to give an error with duplicate usernames with different capitalization
        '''
        facebook = get_facebook_graph(access_token='short_username', persistent_token=False)
        action, user = connect_user(self.request, facebook_graph=facebook)
        user.username = 'Thierry_schellenbach'
        user.save()
        self.request.user = AnonymousUser()
        facebook = get_facebook_graph(access_token='same_username', persistent_token=False)
        action, new_user = connect_user(self.request, facebook_graph=facebook)
        assert user.username != new_user.username and user.id != new_user.id
    
class FQLTest(FacebookTest):
    def test_graph_fql(self):
        from api import get_app_access_token
        token = get_app_access_token()
        facebook = get_facebook_graph(access_token=token, persistent_token=False)
        query = 'SELECT name FROM user WHERE uid = me()'
        result = facebook.fql(query)
        assert result == []
    
    def test_fql(self):
        from django_facebook.official_sdk import fql
        query = 'SELECT name FROM user WHERE uid = me()'
        result = fql(query)
        assert not result
    
    

    
class DataTransformTest(FacebookTest):
    def test_doctest_api(self):
        from django_facebook import api
        import doctest
        doctest.testmod(api)





if __name__ == '__main__':
    
    unittest.main()