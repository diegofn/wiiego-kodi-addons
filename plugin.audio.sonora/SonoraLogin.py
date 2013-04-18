#/*
# *
# * Sonora: Sonora add-on for XBMC.
# *
# * Copyright (C) 2013 Wiiego
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# * 
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import re
import sys
import time
try: import simplejson as json
except ImportError: import json

# ERRORCODES:
# 0 = Ignore
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

class SonoraLogin():
    def __init__(self):
        self.xbmc = sys.modules["__main__"].xbmc
        self.pluginsettings = sys.modules["__main__"].pluginsettings
        self.settings = sys.modules["__main__"].settings
        self.common = sys.modules["__main__"].common
        self.enabledebug = sys.modules["__main__"].enabledebug
        self.core = sys.modules["__main__"].core

    def login(self, params={}):
        get = params.get
        self.common.log("Login")
        
        username = self.pluginsettings.userName()
        userpassword = self.pluginsettings.userPassword()
        result = ""
        status = 500

        # Make the authentication
        result, status = self.core.account_auth(username, userpassword)
        return (result, status)

    
