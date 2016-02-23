from django.core.management.base import NoArgsCommand
from mapit.models import Area, CodeType


class Command(NoArgsCommand):
    help = "Adds missing gss codes from imports"

    def handle_noargs(self, **options):
        for missing in self.missing_codes():
            print "Looking at adding {missing_code} ({missing_code_type}) to {missing_name} ({missing_type})".format(
                missing_code=missing.code, missing_code_type=missing.code_type().code,
                missing_name=missing.area_name, missing_type=missing.area_type
            ),
            if missing.area():
                if missing.add_code_if_needed():
                    print '- code added'
                else:
                    print '- code already present'
            else:
                print '- ERROR: Area missing!'

    def missing_codes(self):
        return [
            # From Register of Geographic Codes (Jul 2015) UK available via
            # https://geoportal.statistics.gov.uk/geoportal/catalog/main/home.page
            MissingGssCode(code='N07000001', area_type='EUR', area_name='Northern Ireland'),
            # Following 4 from:
            # https://github.gds/gds/puppet/commit/66ff9b9506ef93d6274ded22c263148288cb1400
            MissingOnsCode(code='26UG', area_type='DIS', area_name='St Albans Borough Council'),
            MissingOnsCode(code='26UL', area_type='DIS', area_name='Welwyn Hatfield Borough Council'),
            MissingOnsCode(code='00QL', area_type='UTA', area_name='East Dunbartonshire Council'),
            MissingOnsCode(code='00QS', area_type='UTA', area_name='Glasgow City Council'),
            # Next 1 (and above 2) from:
            # https://github.gds/gds/mapit-scripts/blob/master/README.md#notes
            MissingOnsCode(code='00EM', area_type='UTA', area_name='Northumberland Council'),
            # Following 3 used:
            # http://govuklocal.dafyddvaughan.co.uk/authorities/ to find the missing code
            MissingOnsCode(code='26UD', area_type='DIS', area_name='East Hertfordshire District Council'),
            MissingOnsCode(code='26UH', area_type='DIS', area_name='Stevenage Borough Council'),
            MissingOnsCode(code='00CH', area_type='MTD', area_name='Gateshead Borough Council'),
        ]


class MissingCode(object):
    def __init__(self, code, area_type, area_name):
        self.code = code
        self.area_type = area_type
        self.area_name = area_name

    def area(self):
        if not hasattr(self, '_area'):
            self._area = self._get_area()
        return self._area

    def needs_code(self):
        if self.area():
            return not self.area().codes.filter(type=self.code_type())
        else:
            return False

    def add_code_if_needed(self):
        if self.needs_code():
            self.area().codes.create(type=self.code_type(), code=self.code)
            return True
        else:
            return False

    def _get_area(self):
        return Area.objects.filter(type__code=self.area_type).get(name=self.area_name)


class MissingGssCode(MissingCode):
    @classmethod
    def code_type(cls):
        if not hasattr(cls, '_code_type'):
            cls._code_type = CodeType.objects.get(code='gss')
        return cls._code_type


class MissingOnsCode(MissingCode):
    @classmethod
    def code_type(cls):
        if not hasattr(cls, '_code_type'):
            cls._code_type = CodeType.objects.get(code='ons')
        return cls._code_type