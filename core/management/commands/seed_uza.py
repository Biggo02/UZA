from django.core.management.base import BaseCommand
from django.utils.text import slugify
from marketplace.models import Category
CATEGORIES=['Smartphones','Téléphones classiques','Ordinateurs portables','Ordinateurs de bureau','Tablettes','Téléviseurs','Consoles de jeux','Appareils photo','Caméras','Audio / Son','Montres connectées','Électroménager','Réfrigérateurs','Congélateurs','Machines à laver','Fours','Micro-ondes','Climatiseurs','Ventilateurs','Petits appareils électroménagers','Accessoires électroniques','Autres']
class Command(BaseCommand):
    help='Crée les catégories UZA par défaut'
    def handle(self,*args,**kwargs):
        for name in CATEGORIES:Category.objects.get_or_create(slug=slugify(name),defaults={'name':name})
        self.stdout.write(self.style.SUCCESS(f'{len(CATEGORIES)} catégories UZA prêtes.'))
