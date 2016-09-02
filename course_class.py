import itertools

faculties_tmp = {}


class Course:
    def __init__(self, number, name, is_given, is_given_a, is_given_b, is_given_summer, requires, overlaps,
                 incorporates, incorparated, linked, identical, credit_points, hours, description, url):
        self.number = number
        self.name = name
        self.is_given = is_given
        self.is_given_a = is_given_a
        self.is_given_b = is_given_b
        self.is_given_summer = is_given_summer
        self.requires = requires
        self.required = []
        self.overlaps = overlaps
        self.incorporates = incorporates
        self.incorparated = incorparated
        self.linked = linked
        self.linked_with = []
        self.identical = identical
        self.credit_points = credit_points
        self.hours = hours
        self.requirement_depth = -1
        self.description = description
        self.url = url
        self.total_hours = hours['lecture'] + hours['exercise'] + hours['laboratory'] + hours['project_seminar'] + \
                           hours['homework']
        self.faculty = ''
        self.all_required = []
    
    def __str__(self):
        return 'Course {} of faculty {}: {}\nIs given: {}. A: {}. B: {}. Summer: {}.\nPoints: {}\nHours: {}. ' \
               'Total hours: {}.\nRequired by: {}.\nLinked with:{}\nLinked: {}\nRequires: {}. requirement depth: {}\n' \
               'Overlaps with: {}\nIncorporates: {}\nIncorporated by: {}\nDescription: {}\nURL: {}\n\n'.format(
            self.number, self.faculty, self.name, self.is_given, self.is_given_a, self.is_given_b, self.is_given_summer,
            self.credit_points, self.hours, self.total_hours, self.required, self.linked_with, self.linked,
            self.requires, self.requirement_depth, self.overlaps, self.incorporates, self.incorparated,
            self.description, self.url)
    
    def short_str(self):
        return '{} {}'.format(self.number, self.name)


def fill_required(courses):
    for num, course in courses.items():
        for req_course in list(itertools.chain.from_iterable(course.requires)):
            if req_course in courses:
                courses[req_course].required.append(num)
                # else:
                # print(req_course)
        for req_course in list(itertools.chain.from_iterable(course.linked)):
            if req_course in courses:
                courses[req_course].linked_with.append(num)
                # else:
                # print(req_course)
    return courses


def in_req_tree(checked_list, courses, course_searched, course_in):
    for c in list(itertools.chain.from_iterable(courses[course_in].requires)):
        if c in checked_list:
            continue
        checked_list.append(c)
        if c == course_searched:
            return True
        if in_req_tree(checked_list, courses, course_searched, c):
            return True
    
    for c in list(itertools.chain.from_iterable(courses[course_in].linked)):
        if c in checked_list:
            continue
        checked_list.append(c)
        if c == course_searched:
            return True
        if in_req_tree(checked_list, courses, course_searched, c):
            return True
    return False


def fill_requirement_depth(courses):
    fill_list = {}
    
    for num, course in courses.items():
        if len(course.requires) == 0 and len(course.linked) == 0:
            course.requirement_depth = 0
            fill_list[num] = 1
    filled = True
    count = 0
    while filled:
        count += 1
        filled = False
        for num, course in courses.items():
            if num in fill_list:
                continue
            ready = True
            for c in list(itertools.chain.from_iterable(course.requires)):
                if courses[c].requirement_depth == -1 and not in_req_tree([], courses, num, c):
                    ready = False
                    break
            if not ready:
                continue
            for c in list(itertools.chain.from_iterable(course.linked)):
                if courses[c].requirement_depth == -1 and not in_req_tree([], courses, num, c):  # num not in list(
                    # itertools.chain.from_iterable(courses[c].linked)):
                    ready = False
                    break
            if not ready:
                continue
            
            filled = True
            fill_list[num] = 1
            maxd = 0
            if len(course.requires) > 0:
                min_or_req = 9999
            else:
                min_or_req = 0
            for cl in course.requires:
                maxand = 0
                for c in cl:
                    if not c in courses:
                        print(c)
                        break
                    add = 0
                    if course.is_given_a != course.is_given_b and course.is_given_a == courses[
                        c].is_given_a and course.is_given_b == courses[c].is_given_b:
                        add += 1
                    if courses[c].requirement_depth + 1 + add > maxand:
                        maxand = courses[c].requirement_depth + 1 + add
                if maxand < min_or_req:
                    min_or_req = maxand
            if len(course.linked) > 0:
                min_or_link = 9999
            else:
                min_or_link = 0
            for cl in course.linked:
                for c in cl:
                    if not c in courses:
                        print(c)
                        break
                    maxand = 0
                    add = 0
                    if course.is_given_a != course.is_given_b and course.is_given_a != courses[
                        c].is_given_a and course.is_given_b != courses[c].is_given_b:
                        add += 1
                    if courses[c].requirement_depth + add > maxand:
                        maxand = courses[c].requirement_depth + add
                if maxand < min_or_link:
                    min_or_link = maxand
            course.requirement_depth = max(min_or_link, min_or_req)
            # print('{} {}'.format(course.short_str(), course.requirement_depth))
    
    return courses


def fill_faculties(courses, faculties):
    for num, course in courses.items():
        for key, value in faculties.items():
            if course.number in value:
                course.faculty = key
        if course.faculty == '' and course.number // 1000 in faculties_tmp:
            course.faculty = faculties_tmp[course.number // 1000]
    return courses


def course_fill_all_required(courses, course):
    course.all_required += course.required
    for c in course.required:
        if courses[c].required == []:
            continue
        if courses[c].all_required == []:
            course_fill_all_required(courses, courses[c])
        course.all_required += courses[c].all_required
    course.all_required = sorted(list(set(course.all_required)))
    return course


def fill_all_required(courses):
    for course in courses.values():
        course = course_fill_all_required(courses, course)
    return courses


def shortest_req_list(course, courses, req_list):
    if len(course.linked) > 0:
        linked_best = 0
        depth = 9999
        for i in range(len(course.linked)):
            max = 0
            for x in course.linked[i]:
                if courses[x].requirement_depth > max:
                    max = courses[x].requirement_depth
            if depth > max:
                linked_best = i
                depth = max
        for c in course.linked[linked_best]:
            if c not in req_list:
                req_list.append(c)
                req_list = shortest_req_list(courses[c], courses, req_list)
    
    if len(course.requires) > 0:
        required_best = 0
        depth = 9999
        for i in range(len(course.requires)):
            max = 0
            for x in course.requires[i]:
                if courses[x].requirement_depth > max:
                    max = courses[x].requirement_depth
            if depth > max:
                requires_best = i
                depth = max
        for c in course.requires[required_best]:
            if c not in req_list:
                req_list.append(c)
                req_list = shortest_req_list(courses[c], courses, req_list)
    
    return req_list


def shortest_req_str(course, courses):
    req_list = sorted(shortest_req_list(course, courses, []), key=lambda x: -courses[x].requirement_depth)
    result = 'Shortest requirement list for ' + course.name + ':\n'
    for req in req_list:
        result += '{}: {}\n'.format(courses[req].short_str(), courses[req].requirement_depth)
    return result
