import itertools
import pickle
import sys

from selenium.webdriver import Firefox  # pip install selenium

import course_class

# from selenium.webdriver.support.ui import WebDriverWait
sys.setrecursionlimit(2000)
subj_url = 'http://www.graduate.technion.ac.il/eng/subjects/?SUB='
driver_timeout = 30
driver_timeout2 = 2
tries = 7
conn_types = ['Prerequisites:', 'Overlapping Courses:', 'Linked Courses:', 'Incorporated Courses:',
              'Incorporating Courses:', 'Identical Courses:']


def get_course(browser, id):
    link = subj_url + str(id)
    browser.get(link)
    # WebDriverWait(browser, timeout=driver_timeout).until(lambda x: x.find_element_by_class_name('update'))
    namenum = browser.find_elements_by_tag_name('span')[1].text  # dirty
    name_num_list = namenum.split('-')
    name = '-'.join(name_num_list[:-1]).strip()
    name = ' '.join(name.split())
    number = int(name_num_list[-1].strip())
    
    points_table = browser.find_element_by_id('points').find_element_by_tag_name('tbody').find_element_by_tag_name('tr')
    credit_points = float(points_table.find_elements_by_tag_name('td')[1].text)
    
    is_given = len(browser.find_elements_by_class_name('red')) == 0
    # is_given_not_known = len(browser.find_elements_by_class_name('green')) != 0 and 'Will be learned' in
    # browser.find_element_by_class_name('green').text
    is_given_not_known = len(points_table.find_elements_by_tag_name('td')) < 12
    
    is_given_a = False
    is_given_b = False
    is_given_summer = False
    
    if is_given and not is_given_not_known:
        given_str = points_table.find_elements_by_tag_name('td')[4].text
        for sem in given_str.split('+'):
            if sem == 'a':
                is_given_a = True
            elif sem == 'b':
                is_given_b = True
            elif sem == 'Summer':
                is_given_summer = True
        hours_start = 7
    else:
        hours_start = 4
    
    hours = {}
    h = []
    for i in range(5):
        txt = points_table.find_elements_by_tag_name('td')[hours_start + i].text
        h.append(float(txt) if txt != ' ' else 0.0)
    
    hours['lecture'] = h[0]
    hours['exercise'] = h[1]
    hours['laboratory'] = h[2]
    hours['project_seminar'] = h[3]
    hours['homework'] = h[4]
    
    conn_course_dict = {}
    for conn in conn_types:
        conn_course_dict[conn] = []
    
    try:
        connected_courses = browser.find_element_by_class_name('tab0').find_element_by_tag_name('tbody')
        current = ' '
        for row in connected_courses.find_elements_by_tag_name('tr'):
            columns = row.find_elements_by_tag_name('td')
            if len(columns) == 1:
                continue
            if columns[0].text.strip() != '':
                current = columns[0].text.strip()
            if columns[0].text.strip() != '' or columns[1].text.strip() != '':
                conn_course_dict[current].append([])
            conn_course_dict[current][-1].append(int(columns[5].text))
    except:
        pass
    if len(conn_types) < len(conn_course_dict):
        print(conn_course_dict)
        with open('att.txt', 'a') as file:
            file.write('{}\n'.format(i))
    
    description = browser.find_element_by_class_name('syl').text
    
    course = course_class.Course(number, name, is_given, is_given_a, is_given_b, is_given_summer,
                                 conn_course_dict['Prerequisites:'], conn_course_dict['Overlapping Courses:'],
                                 conn_course_dict['Incorporated Courses:'], conn_course_dict['Incorporating Courses:'],
                                 conn_course_dict['Linked Courses:'], conn_course_dict['Identical Courses:'],
                                 credit_points, hours, description, link)
    return course


def get_all_existing_courses(browser):
    courses = []
    # with open('courses.txt', 'w') as file:
    #    file.write('')
    faculties = {}
    with open('failes.txt', 'w') as file:
        file.write('')
    faculty_url = 'http://www.graduate.technion.ac.il/eng/faculties/subject.asp?faculty='
    for i in range(100):
        link = faculty_url + str(i)
        browser.get(link)
        try:
            coursestable = browser.find_element_by_class_name('border').find_element_by_tag_name('tbody')
        except:
            continue
        
        fname = browser.find_element_by_class_name('main_header').text.split('-')[1].strip()
        faculties[fname] = []
        for row in coursestable.find_elements_by_tag_name('tr'):
            num = int(row.find_elements_by_tag_name('td')[-1].text)
            courses.append(num)
            faculties[fname].append(num)
            with open('courses.txt', 'a') as file:
                file.write(str(num) + '\n')
                # print(num)
        print('{} - {}'.format(i, fname))
    faculty_url2 = 'http://ug.technion.ac.il/Catalog/CatalogEng/fac{}.html'
    for i in range(100):
        link = faculty_url2.format(str(i).zfill(3))
        browser.get(link)
        try:
            coursestable = browser.find_element_by_tag_name('ul').find_elements_by_tag_name('li')
        except:
            continue
        
        fname = browser.find_element_by_tag_name('table').find_element_by_tag_name('tbody').find_element_by_tag_name(
            'tr').find_elements_by_tag_name('td')[1].text.split('-')[0].strip()
        if not fname in faculties:
            faculties[fname] = []
        for row in coursestable:
            num = int(row.text.split('-')[0])
            courses.append(num)
            faculties[fname].append(num)
            with open('courses.txt', 'a') as file:
                file.write(str(num) + '\n')
                # print(num)
        print('{} - {}'.format(i, fname))
    courses = sorted(list(set(courses)))
    with open('faculties.pickle', 'wb') as file:
        pickle.dump(faculties, file)
    return courses


