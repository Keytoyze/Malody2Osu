from django.test import TestCase
from app.converter import malody_osu
from django.template import loader


# Create your tests here.

class Malody2OsuTest(TestCase):
    def test_conversion(self):
        print(malody_osu.mc_osu_v14(loader.render_to_string('mc.json'))[0])
