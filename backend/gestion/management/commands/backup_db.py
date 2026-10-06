import sqlite3
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Copia segura de la base SQLite a DATA_DIR/backups (funciona con el servidor andando).'

    def add_arguments(self, parser):
        parser.add_argument('--conservar', type=int, default=14,
                            help='Cantidad de backups a conservar (default 14)')
        parser.add_argument('--motivo', default='diario',
                            help='Texto que se agrega al nombre del archivo')

    def handle(self, *args, **opts):
        db_path = Path(settings.DATABASES['default']['NAME'])
        if not db_path.exists():
            self.stdout.write('No existe la base todavía, nada para respaldar.')
            return

        destino_dir = Path(settings.DATA_DIR) / 'backups'
        destino_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        destino = destino_dir / f'db-{stamp}-{opts["motivo"]}.sqlite3'

        # backup() de sqlite es consistente aunque haya escrituras en curso
        origen = sqlite3.connect(db_path)
        copia = sqlite3.connect(destino)
        with copia:
            origen.backup(copia)
        copia.close()
        origen.close()
        self.stdout.write(self.style.SUCCESS(f'Backup creado: {destino}'))

        backups = sorted(destino_dir.glob('db-*.sqlite3'))
        for viejo in backups[:-opts['conservar']]:
            viejo.unlink()
