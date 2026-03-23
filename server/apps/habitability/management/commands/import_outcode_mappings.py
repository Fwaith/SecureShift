import csv
import os
from django.core.management.base import BaseCommand
from habitability.models import OutcodeCountyMapping

class Command(BaseCommand):
    help = 'Import outcode-to-county mappings from postcodes_cleaned.csv'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            nargs='?',
            default='postcodes_cleaned.csv',
            help='Path to postcodes_cleaned.csv file (default: postcodes_cleaned.csv in server root)'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        
        # If relative path provided, look in server directory
        if not os.path.isabs(csv_path) and not os.path.exists(csv_path):
            csv_path = os.path.join(os.path.dirname(__file__), '../../../../', csv_path)
        
        csv_path = os.path.abspath(csv_path)
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(
                    f'CSV file not found at {csv_path}'
                )
            )
            return
        
        created_count = 0
        updated_count = 0
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    outcode = row['outcode'].strip()
                    county = row['county'].strip()
                    latitude = row['latitude'].strip()
                    longitude = row['longitude'].strip()
                    
                    lat = float(latitude) if latitude else None
                    lon = float(longitude) if longitude else None
                    
                    mapping, created = OutcodeCountyMapping.objects.update_or_create(
                        outcode=outcode,
                        defaults={'county': county, 'lat': lat, 'lon': lon}
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {created_count} new mappings and updated {updated_count}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error importing CSV: {str(e)}'
                )
            )
