CREATE = 'CREATE'
UPDATE = 'UPDATE'
RESOLUTION_ADD = 'RESOLUTION_ADD'
SOLUTION_ASSOCIATION = 'SOLUTION_ASSOCIATION'
RESOLUTION_UPDATE = 'RESOLUTION_UPDATE'
RESOLVED = 'RESOLVED'
DELETE = 'DELETE'
RESTORE = 'RESTORE'
REQ_CONVER = 'REQ_CONVER'
SLA_VIOLATION = 'SLA_VIOLATION'
ADD_REQUEST_TASK = 'ADD_REQUEST_TASK'
COMPLETED = 'COMPLETED'
CLOSE = 'CLOSE'

ACTIVITY_CHOICES = [
    (CREATE, 'Create'),
    (UPDATE, 'Update'),
    (RESOLUTION_ADD, 'Resolution Add'),
    (SOLUTION_ASSOCIATION, 'Solution Association'),
    (RESOLUTION_UPDATE, 'Resolution Update'),
    (RESOLVED, 'Resolved'),
    (DELETE, 'Delete'),
    (RESTORE, 'Restore'),
    (REQ_CONVER, 'Req Conver'),
    (SLA_VIOLATION, 'SLA Violation'),
    (ADD_REQUEST_TASK, 'Add Request Task'),
    (COMPLETED, 'Completed'),
    (CLOSE, 'Close'),
]

PATTERN_CHOICES = [
    ('Similar Value', 'Similar Value'),
    ('Similar Reference', 'Similar Reference'),
    ('Exact Match', 'Exact Match'),
    ('Similar Date', 'Similar Date'),
    ('Similar Vendor', 'Similar Vendor'),
    ('Multiple', 'Multiple'),
]

