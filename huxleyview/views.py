#!/bin/env python
# -*- coding: utf-8 -*-
#Filename:  view.py
#Date:      2013-09-03
import os
import re
import glob
import json
import pprint

from django.conf import settings
from django.shortcuts import render_to_response
from django.views.decorators.http import require_POST
from django.http import HttpResponse, Http404, HttpResponseRedirect

def home(request):
    tcase_history = _get_tcase_history('npmhelp')
    return render_to_response('index.html')

def history(request, tcasepath="None", btime='00000000000000', etime='00000000000000'):
    print tcasepath
    tcase_history = _get_tcase_history(tcasepath, btime, etime)
    return render_to_response('tests.html', _render_val(tcase_history))

@require_POST
def get_latest_testcase(request):
    latest_run_time = _get_all_testcase_run_times()[-1][0]
    return HttpResponse(json.dumps({
                                    'data':_get_all_testcase_by_time(latest_run_time),
                                    'timestamp':latest_run_time
                                    })
                        )

@require_POST
def get_all_testcase_run_times(request):
    return HttpResponse(json.dumps(_get_all_testcase_run_times()))

@require_POST
def get_all_testcase(request):
    return HttpResponse(json.dumps(_get_all_testcase_by_time(request.POST.get('timestamp'))))

def _render_val(tcase_history):
    val = {'projects':[tcase_history['project']],
           'tcasepath':tcase_history['tcasepath'],
           'steps': sorted(tcase_history['screenshots'].keys(), key=lambda x:int(x[4:])),
           'screenshots':tcase_history['screenshots']}
    pprint.pprint(val)
    return val

def _get_all_testcase_run_times():
    """get all testcase run times
    exp:
        _get_all_testcase_run_times()
        -->return
        [('20130101000000', 'failed'), ('20130102000000','ok') ...]
    """
    testcase_run_time_list = []
    for root, dirs, files in os.walk(settings.HUXLEY_TEST_ROOT):
        for idir in dirs:
            if re.match(r'\d+', idir) and (not idir in [item[0] for item in testcase_run_time_list]):
                testcases = _get_all_testcase_by_time(idir)
                if 'failed' in [item[1] for item in testcases]:
                    testcase_run_time_list.append((idir, 'failed'))
                else:
                    testcase_run_time_list.append((idir, 'ok'))
    return sorted(testcase_run_time_list, key=lambda x:x[0])

def _get_all_testcase_by_time(timestamp):
    """get all testcase by time
    exp:
        _get_all_testcase_by_time('20130101000000')
        -->return
        [('test_npm/test_npmhelp', 'failed'), ('test_npm/test_npmhelp_en', 'ok')...]
    """
    testcase_list = []
    for root, dirs, files in os.walk(settings.HUXLEY_TEST_ROOT):
        if timestamp in dirs:
            if glob.glob(os.path.join(root, timestamp, '*diff.png')):
                testcase_list.append((os.path.relpath(root, settings.HUXLEY_TEST_ROOT), 'failed'))
            else:
                testcase_list.append((os.path.relpath(root, settings.HUXLEY_TEST_ROOT), 'ok'))
    return sorted(testcase_list, key=lambda x:x[0])

def _get_tcase_history(tcasepath='Noname', btime='00000000000000', etime='20300000000000'):
    """return project screenshots json

    for exp:
    {
        'project':'npmhelp',
        'tcasepath':'test_npmhelp/npmhelp.huxley',
        'screenshots':
            {'step0':[
                            {
                                'prev':{'name':'screenshot0.png',       'timestamp':'20130801000000'},
                                'curr':{'name':'screenshot0.png',       'timestamp':'20130802000000'},
                                'diff':{'name':'screenshot0_diff.png',  'timestamp':'20130802000000'},
                            },
                            {
                                'prev':{'name':'screenshot0.png',       'timestamp':'20130801000000'},
                                'curr':{'name':'screenshot0.png',       'timestamp':'20130802000000'},
                                'diff':{'name':'screenshot0_diff.png',  'timestamp':'20130802000000'},
                            },
                            ...
                      ]
            },

            'step1':[
            ],
            ...
        ]

    }
    """
    tcase_image_path = _get_tcase_image_path(tcasepath)
    if not os.path.exists(tcase_image_path):
        return None
    history_screenshot_paths = _get_all_history_screenshot_time(tcase_image_path, btime, etime)

    his_result = {'project':os.path.basename(tcasepath).rstrip('.huxley'),
                  'tcasepath':tcasepath, 'screenshots':{}}

    for screenshot_time in history_screenshot_paths:
        for item in gen_steps_history_item(tcase_image_path, screenshot_time):
            step = "step%s" % item['step']
            if step in his_result['screenshots'].keys():
                his_result['screenshots'][step].append(item['history'])
            else:
                his_result['screenshots'][step] = [item['history']]

    #sort by timestamp
    for step, history in his_result['screenshots'].items():
        his_result['screenshots'][step] = sorted(history[:], key=lambda i:i['curr']['timestamp'])
    return his_result

