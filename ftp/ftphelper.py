#!/usr/bin/python3k
# -*- coding: utf-8 -*-
###########################################################
# Feature: ftp helper
# Author : Bing
# Version: 1.1
# Email  : kun1.huang@outlook.com
# Date   : 2016-11-24
###########################################################

from ftplib import FTP
import sc_project.base_lib as base_lib

class FtpHelper:
    """ Ftp_helper """
    def __init__(self, host, user, passwd, port=21):
        self.host = host
        self.user = user
        self.password = passwd
        self.port = port
        self.ftp = self.connect()
        print(self.ftp.getwelcome())

    def connect(self, debug=False):
        """ Ftp_helper """
        if self.host and self.user and self.password and self.port:
            try:
                ftp = FTP()
                ftp.connect(self.host, self.port)
                ftp.login(self.user, self.password)
                ########
                #ftp.set_debuglevel(2)
                return ftp
            except Exception as ex:
                raise ex
        else:
            return None


    def download_file(self, src, dest):
        """ Ftp_helper """
        try:
            bufsize = 1024
            dest = base_lib.get_dest_file(src, dest)
            file = open(dest, 'wb')
            self.ftp.retrbinary('RETR %s'%src, file.write, bufsize)
            #ftp.set_debuglevel(0)
            file.close()
            return True
        except Exception as ex:
            raise ex

    def get_file_list(self, src=''):
        """ Ftp_helper """
        try:
            if src:
                self.ftp.cwd(src)
            filelist = self.ftp.nlst()
            return filelist
        except Exception as ex:
            raise ex

    def remove_file(self, src):
        """ Ftp_helper """
        try:
            res = self.ftp.delete(src)
            return res
        except Exception as ex:
            raise ex

    def upload_file(self, src, dest=''):
        """ Ftp_helper """
        pass

    def close(self):
        """ Ftp_helper """
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as ex:
                raise ex

    def is_file_exists(self, src):
        """ Ftp_helper """
        try:
            self.ftp.cwd(src)
            return True
        except Exception as ex:
            print(ex)
            return False

    def is_connected(self):
        """ Ftp_helper """
        if self.ftp:
            return True
        return False

    def cwd(self, dest):
        """ Ftp_helper """
        if dest:
            try:
                self.ftp.cwd(dest)
                return True
            except Exception as ex:
                raise ex
        return True


