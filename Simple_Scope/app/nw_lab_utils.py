''''These are methods borrowed from nw lab, find the original code in the nw lab repo'''


# help_dict = dict(intro = "Welcome to the DateStamp module. Niftly little thing to keep formatting date time strings consistant and make it easier to call maybe \n",
#                 date_stamp = "date_stamp: A string representing the current Date (default YYYY.MM.DD)",
#                 time_stamp = "time_stamp: A string representing the current Time (default hh.mm.ss)",
#                 full_stamp = "full_stamp: A string representing the current Date and Time (default YYYY.MM.DD_hh.mm.ss)",
#                 datestamp = "datestamp(): an Alies for full_stamp for legacy compatability",
#                 formatting_seperator = "formatting_seperator: the character used between elements of date and time, Default - '.'",
#                 formatting_spacer = "formatting_spacer: the character used between date and time strings, Default - '_'")    

import datetime
# from .base_classes import base_class

class DateStamp:
    
    def __new__(cls):
#         print("__new__")
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
            cls.instance._singleton_init_()
        return cls.instance
    
    def __init__(self):
        pass
        
    def _singleton_init_(self):
#         print("_singleton_init_")
        self._fse = '.' 
        self._fsp = '_'
    
    @property # maybe a little excessive but this is just to make the string formatting lines shorter...
    def formatting_seperator(self):
        return self._fse

    @formatting_seperator.setter
    def formatting_seperator(self, char):
        self._fse = char  

    @property # maybe a little excessive but this is just to make the string formatting lines shorter...
    def formatting_spacer(self):
        return self._fsp

    @formatting_spacer.setter
    def formatting_spacer(self, char):
        self._fsp = char
    
    def _date_stamp(self):
        return datetime.datetime.now().strftime(f"%Y{self._fse}%m{self._fse}%d")

    def _time_stamp(self):
        return datetime.datetime.now().strftime(f"%H{self._fse}%M{self._fse}%S")

    def _full_stamp(self):
        return datetime.datetime.now().strftime(f"%Y{self._fse}%m{self._fse}%d{self._fsp}%H{self._fse}%M{self._fse}%S")

    @property
    def date_stamp(self):
        return self._date_stamp()
        # return datetime.datetime.now().strftime(f"%Y{self._fse}%m{self._fse}%d")

    @property
    def time_stamp(self):
        return self._time_stamp()
        # return datetime.datetime.now().strftime(f"%H{self._fse}%M{self._fse}%S")

    @property
    def full_stamp(self):
        return self._full_stamp()
        # return datetime.datetime.now().strftime(f"%Y{self._fse}%m{self._fse}%d{self._fsp}%H{self._fse}%M{self._fse}%S")
        
    # def help(self, help_with=None):
    #     '''should this be a baseclass or something'''
    #     if help_with:
    #         print(help_dict.get(help_with, f"{help_with} not found in DateStamp module"))
    #     else:
    #         print('\n'.join(help_dict.values()))


