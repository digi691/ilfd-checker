#!/bin/usr/env python

__author__ = 'cdigiovanni'
import urllib2
import pickle
import os
import sys
from subprocess import Popen, PIPE
from email.mime.text import MIMEText
from bs4 import BeautifulSoup

class FieldDayChecker(object):
    def __init__(self):
        self.url = "http://www.dnr.illinois.gov/safety/EducationCourses/fieldday.htm"
        self.html_page = self.get_page(self.url)
        self.class_table = self.parse_page()
        self.count = self.count_classes(self.class_table)
        self.previous_count = None

    def get_page(self, url):
        response = urllib2.urlopen(url)
        html_page = response.read()
        return html_page

    def parse_page(self):
        soup = BeautifulSoup(self.html_page)
        table = soup.table
        return table

    def count_classes(self, table):
        class_count = []
        for row in table.find_all("tr"):
            class_count.append(row)
        return len(class_count) - 1

def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, "Usage: {0} youremail@email.com".format(sys.argv[0])
        exit(1)
    home = os.path.expanduser("~")
    checker = FieldDayChecker()
    try:
        file = open('%s/fdchecker.pkl' % home, 'r')
        data = pickle.load(file)
        checker.previous_count = data
    except:
      pass
    file = open('%s/fdchecker.pkl' % home, 'w+')
    pickle.dump(checker.count,file)
    if checker.previous_count == None or checker.previous_count == checker.count:
        exit(0)
    elif checker.previous_count < checker.count:
        msg = MIMEText("A new class has been added to the schedule\n%s" % checker.url)
    else:
        msg = MIMEText("A class has been dropped from the schedule\n%s" % checker.url)
    msg['Subject'] = "Hunter Safety Course Schedule Update!"
    msg['From'] = argv[1]
    msg['To'] = argv[1]
    p = Popen(["/usr/bin/sendmail", "-t"], stdin=PIPE)
    p.communicate(msg.as_string())

if __name__ == "__main__":
    main(sys.argv)
