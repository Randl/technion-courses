def get_deepest(courses, num=20, faculty='', existing=False):
    if faculty == '':
        choice = [x for x in courses.values()]
    else:
        choice = [x for x in courses.values() if x.faculty == faculty]
    if existing:
        choice = [x for x in choice if x.is_given == True]
    
    deepest = sorted(choice, key=lambda x: -x.requirement_depth)
    return deepest[:num]


def get_most_points(courses, num=20, faculty='', existing=False):
    if faculty == '':
        choice = [x for x in courses.values()]
    else:
        choice = [x for x in courses.values() if x.faculty == faculty]
    if existing:
        choice = [x for x in choice if x.is_given == True]
    
    deepest = sorted(choice, key=lambda x: -x.credit_points)
    return deepest[:num]


def find(courses, text, faculty='', existing=False, exact=False):
    if not exact:
        text = text.lower().strip()
    if faculty == '':
        choice = [x for x in courses.values()]
    else:
        choice = [x for x in courses.values() if x.faculty == faculty]
    if existing:
        choice = [x for x in choice if x.is_given == True]
    
    found = []
    for course in choice:
        if text in course.name.lower() or text in course.description.lower():
            found.append(course)
    
    return found


def print_and_find(courses, text, faculty='', existing=False, exact=False, sort_by_depth=True):
    if sort_by_depth:
        t = sorted(find(courses, text, faculty, existing, exact), key=lambda x: -x.requirement_depth)
    else:
        t = find(courses, text, faculty, existing, exact)
    print('{} courses:'.format(text))
    for c in t:
        print('{}: {}'.format(c.short_str(), c.requirement_depth))
    print('\n\n')
