from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pathlib import Path
import json
from decimal import Decimal
import re
from datetime import timedelta
import unicodedata


class Command(BaseCommand):
    help = "Import scraped JSON payloads into Etterem, Etel, EtteremKoltseg and EtteremEtelInfo"

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='*', help='Paths to extracted JSON files. If empty, defaults to data/*.extracted.json')

    def handle(self, *args, **options):
        base = Path.cwd()
        files = options['files'] or []
        if not files:
            files = [str(p) for p in (base / 'data').glob('*.extracted.json')]

        if not files:
            raise CommandError('No files to import. Provide paths or place extracted JSONs in data/*.extracted.json')

        self.stdout.write(f'Importing files: {files}')

        # Import models lazily to avoid startup issues
        from catalog.models import Etel, Etterem
        from billing.models import EtteremKoltseg
        from compare.models import EtteremEtelInfo

        counts = {'etterem_created': 0, 'etel_created': 0, 'koltseg_created': 0, 'info_created': 0,
                  'etterem_updated': 0, 'etel_updated': 0, 'koltseg_updated': 0, 'info_updated': 0}

        # We'll process files but keep a global etel name index to avoid duplicates across files
        def normalize_name(s: str) -> str:
            if not s:
                return ''
            s = str(s).strip().lower()
            s = re.sub(r"\s+", ' ', s)
            # remove diacritics
            s = unicodedata.normalize('NFKD', s)
            s = ''.join(ch for ch in s if not unicodedata.combining(ch))
            return s

        # preload existing Etel objects into a name->object map
        etel_by_norm = {}
        for et in Etel.objects.all():
            etel_by_norm[normalize_name(et.nev)] = et

        for f in files:
            p = Path(f)
            if not p.exists():
                self.stdout.write(self.style.WARNING(f'File not found: {p}'))
                continue
            data = json.loads(p.read_text(encoding='utf-8'))

            # per-file mappings from scraped id -> DB object
            etterem_map = {}
            etel_map = {}

            # 1) Import restaurants and build etterem_map
            for r in data.get('etterem', []):
                scraped_id = r.get('id')
                platform = (r.get('platform') or '').lower()
                platform_url = r.get('platform_url') or r.get('platformUrl') or ''
                name = r.get('nev') or r.get('name') or ''
                address = r.get('cim') or r.get('address') or ''

                etterem = None
                if platform_url:
                    etterem = Etterem.objects.filter(platform=platform, platform_url=platform_url).first()
                if not etterem and name:
                    etterem = Etterem.objects.filter(platform=platform, nev__iexact=name).first()

                if etterem:
                    changed = False
                    if address and etterem.cim != address:
                        etterem.cim = address; changed = True
                    if platform_url and etterem.platform_url != platform_url:
                        etterem.platform_url = platform_url; changed = True
                    if changed:
                        etterem.save(); counts['etterem_updated'] += 1
                else:
                    etterem = Etterem.objects.create(nev=name or 'N/A', cim=address or '', platform=platform or 'egyeb', platform_url=platform_url or '')
                    counts['etterem_created'] += 1

                if scraped_id is not None:
                    etterem_map[str(scraped_id)] = etterem

            # 2) Import foods (deduplicate by normalized name) and build etel_map
            for e in data.get('etel', []):
                scraped_id = e.get('id')
                name = e.get('nev') or e.get('name') or ''
                norm = normalize_name(name)
                desc = e.get('leiras') or e.get('description') or ''
                cat = e.get('kategoria') or e.get('kategoria') or ''
                kep = e.get('kep_url') or e.get('kepUrl') or e.get('kep') or ''

                etel = etel_by_norm.get(norm)
                if etel:
                    changed = False
                    if desc and etel.leiras != desc:
                        etel.leiras = desc; changed = True
                    if cat and etel.kategoria != cat:
                        etel.kategoria = cat; changed = True
                    if kep and etel.kep_url != kep:
                        etel.kep_url = kep; changed = True
                    if changed:
                        etel.save(); counts['etel_updated'] += 1
                else:
                    etel = Etel.objects.create(nev=name or 'N/A', leiras=desc or '', kategoria=cat or '', kep_url=kep or '')
                    etel_by_norm[norm] = etel
                    counts['etel_created'] += 1

                if scraped_id is not None:
                    etel_map[str(scraped_id)] = etel

            # 3) Import costs (etterem_koltseg) using etterem_map
            for k in data.get('etterem_koltseg', []) + data.get('costs', []):
                etterem_id = k.get('etterem_id') or k.get('etteremId')
                koltseg_tipus = k.get('koltseg_tipus') or k.get('tipus') or ''
                osszeg = k.get('osszeg') if k.get('osszeg') is not None else k.get('amount')

                etterem_obj = None
                if etterem_id is not None:
                    etterem_obj = etterem_map.get(str(etterem_id))

                if not etterem_obj:
                    platform_hint = (data.get('etterem') or [{}])[0].get('platform') if data.get('etterem') else None
                    etterem_obj = Etterem.objects.filter(platform=platform_hint).first() if platform_hint else Etterem.objects.first()

                if not etterem_obj:
                    self.stdout.write(self.style.WARNING(f"Skipping cost: could not resolve restaurant for cost entry {k}"))
                    continue

                koltseg_tipus_norm = koltseg_tipus or 'egyeb'
                koltseg, created = EtteremKoltseg.objects.get_or_create(etterem=etterem_obj, koltseg_tipus=koltseg_tipus_norm, defaults={'osszeg': Decimal(0)})
                try:
                    dec = Decimal(osszeg or 0)
                except Exception:
                    dec = Decimal(0)
                if not created:
                    if koltseg.osszeg != dec:
                        koltseg.osszeg = dec; koltseg.save(); counts['koltseg_updated'] += 1
                else:
                    koltseg.osszeg = dec; koltseg.save(); counts['koltseg_created'] += 1

            # 4) Import offers (etterem_etel_info) using etel_map and etterem_map
            for info in data.get('etterem_etel_info', []) + data.get('offers', []):
                etel_id = info.get('etel_id') or info.get('etelId')
                etterem_id = info.get('etterem_id') or info.get('etteremId')
                platform = (info.get('platform') or '').lower() or (data.get('etterem') or [{}])[0].get('platform', '')
                ar = info.get('ar') or info.get('price') or 0
                szallitas_text = info.get('szallitas_ido') or info.get('szallitasIdo') or info.get('szallitas') or ''
                ertek = info.get('felhaszn_ertekeles') or info.get('ertekeles') or None
                promocio = info.get('promocio') if info.get('promocio') is not None else info.get('promo')

                etel_obj = None
                if etel_id is not None:
                    etel_obj = etel_map.get(str(etel_id))
                if not etel_obj:
                    # try match by name in payload
                    for e in data.get('etel', []):
                        if str(e.get('id')) == str(etel_id):
                            etel_obj = etel_by_norm.get(normalize_name(e.get('nev')))
                            break
                if not etel_obj:
                    # fallback: pick any
                    etel_obj = Etel.objects.first()

                etterem_obj = None
                if etterem_id is not None:
                    etterem_obj = etterem_map.get(str(etterem_id))
                if not etterem_obj:
                    # try to resolve by name in payload
                    for r in data.get('etterem', []):
                        if str(r.get('id')) == str(etterem_id):
                            etterem_obj = Etterem.objects.filter(nev__iexact=r.get('nev')).first()
                            break
                if not etterem_obj:
                    etterem_obj = Etterem.objects.filter(platform=platform).first()

                if not etel_obj or not etterem_obj:
                    self.stdout.write(self.style.WARNING(f"Skipping offer: could not resolve etel or etterem for {info}"))
                    continue

                # parse duration
                def parse_duration(text):
                    if not text: return None
                    text = str(text).strip()
                    m = re.search(r"(\d+)", text)
                    if not m: return None
                    n = int(m.group(1))
                    if 'óra' in text or 'ora' in text:
                        return timedelta(hours=n)
                    if 'nap' in text:
                        return timedelta(days=n)
                    return timedelta(minutes=n)

                dur = parse_duration(szallitas_text)
                try:
                    dec_ar = Decimal(ar or 0)
                except Exception:
                    dec_ar = Decimal(0)

                info_obj, created = EtteremEtelInfo.objects.get_or_create(
                    etel=etel_obj, etterem=etterem_obj, platform=platform or 'egyeb',
                    defaults={'ar': dec_ar, 'szallitas_ido': dur, 'felhaszn_ertekelesek': Decimal(ertek) if ertek is not None else None, 'promocio': str(promocio) if promocio is not None else ''}
                )
                if not created:
                    changed = False
                    if info_obj.ar != dec_ar:
                        info_obj.ar = dec_ar; changed = True
                    if dur and info_obj.szallitas_ido != dur:
                        info_obj.szallitas_ido = dur; changed = True
                    if ertek is not None:
                        try:
                            dec_ertek = Decimal(ertek)
                            if info_obj.felhaszn_ertekelesek != dec_ertek:
                                info_obj.felhaszn_ertekelesek = dec_ertek; changed = True
                        except Exception:
                            pass
                    if promocio is not None:
                        promo_text = str(promocio)
                        if info_obj.promocio != promo_text:
                            info_obj.promocio = promo_text; changed = True
                    if changed:
                        info_obj.save(); counts['info_updated'] += 1
                else:
                    counts['info_created'] += 1

        # Summary
        self.stdout.write(self.style.SUCCESS('Import finished. Summary:'))
        for k, v in counts.items():
            self.stdout.write(f'  {k}: {v}')
