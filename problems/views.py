from django.shortcuts import render
import requests as req
import os
from .models import Ladder
# from ..accounts/models import accounts_userdata
from django.contrib.auth.models import User
# Create your views here.


# def get_problems(request):
#     export_ladders()
#     return render(request, 'problems.html')

# To pre-render a ladder database
# for future use (if it does not exist)
def export_ladders():

    # Return this for use in dropdown menu
    for_dropdown = []

    fs = os.listdir('saved')
    dirs = {}
    for f in fs:
        t = f.split('.')
        dirs[int(t[0])] = t[1].strip().replace('L', '<').replace(
            'G', '>').replace(' ', '_') + '.' + t[2]
        print(dirs[int(t[0])])

    for l_num in (dirs):

        l_name = dirs[l_num].replace('_', ' ')
        for_dropdown.append([dirs[l_num].replace('_', ' ')[0:-4], l_num+1])

        # Name in saved folder
        fname = os.path.join(('saved'), (str(
            l_num) + '. ' + dirs[l_num].replace('<', 'L').replace('>', 'G').replace('_', ' ')))

        # If Ladder not found in DB
        if Ladder.objects.filter(name__startswith=l_name).count() == 0:

            # Make a new Ladder
            lad = Ladder(name=l_name)
            lad.save()

            # and fill the Ladder with contents of file(Problems)
            f = open(fname, 'r')
            print('opening:', fname)
            total = 0

            for line in f.readlines():
                k = line.split('|')
                lad.problem_set.create(pid=k[1], name=k[0], link=str(k[3])[
                                       0:-1], difficulty=int(k[2]))
                lad.save()
                # print(k)
                # pr = Problem()
                # pr.save()
                total += 1

            # Update total Questions
            lad.total_q = total
            lad.save()
            print('Done exporting', k[0])
        else:
            print('if condition false')
    return for_dropdown


def get_problems(request, prob_id=0):
    dropdown = export_ladders()

    # To be commented after getting dynamic input
    handle = 'haritmohanhm'

    # Make a list of list to pass in render function
    print_ladder = []
    ak = Ladder.objects.get(pk=prob_id+1).problem_set.all()

    if User.is_authenticated:

        # handle = accounts_userdata.objects.filter()
        while(1):
            obj = req.get(
                'https://codeforces.com/api/user.status?handle=' + handle).json()
            if obj['status'] == 'OK':
                break

        # print(obj['result'][0]['problem'])

        all_problems_verdict = {}

        for submission in obj['result']:
            id = str(submission['problem']['contestId']) + \
                submission['problem']['index']
            verdict = submission['verdict']

            if id not in all_problems_verdict:
                all_problems_verdict[id] = []

            if verdict not in all_problems_verdict[id]:
                all_problems_verdict[id].append(verdict)
        solved = 0
        for k in ak:
            if k.pid in all_problems_verdict:
                if 'OK' in all_problems_verdict[k.pid]:
                    status = 'Accepted'
                    solved += 1
                else:
                    status = all_problems_verdict[k.pid][0]
            else:
                status = 'Not Attempted'
            print_ladder.append([k.name, k.link, status, k.difficulty])
    else:
        for k in ak:
            print_ladder.append(
                [k.name, k.link, 'Not Attempted', k.difficulty])
    dropdown.sort(key=lambda x: x[1])
    print(print_ladder)
    print(dropdown)
    return render(request, 'problems.html', {'ladder': print_ladder, 'items': dropdown, 'solved': solved, 'total': Ladder.objects.get(pk=prob_id+1).total_q})