from django.core.management.base import BaseCommand
from pathlib import Path

INDEX_DIR = Path('media/.uza_visual_index')

class Command(BaseCommand):
    help = 'Build or rebuild the local UZA visual reference index.'

    def add_arguments(self, parser):
        parser.add_argument('--rebuild', action='store_true', help='Replace the existing index.')

    def handle(self, *args, **options):
        from marketplace.models import ListingImage
        from marketplace.vision_index import build_index

        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        rows = []
        images = ListingImage.objects.select_related('listing', 'listing__category').order_by('listing_id', 'sort_order')
        for item in images.iterator():
            if item.listing.status != 'PUBLISHED':
                continue
            path = Path(item.image.path)
            if not path.exists():
                continue
            rows.append({
                'image_path': str(path),
                'listing_id': item.listing_id,
                'category': item.listing.category.name,
                'brand': item.listing.brand,
                'model': item.listing.model,
                'title': item.listing.title,
            })

        result = build_index(rows, INDEX_DIR, rebuild=options['rebuild'])
        self.stdout.write(self.style.SUCCESS(
            f"Index UZA prêt: {result['vectors']} vecteurs, {result['references']} références, {result['file']}"
        ))
