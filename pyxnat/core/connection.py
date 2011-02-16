class ConnectionManager(object):
    def __init__(self, interface):
        self._intf = interface

    def set_strategy(self, name):
        """ Set the connection strategy.

            Possible values for the stategy are:
                - default: always query the resources online and uses a 
                1 second memcache
                - strict: always query the resources online without 
                any memcache
                - fast: only query the resources that are not in cache 
                but performs a sync at the first connection to be up to 
                date with the server
                - offline: only query the resources that are not in cache
        """
        if name == 'strict':
            self._intf._last_memtimeout = self._intf._memtimeout
            self._intf._last_mode = self._intf._mode
            self._intf._mode = 'online'
            self._intf._memtimeout = 0.0
        elif name == 'fast':
            self._intf._last_memtimeout = self._intf._memtimeout
            self._intf._last_mode = self._intf._mode
            self._intf._mode = 'offline'
            self._intf._memtimeout = 1.0
        elif name == 'offline':
            self._intf._last_memtimeout = self._intf._memtimeout
            self._intf._last_mode = self._intf._mode
            self._intf._mode = 'offline'
            self._intf._memtimeout = 1.0
        else:
            self._intf._last_memtimeout = self._intf._memtimeout
            self._intf._last_mode = self._intf._mode
            self._intf._mode = 'online'
            self._intf._memtimeout = 1.0

    def revert_strategy(self):
        _ = self._intf._memtimeout
        __ = self._intf._mode
        self._intf._memtimeout = self._intf._last_memtimeout
        self._intf._mode = self._intf._last_mode
        self._intf._last_memtimeout = _
        self._intf._last_mode = __