def get_all_courses(browser, courses_ex):
    courses = {}
    with open('failes.txt', 'w') as file:
        file.write('')
    count = 0
    for i in courses_ex:
        result = None
        t = 0
        # try tries times or until succeed
        while result is None and t < tries:
            try:
                # connect
                result = get_course(browser, i)
            except:
                t = t + 1
        count += 1
        if result is None:
            print('FAIL: {}'.format(i))
            with open('failes.txt', 'a') as file:
                file.write('{}\n'.format(i))
        else:
            print('{}/{}: {}'.format(count, len(courses_ex), result.short_str()))
            courses[result.number] = result
            filename = 'courses/' + str(i).strip() + '.pickle'
            with open(filename, 'wb') as file:
                pickle.dump(result, file)
            for x in list(itertools.chain.from_iterable(result.linked)):
                if x not in courses_ex:
                    courses_ex.append(x)
                    print('ADDED: {}'.format(x))
            for x in list(itertools.chain.from_iterable(result.requires)):
                if x not in courses_ex:
                    courses_ex.append(x)
                    print('ADDED: {}'.format(x))
            for x in list(itertools.chain.from_iterable(result.overlaps)):
                if x not in courses_ex:
                    courses_ex.append(x)
                    print('ADDED: {}'.format(x))
            for x in list(itertools.chain.from_iterable(result.incorporates)):
                if x not in courses_ex:
                    courses_ex.append(x)
                    print('ADDED: {}'.format(x))
            for x in list(itertools.chain.from_iterable(result.incorparated)):
                if x not in courses_ex:
                    courses_ex.append(x)
                    print('ADDED: {}'.format(x))
            for x in list(itertools.chain.from_iterable(result.identical)):
                if x not in courses_ex:
                    courses_ex.append(x)
                    print('ADDED: {}'.format(x))
    
    with open('courses_ex.pickle', 'wb') as file:
        pickle.dump(courses_ex, file)
    return courses


def run_get_courses():
    # run browser
    started = False
    while not started:
        try:
            browser = Firefox()
            started = True
        except:
            pass
    
    browser.set_page_load_timeout(8)
    browser.set_script_timeout(8)
    
    # get courses' numbers
    courses_ex = get_all_existing_courses(browser)
    with open('courses_ex.pickle', 'wb') as file:
        pickle.dump(courses_ex, file)
    
    courses = get_all_courses(browser, courses_ex)
    with open('courses1.pickle', 'wb') as file:
        pickle.dump(courses, file)
    browser.close()
    
    # with open('courses1.pickle', 'rb') as file:
    #    courses = pickle.load(file)
    print('{} courses loaded'.format(len(courses)))
    
    with open('faculties.pickle', 'rb') as file:
        faculties = pickle.load(file)
    
    courses[104223].requires = [[104013, 104016, 104131], [104014, 104016, 104131], [104020, 104016, 104131],
                                [104022, 104016, 104131], [104281, 104016, 104131], [104013, 104171, 104131],
                                [104014, 104171, 104131], [104020, 104171, 104131], [104022, 104171, 104131],
                                [104281, 104171, 104131], [104013, 104016, 104135], [104014, 104016, 104135],
                                [104020, 104016, 104135], [104022, 104016, 104135], [104281, 104016, 104135],
                                [104013, 104171, 104135], [104014, 104171, 104135], [104020, 104171, 104135],
                                [104022, 104171, 104135], [104281, 104171, 104135], [104013, 104016, 104285],
                                [104014, 104016, 104285], [104020, 104016, 104285], [104022, 104016, 104285],
                                [104281, 104016, 104285], [104013, 104171, 104285], [104014, 104171, 104285],
                                [104020, 104171, 104285], [104022, 104171, 104285], [104281, 104171, 104285]]
    courses = course_class.fill_required(courses)
    courses = course_class.fill_all_required(courses)
    courses = course_class.fill_faculties(courses, faculties)
    courses = course_class.fill_requirement_depth(courses)
    
    with open('courses.pickle', 'wb') as file:
        pickle.dump(courses, file)
    print('Processing finished')


def load_ready_courses():
    with open('courses.pickle', 'rb') as file:
        courses = pickle.load(file)
    return courses


run_get_courses()
courses = load_ready_courses()
