from django.test import TestCase
from app.converter import mc_osu
from django.template import loader


# Create your tests here.

class Malody2OsuTest(TestCase):
    @staticmethod
    def test_conversion():
        re = mc_osu.mc_osu_v14(loader.render_to_string('mc.json'))
        if not re[1]:
            raise re[0]
        print(re[0])
