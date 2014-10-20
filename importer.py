#!/usr/bin/env python

import re
import requests
import sys

import phabricator
import conf

phab = phabricator.Phabricator(conf.HOST, conf.USER, conf.CERT)


def get_bz_title(num):
    url = 'https://bugzilla.wikimedia.org/show_bug.cgi?id=%s' % num
    r = requests.get(url)
    title = re.findall('<title>(.*?)</title>', r.text)
    if not title:
        print 'Error: Could not extract title from <%s>.' % url
        quit()
    return title[0].split('&ndash;', 1)[1].strip()


def get_project_phid(phab, name):
    data = phab.request('project.query', {
        'names': [name]
    })
    return data['data'].keys()[0]


def build_descr(num):
    return """
This is a placeholder for <https://bugzilla.wikimedia.org/%s>, so it can be used inside a Phabricator board.

There may be patches related to this bug at <https://gerrit.wikimedia.org/r/#/q/bug:%s,n,z>.
    """.strip() % (num, num)


def convert_bz_to_phab(num):
    phid = get_project_phid(phab, conf.PHAB_PROJ)
    title = get_bz_title(num)
    title = '[Bug %s] %s' % (num, title)  # [Bug 123] The description
    task = phab.request('maniphest.createtask', {
        'title': title,
        'description': build_descr(num),
        'projectPHIDs': [phid],
    })
    print 'Created %s' % task['uri']
    return task


if __name__ == '__main__':
    num = sys.argv[1]
    convert_bz_to_phab(num)
