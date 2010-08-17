import os

from .jsonutil import JsonTable

class Users(object):
    """ Database user management interface. It is used to retrieve information
        on users registered on a server.

        .. note::
        
            At the moment user creation and deletion is not supported through 
            the REST API but it will be at some point.

        Examples
        --------
            >>> interface.users()
            ['list_of_users']
            >>> interface.firstname('nosetests')
            'nose'

        See Also
        --------
        Project.users()
        Project.add_user()
        Project.remove_user()
    """

    def __init__(self, interface):
        """ 
            Parameters
            ----------
            interface: :class:`Interface`
                Main interface reference.
        """
        self._intf = interface

    def __call__(self):
        """ Returns the list of all registered users on the server.
        """
        return JsonTable(self._intf._get_json('/REST/users')).get('login', always_list=True)

    def firstname(self, login):
        """ Returns the firstname of the user.
        """
        return JsonTable(self._intf._get_json('/REST/users')).where(login=login)['firstname']

    def lastname(self, login):
        """ Returns the lastname of the user.
        """
        return JsonTable(self._intf._get_json('/REST/users')).where(login=login)['lastname']

    def id(self, login):
        """ Returns the id of the user.
        """
        return JsonTable(self._intf._get_json('/REST/users')).where(login=login)['xdat_user_id']

    def email(self, login):
        """ Returns the email of the user.
        """
        return JsonTable(self._intf._get_json('/REST/users')).where(login=login)['email']

