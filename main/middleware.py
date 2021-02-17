from django.conf import settings
from django.contrib import auth
from datetime import datetime, timedelta
import time


'''
    AutoInactivityLogout:
        with each user request check the time difference between this request
        and the previous request. If difference exceeds AUTO_LOGOUT_DELAY (defined
        in settings) then logout user due to exceeding inactivity period.
        
        Code structure based on django documentation
'''
class AutoInactivityLogOut:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'last_request_time' in request.session:
            if request.user.is_authenticated:
                # User must be logged in to be considered to logging out
                if(time.time() - request.session['last_request_time'] > settings.AUTO_LOGOUT_DELAY):
                    # inactive long enough and log out
                    auth.logout(request)
                else:
                    # reset timer due to recent activity
                    request.session['last_request_time'] = time.time()
        else:
            # this must be the first request for the user
            # add 'last_request_time' to request.session
            request.session['last_request_time'] = time.time()

        response = self.get_response(request)

        return response