def gen_steps_history_item(tcase_image_path, curr):
    """gen steps history item

    for exp:
        current testcase result:.
        `-- npmhelp.huxley
            |-- 20130830152009
            |   `-- screenshot0.png
            |-- 20130830152414
            |   `-- screenshot0.png
            |-- 20130830152743
            |   |-- screenshot0.png
            |   `-- screenshot0_diff.png
            `-- record.json

            gen_steps_history_item('../npmhelp.huxley/', '20130830152414')
                ==>return
                    {'step':0
                     'history':
                                {
                                    'prev':{'name':'screenshot0.png',       'timestamp':'20130830152009'},
                                    'curr':{'name':'screenshot0.png',       'timestamp':'20130830152414'},
                                    'diff':{'name':None,                    'timestamp':None},
                                }
                    },

            gen_steps_history_item('../npmhelp.huxley/', '20130830152743')
                ==>return
                    {'step':0
                     'history':
                                {
                                    'prev':{'name':'screenshot0.png',       'timestamp':'20130830152414'},
                                    'curr':{'name':'screenshot0.png',       'timestamp':'20130830152743'},
                                    'diff':{'name':'screenshot0_diff.png',  'timestamp':'20130830152414'},
                                }
                    },


    """
    all_history_time = _get_all_history_screenshot_time(tcase_image_path)
    his_iter_case = {}
    for item in os.listdir(os.path.join(tcase_image_path, curr)):
        re_image_name = re.match(r'(%s)(\d+).png' % settings.HUXLEY_IMAGE_PREFIX, item)
        if re_image_name:
            his_iter_case['step'] = re_image_name.groups()[1]
            his_iter_case['history'] = {}

            his_curr_name = "%s%s.png" % (settings.HUXLEY_IMAGE_PREFIX, his_iter_case['step'])
            his_prev_name = "%s%s.png" % (settings.HUXLEY_IMAGE_PREFIX, his_iter_case['step'])
            his_diff_name = "%s%s_diff.png" % (settings.HUXLEY_IMAGE_PREFIX, his_iter_case['step'])

            item_index = all_history_time.index(curr)
            his_iter_case['history']['curr'] = \
                    {'name': his_curr_name, 'timestamp':curr}

            if item_index > 0 and \
                    os.path.exists(os.path.join(tcase_image_path, all_history_time[item_index-1], his_prev_name)):
                his_iter_case['history']['prev'] = \
                        {'name':his_prev_name, 'timestamp':all_history_time[item_index-1]}
            else:
                his_iter_case['history']['prev'] = {'name':None, 'timestamp':None}

            if os.path.exists(os.path.join(tcase_image_path, curr, his_diff_name)):
                his_iter_case['history']['diff'] = {'name':his_diff_name, 'timestamp':curr}
            else:
                his_iter_case['history']['diff'] = {'name':None, 'timestamp':None}

            yield his_iter_case
        else:
            continue

def _get_tcase_image_path(tcasepath):
    return os.path.join(settings.HUXLEY_TEST_ROOT, tcasepath)


def _get_all_history_screenshot_time(tcase_image_path, btime='00000000000000', etime='20300000000000'):
    return sorted([item for item in os.listdir(tcase_image_path) \
                             if os.path.isdir(os.path.join(tcase_image_path, item)) \
                             and item >= btime and item <= etime])


