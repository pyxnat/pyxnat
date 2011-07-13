from .uriutil import check_entry
from .jsonutil import JsonTable

class Users(object):
    """ Database user management interface. It is used to retrieve information
        on users registered on a server.

        .. note::
        
            At the moment user creation and deletion is not supported through 
            the REST API but it will be at some point.

        Examples
        --------
            >>> interface.manage.users()
            ['list_of_users']
            >>> interface.manage.users.firstname('nosetests')
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
        self._intf._get_entry_point()

        return JsonTable(self._intf._get_json('%s/users' % self._intf._entry)
                         ).get('login', always_list=True)

    def firstname(self, login):
        """ Returns the firstname of the user.
        """
        self._intf._get_entry_point()

        return JsonTable(self._intf._get_json('%s/users' % self._intf._entry)
                         ).where(login=login)['firstname']

    def lastname(self, login):
        """ Returns the lastname of the user.
        """
        self._intf._get_entry_point()

        return JsonTable(self._intf._get_json('%s/users' % self._intf._entry)
                         ).where(login=login)['lastname']

    def id(self, login):
        """ Returns the id of the user.
        """
        self._intf._get_entry_point()

        return JsonTable(self._intf._get_json('%s/users' % self._intf._entry)
                         ).where(login=login)['xdat_user_id']

    def email(self, login):
        """ Returns the email of the user.
        """
        self._intf._get_entry_point()

        return JsonTable(self._intf._get_json('%s/users' % self._intf._entry)
                         ).where(login=login)['email']


    def resources(self):
        """ Returns the resources of the user.
        """
        self._intf._get_entry_point()

        print self._intf._get_json(
            '%s/user/cache/resources' % self._intf._entry)
