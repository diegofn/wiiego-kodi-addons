#/*
# *
# * ColombiaTV: ColombiaTV add-on for Kodi.
# *
# * Copyleft 2013-2020 Wiiego
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
import sys

class ColombiaTVPluginSettings():

    def __init__(self):
        self.addon = sys.modules["__main__"].addon
        self.enabledeveloper = sys.modules["__main__"].enabledeveloper
        self.enabledebug = sys.modules["__main__"].enabledebug

    def enabledebug(self):
        return self.addon.getSetting("enabledebug") == "false"

    def enabledeveloper(self):
        return self.addon.getSetting("enabledeveloper") == "false"

