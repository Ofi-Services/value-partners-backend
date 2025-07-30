import csv
from django.core.management.base import BaseCommand
from api.models import Case, Activity, Variant, Inventory, OrderItem, Supplier, CatalogItems, Invoice, Contract, GoodRecevied
from django.conf import settings
import os
from datetime import datetime
from collections import defaultdict
import random
from datetime import timedelta
from ..constants import NAMES, BRANCHES, SUPPLIERS
import json
from django.utils import timezone
from ..utils.duplicate_utils import create_invoice



class Command(BaseCommand):
    """
    Django management command to add data to the database from a CSV file.
    """
    help = 'Add data to the database from CSV file'

    cases_ids = []


    def add_case_ids(self, case_id):
        """
        Add a case ID to the list of case IDs.
        """
        if case_id not in self.cases_ids:
            self.cases_ids.append(case_id)

    def create_cases(self):
        """
        Creates a list of cases with random attributes and saves them to the database.
        This method generates a list of cases with random attributes such as case type, timestamps, 
        branch, client, creator, and insurance details. It also determines the insurance creation, 
        start, and end dates based on a random condition. The cases are then saved to the database.
        """
        for i in range(1000):
            case = Case.objects.create(
                id=i,
                order_date=self.random_date(),
                branch=random.choice(BRANCHES),
                supplier=random.choice(SUPPLIERS),
                total_price=random.randint(1000, 10000),
                estimated_delivery=self.random_date(),
                delivery=self.random_date(),
                on_time=random.choice([True, False]),
                in_full=random.choice([True, False]),
                number_of_items=random.randint(1, 10),
                ft_items=random.randint(0, 5)
            )
            self.add_case_ids(case.id)
    def random_date(self):
        start = datetime(2025, 1, 1)
        day = random.randint(0, 97)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return start + timedelta(days=day, hours=hour, minutes=minute, seconds=second)
    


    def save_activity(self, case_info: dict, activity):


        
        #Get the case and create the activity
        case = Case.objects.get(id=case_info['case_id'])
        print('SAVE ACTIVITY', case_info['case_id'], 'ACTIVITY', activity)
        Activity.objects.create(
            case=case,
            timestamp=case_info['last_timestamp'],
            name=activity,
            user=case_info['user'],
            user_type=case_info['user_type'],
            automatic=case_info['automatic'],
            rework=case_info['rework'],
            case_index= case.id
        )
        print('ACTIVITY', activity, 'CASE', case_info['case_id'], 'TIMESTAMP', case_info['last_timestamp'])


    def update_case(self, case_info: dict, activity):
        """
        Updates the state and last timestamp of a given case, and synchronizes the changes
        with the corresponding database entry. Additionally, logs the update to a file.
        Args:
            case (Case): The case object to be updated.
            activity: The new state/activity to assign to the case.
        Side Effects:
            - Modifies the `last_timestamp` and `state` attributes of the provided `case` object.
            - Updates the corresponding database entry for the case with the new state.
            - Writes the updated case information and activity to a file.
        Raises:
            Case.DoesNotExist: If no case with the given `case_id` exists in the database.
        """
        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))
        print('UPDATE CASE', case_info['case_id'], 'ACTIVITY', activity)
        self.save_activity(case_info, activity)

    def start(self, case_id):
        """
        Simulates the creation of a dummy case with randomized attributes and stores it in the database.
        The method generates a case with random attributes such as case type, timestamps, branch, 
        client, creator, and insurance details. It also determines the insurance creation, start, 
        and end dates based on a random condition. The case is then saved to the database, and 
        additional actions are performed based on the case type.
        Actions:
        - If the case type is 'Policy onboarding', the `ingresar_tramite` method is called.
        - If the case type is 'Renewal', there is a 50% chance that the `visado` method is called.
        - The `registro_de_compromiso` method is always called for the case.
        Attributes:
            case_type (str): The type of the case, randomly chosen from 'Renewal', 'Issuance', or 'Policy onboarding'.
            case_id (str): A unique identifier for the case.
            initial_timestamp (datetime): The initial timestamp for the case, randomized within a specific range.
            value (int): The monetary value associated with the case, randomized between 1000 and 10000.
            insurance (str): A randomly generated insurance number.
            insurance_creation (datetime): The timestamp for when the insurance was created.
            insurance_start (datetime): The start date of the insurance.
            insurance_end (datetime): The end date of the insurance.
        Database:
            Creates a `Case` object in the database with the generated attributes.
        Raises:
            None
        Returns:
            None
        """

        print('STARTING CASE', case_id)
        case = Case.objects.get(id=case_id)
        case_info = {}
        case_info['case_id'] = case_id
        case_info['last_timestamp'] = case.order_date
        self.order_creation(case_info)


    def order_creation(self, case_info: dict):
        """
        Add a record of commitment to the database.

        Args:
            case_id (str): The ID of the case.
            initial_timestamp (datetime): The initial timestamp.
            case_type (str): The type of the case.
        """
        print('ORDER CREATION', case_info['case_id'])
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = False
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))




        self.update_case(case_info, 'Order Creation')
        
        self.order_approval(case_info)

    def order_approval(self, case_info: dict):
        """
        Simulates the order approval process for a case.
        Args:
            case_info (dict): A dictionary containing information about the case.
        """
        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = False
        case_info['rework'] = True
        self.save_activity(case_info, 'Order Approval')
        random_number = random.random()
        if random_number < 0.9:  
            self.send_to_supplier(case_info)
            
        elif random_number < 0.95:
            self.order_modification(case_info)
        else:
            self.order_cancelation(case_info)

    
    def order_modification(self, case_info: dict):
        """
        Simulates the order modification process for a case.
        Args:
            case_info (dict): A dictionary containing information about the case.
        """
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = random.choice([True, False])
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Order Modification')

        self.order_approval(case_info)

    def order_cancelation(self, case_info: dict):
        """
        Simulates the order cancellation process for a case.
        Args:
            case_info (dict): A dictionary containing information about the case.
        """
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = True
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Order Cancellation')

    

    def send_to_supplier(self, case_info: dict):

        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = True
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Send to Supplier')

        self.get_confirmation(case_info)
    
    def get_confirmation(self, case_info: dict):
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = random.choice([True, False])
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Get Confirmation from Supplier')

        random_number = random.random()

        if random_number < 0.9:
            self.receive_shipment_confirmation(case_info)
        elif random_number < 0.95:
            self.order_modification(case_info)
        else:
            self.order_cancelation(case_info)
    
    def receive_shipment_confirmation(self, case_info: dict):
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = random.choice([True, False])
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Receive Shipment Confirmation from Supplier')

        self.receive_invoice(case_info)
    

    def receive_invoice(self, case_info: dict):
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = random.choice([True, False])
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        case = Case.objects.get(id=case_info['case_id'])
        self.save_activity(case_info, 'Receive Invoice')
        #get the Order_items of this case
        order_items = OrderItem.objects.filter(order=case)
        for item in order_items:
            quantity = item.quantity
            unit_price = item.unit_price
            create_invoice(date = case_info['last_timestamp'], case=case, quantity=quantity, unit_price=unit_price)

        self.receive_materials(case_info)

    def receive_materials(self, case_info: dict):
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = False
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Receive Materials')

        random_number = random.random()
        if random_number < 0.9:
            self.material_inspection(case_info)
        else:
            self.receive_materials(case_info)

    def material_inspection(self, case_info: dict):
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = 'Manager'
        case_info['automatic'] = False
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Verify Materials')

        random_number = random.random()
        if random_number < 0.9:
            self.material_acceptance(case_info)
        elif random_number < 0.95:
            case_info['user'] = random.choice(NAMES)
            case_info['user_type'] = 'Manager'
            case_info['automatic'] = False
            case_info['rework'] = True

            case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

            self.save_activity(case_info, 'Return Materials')

            self.send_to_supplier(case_info)
        else:
            self.order_cancelation(case_info)
    
    def material_acceptance(self, case_info: dict):
        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = True
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Accept Materials')

        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = False
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Integrate to Inventory')

        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = random.choice([True, False])
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Payment')

        case_info['user'] = random.choice(NAMES)
        case_info['user_type'] = random.choice(['Manager', 'Agent', 'Analyst'])
        case_info['automatic'] = False
        case_info['rework'] = True

        case_info['last_timestamp'] +=  timedelta(hours=random.expovariate(1/24))

        self.save_activity(case_info, 'Distribute Materials')
        

    def add_inventory(self):
        # Path to the CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'Inventory.csv')

        # Read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                product_code = row['Product Code']
                product_name = row['Product Name']
                current_stock = row['Quantity']
                unit_price = row['Unit Price']

                # Create the Inventory
                Inventory.objects.create(
                    product_code=product_code,
                    product_name=product_name,
                    current_stock=current_stock,
                    unit_price=unit_price,
                    new_product=False
                )
                random_number = random.random()
                if random_number < 0.9:
                    #Create contract
                    supplier_index = hash(product_name.lower) % len(SUPPLIERS)
                    supplier_name = SUPPLIERS[supplier_index]
                    supplier = Supplier.objects.filter(name=supplier_name).first()
                    contract = Contract.objects.create(
                        supplier=supplier,
                    )
                CatalogItems.objects.create(
                    product_code=product_code,
                    product_name=product_name,
                    contract=contract,
                )
               
        self.stdout.write(self.style.SUCCESS('Inventory and catalogue data added successfully'))

    def create_goods(self):
        """
        Create goods in the database.
        """
        invoices = Invoice.objects.all()
        for invoice in invoices:
            #Get the case for the invoice
            random_num = random.random()
            quantity_change = 0
            if random_num < 0.1:
                quantity_change = random.randint(-2, 2)
            orderItem = OrderItem.objects.filter(
                order=invoice.case,
                quantity=invoice.quantity,
                unit_price=invoice.unit_price
            ).first()
            
            if not orderItem:
                self.stdout.write(self.style.WARNING(f"OrderItem not found for Invoice ID {invoice.id}"))
                continue

            catalog_item = CatalogItems.objects.filter(
                product_code=orderItem.material_code,
            ).first()
            print('CATALOG ITEM', catalog_item)
            if not catalog_item or not catalog_item.contract:
                self.stdout.write(self.style.WARNING(f"Contract not found for Product Code {orderItem.material_code}"))
                continue

            good_received = GoodRecevied.objects.create(
                unit_price=invoice.unit_price,
                quantity=invoice.quantity + quantity_change,
                invoice=invoice,
                contract=catalog_item.contract,
                product_code=orderItem.material_code,
            )
            if good_received:
                self.stdout.write(self.style.SUCCESS(f"GoodReceived created successfully for Invoice ID {invoice.id}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create GoodReceived for Invoice ID {invoice.id}"))


        self.stdout.write(self.style.SUCCESS('Goods data added successfully'))


    def find_product_code(self, product_name):
        """
        Find the product code for a given product name.
        """
        product_names = Inventory.objects.values_list('product_name', flat=True)

        for name in product_names:
            if name.strip().lower() == product_name.strip().lower():

                code = Inventory.objects.filter(product_name=name).first().product_code
               
                return code
            
    def add_Orders_Items(self):
        # Path to the CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'api', 'data', 'Orders_with_suppliers.csv')
    
        # Read the CSV file
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
    
            for row in reader:
                id = row['order_id']
                total_price = row['total_price']
                order_date_str = row['order_date']
                employee_id = row['employee_id']
                is_free_text = row['is_free_text'] == 'True'
                suggestion = None
                confidence = None
    
                # Check if order_date is empty
                if not order_date_str:
                    self.stdout.write(self.style.WARNING(f"Skipping row with empty order_date for order_id {id}"))
                    continue
    
                # Convert order_date to the correct format
                try:
                    order_date = datetime.strptime(order_date_str, '%m/%d/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Invalid date format for order_id {id}: {order_date_str}"))
                    continue
    
                if is_free_text:
                    prediction = row['Prediction']
                    probability = row['Probability']
                    product_code = self.find_product_code(prediction)
                    suggestion = Inventory.objects.filter(product_code=product_code).first()
                    confidence = float(probability) * 100
    
                # Get order to see if it already exists
                order = Case.objects.filter(id=id).first()
    
                estimated_delivery_offset = timedelta(0)
                on_time = True
                in_full = True
                if random.random() < 0.1:  # 10% chance
                    estimated_delivery_offset += timedelta(days=2)
                    on_time = False
                if random.random() < 0.1:  # 10% chance
                    in_full = False
    
                if is_free_text:
                    ft_items = 1
                else:
                    ft_items = 0
    
                if order is not None:
                    self.add_case_ids(id)
                    order.total_price += int(total_price)
                    order.number_of_items += 1
                    if is_free_text:
                        order.ft_items += 1
    
                    order.save()
                else:
                    supplier = Supplier.objects.filter(name=row['supplier']).first()
                    order = Case.objects.create(
                        id=id,
                        total_price=total_price,
                        order_date=order_date,
                        employee_id=employee_id,
                        branch=random.choice(BRANCHES),
                        supplier=supplier,
                        estimated_delivery=datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=15),
                        delivery=datetime.strptime(order_date, '%Y-%m-%d') + timedelta(days=15) + estimated_delivery_offset,
                        on_time=on_time,
                        in_full=in_full,
                        number_of_items=1,
                        ft_items=ft_items,
                    )
    
                OrderItem.objects.create(
                    order=order,
                    material_name=row['material_name'],
                    material_code=row['material_code'],
                    quantity=row['quantity'],
                    unit_price=row['unit_price'],
                    is_free_text=row['is_free_text'].lower() == 'true',
                    suggestion=suggestion,
                    confidence=confidence,
                )
    
        self.stdout.write(self.style.SUCCESS('Order data added successfully'))


    def add_reworks(self):
        activity_names = [
            "Order Creation",
            "Order Approval",
            "Send to Supplier",
            "Get Confirmation from Supplier",
            "Receive Shipment Confirmation from Supplier",
            "Receive Materials",
            "Verify Materials",
            "Accept Materials",
            "Integrate to Inventory",
            "Payment",
            "Order Modification",
            "Return Materials",
            "Distribute Materials",
            "Order Cancellation",
            "Receive Invoice",
        ]
        for case in Case.objects.all():
            activities = Activity.objects.filter(case=case).order_by('timestamp')
            for name in activity_names:
                activity = activities.filter(name=name).first()
                if activity:
                    activity.rework = False
                    activity.save()


    def  create_variants(self, *args, **kwargs):
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
            case_id = activity.case.id
    
            if case_id not in cases:
                cases.append(case_id)
            case_index = cases.index(case_id)
            timestamp = activity.timestamp
    
            name = activity.name
    
            # Store the timestamp for calculating mean time
            timesPerCase[case_id].append(timestamp)
    
            # Get or create the case
            case, created = Case.objects.get_or_create(id=case_id)
    
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
    
    def add_time_to_cases(self):
        """
        Calculates and assigns the average time (in seconds) between the first and last activities
        for each case in the database.

        This method iterates through all cases, retrieves their associated activities ordered
        by timestamp, and computes the time difference between the first and last activities.
        The computed average time is then saved to the `avg_time` field of each case.

        Note:
            - Assumes that the `Case` model has an `avg_time` field to store the calculated value.
            - Assumes that the `Activity` model has a `timestamp` field and a foreign key to `Case`.

        Raises:
            AttributeError: If any case has no associated activities, as `first()` or `last()` 
                            would return `None` and accessing `timestamp` would fail.
        """
        cases = Case.objects.all()
        for case in cases:
            activities = Activity.objects.filter(case=case).order_by('timestamp')
            if not activities.exists():
                self.stdout.write(self.style.ERROR(f'CASE {case.id} HAS NO ACTIVITIES'))
                continue
            if case.avg_time == 0:
                last_activity = activities.last()
                first_activity = activities.first()
                case.avg_time = (last_activity.timestamp - first_activity.timestamp).total_seconds()
                case.save()

    def create_suppliers(self):
        """
        Create suppliers in the database.
        """
        for supplier in SUPPLIERS:
            supplier_obj, created = Supplier.objects.get_or_create(name=supplier)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Supplier {supplier} created.'))
            else:
                self.stdout.write(self.style.WARNING(f'Supplier {supplier} already exists.'))

    def handle(self, *args, **kwargs):
        """
        Handle the command to add data to the database from the CSV file.
        """
        self.create_suppliers()
        self.stdout.write(self.style.SUCCESS('Suppliers Added'))
        self.add_inventory()
        self.stdout.write(self.style.SUCCESS('Inventory Added'))
        self.add_Orders_Items()
        self.stdout.write(self.style.SUCCESS('Order Items added'))
        for id in self.cases_ids:
            print('case -------------', id)
            self.start(id)
        self.stdout.write(self.style.SUCCESS('Cases added'))
        self.create_goods()
        self.stdout.write(self.style.SUCCESS('Goods added'))

        self.stdout.write(self.style.SUCCESS('Activities added'))
        self.add_reworks()
        self.stdout.write(self.style.SUCCESS('Reworks added'))

        self.stdout.write(self.style.SUCCESS('Adding time to cases'))
        self.add_time_to_cases()
        self.stdout.write(self.style.SUCCESS('Creating variants'))
        self.create_variants()
        self.stdout.write(self.style.SUCCESS('Adding TPT'))
        self.add_TPT()
        self.stdout.write(self.style.SUCCESS('Data added successfully'))

        self.get_mean_time_per_activity(self.get_case_activity_time())
