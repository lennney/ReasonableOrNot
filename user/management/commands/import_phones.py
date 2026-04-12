import csv
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from user.models import Phone


class Command(BaseCommand):
    help = 'Import phone data from CSV file'

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, 'phones_data.csv')

        # Pre-fetch existing phones with their PKs for bulk_update
        existing_phones = {p.model: p for p in Phone.objects.all()}
        existing_models = set(existing_phones.keys())

        phones_to_create = []
        phones_to_update = []

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if len(row) < 14:
                    continue

                brand = row[0].strip()
                model = row[1].strip()

                try:
                    price = int(row[2].replace(',', '').replace('无', '0')) if row[2] else 0
                except:
                    price = 0

                cpu = row[3].strip()

                try:
                    ram = int(float(row[4])) if row[4] else 0
                except:
                    ram = 0

                try:
                    rom = int(float(row[5])) if row[5] else 0
                except:
                    rom = 0

                try:
                    charging = int(float(row[6].replace('无', '0'))) if row[6] else 0
                except:
                    charging = 0

                try:
                    battery = int(float(row[7])) if row[7] else 0
                except:
                    battery = 0

                try:
                    screen_refresh = int(float(row[8])) if row[8] else 60
                except:
                    screen_refresh = 60

                screen_res = row[9].strip()

                try:
                    weight = int(float(row[10].replace('无', '0'))) if row[10] else 0
                except:
                    weight = 0

                try:
                    front_cam = int(float(row[11].replace('暂无数据', '0'))) if row[11] else 0
                except:
                    front_cam = 0

                try:
                    rear_cam = int(float(row[12].replace('暂无数据', '0'))) if row[12] else 0
                except:
                    rear_cam = 0

                try:
                    screen_size = float(row[13]) if row[13] else 0.0
                except:
                    screen_size = 0.0

                if model in existing_models:
                    phone = existing_phones[model]
                    phone.brand = brand
                    phone.price = price
                    phone.cpu = cpu
                    phone.ram = ram
                    phone.rom = rom
                    phone.charging = charging
                    phone.battery = battery
                    phone.screen_refresh_rate = screen_refresh
                    phone.screen_resolution = screen_res
                    phone.weight = weight
                    phone.front_camera = front_cam
                    phone.rear_camera = rear_cam
                    phone.screen_size = screen_size
                    phones_to_update.append(phone)
                else:
                    phones_to_create.append(Phone(
                        brand=brand,
                        model=model,
                        price=price,
                        cpu=cpu,
                        ram=ram,
                        rom=rom,
                        charging=charging,
                        battery=battery,
                        screen_refresh_rate=screen_refresh,
                        screen_resolution=screen_res,
                        weight=weight,
                        front_camera=front_cam,
                        rear_camera=rear_cam,
                        screen_size=screen_size,
                    ))

        # Batch operations in a single transaction
        with transaction.atomic():
            if phones_to_update:
                Phone.objects.bulk_update(
                    phones_to_update,
                    ['brand', 'price', 'cpu', 'ram', 'rom', 'charging', 'battery',
                     'screen_refresh_rate', 'screen_resolution', 'weight',
                     'front_camera', 'rear_camera', 'screen_size']
                )
            if phones_to_create:
                Phone.objects.bulk_create(phones_to_create, ignore_conflicts=True)

        count = Phone.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} phones'))