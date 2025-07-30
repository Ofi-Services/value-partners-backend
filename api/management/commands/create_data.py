import csv
from django.core.management.base import BaseCommand
from api.models import Activity, Variant
from django.conf import settings
import os
from datetime import datetime
from collections import defaultdict
import random
from datetime import timedelta
import json
from django.utils import timezone



class Command(BaseCommand):
    """
    Django management command to add data to the database from a CSV file.
    """
    help = 'Add data to the database from CSV file'

    cases = []

    def get_case_index(self, case_id):
        if case_id not in self.cases:
            self.cases.append(case_id)
        return self.cases.index(case_id)

    def create_activities(self, csv_file):
        """
        Reads a CSV file and creates Activity objects in the database.
        Args:
            csv_file (str): Path to the CSV file containing activity data.
        """
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert timestamp string to datetime object
                timestamp = datetime.strptime(row['timestamp'], '%d-%b-%y %I.%M.%S.%f %p')
                print(f"Processing activity for case {row['case_id']} at {timestamp}")
                # Create Activity object
                activity = Activity(
                    case=row['case_id'],
                    timestamp=timestamp,
                    name=row['name'],
                    tpt=float(0),
                    case_index=self.get_case_index(row['case_id'])
                )
                activity.save()

    def create_variants(self, *args, **kwargs):
        """
        Creates and stores variants of activity sequences for cases, along with their statistics.
        This method processes activities to group them into variants based on the sequence of 
        activity names for each case. It calculates the number of cases for each variant, the 
        percentage of cases that belong to each variant, and the average time duration for each 
        variant. The results are stored in the `Variant` model.
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        Workflow:
            1. Retrieve all activities and group them by their associated case IDs.
            2. Track the sequence of activity names for each case and store timestamps for 
               calculating durations.
            3. Group cases into variants based on their activity sequences.
            4. Calculate statistics for each variant:
                - Number of cases in the variant.
                - Percentage of total cases represented by the variant.
                - Average time duration for the variant.
            5. Store the variant data in the `Variant` model.
        Models:
            - `Activity`: Represents individual activities with attributes such as `case` and `timestamp`.
            - `Case`: Represents a case associated with activities.
            - `Variant`: Stores the variant details including activity sequences, associated cases, 
              number of cases, percentage, and average time.
        Raises:
            Any exceptions raised by the ORM methods `get_or_create` or `create` will propagate.
        Note:
            - The method assumes that the `Activity` model has `case`, `timestamp`, and `name` attributes.
            - The `Variant` model must have fields `activities`, `cases`, `number_cases`, `percentage`, 
              and `avg_time`.
        """

        # List of cases to keep track of existing cases and identify case_index
        cases = []
        variants = defaultdict(list)
        timesPerCase = defaultdict(list)
        activities = Activity.objects.all()
    
        for activity in activities:
            case_id = activity.case
    
            if case_id not in cases:
                cases.append(case_id)
            case_index = cases.index(case_id)
            timestamp = activity.timestamp
    
            name = activity.name
    
            # Store the timestamp for calculating mean time
            timesPerCase[case_id].append(timestamp)
    
    
            # Append activity name to the variants dictionary
            variants[case_id].append(name)
    
        # Grouping keys by their value lists
        grouped_data = defaultdict(list)
        for key, value in variants.items():
            grouped_data[tuple(value)].append(key)
    
        # Convert defaultdict to a regular dictionary and print the result
        grouped_data = dict(grouped_data)
    
        for key, value in grouped_data.items():
            number_cases = len(value)
            percentage = (number_cases / len(cases)) * 100
    
            # Calculate mean time for the variant
            total_duration = 0
            for case_id in value:
                times = timesPerCase[case_id]
                times.sort()
                duration = (times[-1] - times[0]).total_seconds()
                total_duration += duration
            mean_time = total_duration / number_cases
    
            Variant.objects.create(
                activities=str(key),
                cases=str(value),
                number_cases=number_cases,
                percentage=percentage,
                avg_time=mean_time
            )

    def add_TPT(self):
        """
        Calculates and updates the Time Processing Time (TPT) for each activity in the database.
        This method iterates through all distinct case indices in the `Activity` model, retrieves
        the activities associated with each case index, and calculates the time difference (in seconds)
        between consecutive activities based on their timestamps. The calculated time difference is
        then stored in the `tpt` field of the current activity.
        Steps:
        1. Retrieve a list of distinct `case_index` values from the `Activity` model.
        2. For each `case_index`, fetch and order the associated activities by their `timestamp`.
        3. Iterate through the activities and calculate the time difference between consecutive
           activities.
        4. Update the `tpt` field of the current activity with the calculated time difference.
        Note:
        - The `tpt` field is updated only for activities that have a subsequent activity in the
          ordered list.
        Raises:
            AttributeError: If the `Activity` model does not have the required fields (`case_index`,
                            `timestamp`, `tpt`).
            ValueError: If the `timestamp` field contains invalid or non-datetime values.
        """
        index_list = Activity.objects.values_list('case_index', flat=True).distinct()
        for index in index_list:
            activities = Activity.objects.filter(case_index=index).order_by('timestamp')

            for i in range(len(activities) - 1):
                current_activity = activities[i]
                current_id = current_activity.id
                next_activity = activities[i + 1]

                time_diff = (next_activity.timestamp - current_activity.timestamp).total_seconds()
                Activity.objects.filter(id=current_id).update(tpt=time_diff)
   

    def get_case_activity_time(self):
        """
        Retrieves and organizes activity data grouped by case ID.
        This method fetches all activities from the database, groups them by their associated case ID,
        and returns a dictionary where each key is a case ID and the value is a list of dictionaries
        containing activity details such as the activity name and its timestamp.
        Returns:
            defaultdict: A dictionary where keys are case IDs and values are lists of dictionaries
            with activity details. Each dictionary in the list contains:
                - "ACTIVIDAD": The name of the activity.
                - "TIMESTAMP": The timestamp of the activity.
        """


        timesPerActivity = defaultdict(list)
        activities = Activity.objects.all()
        for activity in activities:
            timesPerActivity[activity.case.id].append({"ACTIVIDAD": activity.name, "TIMESTAMP": activity.timestamp})
        return timesPerActivity

    def get_mean_time_per_activity(self, timesPerActivity):
        """
        Calculate the mean time spent on each activity based on the provided activity timestamps.
        Args:
            timesPerActivity (dict): A dictionary where the keys are case IDs and the values are lists of 
                                     dictionaries representing activities. Each activity dictionary must 
                                     contain the keys "TIMESTAMP" (a datetime object) and "ACTIVIDAD" 
                                     (the name of the activity).
        Returns:
            str: A JSON-formatted string representing the mean time (in seconds) spent on each activity.
                 The JSON object has activity names as keys and their corresponding mean durations as values.
        Example:
            Input:
                timesPerActivity = {
                    "case1": [
                        {"TIMESTAMP": datetime(2023, 1, 1, 10, 0), "ACTIVIDAD": "A"},
                        {"TIMESTAMP": datetime(2023, 1, 1, 10, 30), "ACTIVIDAD": "B"}
                    ],
                    "case2": [
                        {"TIMESTAMP": datetime(2023, 1, 1, 11, 0), "ACTIVIDAD": "A"},
                        {"TIMESTAMP": datetime(2023, 1, 1, 11, 45), "ACTIVIDAD": "B"}
                    ]
                }
            Output:
                {
                    "A": 1800.0,
                    "B": 2700.0
                }
        """
        activity_durations = defaultdict(list)
        for case_id, activities in timesPerActivity.items():
            for i in range(len(activities) - 1):
                current_activity = activities[i]
                next_activity = activities[i + 1]
                current_timestamp = current_activity["TIMESTAMP"]
                next_timestamp = next_activity["TIMESTAMP"]
                duration = abs(next_timestamp - current_timestamp)
                activity_durations[current_activity["ACTIVIDAD"]].append(duration.total_seconds())

        mean_time_per_activity = {}
        for activity, durations in activity_durations.items():
            mean_time_per_activity[activity] = sum(durations) / len(durations)

        mean_time_per_activity_json = json.dumps(mean_time_per_activity, indent=4)
        print(mean_time_per_activity_json)
        return mean_time_per_activity_json
    

    def handle(self, *args, **kwargs):
        """
        Handle the command to add data to the database from the CSV file.
        """
       
        self.create_activities(os.path.join(settings.BASE_DIR, 'api', 'data', 'activities.csv'))
        self.stdout.write(self.style.SUCCESS('Activities added'))
        self.stdout.write(self.style.SUCCESS('Adding TPT'))
        self.add_TPT()

        self.stdout.write(self.style.SUCCESS('Creating variants'))
        self.create_variants()

        #self.stdout.write(self.style.SUCCESS('Data added successfully'))

       # self.get_mean_time_per_activity(self.get_case_activity_time())
